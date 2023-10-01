from subprocess import Popen, PIPE
from threading import Timer

from ghostcoder.schema import VerificationResult


def run(cmd, timeout_sec):
    proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
    timer = Timer(timeout_sec, proc.kill)
    try:
        timer.start()
        stdout, stderr = proc.communicate()
        print("stdout", stdout)
        print("stderr", stderr)
        return stdout + stderr
    finally:
        timer.cancel()


class TestTool:

    def run_tests(self) -> VerificationResult:
        pass
