import logging
import logging
import os
import re
import subprocess
from pathlib import Path
from typing import Optional

from ghostcoder.schema import VerificationFailureItem, VerificationResult
from ghostcoder.test_tools.test_tool import TestTool

logger = logging.getLogger("__name__")


class JavaMvnUnit5TestTool(TestTool):

    def __init__(self,
                 test_file_pattern: str = "*Test.java",
                 current_dir: Optional[Path] = None,
                 callback=None,
                 timeout: Optional[int] = 5):
        self.test_file_pattern = test_file_pattern
        self.timeout = timeout
        self.callback = callback

        if current_dir:
            self.current_dir = Path(current_dir)
        else:
            self.current_dir = Path(os.getcwd())

        self.test_files = [f for f in self.current_dir.rglob(self.test_file_pattern)]

    def run_tests(self) -> VerificationResult:
        # TODO: Verify if mvn is installed and a pom.xml file exists

        command = [
            "mvn",
            "test"
        ]

        command_str = " ".join(command)

        logger.info(f"Run tests with command `$ {command_str}` in {self.current_dir}")

        if self.callback:
            self.callback.display("Ghostcoder", f"Run tests with command `$ {command_str}` in directory `{self.current_dir}`")

        try:
            result = subprocess.run(
                command,
                cwd=self.current_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=self.timeout)
        except subprocess.TimeoutExpired:
            logging.info(f"verify(): Tests timed out after {self.timeout} seconds.")
            return VerificationResult(
                success=False,
                verification_count=0,
                message=f"Tests timed out after {self.timeout} seconds indicating an infinite loop."
            )

        output = result.stdout

        verification_result = self.create_verification_result(output)
        if verification_result:
            verification_result.success = result.returncode == 0
            return verification_result
        elif result.returncode != 0:
            logging.warning(f"Tests failed to run. \nOutput from {command_str}:\n{output}")
            return VerificationResult(
                success=False,
                verification_count=0,
                message=f"Tests failed to run.",
                failures=[VerificationFailureItem(output=output)]
            )
        else:
            logging.info(f"No test results found, will return success.") # TODO: Fail?
            return VerificationResult(
                success=True,
                verification_count=0,
                message=f"No tests found?"
            )

    def create_verification_result(self, output: str) -> Optional[VerificationResult]:
        lines = output.split("\n")
        failed_tests = []
        in_result_section = False
        extract = False
        test_results_pattern = r".*Tests run: (\d+), Failures: (\d+), Errors: (\d+), Skipped: (\d+)"

        for line in lines:
            if not in_result_section:
                if line.strip() == "[INFO] Results:":
                    in_result_section = True
                continue

            if "[ERROR] Failures:" in line or "[ERROR] Errors:" in line:
                extract = True
                continue

            if extract and line.startswith("[ERROR]  "):
                result = self.extract_test_details(line)
                if result:
                    failed_tests.append(result)
                else:
                    logger.info(f"Failed to extract test details from line: {line}")
            else:
                extract = False

            if "Tests run:" in line:
                test_results_match = re.search(test_results_pattern, line)
                total_tests = int(test_results_match.group(1)) if test_results_match else 0

                if failed_tests:
                    logging.info(f"{len(failed_tests)} out of {total_tests} tests failed.")
                    return VerificationResult(
                        success=False,
                        verification_count=total_tests,
                        message=f"{len(failed_tests)} out of {total_tests} tests failed.",
                        failures=failed_tests
                    )
                else:
                    logging.info(f"All {total_tests} tests passed.")
                    return VerificationResult(
                        success=True,
                        verification_count=total_tests,
                        message=f"All {total_tests} tests passed."
                    )

        return None

    def extract_test_details(self, line: str) -> Optional[VerificationFailureItem]:
        pattern = r"\[ERROR\]\s+(?P<test_class>.*)\.(?P<test_method>[\w]+):[\d]+ (?P<output>.+)"

        match = re.match(pattern, line)
        if match:
            test_class = match.group("test_class")
            test_files = [test_file for test_file in self.test_files if test_class in test_file.name]
            if test_files:
                test_file = test_files[0]
                test_file = test_file.relative_to(self.current_dir)
            else:
                test_file = None
            return VerificationFailureItem(
                test_method=match.group("test_method"),
                test_class=test_class,
                test_file=str(test_file),
                output=match.group("output")
            )
        return None


if __name__ == "__main__":
    verifier = JavaMvnUnit5TestTool()

    result = verifier.run_tests()

    if result.failures:
        print("Failed tests:")
        for item in result.failures:
            print(f"- {item.test_file}:{item.test_class}:{item.test_method}")
