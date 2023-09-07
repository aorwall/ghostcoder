from ghostcoder.verify.verify_python_unittest import  find_failed_tests


def test_parse_output():
    output = """FFFFFFFFFF
======================================================================
FAIL: test_bird (food_chain_test.FoodChainTest.test_bird)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "food-chain/food_chain_test.py", line 34, in test_bird
    self.assertEqual(
AssertionError: None != ['I know an old lady who swallowed a bird[236 chars]ie."]

======================================================================
FAIL: test_cat (food_chain_test.FoodChainTest.test_cat)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "food-chain/food_chain_test.py", line 46, in test_cat
    self.assertEqual(
AssertionError: None != ['I know an old lady who swallowed a cat.[281 chars]ie."]
----------------------------------------------------------------------

Ran 2 tests in 0.001s

FAILED (failures=2)"""

    failures = find_failed_tests(output)
    print(failures)

