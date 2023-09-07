from langchain import PromptTemplate

from ghostcoder.schema import Message, TextItem, FileItem, UpdatedFileItem

DO_EXERCISE_ROLE_PROMPT = "Act as a an automated AI with superior programming skills."

SKILLS = [
    "problem-solving abilities",
    "coding proficiency",
    "algorithmic thinking",
    "data structure usage",
    "attention to detail",
    "code readability",
    "modularity and reusability",
    "optimization techniques",
    "debugging",
    "time complexity analysis",
    "space complexity analysis",
    "SOLID principles",
    "error handling",
    "code documentation",
    "system scalability",
    "real-world applicability",
    "clean coding practices",
    "adherence to coding standards",
    "state management",
    "concurrency and multithreading",
    "input validation",
    "output formatting",
    "resource management",
    "use of design patterns",
    "exception handling",
    "type safety",
    "database interactions",
    "API usage",
    "avoidance of code duplication",
    "prevention of memory leaks",
    "API design",
    "loose coupling and high cohesion",
    "event-driven architecture",
]

BUSINESS_AREAS = [
    "Finance and Accounting",
    "Marketing and Public Relations",
    "Sales and Customer Service",
    "Human Resources",
    "Information Technology",
    "Supply Chain Management",
    "Health Care Administration",
    "Real Estate",
    "Retail Management",
    "Manufacturing & Production",
    "Consulting",
    "Hospitality & Tourism",
    "Operations Management",
    "Construction & Project Management",
    "E-commerce",
    "Agriculture & Farming",
    "Education and Training",
    "Legal and Compliance",
    "Event Planning",
    "Logistics and Distribution",
    "Business Development",
    "Environmental Management",
    "Advertising and Promotion",
    "Non-profit Management",
    "International Business",
]

BUSINESS_AREAS_PROMPT = """Pick a random business area."""

INSTRUCTION_SYSTEM_PROMPT = """You're a staff engineer with long experience in writing programming exercises. 

When writing new programming exercises you should follow the following rules: 
* The exercise must be unique in a way that makes it impossible to find similar exercises or code on the internet. Think outside the box!
* The exercise should not adhere to a specific programming language. 
* Do not imply on the use of any programming language by including names based on code conventions, the use of specific libaries etc.
* Do not suggest names for variables, functions, classes etc. 
* The solution should be possible to implement in a single file. 
* Another developer will handle the implementation of tests, so you don't need add any instruction about writing tests. 
* The solution should be implementable using only the standard libraries.
* The solution will solely be invoked through test cases and does not require a user interface, database connections, APIs, or command-line interfaces.
* Do not provide any code in the instruction. 

Use the following response format. "path_to/" should be replaced with a relevant directory name with max 24 characters.  

Filepath: path_to/instructions.md
```
# Title 
...description...

## Instructions
1. ... 
2. ...

## Constraints
1. ...
2. ...
```
"""

EXAMPLE_EXERCISE_NAME = "precision_cut"

EXAMPLE_INSTRUCTION = """# Precision Manufacturing 
Modern manufacturing & production businesses require careful control and precise attention to detail, especially when you are tasked to cut the material for use. In this task, you are to implement a small class that will simulate precision cutting on a manufacturing line.

## Instructions
1. Create a class to represent a single piece of raw material. The raw material should have parameters for length, width, and height.
2. Implement a method within the class, which takes in three cutting measurements (length, width, height) as parameters. This should simulate a precision cut of the raw piece in-place, effectively reducing its size.
    * Ensure the cut does not result in any dimension of the raw material becoming negative or zero. If any such cut is attempted, then it should be considered as invalid. 
    * After a successful cut, update the size of the raw material and return an appropriate message with the new dimensions.
    * In case of an invalid cut, return an appropriate error message.
3. Implement a method which returns the current dimensions of the material.
4. Implement a method which returns the volume of the material after all the applied cuts.

## Constraints
1. The initial length, width, and height of a piece of raw material should not exceed 10000 units.
2. All dimensions are positive integers.
3. Each method should be able to handle a maximum of 100 function calls within 1 second.
"""

CREATE_BUSINESS_INSTRUCTION_PROMPT = PromptTemplate.from_template("""Write a instruction for a programming exercise of {difficulty} difficulty that is related to the {business_area} business. 
It's especially important that the exercise evaluates the candidate's knowledge of {skill}. 
""")

INSTRUCTION_FEW_SHOTS = [
    Message(sender="Human", items=[
        TextItem(text="""Write a short instruction for a small programming exercise of easy difficulty that is related to the Event Planning business. 
It's especially important that the exercise evaluates the candidate's knowledge of attention to detail. """),
    ]),
    Message(sender="AI", items=[
        FileItem(file_path=f"{EXAMPLE_EXERCISE_NAME}/instructions.md", content=EXAMPLE_INSTRUCTION, read_only=True)
    ])
]

REVIEW_INSTRUCTION_SYSTEM_PROMPT = """You are a staff engineer at a large company and are responsible for reviewing a 
suggestion on a new programming exercise that can be used in the interview process. It's created by a junior developer
and there may be issues in the submitted work that need to be addressed. 
 
Respond with the updated file and list of the changes you made.

Things to look for:
* Skill: Does the exercise evaluate the candidate's knowledge of {skill} 
* No Contradictions: Check to see if there are conflicting instructions or requirements.
* Level of Difficulty: Verify that the exercise is of {difficulty} difficulty
* Clarity of Instructions: Ensure that the problem statement is clear and easy to understand. Avoid jargon unless it's explained or necessary for the exercise.
"""


WRITE_TEST_AND_STUB_SYSTEM_PROMPT = """You are a staff engineer at a large company, you have been given an programming exercise 
instruction and should write a test suite to validate the implementation based on the given requirements. Provide a 
skeletal code file (file stub) containing only the functions and structures that are essential for your tests 
to run successfully.

Please adhere to the following rules:
* There should be no contradictions between the test suite and the instructions.
* Either the instructions must clearly specify the types, data structures, etc., needed to run the tests.
* The tests should cover all the requirements, corner cases, and constraints specified in the instructions.
* All test methods must be properly implemented. If a test method cannot be implemented due to missing instructions, 
"""

WRITE_TEST_AND_STUB_PROMPT = PromptTemplate.from_template("""Create a test suite and stub in {language}""")

VERIFY_TEST_SYSTEM_PROMPT = """The programming exercise can be found in the file instructions.md. Accompanying these instructions is a test suite to 
verify that the requirements have been implemented correctly.

Please verify the following in the files:
* There should be no contradictions between the test suite and the instructions.
* The tests should cover all the requirements, edge cases, and constraints specified in the instructions.
* All test methods must be properly implemented. If a test method cannot be implemented due to missing instructions, the instructions file needs to be updated.

Please return the updated files.
"""

VERIFY_STUB_PROMPT = """{role_description}

The programming exercise can be found in the instructions.md file. Accompanying these instructions is a test suite 
designed to verify that the requirements have been correctly implemented. The individual who will implement the exercise 
will not have access to these tests, and the verification will be conducted automatically without human intervention.

To assist in this process, a skeletal code file (also known as a file stub) is provided. This file should contain only 
the functions and structures essential for running the tests. All other implementation details should be handled by the 
person completing the exercise.

Please verify that the file stub is compatible with the tests.

Return the updated files if necessary.
"""

VERIFY_AFTER_TEST_SYSTEM_PROMPT = """You are a staff engineer at a large company who implemented a new programming 
exercise. A junior developer did the exercise and the test suite failed. Analyse if the test suite or the 
instructions need to be corrected or if the developer made a mistake. Do not change the developers implementation.

Respond with the updated files and list of the changes you made.
"""

VERIFY_AFTER_TEST_NO_CHANGES_PROMPT = PromptTemplate.from_template("""
I tried to implement the exercise in {implementation_file} which resulted in failed tests.

The testas fails with the following output:
{test_output}
""")


EXAMPLE_INCOMPLETE_TEST_SUITE = """import unittest
from precision_cut import RawMaterial

class TestRawMaterial(unittest.TestCase):

    def setUp(self):
        self.material = RawMaterial(100, 100, 100)

    def test_precise_cut_valid(self):
        response = self.material.precise_cut(10, 10, 10)
        self.assertEqual(response, "Cut successful. New dimensions are: 90, 90, 90")

    def test_precise_cut_invalid(self):
        response = self.material.precise_cut(110, 110, 110)
        self.assertEqual(response, "Invalid cut. Dimensions cannot be negative or zero.")

    def test_get_current_size(self):
        self.material.precise_cut(10, 10, 10)
        size = self.material.get_current_size()
        self.assertEqual(size, (90, 90, 90))

if __name__ == '__main__':
    unittest.main()
"""

EXAMPLE_EXTENDED_TEST_SUITE = """import unittest
from precision_cut import RawMaterial

class TestRawMaterial(unittest.TestCase):

    def setUp(self):
        self.material = RawMaterial(100, 100, 100)

    def test_initial_size(self):
        self.assertEqual(self.material.get_current_size(), (100, 100, 100))

    def test_max_initial_size(self):
        with self.assertRaises(ValueError):
            RawMaterial(10001, 10000, 10000)

    # ... existing tests

    def test_get_volume(self):
        self.material.precise_cut(10, 10, 10)
        volume = self.material.get_volume()
        self.assertEqual(volume, 90*90*90)

if __name__ == '__main__':
    unittest.main()
"""

VERIFY_TEST_SUIT_FEW_SHOTS = [
    Message(sender="Human", items=[
        FileItem(file_path=f"{EXAMPLE_EXERCISE_NAME}/instructions.md", content=EXAMPLE_INSTRUCTION, read_only=True),
        FileItem(file_path=f"{EXAMPLE_EXERCISE_NAME}/python/{EXAMPLE_EXERCISE_NAME}_test.py", content=EXAMPLE_INCOMPLETE_TEST_SUITE)
    ]),
    Message(sender="AI", items=[
        TextItem(text="""The instructions and the test suite seem to be in alignment, but there are a few things missing:

1. There is no test case for the initial creation of the `RawMaterial` object. This should be tested to ensure that the initial dimensions are set correctly and that they do not exceed the maximum allowed size of 10000 units.

2. There is no test case for the `get_volume` method, which is supposed to return the volume of the material after all the applied cuts.

3. There is no test case for edge cases, such as when the cut dimensions are equal to the current dimensions of the material, or when the cut dimensions are zero."""),
        UpdatedFileItem(file_path=f"{EXAMPLE_EXERCISE_NAME}/python/{EXAMPLE_EXERCISE_NAME}_test.py", content=EXAMPLE_EXTENDED_TEST_SUITE, read_only=True)
    ])
]
