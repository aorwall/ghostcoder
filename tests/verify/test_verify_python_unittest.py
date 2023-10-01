import os
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest

from ghostcoder.test_tools.verify_python_unittest import PythonUnittestTestTool


@pytest.fixture
def temp_dir():
    with TemporaryDirectory() as temp_dir:
        open(os.path.join(temp_dir, "food_chain_test.py"), "w").close()
        open(os.path.join(temp_dir, "sales_queries_test.py"), "w").close()
        open(os.path.join(temp_dir, "healthcare_app_administration_test.py"), "w").close()

        yield temp_dir


@pytest.fixture
def verifier(temp_dir):
    return PythonUnittestTestTool(current_dir=Path(temp_dir))


def test_parse_output(temp_dir, verifier):
    test_output = f"""FFFFFFFFFF
======================================================================
FAIL: test_bird (food_chain_test.FoodChainTest.test_bird)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "{temp_dir}/food_chain_test.py", line 34, in test_bird
    self.assertEqual(
AssertionError: None != ['I know an old lady who swallowed a bird[236 chars]ie."]

======================================================================
FAIL: test_cat (food_chain_test.FoodChainTest.test_cat)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "{temp_dir}/food_chain_test.py", line 46, in test_cat
    self.assertEqual(
AssertionError: None != ['I know an old lady who swallowed a cat.[281 chars]ie."]
----------------------------------------------------------------------

Ran 3 tests in 0.001s

FAILED (failures=2)"""

    failed, total = verifier.parse_test_results(test_output)
    assert failed == 2
    assert total == 3

    failures = verifier.find_failed_tests(test_output)

    assert len(failures) == 2

    assert failures[0].test_method == "test_bird"
    assert failures[0].test_class == "FoodChainTest"
    assert failures[0].test_file == "food_chain_test.py"
    assert failures[0].output == """line 34, in test_bird
    self.assertEqual(
AssertionError: None != ['I know an old lady who swallowed a bird[236 chars]ie."]"""

    assert failures[1].test_method == "test_cat"
    assert failures[1].test_class == "FoodChainTest"
    assert failures[1].test_file == "food_chain_test.py"
    assert failures[1].output == """line 46, in test_cat
    self.assertEqual(
AssertionError: None != ['I know an old lady who swallowed a cat.[281 chars]ie."]"""


# TODO
def test_parse_test_results_errors(temp_dir, verifier):
    test_output = f"""E.......E.E..
======================================================================
ERROR: test_add_customer (sales_queries_test.TestCustomerDatabase.test_add_customer)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "{temp_dir}/sales_queries_test.py", line 11, in test_add_customer
    self.assertEqual(self.db.customers[1].name, 'John Doe')
                     ~~~~~~~~~~~~~~~~~^^^
IndexError: list index out of range

======================================================================
ERROR: sales_queries_test (unittest.loader._FailedTest.sales_queries_test)
----------------------------------------------------------------------
ImportError: Failed to import test module: sales_queries_test
Traceback (most recent call last):
  File "/usr/lib/python3.11/unittest/loader.py", line 407, in _find_test_path
    module = self._get_module_from_name(name)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.11/unittest/loader.py", line 350, in _get_module_from_name
    __import__(name)
  File "{temp_dir}/sales_queries_test.py", line 2, in <module>
    from sales_queries import CustomerDatabase
  File "{temp_dir}/sales_queries.py", line 23
    if id not in self.customers:
    ^^
IndentationError: expected an indented block after function definition on line 22
----------------------------------------------------------------------

Ran 13 tests in 0.009s

FAILED (errors=2)
"""

    failed, total = verifier.parse_test_results(test_output)
    assert failed == 2
    assert total == 13

    failures = verifier.find_failed_tests(test_output)

    assert len(failures) == 2

    assert failures[0].test_method == "test_add_customer"
    assert failures[0].test_class == "TestCustomerDatabase"
    assert failures[0].test_file == "sales_queries_test.py"
    assert failures[0].output == """line 11, in test_add_customer
    self.assertEqual(self.db.customers[1].name, 'John Doe')
                     ~~~~~~~~~~~~~~~~~^^^
IndexError: list index out of range"""

    assert failures[1].test_method == "sales_queries_test"
    assert failures[1].test_class is None
    assert failures[1].test_file is None
    assert failures[1].output == """ImportError: Failed to import test module: sales_queries_test
Traceback (most recent call last):
  File "/usr/lib/python3.11/unittest/loader.py", line 407, in _find_test_path
    module = self._get_module_from_name(name)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.11/unittest/loader.py", line 350, in _get_module_from_name
    __import__(name)
  File "sales_queries_test.py", line 2, in <module>
    from sales_queries import CustomerDatabase
  File "sales_queries.py", line 23
    if id not in self.customers:
    ^^
IndentationError: expected an indented block after function definition on line 22"""


def test_parse_test_results_both_failures_and_errors(temp_dir, verifier):
    test_output = f"""EFFF.F..E.EF.
======================================================================
ERROR: test_add_customer (sales_queries_test.TestCustomerDatabase.test_add_customer)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "{temp_dir}/sales_queries_test.py", line 11, in test_add_customer
    self.assertEqual(self.db.customers[1].name, 'John Doe')
                     ~~~~~~~~~~~~~~~~~^^^
IndexError: list index out of range

======================================================================
FAIL: test_add_customer_with_invalid_purchase (sales_queries_test.TestCustomerDatabase.test_add_customer_with_invalid_purchase)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "{temp_dir}/sales_queries_test.py", line 28, in test_add_customer_with_invalid_purchase
    with self.assertRaises(ValueError):
AssertionError: ValueError not raised

----------------------------------------------------------------------
Ran 13 tests in 0.011s

FAILED (failures=1, errors=1)
"""

    failed, total = verifier.parse_test_results(test_output)
    assert failed == 2
    assert total == 13

    failures = verifier.find_failed_tests(test_output)
    assert len(failures) == 2

    assert failures[0].test_method == "test_add_customer"
    assert failures[0].test_class == "TestCustomerDatabase"
    assert failures[0].test_file == "sales_queries_test.py"
    assert failures[0].output == """line 11, in test_add_customer
    self.assertEqual(self.db.customers[1].name, 'John Doe')
                     ~~~~~~~~~~~~~~~~~^^^
IndexError: list index out of range"""

    assert failures[1].test_method == "test_add_customer_with_invalid_purchase"
    assert failures[1].test_class == "TestCustomerDatabase"
    assert failures[1].test_file == "sales_queries_test.py"
    assert failures[1].output == """line 28, in test_add_customer_with_invalid_purchase
    with self.assertRaises(ValueError):
AssertionError: ValueError not raised"""


def test_parse_test_result_import_error(temp_dir, verifier):
    test_output = f""".E..F.
======================================================================
ERROR: test_assign_patient (healthcare_app_administration_test.TestQueueManagementSystem.test_assign_patient)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "{temp_dir}/healthcare_app_administration_test.py", line 24, in test_assign_patient
    assigned_patient, health_professional = self.system.assign_patient()
                                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "{temp_dir}/healthcare_app_administration.py", line 34, in assign_patient
    raise Exception("No health professionals available")
Exception: No health professionals available

----------------------------------------------------------------------
Ran 6 tests in 0.010s

FAILED (errors=1)
"""

    failed, total = verifier.parse_test_results(test_output)
    assert failed == 1
    assert total == 6

    failures = verifier.find_failed_tests(test_output)
    assert len(failures) == 1

    assert failures[0].test_method == "test_assign_patient"
    assert failures[0].test_class == "TestQueueManagementSystem"
    assert failures[0].test_file == "healthcare_app_administration_test.py"
    assert failures[0].output == """line 24, in test_assign_patient
    assigned_patient, health_professional = self.system.assign_patient()
                                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "healthcare_app_administration.py", line 34, in assign_patient
    raise Exception("No health professionals available")
Exception: No health professionals available"""

def test_parse_test_result_import_error(temp_dir, verifier):
    test_output = f"""ETraceback (most recent call last):

  File "/usr/lib/python3.11/unittest/loader.py", line 154, in loadTestsFromName
    module = __import__(module_name)
             ^^^^^^^^^^^^^^^^^^^^^^^
  File "{temp_dir}/sales_queries_test.py", line 2, in <module>
    from real_estate_concurrent_processing import Property, calculate_price, calculate_prices_concurrently
  File "{temp_dir}/sales_queries.py", line 32, in <module>
    num_threads = min(8, len(properties))
                             ^^^^^^^^^^
NameError: name 'properties' is not defined. Did you mean: 'Property'?
"""

    failed, total = verifier.parse_test_results(test_output)
    assert failed == 1
    assert total == 1

    failures = verifier.find_failed_tests(test_output)

    assert len(failures) == 1
    assert failures[0].test_method is None
    assert failures[0].test_class == "TestQueueManagementSystem"
    assert failures[0].test_file == "healthcare_app_administration_test.py"
    assert failures[0].output == """line 24, in test_assign_patient
        assigned_patient, health_professional = self.system.assign_patient()
                                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
      File "healthcare_app_administration.py", line 34, in assign_patient
        raise Exception("No health professionals available")
    Exception: No health professionals available"""
