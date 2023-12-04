import logging
import os
import re
import subprocess
from pathlib import Path
from typing import List, Optional

from ghostcoder.schema import VerificationFailureItem, VerificationResult
from ghostcoder.test_tools.test_tool import TestTool

logger = logging.getLogger(__name__)


class PythonPytestTestTool(TestTool):
    def __init__(self,
                 test_file_pattern: str = "*",
                 current_dir: Optional[Path] = None,
                 callback = None,
                 parse_test_results: bool = True,
                 include_test_code: bool = False,
                 timeout: Optional[int] = 30):
        self.test_file_pattern = test_file_pattern
        self.timeout = timeout
        self.callback = callback
        self.parse_test_results = parse_test_results
        self.include_test_code = include_test_code

        if current_dir:
            self.current_dir = Path(current_dir)
        else:
            self.current_dir = Path(os.getcwd())

    def run_tests(self) -> VerificationResult:
        command = [
            "pytest",
            "-v",
        ]

        command_str = " ".join(command)

        if self.callback:
            self.callback.display("Ghostcoder", f"Run tests with command `$ {command_str}` in directory `{self.current_dir}`")

        logger.info(f"Run tests with command: `$ {command_str}` in {self.current_dir}")

        try:
            result = subprocess.run(
                command,
                cwd=self.current_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=self.timeout)
        except subprocess.TimeoutExpired as e:
            logger.info(f"Tests timed out after {self.timeout} seconds .")
            output = e.output.decode("utf-8")

            return VerificationResult(
                success=False,
                error=True,
                verification_count=0,
                failed_tests_count=0,
                message=f"Tests timed out after {self.timeout} seconds.",
                failures=self.find_timed_out(output)
            )

        output = result.stdout
        output = output.replace(str(self.current_dir), "")

        failed_tests_count, passed_tests_count, error_count = self.get_number_of_tests(output)
        failed_tests_count += error_count
        total_test_count = failed_tests_count + passed_tests_count

        error = error_count > 0 or "= ERRORS =" in output or "! Interrupted" in output

        if result.returncode != 0:
            if failed_tests_count:
                failed_tests = self.find_failed_tests(output)

                logger.info(f"{failed_tests_count} out of {total_test_count} tests failed. "
                            f"Return {len(failed_tests)} failure items.")
                return VerificationResult(
                    success=False,
                    error=error,
                    verification_count=total_test_count,
                    failed_tests_count=failed_tests_count,
                    message=f"{failed_tests_count} out of {total_test_count} tests failed.",
                    failures=failed_tests
                )
            elif "no tests ran" in output:
                logger.info(f"No tests found.")
                return VerificationResult(
                    success=True,
                    error=error,
                    verification_count=0,
                    failed_tests_count=failed_tests_count,
                    message=f""
                )
            else:
                logger.warning(f"Tests failed to run. \nOutput from {command_str}:\n{output}")
                return VerificationResult(
                    success=False,
                    error=error,
                    verification_count=total_test_count,
                    failed_tests_count=failed_tests_count,
                    message=f"Tests failed to run.",
                    failures=[VerificationFailureItem(output=output)]
                )
        else:
            logger.info(f"All {total_test_count} tests passed.")
            return VerificationResult(
                success=True,
                error=False,
                verification_count=total_test_count,
                failed_tests_count=failed_tests_count,
                message=f"All {total_test_count} tests passed."
            )

    def get_number_of_tests(self, output: str) -> (int, int):
        failed_match = re.search(r'(\d+) failed', output)
        passed_match = re.search(r'(\d+) passed', output)
        error_match = re.search(r'(\d+) errors', output)

        if failed_match:
            failed_count = int(failed_match.group(1))
        else:
            failed_count = 0

        if error_match:
            error_count = int(error_match.group(1))
        else:
            error_count = 0

        if passed_match:
            passed_count = int(passed_match.group(1))
        else:
            passed_count = 0

        return failed_count, passed_count, error_count

    def find_timed_out(self, output: str) -> List[VerificationFailureItem]:
        match = re.search(r'(\w+.py)::(\w+)::(\w+)', output)
        if match:
            file_name = match.group(1)
            class_name = match.group(2)
            method_name = match.group(3)
            return [VerificationFailureItem(test_file=file_name, test_class=class_name, test_method=method_name, output="Timed out")]

        match = re.search(r'(\w+.py)\s\.\.\.', output)
        if match:
            file_name = match.group(1)
            return [VerificationFailureItem(test_file=file_name, output="Timed out")]

        return [VerificationFailureItem(output="Timed out")]

    def find_failed_tests(self, data: str) -> List[VerificationFailureItem]:
        if not self.parse_test_results:
            return [VerificationFailureItem(output=data)]

        test_output = ""
        test_file = None
        test_class = None
        test_method = None
        test_code = None
        test_linenumber = None

        failures = []
        extract_output = False
        extract = False
        lines = data.split("\n")
        for line in lines:
            if "= FAILURES =" in line:
                extract = True
                continue

            if extract:
                test_file_search = re.search(r'^(\w+\.py):(\d+)', line)

                if line.startswith("="):
                    failures.append(
                        VerificationFailureItem(test_file=test_file,
                                                test_linenumber=test_linenumber,
                                                test_class=test_class,
                                                test_method=test_method,
                                                output=test_output,
                                                test_code=test_code))
                    return failures
                elif line.startswith("__"):
                    match = re.search(r'(\w+)\.(\w+)', line)
                    single_match = re.search(r'_\s(\w+)\s_', line)

                    if match or single_match:
                        if test_file:
                            failures.append(
                                VerificationFailureItem(test_file=test_file,
                                                        test_linenumber=test_linenumber,
                                                        test_class=test_class,
                                                        test_method=test_method,
                                                        output=test_output,
                                                        test_code=test_code))
                            test_output = ""
                            test_code = None
                            test_file = None

                        if match:
                            test_class = match.group(1)
                            test_method = match.group(2)
                        else:
                            test_class = None
                            test_method = single_match.group(1)
                elif not test_file and test_file_search:
                    test_file = test_file_search.group(1)
                    test_linenumber = test_file_search.group(2)
                    extract_output = False
                elif line.startswith("E ") or (line.startswith("> ") and "???" not in line):
                    test_output += line + "\n"
                    extract_output = True
                elif extract_output and not test_file_search:
                    test_output += line + "\n"
                elif test_file_search:
                    extract_output = False
                elif self.include_test_code and not line.startswith("self") and line.strip() and not test_file:
                    if not test_code:
                        test_code = line
                    else:
                        test_code += "\n" + line

        if test_file:
            failures.append(VerificationFailureItem(test_file=test_file,
                                                    test_linenumber=test_linenumber,
                                                    test_class=test_class,
                                                    test_method=test_method,
                                                    output=test_output,
                                                    test_code=test_code))

        return failures

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    verifier = PythonPytestTestTool(test_file_pattern="*.py")

    result = verifier.run_tests()

    if result.failures:
        step_input = "\n\n".join([item.to_prompt() for item in result.failures])

        print("Failed tests:\n" + step_input)