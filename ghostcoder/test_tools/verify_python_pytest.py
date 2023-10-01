import logging
import os
import re
import subprocess
from pathlib import Path
from typing import List, Optional

from ghostcoder.ipython_callback import DisplayCallback
from ghostcoder.schema import VerificationFailureItem, VerificationResult
from ghostcoder.test_tools.test_tool import TestTool

logger = logging.getLogger(__name__)

class PythonPytestTestTool(TestTool):

    def __init__(self,
                 test_file_pattern: str = "*.py",
                 current_dir: Optional[Path] = None,
                 callback: DisplayCallback = None,
                 timeout: Optional[int] = 30):
        self.test_file_pattern = test_file_pattern
        self.timeout = timeout
        self.callback = callback

        if current_dir:
            self.current_dir = Path(current_dir)
        else:
            self.current_dir = Path(os.getcwd())

    def run_tests(self) -> VerificationResult:
        command = [
            "pytest"
        ]

        command_str = " ".join(command)

        if self.callback:
            self.callback.display("Ghostcoder", f"Run tests with command `$ {command_str}` in directory `{self.current_dir}`")

        logger.info(f"Run tests with command `$ {command_str}` in {self.current_dir}")

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
                verification_count=0,
                message=f"Tests timed out after {self.timeout} seconds.",
                failures=self.find_timed_out(output)
            )

        output = result.stdout

        failed_tests_count, passed_tests_count = self.parse_test_results(output)
        total_test_count = failed_tests_count + passed_tests_count

        if result.returncode != 0:
            if failed_tests_count:
                failed_tests = self.find_failed_tests(output)
                total_test_count = failed_tests_count + passed_tests_count
                logger.info(f"{failed_tests_count} out of {total_test_count} tests failed. "
                            f"Return {len(failed_tests)} failure items.")
                return VerificationResult(
                    success=False,
                    verification_count=total_test_count,
                    message=f"{failed_tests_count} out of {total_test_count} tests failed.",
                    failures=failed_tests
                )
            else:
                logger.warning(f"Tests failed to run. \nOutput from {command_str}:\n{output}")
                return VerificationResult(
                    success=False,
                    verification_count=total_test_count,
                    message=f"Tests failed to run.",
                    failures=[VerificationFailureItem(output=output)]
                )
        else:
            logger.info(f"All {total_test_count} tests passed.")
            return VerificationResult(
                success=True,
                verification_count=total_test_count,
                message=f"All {total_test_count} tests passed."
            )

    def parse_test_results(self, output: str) -> (int, int):
        failed_match = re.search(r'(\d+) failed', output)
        passed_match = re.search(r'(\d+) passed', output)

        if failed_match:
            failed_count = int(failed_match.group(1))
        else:
            failed_count = 0

        if passed_match:
            passed_count = int(passed_match.group(1))
        else:
            passed_count = 0

        return failed_count, passed_count

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
        test_output = ""
        test_file = None
        test_class = None
        test_method = None
        test_code = None

        failures = []
        extract = False
        for line in data.split("\n"):
            if "= FAILURES =" in line:
                extract = True
                continue

            if extract:
                test_file_search = re.search(r'(\w+\.py)', line)

                if line.startswith("=") or line.startswith("_"):
                    match = re.search(r'(\w+)\.(\w+)', line)
                    if match:
                        if test_file:
                            failures.append(
                                VerificationFailureItem(test_file=test_file, test_class=test_class, test_method=test_method,
                                                        output=test_output, test_code=test_code))
                            test_output = ""
                            test_code = None
                            test_file = None

                        test_class = match.group(1)
                        test_method = match.group(2)

                    if line.startswith("="):
                        failures.append(
                            VerificationFailureItem(test_file=test_file, test_class=test_class, test_method=test_method,
                                                    output=test_output, test_code=test_code))
                        return failures

                elif not test_file and test_file_search:
                    test_file = test_file_search.group(1)
                elif line.startswith("E "):
                    test_output += line[2:].strip() + "\n"
                elif not line.startswith("self") and line.strip() and not test_file:
                    if not test_code:
                        test_code = line
                    else:
                        test_code += "\n" + line

        if test_file:
            failures.append(VerificationFailureItem(test_file=test_file, test_class=test_class, test_method=test_method,
                                                        output=test_output, test_code=test_code))

        return failures

    def extract_test_details(self, section: str) -> Optional[VerificationFailureItem]:
        class_method_match = re.search(r'(\w+)\.(\w+)', section)
        if class_method_match:
            class_name = class_method_match.group(1)
            method_name = class_method_match.group(2)

        # Using regex to extract filename and line number
        file_line_match = re.search(r'(\w+.py):(\d+):', section)
        if file_line_match:
            file_name = file_line_match.group(1)

        return VerificationFailureItem(test_file=file_name, test_class=class_name, test_method=method_name, output=section)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    verifier = PythonPytestTestTool(test_file_pattern="*.py")

    result = verifier.run_tests()

    if result.failures:
        print("Failed tests:")
        for item in result.failures:
            print(f"- {item.test_file} : {item.test_class} : {item.test_method}\n{item.test_code}\n  {item.output}")
