import logging
import re
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

from benchmark.utils import create_openai_client
from ghostcoder import FileRepository
from ghostcoder.actions import WriteCodeAction
from ghostcoder.llm import LLMWrapper
from ghostcoder.schema import UpdatedFileItem, TextItem, Message, FileItem
from ghostcoder.verify.verify_python_unittest import find_failed_tests


@dataclass
class BenchmarkExerciseResult:
    exercise: str
    success: bool
    retries: int
    result_dir: Path
    llm_name: str
    test_failure: Optional[str] = None
    no_change_arguments: Optional[str] = None


class Benchmark:

    def __init__(self,
                 llm: LLMWrapper,
                 model_name: str,
                 log_dir: Path,
                 exercises_dir: Path,
                 benchmarks_dir: Path,
                 run_tests):
        self.llm = llm
        self.model_name = model_name
        self.log_dir = log_dir
        self.exercises_dir = exercises_dir
        self.benchmark_result_dir = self.create_test_dir(benchmarks_dir)
        self.run_tests = run_tests

    def run_exercise(self, exercise: str, language: str = "python"):
        exercise_dir = self.exercises_dir / exercise
        exercise_benchmark_result_dir = self.benchmark_result_dir / exercise
        logging.debug(f"Copy exercise {exercise_dir} to {exercise_benchmark_result_dir}")
        shutil.copytree(exercise_dir, exercise_benchmark_result_dir, dirs_exist_ok=True)

        test_repo = FileRepository(repo_path=str(exercise_benchmark_result_dir), use_git=False)
        action = WriteCodeAction(llm=self.llm, repository=test_repo, auto_mode=True)

        return self._run_exercise(exercise=exercise, action=action, language=language)

    def _run_exercise(self, exercise: str, action: WriteCodeAction, language: str = "python", test_output: str = None, retry: int = 0):
        exercise_benchmark_result_dir = self.benchmark_result_dir / exercise

        logging.info(f"Trying to solve [{exercise}], retry: {retry}")

        instruction_file = exercise_benchmark_result_dir / "instructions.md"
        instructions = instruction_file.read_text()
        implementation_file = f"{language}/{exercise}.py" # TODO: Not only python
        implementation_file_full_path = Path(exercise_benchmark_result_dir / implementation_file)

        contents_before = implementation_file_full_path.read_text()

        if retry > 0 and test_output:
            request = f"""The implementation of the instructions failed. The tests failed with the following output:
{test_output}

The tests used are correct and should not be changed.
Fix the code in {implementation_file} to resolve the errors.
"""
        else:
            request = """Use the above instructions to modify the supplied files: {stub_file}
Keep and implement the existing function or class stubs, they will be called from existing unit tests.
Only use standard python libraries, don't suggest installing any packages."""

        message = Message(sender="Human", items=[
            TextItem(text=instructions),
            TextItem(text=request),
            FileItem(file_path=implementation_file),
        ])

        response_messages = action.execute(message=message)
        response_message = response_messages[-1]

        if contents_before == implementation_file_full_path.read_text():
            arguments = ""
            for item in response_message.items:
                if isinstance(item, TextItem):
                    arguments = item.to_prompt() + "\n"

            logging.info(f"No changed found in file {implementation_file}.\nResponse message:\n{arguments}")
            return BenchmarkExerciseResult(
                success=False,
                exercise=exercise,
                llm_name=self.model_name,
                result_dir=exercise_benchmark_result_dir,
                test_failure=test_output,
                no_change_arguments=arguments,
                retries=retry)

        success, output = self.run_tests(exercise_benchmark_result_dir / language)
        if success:
            logging.info(f"Tests successful")

            return BenchmarkExerciseResult(
                success=True,
                exercise=exercise,
                llm_name=self.model_name,
                result_dir=exercise_benchmark_result_dir,
                retries=retry)
        elif retry < 2:
            logging.info(f"Tests failed, will retry")
            return self._run_exercise(
                exercise=exercise,
                action=action,
                language=language,
                test_output=output,
                retry=retry+1)
        else:
            logging.info(f"Tests failed, giving up")
            return BenchmarkExerciseResult(
                success=False,
                exercise=exercise,
                llm_name=self.model_name,
                result_dir=exercise_benchmark_result_dir,
                test_failure=output,
                retries=retry)

    def create_test_dir(self, benchmarks_dir: Path):
        now = datetime.now()
        now = now.strftime("%Y-%m-%d-%H-%M-%S")
        benchmark_result_dir = Path(benchmarks_dir / now)
        benchmark_result_dir.mkdir(parents=True, exist_ok=True)
        return benchmark_result_dir



def run_python_unittest(testdir):
    command = [
        "python",
        "-m",
        "unittest",
        "discover",
        "-p",
        "*_test.py",
    ]

    #logging.info("Run command [" + str(command) + "] in directory " + testdir)

    timeout = 5

    result = subprocess.run(
        command,
        cwd=testdir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=timeout,
    )

    success = result.returncode == 0
    output = result.stdout

    failed_tests = find_failed_tests(output)
    if failed_tests:
        for test in failed_tests:
            logging.info(f"Failed test: {test.test_method}")

    if not success:
        output = cleanup_test_output(output, testdir)

    logging.debug("Test results:\n" + output)

    return success, output


def cleanup_test_output(output, testdir):
    # remove timing info, to avoid randomizing the response to GPT
    res = re.sub(
        r"^Ran \d+ tests in \d+\.\d+s$",
        "",
        output,
        flags=re.MULTILINE,
    )
    res = re.sub(
        r"^====*$",
        "====",
        res,
        flags=re.MULTILINE,
    )
    res = re.sub(
        r"^----*$",
        "----",
        res,
        flags=re.MULTILINE,
    )

    res = res.replace(str(testdir), str(testdir.name))
    return res
