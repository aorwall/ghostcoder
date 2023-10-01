import json
import logging
import shutil
from datetime import datetime
from itertools import groupby
from pathlib import Path
from typing import Optional, List

from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from ghostcoder import FileRepository, Ghostcoder
from ghostcoder.actions import CodeWriter
from ghostcoder.benchmark.prompts import FEEDBACK_SYSTEM_PROMPT
from ghostcoder.callback import LogCallbackHandler
from ghostcoder.codeblocks import create_parser, CodeBlock, CodeBlockType
from ghostcoder.ipython_callback import DisplayCallback
from ghostcoder.ipython_callback_2 import DisplayCallbackOne
from ghostcoder.llm import LLMWrapper
from ghostcoder.schema import TextItem, Message, FileItem, VerificationFailureItem, VerificationResult, \
    CodeItem
from ghostcoder.test_tools.verify_java_mvn_junit5 import JavaMvnUnit5TestTool
from ghostcoder.test_tools.verify_python_unittest import PythonUnittestTestTool
from ghostcoder.utils import get_extension

logger = logging.getLogger("ghostcoder.benchmark")

class BenchmarkFeedback(BaseModel):
    correct: bool = Field(description="If the submitted code is correct.")
    correctness_feedback: str = Field(description="The feedback to the candidate about if it's correct.", )
    compliant: bool = Field(description="If the submitted code is compliant with the requirements and evaluation criteria.")
    compliance_feedback: str = Field(description="The feedback to the candidate about if it's compliant.")
    extra_code: bool = Field(description="If there is extra code in the submission.")
    extra_code_feedback: str = Field(description="The feedback to the candidate about if there is extra code.")
    test_arguments: bool = Field(description="If the candidate argues that the tests are incorrect.")
    tests_correct: bool = Field(description="If your tests are correct.")
    tests_feedback: str = Field(description="The feedback to the candidate why their implementation didn't pass your tests or if the tests needs to be fixed.")


class BenchmarkResult(BaseModel):
    exercise: str
    success: bool
    result_dir: str
    llm_name: str
    llm_params: dict
    verification_result: VerificationResult = None
    no_change_arguments: Optional[str] = None
    feedback: Optional[BenchmarkFeedback] = None


class Benchmark:

    def __init__(self,
                 llm: LLMWrapper,
                 basic_llm: LLMWrapper,
                 llm_name: str,
                 exercises_dir: Path,
                 benchmarks_dir: Path,
                 language: str = "python",
                 exercise: str = None,
                 reviewer_llm: LLMWrapper = None,
                 llm_params: dict = {},
                 max_retries: int = 2,
                 stubs_with_comments: bool = False,
                 callback: DisplayCallback = DisplayCallbackOne()):
        self.llm = llm
        self.basic_llm = basic_llm
        self.reviewer_llm = reviewer_llm
        self.language = language
        self.llm_name = llm_name
        self.llm_params = llm_params
        self.exercises_dir = exercises_dir

        self.benchmark_result_dir = self.create_test_dir(benchmarks_dir, llm_name)

        if exercise:
            self.copy_exercise(exercise=exercise)
        else:
            self.copy_exercises()

        self.stubs_with_comments = stubs_with_comments
        self.max_retries = max_retries
        self.feedback_parser = PydanticOutputParser(pydantic_object=BenchmarkFeedback)
        self.callback = callback

    def run_exercise(self, exercise: str):
        exercise_benchmark_result_dir = self.benchmark_result_dir / exercise

        log_dir = exercise_benchmark_result_dir / ".prompt_log"
        self.llm.llm.callbacks = [LogCallbackHandler(str(log_dir))]
        self.reviewer_llm.llm.callbacks = [LogCallbackHandler(str(log_dir))]

        exercise_repo = FileRepository(repo_path=exercise_benchmark_result_dir, use_git=False)

        ghostcoder = Ghostcoder(llm=self.llm,
                                basic_llm=self.basic_llm,
                                callback=self.callback,
                                repository=exercise_repo,
                                verify_code=True,
                                language=self.language,
                                max_retries=3)

        if self.callback:
            self.callback.display_gc(f"Running benchmark on exercise *{exercise}*")

        benchmark_result, messages = self._run_exercise(
            exercise=exercise,
            exercise_benchmark_result_dir=exercise_benchmark_result_dir,
            coder=ghostcoder)

        benchmark_result = self.review_benchmark_result(
            benchmark_result=benchmark_result,
            exercise_benchmark_result_dir=exercise_benchmark_result_dir,
            messages=messages)

        with open(exercise_benchmark_result_dir / "result.json", "w") as f:
            json.dump(benchmark_result.dict(), f, indent=2)

    def _run_exercise(self,
                      exercise: str,
                      exercise_benchmark_result_dir: Path,
                      coder: Ghostcoder):
        logger.info(f"Will try to solve [{exercise}]")

        instruction_file = exercise_benchmark_result_dir / "instructions.md"
        instructions = instruction_file.read_text()

        file_items = self.get_files(exercise_benchmark_result_dir)

        message = Message(sender="Human", items=[
            TextItem(text=instructions),
            TextItem(text=f"""Use the above instructions to modify the supplied files. 
Keep and implement the existing function or class stubs, they will be called from existing unit tests.
Only use standard python libraries, don't suggest installing any packages.""")
        ] + file_items)  # TODO: Explicit mention the files that should be changed

        response_messages = coder.run(message=message)

        if self.language == "java":
            test_tool = JavaMvnUnit5TestTool(current_dir=exercise_benchmark_result_dir)
        elif self.language == "python":
            test_tool = PythonUnittestTestTool(current_dir=exercise_benchmark_result_dir)
        else:
            raise ValueError(f"Unsupported language {self.language}")

        verification_result = test_tool.run_tests()

        if verification_result.success:
            if self.callback:
                self.callback.display_gc(f"Tests passed, benchmark succeeded the implementation can be found in "
                                         f"directory `{str(exercise_benchmark_result_dir)}`")
            logger.info(f"Tests passed successfully")
            return BenchmarkResult(
                success=True,
                exercise=exercise,
                llm_name=self.llm_name,
                llm_params=self.llm_params,
                result_dir=str(exercise_benchmark_result_dir)), response_messages
        else:
            if self.callback:
                self.callback.display_gc(f"{len(verification_result.failures)} out of "
                                         f"{verification_result.verification_count} tests failed. "
                                         f"The implementation can be found in `{str(exercise_benchmark_result_dir)}`")
            logger.info(f"Tests failed, giving up")
            return BenchmarkResult(
                success=False,
                exercise=exercise,
                llm_name=self.llm_name,
                llm_params=self.llm_params,
                result_dir=str(exercise_benchmark_result_dir),
                verification_result=verification_result), response_messages

    def review_benchmark_result(self,
                                benchmark_result: BenchmarkResult,
                                exercise_benchmark_result_dir: Path,
                                messages: List[Message]):
        if not self.reviewer_llm or not benchmark_result:
            return benchmark_result

        if self.callback:
            self.callback.display_gc(f"Review benchmark result for {benchmark_result.exercise}")
        logger.info(f"Reviewing benchmark result {benchmark_result}")

        items = []

        file_items = self.get_files(exercise_benchmark_result_dir, include_test_files=True)

        items.append(TextItem(text="Review the provided code from the candidate and the conversation above."))
        if not benchmark_result.success:
            test_fail_message = TextItem(text="There are failing tests in the candidate's submission.")
            items.append(test_fail_message)
            if benchmark_result.verification_result:
                items.extend(benchmark_result.verification_result.failures)

        items.extend(file_items)

        message = Message(sender="Human", items=items)
        test_repo = FileRepository(repo_path=exercise_benchmark_result_dir, use_git=False)
        action = CodeWriter(llm=self.reviewer_llm,
                            sys_prompt=FEEDBACK_SYSTEM_PROMPT,
                            repository=test_repo,
                            callback=self.callback,
                            auto_mode=True)

        human_message = next(([m] for m in messages if m.sender == "Human"), [])
        ai_message = next(([m] for m in reversed(messages) if m.sender == "AI"), [])

        response_messages = action.execute(human_message + ai_message + [message])
        response_message = response_messages[-1]
        for item in response_message.items:
            feedback = None
            if isinstance(item, CodeItem):
                feedback = self.feedback_parser.parse(item.content)
            elif isinstance(item, TextItem) and item.text.startswith("{"):
                feedback = self.feedback_parser.parse(item.text)

            if feedback:
                benchmark_result.feedback = feedback
                if self.callback:
                    self.callback.display_gc(f"Feedback: correct: {feedback.correct}, compliant: {feedback.compliant}, "
                                            f"extra code: {feedback.extra_code}, tests correct: {feedback.tests_correct}")
                return benchmark_result

        if not benchmark_result.feedback and self.callback:
            self.callback.display_gc(f"No feedback found in response.")
        return benchmark_result

    def create_test_dir(self, benchmarks_dir: Path, llm_name: str = None):
        dir_name = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        if llm_name:
            dir_name += "--" + llm_name
        benchmark_result_dir = Path(benchmarks_dir / dir_name)
        benchmark_result_dir.mkdir(parents=True, exist_ok=True)
        return benchmark_result_dir

    def copy_exercises(self):
        for dir in self.exercises_dir.iterdir():
            if dir.is_dir():
                self.copy_exercise(exercise=dir.name)

    def copy_exercise(self, exercise: str):
        exercise_dir = self.exercises_dir / exercise
        exercise_benchmark_result_dir = self.benchmark_result_dir / exercise
        exercise_benchmark_result_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Copy exercise {exercise_dir} to {exercise_benchmark_result_dir}")

        shutil.copyfile(exercise_dir / "instructions.md", exercise_benchmark_result_dir / "instructions.md")
        exercise_code_dir = exercise_dir / self.language
        shutil.copytree(exercise_code_dir, exercise_benchmark_result_dir, ignore=shutil.ignore_patterns(".example"), dirs_exist_ok=True)
        logger.debug(f"Copy files from {exercise_code_dir} to {exercise_benchmark_result_dir}")

    def get_test_files(self, failures: List[VerificationFailureItem], exercise_benchmark_result_dir: Path):
        parser = create_parser(language=self.language)
        test_files = []

        sorted_failures = sorted(failures, key=lambda x: x.test_file)
        for test_file_path, grouped_failures in groupby(sorted_failures, key=lambda x: x.test_file):
            if not test_file_path:
                continue

            test_file = exercise_benchmark_result_dir / test_file_path
            test_file_block = parser.parse(test_file.read_text())

            keep_blocks = []
            if self.language == "python":
                keep_blocks.append(
                    CodeBlock(content="setUp(", type=CodeBlockType.FUNCTION),  # TODO: Not only python unittest
                )

            for failure in grouped_failures:
                if failure.test_method:
                    keep_blocks.append(CodeBlock(content=failure.test_method + "(", type=CodeBlockType.FUNCTION))

            trimmed_block = test_file_block.trim(keep_blocks=keep_blocks, keep_level=1,
                                                 comment_out_str=" ... rest of the code ... ")

            test_files.append(FileItem(file_path=test_file_path, content=trimmed_block.to_string(), readonly=True))

        return test_files

    def get_files(self, exercise_benchmark_result_dir: Path, include_test_files: bool = False):
        language_test_suffix = {
            "python": "_test.py",
            "java": "Test.java"
        }

        file_pattern = f"*{get_extension(self.language)}"
        all_files = list(exercise_benchmark_result_dir.rglob(file_pattern))
        file_paths = [
            file
            for file in all_files
            if file.is_file()
               and (include_test_files or not (file.name.endswith(language_test_suffix[self.language])))
               and not file.parent.name.startswith(".")
        ]

        return [
            FileItem(file_path="/" + str(file.relative_to(exercise_benchmark_result_dir)), content=file.read_text())
            for file in file_paths
        ]

    def run_unit_tests(self, testdir):
        verifier = PythonUnittestTestTool(current_dir=testdir, test_file_pattern="*_test.py")  # TODO: Not only python
        return verifier.run_tests()
