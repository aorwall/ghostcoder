# HR Report Formatting

As a developer at a Human Resources firm, your task is to integrate and format different datasets related to the employees in the firm. The data includes personal details such as name, age, department, job role, and length of service. The data comes in an array of dictionaries where each dictionary represents an individual employee. Your task is to sort the data and output it in a specific format.

## Instructions
1. Write a function that takes in an array of dictionaries. Each dictionary represents an individual employee and contains the following keys: 'name', 'age', 'department', 'job role', and 'length of service'.
2. The function should sort the array in descending order of the length of service. If two employees have the same length of service, sort them in ascending order of their names.
3. The function should return a list of strings. Each string should represent an employee and should be in the following format: "[name] is [age] years old, works in the [department] department as a [job role], and has been with the firm for [length of service] years."

## Constraints
1. 'name', 'department', and 'job role' are strings of alphanumeric characters (1-100).
2. 'age' is an integer ranging from 18 to 75.
3. 'length of service' is a positive integer.
4. The function should handle edge cases such as empty input or missing keys in the dictionaries.

## Evaluation Criteria
1. Correct implementation of the sorting criteria.
2. Correct implementation of the output format.
3. Correct handling of edge cases.
4. No data should be lost or modified in the process of sorting or formatting.