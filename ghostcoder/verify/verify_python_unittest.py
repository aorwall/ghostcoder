import os
import re
import subprocess
from typing import List, Optional

from ghostcoder.schema import VerificationFailureItem

def extract_test_details(section: str) -> Optional[VerificationFailureItem]:
    pattern = r'FAIL: ([^\s]+) \(([^.]+)\.([^\.]+)\.([^\)]+)\)[\s\S]+?.*File "([^"]+)", (.*)'
    match = re.search(pattern, section, re.DOTALL)
    if match:
        test_method, module, test_class, function, file_path, traceback = match.groups()
        return VerificationFailureItem(
            test_method=test_method,
            test_class=test_class,
            test_file=file_path,
            output=traceback
        )
    return None

def find_failed_tests(output: str) -> List[VerificationFailureItem]:
    sections = output.split("======================================================================")
    failed_tests = [extract_test_details(section) for section in sections if "FAIL:" in section]
    return [test for test in failed_tests if test is not None]


def verify() -> List[VerificationFailureItem]:
    command = ["python", "-m", "unittest", "*"]
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print("Finished running command:", " ".join(command))
    output = result.stdout.decode('utf-8')

    current_dir = os.getcwd()
    output.replace(current_dir + "/", "")

    if result.returncode != 0:
        failed_tests = find_failed_tests(output)
        if failed_tests:
            return failed_tests
        else:
            return [VerificationFailureItem(output=output)]

    return []

if __name__ == "__main__":
    print(verify())
