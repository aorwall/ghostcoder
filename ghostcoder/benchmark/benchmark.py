import json
import logging
import shutil
from datetime import datetime
from itertools import groupby
from pathlib import Path
from typing import Optional, List

from IPython.core.display import Markdown, Pretty
from IPython.core.display_functions import display, update_display
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from codeblocks import create_parser, CodeBlock, CodeBlockType
from ghostcoder import FileRepository
from ghostcoder.actions import WriteCodeAction
from ghostcoder.benchmark.prompts import FEEDBACK_SYSTEM_PROMPT
from ghostcoder.callback import LogCallbackHandler
from ghostcoder.llm import LLMWrapper
from ghostcoder.schema import UpdatedFileItem, TextItem, Message, FileItem, VerificationFailureItem, VerificationResult, \
    CodeItem
from ghostcoder.verify.verify_java_mvn_junit5 import JavaMvnUnit5Verifier
from ghostcoder.verify.verify_python_unittest import PythonUnittestVerifier

logger = logging.getLogger(__name__)


class BenchmarkFeedback(BaseModel):
    correct: bool = Field(description="If the submitted code is correct.")
    correctness_feedback: str = Field(description="The feedback to the candidate about if it's correct.", )
    compliant: bool = Field(
        description="If the submitted code is compliant with the requirements and evaluation criteria.")
    compliance_feedback: str = Field(description="The feedback to the candidate about if it's compliant.")
    extra_code: bool = Field(description="If there is extra code in the submission.")
    extra_code_feedback: str = Field(description="The feedback to the candidate about if there is extra code.")
    tests_correct: bool = Field(description="If your tests are correct.")
    tests_feedback: str = Field(
        description="The feedback to the candidate why their implementation didn't pass your tests or if the tests needs to be fixed.")


class BenchmarkResult(BaseModel):
    exercise: str
    success: bool
    retries: int
    result_dir: str
    llm_name: str
    llm_params: dict
    verification_result: VerificationResult = None
    no_change_arguments: Optional[str] = None
    feedback: Optional[BenchmarkFeedback] = None


class Benchmark:

    def __init__(self,
                 llm: LLMWrapper,
                 llm_name: str,
                 exercises_dir: Path,
                 benchmarks_dir: Path,
                 language: str = "python",
                 reviewer_llm: LLMWrapper = None,
                 llm_params: dict = {},
                 max_retries: int = 2,
                 stubs_with_comments: bool = False):
        self.llm = llm
        self.reviewer_llm = reviewer_llm
        self.language = language
        self.llm_name = llm_name
        self.llm_params = llm_params
        self.exercises_dir = exercises_dir
        self.benchmark_result_dir = self.create_test_dir(benchmarks_dir)
        self.stubs_with_comments = stubs_with_comments
        self.max_retries = max_retries
        self.feedback_parser = PydanticOutputParser(pydantic_object=BenchmarkFeedback)

    def run_exercise(self, exercise: str):
        exercise_benchmark_result_dir = self.copy_exercise(exercise=exercise)

        log_dir = exercise_benchmark_result_dir / "prompt_log"
        self.llm.llm.callbacks = [LogCallbackHandler(str(log_dir))]
        self.reviewer_llm.llm.callbacks = [LogCallbackHandler(str(log_dir))]

        test_repo = FileRepository(repo_path=str(exercise_benchmark_result_dir), use_git=False)
        action = WriteCodeAction(llm=self.llm, repository=test_repo, auto_mode=True)

        display(Pretty(f"Running benchmark on exercise *{exercise}*"),
                display_id=str(exercise_benchmark_result_dir))

        benchmark_result = self._run_exercise(
            exercise=exercise,
            action=action,
            exercise_benchmark_result_dir=exercise_benchmark_result_dir
        )

        benchmark_result = self.review_benchmark_result(
            benchmark_result=benchmark_result,
            exercise_benchmark_result_dir=exercise_benchmark_result_dir)

        with open(exercise_benchmark_result_dir / "result.json", "w") as f:
            json.dump(benchmark_result.dict(), f, indent=2)

        return benchmark_result

    def _run_exercise(self,
                      exercise: str,
                      exercise_benchmark_result_dir: Path,
                      action: WriteCodeAction,
                      language: str = "python",
                      verification_failure: VerificationResult = None,
                      retry: int = 0):
        logger.info(f"Will try to solve [{exercise}], retry: {retry}/{self.max_retries}")

        instruction_file = exercise_benchmark_result_dir / "instructions.md"
        instructions = instruction_file.read_text()
        implementation_file = f"{exercise}.py"  # TODO: Not only python
        implementation_file_full_path = Path(exercise_benchmark_result_dir / implementation_file)

        contents_before = implementation_file_full_path.read_text()

        if retry == 0:
            message = Message(sender="Human", items=[
                TextItem(text=instructions),
                TextItem(text=f"""Use the above instructions to modify the supplied files: {implementation_file}
Keep and implement the existing function or class stubs, they will be called from existing unit tests.
Only use standard python libraries, don't suggest installing any packages."""),
                FileItem(file_path=implementation_file)
            ])

        else:
            message = Message(sender="Human", items=[
                TextItem(text=instructions),
                FileItem(file_path=implementation_file),
                TextItem(text=f"""The tests failed. 
The tests are correct and should not be changed.
Fix the code in {implementation_file} to resolve the errors.""")
            ])

            message.items.extend(verification_failure.failures)

            test_files = self.get_test_files(failures=verification_failure.failures,
                                             exercise_benchmark_result_dir=exercise_benchmark_result_dir)
            message.items.extend(test_files)

        response_messages = action.execute(message=message)
        response_message = response_messages[-1]

        if contents_before == implementation_file_full_path.read_text():
            arguments = ""
            for item in response_message.items:
                if isinstance(item, TextItem):
                    arguments = item.to_prompt() + "\n\n"

            update_display(Pretty(f"No updated files, benchmark failed after retry {retry} the implementation can "
                                  f"be found in directory {str(exercise_benchmark_result_dir)}"),
                           display_id=str(exercise_benchmark_result_dir))
            logger.info(f"No changed found in file {implementation_file}.\nResponse message:\n{arguments}")
            return BenchmarkResult(
                success=False,
                exercise=exercise,
                llm_name=self.llm_name,
                llm_params=self.llm_params,
                result_dir=str(exercise_benchmark_result_dir),
                verification_result=verification_failure,
                no_change_arguments=arguments,
                retries=retry)

        if self.language == "java":
            verifier = JavaMvnUnit5Verifier(current_dir=exercise_benchmark_result_dir)
        elif self.language == "python":
            verifier = PythonUnittestVerifier(current_dir=exercise_benchmark_result_dir)
        else:
            raise ValueError(f"Unsupported language {self.language}")

        verification_result = verifier.verify()

        if verification_result.success:
            update_display(Pretty(f"Tests passed, benchmark succeeded after retry {retry}, "
                                  f"the implementation can be found in `{str(exercise_benchmark_result_dir)}`"),
                           display_id=str(exercise_benchmark_result_dir))
            logger.info(f"Tests passed successfully")
            return BenchmarkResult(
                success=True,
                exercise=exercise,
                llm_name=self.llm_name,
                llm_params=self.llm_params,
                result_dir=str(exercise_benchmark_result_dir),
                retries=retry)
        elif retry < self.max_retries:
            update_display(Pretty(data=f"{len(verification_result.failures)} out of "
                                       f"{verification_result.verification_count} tests failed, will do retry "
                                       f"{retry + 1}/{self.max_retries}"),
                           display_id=str(exercise_benchmark_result_dir))
            logger.info(f"Tests failed, will retry")
            return self._run_exercise(
                exercise=exercise,
                action=action,
                exercise_benchmark_result_dir=exercise_benchmark_result_dir,
                language=language,
                verification_failure=verification_result,
                retry=retry + 1)
        else:
            update_display(Pretty(f"{len(verification_result.failures)} out of {verification_result.verification_count}"
                                  f" tests failed failed after retry {retry}/{self.max_retries}. Giving up. "
                                  f"The implementation can be found in `{str(exercise_benchmark_result_dir)}`"),
                           display_id=str(exercise_benchmark_result_dir))
            logger.info(f"Tests failed, giving up")
            return BenchmarkResult(
                success=False,
                exercise=exercise,
                llm_name=self.llm_name,
                llm_params=self.llm_params,
                result_dir=str(exercise_benchmark_result_dir),
                verification_result=verification_result,
                retries=retry)

    def review_benchmark_result(self, benchmark_result: BenchmarkResult, exercise_benchmark_result_dir: Path):
        if not self.reviewer_llm or not benchmark_result:
            return benchmark_result

        if not benchmark_result.success and not benchmark_result.no_change_arguments:
            display(Pretty(
                "Will skip the review step as verification failed and there are no arguments for incorrect tests."))
            return benchmark_result

        display_id = benchmark_result.exercise + "review" + str(datetime.now())
        display(Pretty(f"Review benchmark result for {benchmark_result.exercise}"), display_id=display_id)
        logger.info(f"Reviewing benchmark result {benchmark_result}")

        items = []

        file_items = [FileItem(file_path=str(f), readonly=True)
                      for f in exercise_benchmark_result_dir.iterdir()
                      if f.is_file()]

        if not benchmark_result.success:
            test_fail_message = ("There are failing tests in the candidate's submission. The candidate didn't correct "
                                 f"the code with the following arguments: \n{benchmark_result.no_change_arguments}")
            items.append(TextItem(text=test_fail_message))
            if benchmark_result.verification_result:
                items.extend(benchmark_result.verification_result.failures)

        items.extend(file_items)

        message = Message(sender="Human", items=items)
        test_repo = FileRepository(repo_path=str(exercise_benchmark_result_dir), use_git=False)
        action = WriteCodeAction(llm=self.reviewer_llm, sys_prompt=FEEDBACK_SYSTEM_PROMPT, repository=test_repo,
                                 auto_mode=True)
        response_messages = action.execute(message)
        response_message = response_messages[-1]
        for item in response_message.items:
            feedback = None
            if isinstance(item, CodeItem):
                feedback = self.feedback_parser.parse(item.content)
            elif isinstance(item, TextItem) and item.text.startswith("{"):
                feedback = self.feedback_parser.parse(item.text)

            if feedback:
                benchmark_result.feedback = feedback
                update_display(Pretty(f"Feedback: correct: {feedback.correct}, compliant: {feedback.compliant}, "
                                      f"extra code: {feedback.extra_code}, tests correct: {feedback.tests_correct}"),
                               display_id=display_id)
                return benchmark_result

        if not benchmark_result.feedback:
            update_display(Pretty(f"No feedback found in response."),
                           display_id=benchmark_result.exercise + "review")
        return benchmark_result

    def create_test_dir(self, benchmarks_dir: Path):
        now = datetime.now()
        now = now.strftime("%Y-%m-%d-%H-%M-%S")
        benchmark_result_dir = Path(benchmarks_dir / now)
        benchmark_result_dir.mkdir(parents=True, exist_ok=True)
        return benchmark_result_dir

    def copy_exercise(self, exercise: str, language: str = "python") -> Path:
        exercise_dir = self.exercises_dir / exercise
        exercise_benchmark_result_dir = self.benchmark_result_dir / exercise
        exercise_benchmark_result_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Copy exercise {exercise_dir} to {exercise_benchmark_result_dir}")

        shutil.copyfile(exercise_dir / "instructions.md", exercise_benchmark_result_dir / "instructions.md")

        exercise_code_dir = exercise_dir / language

        if language == "python":
            test_files = [f for f in exercise_code_dir.iterdir() if
                          f.is_file() and f.name.endswith("_test.py")]
            test_dir = exercise_benchmark_result_dir
            src_dir = exercise_benchmark_result_dir
        elif language == "java":
            test_files = [f for f in exercise_code_dir.iterdir() if
                          f.is_file() and f.name.endswith("Test.java")]
            test_dir = exercise_benchmark_result_dir / "src/test/java"
            src_dir = exercise_benchmark_result_dir / "src/main/java"
            test_dir.mkdir(parents=True, exist_ok=True)
            src_dir.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(exercise_code_dir / "pom.xml", exercise_benchmark_result_dir / "pom.xml")
        else:
            raise ValueError(f"Unsupported language {language}")

        if not test_files:
            raise ValueError(f"No test files found in {exercise_code_dir}")

        for test_file in test_files:
            shutil.copy(test_file, test_dir)

        stub_dir_name = "stubs_with_comments" if self.stubs_with_comments else "stubs"
        stub_dir = exercise_code_dir / stub_dir_name
        if not any(stub_dir.iterdir()):
            raise ValueError(f"No files found in {stub_dir}")
        shutil.copytree(stub_dir, src_dir, dirs_exist_ok=True)

        return exercise_benchmark_result_dir

    def get_test_files(self, failures: List[VerificationFailureItem], exercise_benchmark_result_dir: Path):
        parser = create_parser(language="python")  # TODO: Not only python
        test_files = []

        sorted_failures = sorted(failures, key=lambda x: x.test_file)
        for test_file_path, grouped_failures in groupby(sorted_failures, key=lambda x: x.test_file):
            if not test_file_path:
                continue

            test_file = exercise_benchmark_result_dir / test_file_path
            test_file_block = parser.parse(test_file.read_text())

            keep_blocks = [
                CodeBlock(content="setUp(", type=CodeBlockType.FUNCTION),  # TODO: Not only python and unittest
            ]

            for failure in grouped_failures:
                if failure.test_method:
                    keep_blocks.append(CodeBlock(content=failure.test_method + "(", type=CodeBlockType.FUNCTION))

            trimmed_block = test_file_block.trim(keep_blocks=keep_blocks, keep_level=1,
                                                 comment_out_str=" ... rest of the code ... ")

            test_files.append(FileItem(file_path=test_file_path, content=trimmed_block.to_string(), readonly=True))

        return test_files

    def run_unit_tests(self, testdir):
        verifier = PythonUnittestVerifier(current_dir=testdir, test_file_pattern="*_test.py")  # TODO: Not only python
        return verifier.verify()
