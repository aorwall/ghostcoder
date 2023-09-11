import unittest
from human_resources_formatting import format_employee_data

class TestHumanResourcesFormatting(unittest.TestCase):
    def test_empty_input(self):
        # Test case for empty input
        self.assertEqual(format_employee_data([]), [])

    def test_missing_keys(self):
        # Test case for missing keys in the dictionaries
        self.assertEqual(format_employee_data([{'name': 'John', 'age': 30, 'department': 'IT'}]), ['John is 30 years old, works in the IT department as a Unknown, and has been with the firm for Unknown years.'])

    def test_sorting_criteria(self):
        # Test case for correct implementation of the sorting criteria
        input_data = [{'name': 'John', 'age': 30, 'department': 'IT', 'job role': 'Developer', 'length of service': 5}, {'name': 'Alice', 'age': 35, 'department': 'HR', 'job role': 'Manager', 'length of service': 10}]
        expected_output = ['Alice is 35 years old, works in the HR department as a Manager, and has been with the firm for 10 years.', 'John is 30 years old, works in the IT department as a Developer, and has been with the firm for 5 years.']
        self.assertEqual(format_employee_data(input_data), expected_output)

    def test_sorting_criteria_same_length_of_service(self):
        # Test case for correct implementation of the sorting criteria when length of service is the same
        input_data = [{'name': 'John', 'age': 30, 'department': 'IT', 'job role': 'Developer', 'length of service': 5}, {'name': 'Alice', 'age': 35, 'department': 'HR', 'job role': 'Manager', 'length of service': 5}]
        expected_output = ['Alice is 35 years old, works in the HR department as a Manager, and has been with the firm for 5 years.', 'John is 30 years old, works in the IT department as a Developer, and has been with the firm for 5 years.']
        self.assertEqual(format_employee_data(input_data), expected_output)

    def test_output_format(self):
        # Test case for correct implementation of the output format
        input_data = [{'name': 'John', 'age': 30, 'department': 'IT', 'job role': 'Developer', 'length of service': 5}]
        expected_output = ['John is 30 years old, works in the IT department as a Developer, and has been with the firm for 5 years.']
        self.assertEqual(format_employee_data(input_data), expected_output)

if __name__ == '__main__':
    unittest.main()