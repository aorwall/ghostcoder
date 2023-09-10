import logging
import shutil
from datetime import datetime
from itertools import groupby
from pathlib import Path
from typing import Optional, List

from IPython.core.display import Markdown
from IPython.core.display_functions import display, update_display
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

from codeblocks import create_parser, CodeBlock, CodeBlockType
from ghostcoder import FileRepository
from ghostcoder.actions import WriteCodeAction
from ghostcoder.callback import LogCallbackHandler
from ghostcoder.llm import LLMWrapper
from ghostcoder.schema import UpdatedFileItem, TextItem, Message, FileItem, VerificationFailureItem, VerificationResult, \
    CodeItem
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
    result_dir: Path
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
                 reviewer_llm: LLMWrapper = None,
                 llm_params: dict = {},
                 max_retries: int = 2,
                 stubs_with_comments: bool = False):
        self.llm = llm
        self.reviewer_llm = reviewer_llm
        self.llm_name = llm_name
        self.llm_params = llm_params
        self.exercises_dir = exercises_dir
        self.benchmark_result_dir = self.create_test_dir(benchmarks_dir)
        self.stubs_with_comments = stubs_with_comments
        self.max_retries = max_retries
        self.feedback_parser = PydanticOutputParser(pydantic_object=BenchmarkFeedback)

    def run_exercise(self, exercise: str, language: str = "python"):
        exercise_benchmark_result_dir = self.copy_exercise(exercise=exercise, language=language)

        log_dir = exercise_benchmark_result_dir / "prompt_log"
        self.llm.llm.callbacks = [LogCallbackHandler(str(log_dir))]
        self.reviewer_llm.llm.callbacks = [LogCallbackHandler(str(log_dir))]

        test_repo = FileRepository(repo_path=str(exercise_benchmark_result_dir), use_git=False)
        action = WriteCodeAction(llm=self.llm, repository=test_repo, auto_mode=True)

        display(Markdown(f"Running benchmark on exercise *{exercise}*"),
                display_id=str(exercise_benchmark_result_dir))

        benchmark_result = self._run_exercise(
            exercise=exercise,
            action=action,
            exercise_benchmark_result_dir=exercise_benchmark_result_dir,
            language=language)

        self.review_benchmark_result(
            benchmark_result=benchmark_result,
            exercise_benchmark_result_dir=exercise_benchmark_result_dir)

        return benchmark_result

    def _run_exercise(self,
                      exercise: str,
                      exercise_benchmark_result_dir: Path,
                      action: WriteCodeAction,
                      display_id: str = None,
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

            update_display(Markdown(f"No updated files, benchmark failed after retry {retry}"
                                    f"the implementation can be found in `{str(exercise_benchmark_result_dir)}`"),
                           display_id=str(exercise_benchmark_result_dir))
            logger.info(f"No changed found in file {implementation_file}.\nResponse message:\n{arguments}")
            return BenchmarkResult(
                success=False,
                exercise=exercise,
                llm_name=self.llm_name,
                llm_params=self.llm_params,
                result_dir=exercise_benchmark_result_dir,
                verification_result=verification_failure,
                no_change_arguments=arguments,
                retries=retry)

        verification_result = self.run_unit_tests(exercise_benchmark_result_dir)
        if verification_result.success:
            update_display(Markdown(f"Tests passed, benchmark succeeded after retry {retry}, "
                                    f"the implementation can be found in `{str(exercise_benchmark_result_dir)}`"),
                                    display_id=str(exercise_benchmark_result_dir))
            logger.info(f"Tests passed successfully")
            return BenchmarkResult(
                success=True,
                exercise=exercise,
                llm_name=self.llm_name,
                llm_params=self.llm_params,
                result_dir=exercise_benchmark_result_dir,
                retries=retry)
        elif retry < self.max_retries:
            update_display(Markdown(data=f"Tests failed, will do retry {retry + 1}/{self.max_retries}"),
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
            update_display(Markdown(f"Tests failed after retry {retry}/{self.max_retries}. Giving up. "
                                    f"The implementation can be found in `{str(exercise_benchmark_result_dir)}`"),
                           display_id=str(exercise_benchmark_result_dir))
            logger.info(f"Tests failed, giving up")
            return BenchmarkResult(
                success=False,
                exercise=exercise,
                llm_name=self.llm_name,
                llm_params=self.llm_params,
                result_dir=exercise_benchmark_result_dir,
                verification_result=verification_result,
                retries=retry)

    def review_benchmark_result(self, benchmark_result: BenchmarkResult, exercise_benchmark_result_dir: Path):
        if not self.reviewer_llm or not benchmark_result:
            return benchmark_result

        display_id = benchmark_result.exercise + "review" + str(datetime.now())

        display(Markdown(f"Review benchmark result for {benchmark_result.exercise}"), display_id=display_id)
        logger.info(f"Reviewing benchmark result {benchmark_result}")

        items = []

        file_items = [FileItem(file_path=str(f), readonly=True) for f in exercise_benchmark_result_dir.iterdir() if
                      f.is_file()]

        prompt = """You are a staff engineer at a large company who is reviewing a candidate's code submission. 

* Review if the candidate's code submission is correct and meets the requirements. Fill in your response below in the "correct" and "feedback" fields.
* Review if the code submission is compliant with the evaluation criteria. Fill in your response below in the "compliant" and "compliance_feedback" fields.
* Verify that there is no extra not required code in the submission. Fill in your response below in the "extra_code" and "extra_code_feedback" fields.
* If the tests are failing, review the candidate's code and provide feedback on how to fix the code. Fill in your response below in the field "tests_feedback".
* If the candidate argues that the tests are incorrect, review the tests and provide feedback on how to fix the tests if needed. Fill in your response below in the field "tests_correct" and "tests_feedback".

The output should be formatted as a JSON instance that conforms to the JSON schema below. The JSON should be saved to the file `feedback.json`

As an example, for the schema {"properties": {"foo": {"title": "Foo", "description": "a list of strings", "type": "array", "items": {"type": "string"}}}, "required": ["foo"]}
the object {"foo": ["bar", "baz"]} is a well-formatted instance of the schema. The object {"properties": {"foo": ["bar", "baz"]}} is not well-formatted.

```
{"properties": {"correct": {"title": "Correct", "description": "If the submitted code is correct.", "type": "boolean"}, "correctness_feedback": {"title": "Correctness Feedback", "description": "The feedback to the candidate about if it's correct.", "type": "string"}, "compliant": {"title": "Compliant", "description": "If the submitted code is compliant with the requirements and evaluation criteria.", "type": "boolean"}, "compliance_feedback": {"title": "Compliance Feedback", "description": "The feedback to the candidate about if it's compliant.", "type": "string"}, "extra_code": {"title": "Extra Code", "description": "If there is extra code in the submission.", "type": "boolean"}, "extra_code_feedback": {"title": "Extra Code Feedback", "description": "The feedback to the candidate about if there is extra code.", "type": "string"}, "tests_correct": {"title": "Tests Correct", "description": "If your tests are correct.", "type": "boolean"}, "tests_feedback": {"title": "Tests Feedback", "description": "The feedback to the candidate why their implementation didn't pass your tests or if the tests needs to be fixed.", "type": "string"}}, "required": ["correct", "correctness_feedback", "compliant", "compliance_feedback", "extra_code", "extra_code_feedback", "tests_correct", "tests_feedback"]}
```

Example feedback:
feedback.json
```
{
  "correct": false,
  "correctness_feedback": "The code does not handle missing keys in the dictionaries correctly. When a key is missing, the code should replace it with 'Unknown' for string values and '0' for numeric values. ",
  "compliant": true,
  "compliance_feedback": "The submission adheres to all the given evaluation criteria.",
  "extra_code": false,
  "extra_code_feedback": "There is no extra code in the submission.",
  "tests_correct": true,
  "tests_feedback": "The failing test `test_missing_keys` is correctly testing the requirement to handle missing keys in the dictionaries."
}
```
"""

        if not benchmark_result.success:
            test_fail_message = ""
            if not benchmark_result.verification_result.success:
                test_fail_message = "There are failing tests in the candidate's submission. "

            if benchmark_result.no_change_arguments:
                test_fail_message += (f"The candidate didn't correct the code with the following arguments:"
                                      f"\n{benchmark_result.no_change_arguments}")

            items.append(TextItem(text=test_fail_message))
            items.extend(benchmark_result.verification_result.failures)

        items.extend(file_items)
        items.append(FileItem(file_path="feedback.json", readonly=False))

        message = Message(sender="Human", items=items)
        test_repo = FileRepository(repo_path=str(exercise_benchmark_result_dir), use_git=False)
        action = WriteCodeAction(llm=self.reviewer_llm, repository=test_repo, auto_mode=True, sys_prompt=prompt)
        response_messages = action.execute(message)

        response_message = response_messages[-1]
        for item in response_message.items:
            if isinstance(item, UpdatedFileItem) and item.file_path == "feedback.json" or isinstance(item, CodeItem):
                feedback = self.feedback_parser.parse(item.content)
                benchmark_result.feedback = feedback
                update_display(Markdown(f"Feedback: correct: {feedback.correct}, compliant: {feedback.compliant}, "
                                        f"extra code: {feedback.extra_code}, tests correct: {feedback.tests_correct}"),
                               display_id=display_id)

                # TODO: Save feedback.json if CodeItem
            else:
                update_display(Markdown(f"No feedback found"), display_id=benchmark_result.exercise + "review")

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
        test_files = [f for f in exercise_code_dir.iterdir() if
                      f.is_file() and f.name.endswith("_test.py")]  # TODO: Not only python
        if not test_files:
            raise ValueError(f"No test files found in {exercise_code_dir}")

        for test_file in test_files:
            shutil.copy(test_file, exercise_benchmark_result_dir)

        stub_dir_name = "stubs_with_comments" if self.stubs_with_comments else "stubs"
        stub_dir = exercise_code_dir / stub_dir_name

        if not any(stub_dir.iterdir()):
            raise ValueError(f"No files found in {stub_dir}")

        shutil.copytree(stub_dir, exercise_benchmark_result_dir, dirs_exist_ok=True)

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
