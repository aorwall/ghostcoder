import os
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from ghostcoder.test_tools.verify_java_mvn_junit5 import JavaMvnUnit5TestTool
from ghostcoder.test_tools.verify_python_unittest import PythonUnittestTestTool


@pytest.fixture
def temp_dir():
    with TemporaryDirectory() as temp_dir:
        open(os.path.join(temp_dir, "food_chain_test.py"), "w").close()

        yield temp_dir


@pytest.fixture
def verifier(temp_dir):
    return JavaMvnUnit5TestTool(current_dir=Path(temp_dir))

def test_verify(temp_dir, verifier):
    test_output = f"""[INFO] -------------------------------------------------------
[INFO]  T E S T S
[INFO] -------------------------------------------------------
[INFO] Running CoffeeMachineProgram3Test
[ERROR] Tests run: 2, Failures: 2, Errors: 0, Skipped: 0, Time elapsed: 0.083 s <<< FAILURE! -- in CoffeeMachineProgram3Test
[ERROR] CoffeeMachineProgram3Test.testCalculateMaxCupsWithInsufficientBeans -- Time elapsed: 0.048 s <<< FAILURE!
org.opentest4j.AssertionFailedError: expected: <5> but was: <0>
	at org.junit.jupiter.api.AssertionFailureBuilder.build(AssertionFailureBuilder.java:151)
	at org.junit.jupiter.api.AssertionFailureBuilder.buildAndThrow(AssertionFailureBuilder.java:132)
	at org.junit.jupiter.api.AssertEquals.failNotEqual(AssertEquals.java:197)
	at org.junit.jupiter.api.AssertEquals.assertEquals(AssertEquals.java:150)
	at org.junit.jupiter.api.AssertEquals.assertEquals(AssertEquals.java:145)
	at org.junit.jupiter.api.Assertions.assertEquals(Assertions.java:527)
	at CoffeeMachineProgram3Test.testCalculateMaxCupsWithInsufficientBeans(CoffeeMachineProgram3Test.java:13)
	at java.base/java.lang.reflect.Method.invoke(Method.java:568)
	at java.base/java.util.ArrayList.forEach(ArrayList.java:1511)
	at java.base/java.util.ArrayList.forEach(ArrayList.java:1511)

[ERROR] CoffeeMachineProgram3Test.testCalculateMaxCups -- Time elapsed: 0.004 s <<< FAILURE!
org.opentest4j.AssertionFailedError: expected: <5> but was: <0>
	at org.junit.jupiter.api.AssertionFailureBuilder.build(AssertionFailureBuilder.java:151)
	at org.junit.jupiter.api.AssertionFailureBuilder.buildAndThrow(AssertionFailureBuilder.java:132)
	at org.junit.jupiter.api.AssertEquals.failNotEqual(AssertEquals.java:197)
	at org.junit.jupiter.api.AssertEquals.assertEquals(AssertEquals.java:150)
	at org.junit.jupiter.api.AssertEquals.assertEquals(AssertEquals.java:145)
	at org.junit.jupiter.api.Assertions.assertEquals(Assertions.java:527)
	at CoffeeMachineProgram3Test.testCalculateMaxCups(CoffeeMachineProgram3Test.java:8)
	at java.base/java.lang.reflect.Method.invoke(Method.java:568)
	at java.base/java.util.ArrayList.forEach(ArrayList.java:1511)
	at java.base/java.util.ArrayList.forEach(ArrayList.java:1511)

[INFO] Running CoffeeMachineProgramTest
[ERROR] Tests run: 6, Failures: 0, Errors: 1, Skipped: 0, Time elapsed: 0.023 s <<< FAILURE! -- in CoffeeMachineProgramTest
[ERROR] CoffeeMachineProgramTest.testCalculateMaxCups -- Time elapsed: 0.004 s <<< ERROR!
java.lang.RuntimeException: Unexpected failure
	at CoffeeMachineProgramTest.testCalculateMaxCups(CoffeeMachineProgramTest.java:7)
	at java.base/java.lang.reflect.Method.invoke(Method.java:568)
	at java.base/java.util.ArrayList.forEach(ArrayList.java:1511)
	at java.base/java.util.ArrayList.forEach(ArrayList.java:1511)

[INFO] Running CoffeeMachineProgram2Test
[INFO] Tests run: 1, Failures: 0, Errors: 0, Skipped: 0, Time elapsed: 0.003 s -- in CoffeeMachineProgram2Test
[INFO] 
[INFO] Results:
[INFO] 
[ERROR] Failures: 
[ERROR]   CoffeeMachineProgram3Test.testCalculateMaxCups:8 expected: <5> but was: <0>
[ERROR]   CoffeeMachineProgram3Test.testCalculateMaxCupsWithInsufficientBeans:13 expected: <5> but was: <0>
[ERROR] Errors: 
[ERROR]   CoffeeMachineProgramTest.testCalculateMaxCups:7 Runtime Unexpected failure
[INFO] 
[ERROR] Tests run: 9, Failures: 2, Errors: 1, Skipped: 0
[INFO] 
"""

    result = verifier.create_verification_result(test_output)

    assert len(result.failures) == 3

    assert result.failures[0].test_method == "testCalculateMaxCups"
    assert result.failures[0].test_class == "CoffeeMachineProgram3Test"
    assert result.failures[0].test_file == "CoffeeMachineProgram3Test.java"
    assert result.failures[0].output == "expected: <5> but was: <0>"

    assert result.failures[1].test_method == "testCalculateMaxCupsWithInsufficientBeans"
    assert result.failures[1].test_class == "CoffeeMachineProgram3Test"
    assert result.failures[1].test_file == "CoffeeMachineProgram3Test.java"
    assert result.failures[1].output == "expected: <5> but was: <0>"

    assert result.failures[2].test_method == "testCalculateMaxCups"
    assert result.failures[2].test_class == "CoffeeMachineProgramTest"
    assert result.failures[2].test_file == "CoffeeMachineProgramTest.java"
    assert result.failures[2].output == "Runtime Unexpected failure" # TODO: Parse out full stacktrace on errors


def test_compilation_error(temp_dir, verifier):
    test_output = f"""[INFO] Scanning for projects...
[INFO] 
[INFO] --------------------< com.example:just-for-testing >--------------------
[INFO] Building just-for-testing 1.0-SNAPSHOT
[INFO]   from pom.xml
[INFO] --------------------------------[ jar ]---------------------------------
[INFO] 
[INFO] --- resources:3.3.1:resources (default-resources) @ just-for-testing ---
[WARNING] Using platform encoding (UTF-8 actually) to copy filtered resources, i.e. build is platform dependent!
[INFO] skip non existing resourceDirectory {temp_dir}/src/main/resources
[INFO] 
[INFO] --- compiler:3.11.0:compile (default-compile) @ just-for-testing ---
[INFO] Changes detected - recompiling the module! :source
[WARNING] File encoding has not been set, using platform encoding UTF-8, i.e. build is platform dependent!
[INFO] Compiling 1 source file with javac [debug target 1.8] to target/classes
[INFO] -------------------------------------------------------------
[WARNING] COMPILATION WARNING : 
[INFO] -------------------------------------------------------------
[WARNING] bootstrap class path not set in conjunction with -source 8
[INFO] 1 warning
[INFO] -------------------------------------------------------------
[INFO] -------------------------------------------------------------
[ERROR] COMPILATION ERROR : 
[INFO] -------------------------------------------------------------
[ERROR] {temp_dir}/src/main/java/CoffeeMachineProgram.java:[3,9] incompatible types: missing return value
[INFO] 1 error
[INFO] -------------------------------------------------------------
[INFO] ------------------------------------------------------------------------
[INFO] BUILD FAILURE
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  0.881 s
[INFO] Finished at: 2023-09-12T08:50:20+02:00
[INFO] ------------------------------------------------------------------------
[ERROR] Failed to execute goal org.apache.maven.plugins:maven-compiler-plugin:3.11.0:compile (default-compile) on project just-for-testing: Compilation failure
[ERROR] {temp_dir}/src/main/java/CoffeeMachineProgram.java:[3,9] incompatible types: missing return value
[ERROR] 
[ERROR] -> [Help 1]
[ERROR] 
[ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
[ERROR] Re-run Maven using the -X switch to enable full debug logging.
[ERROR] 
[ERROR] For more information about the errors and possible solutions, please read the following articles:
[ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/MojoFailureException"""

    result = verifier.create_verification_result(test_output)

    assert len(result.failures) == 1
    # TODO: Handle compilation errors!

    assert result.failures[0].test_method == "testCalculateMaxCups"
    assert result.failures[0].test_class == "CoffeeMachineProgram3Test"
    assert result.failures[0].test_file == "CoffeeMachineProgram.java"
    assert result.failures[0].output == "expected: <5> but was: <0>"


def test_extract_test_details(verifier):
    line = "[ERROR]   PredatoryShoeCounterTest.testCountLostSocks_TimeValuesDoNotExceedLimit:55 expected: <1> but was: <3>"

    result = verifier.extract_test_details(line)

    print(result)
