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
* The solution should be possible implement in a single function. 
* Max 3 instructions
* The exercise must be unique in a way that makes it impossible to find similar exercises or code on the internet. Think outside the box!
* The exercise should not adhere to a specific programming language. 
* Do not imply on the use of any programming language by including names based on code conventions, the use of specific libaries etc.
* Do not suggest names for variables, functions, classes etc. 
* Another developer will handle the implementation of tests, so you don't need add any instruction about writing tests. 
* The solution should be implementable using only the standard libraries.
* The solution will solely be invoked through test cases and does not require a user interface, database connections, APIs, or command-line interfaces.
* Do not provide any code in the instruction. 

Respond with the following format:

# ...Title... 
...description...

## Instructions
1. ... 
2. ...

## Constraints
1. ...
2. ...

## Evaluation Criteria
1. ...
2. ...
"""

DIRECTORY_NAME_PROMPT = """Come up with a directory name for the exercise. It should be in snake_case with max 24 characters. Only return the directory name."""

FILE_SCOPE = "* The solution should be possible to implement in a single file. "
FUNCTION_SCOPE = "* The instructions should eb for a solution small and simple enough to implement in a single function. "

EXAMPLE_EXERCISE_NAME = "sales_queries"

EXAMPLE_INSTRUCTION = """# Customer Database Tracker
In a Sales and Customer Service business, it's critical to maintain customer details for future interactions. Your task is to implement a lightweight, temporary in-memory "database" to store and process customer information.

## Instructions
1. Implement a class representing an in-memory database of customers. Each customer should have an id, name, and total purchases value.
2. Method to add a new customer into your database. The input will be an id, a name, and the total purchases. No two customers can have the same id.
3. Method to delete a customer from the database, given a customer's id.
4. Method that returns a list of all customers' information, sorted by the total purchases in descending order.
5. Method that takes in an id and a purchase value, then updates the corresponding customer’s total purchases.

## Constraints
1. The length of the customer name does not exceed 100 characters.
2. Ids are unique positive integers not exceeding 10,000 and purchases are decimal numbers between 0.1 and 1,000,000. 
3. The 'database' should be able to handle a maximum of 1,000 customers.
4. Each method should be able to handle a maximum of 100 function calls within 1 second."""

CREATE_BUSINESS_INSTRUCTION_PROMPT = PromptTemplate.from_template("""Write a instruction for a programming exercise of **{difficulty}** difficulty that is related to the **{business_area}** business. 

It's especially important that the exercise evaluates the candidate's knowledge of **{skill}**.""")

INSTRUCTION_FEW_SHOTS = [
    Message(sender="Human", items=[
        TextItem(text="""Write a instruction for a programming exercise of easy difficulty that is related to the Sales and Customer Service business. 
It's especially important that the exercise evaluates the candidate's knowledge of database interaction. """),
    ]),
    Message(sender="AI", items=[
        FileItem(file_path=f"{EXAMPLE_EXERCISE_NAME}/instructions.md", content=EXAMPLE_INSTRUCTION, read_only=True)
    ])
]

REVIEW_INSTRUCTION_SYSTEM_PROMPT = """You are a staff engineer at a large company and are responsible for reviewing a 
suggestion on a new programming exercise that can be used in the interview process. It's created by a junior developer
and there may be issues in the submitted work that need to be addressed.  

First list of the changes you made and then print out the updated file.
 
Do not add any other sections than Instructions, Constraints and Evaluation Criteria.

Do not change the description of the exercise or the title if not absolutely necessary.

Things to look for:
* Skill: Does the exercise evaluate the candidate's knowledge of {skill} 
* No Contradictions: Check to see if there are conflicting instructions or requirements.
* Level of Difficulty: Verify that the exercise is of {difficulty} difficulty
* Clarity of Instructions: Ensure that the problem statement is clear and easy to understand. Avoid jargon unless it's explained or necessary for the exercise.
"""

WRITE_TEST_AND_SOLUTION_SYSTEM_PROMPT = PromptTemplate.from_template("""You are a staff engineer at a large company, you have been given an programming exercise 
instruction and should write an example implementation and a test suite in {language} to validate the implementation based on the given requirements.

Please adhere to the following rules:
* Each test case should be in its own test method.
* There should be at least one test method for each instruction and constraint.
* There should be no contradictions between the test suite and the instructions.
* The interfaces in the solution code should clearly specify the types, data structures, etc., needed to run the tests.
* All test methods must be properly implemented. If a test method cannot be implemented due to missing instructions, 
* Write a description of the test case on which instructions or constraints it tests. 
{language_specifics}
""")

EXAMPLE_IMPLEMENTATION = """class Customer:
    def __init__(self, id: int, name: str, total_purchases: float):
        self.id = id
        self.name = name
        self.total_purchases = total_purchases

class CustomerDatabase:
    def __init__(self):
        self.customers = {}

    def add_customer(self, id: int, name: str, total_purchases: float):
        if id in self.customers:
            raise ValueError("A customer with this id already exists.")
        if len(name) > 100:
            raise ValueError("The customer name is too long.")
        if id > 10000:
            raise ValueError("The id is too large.")
        if not (0.1 <= total_purchases <= 1000000):
            raise ValueError("The purchase amount is invalid.")
        self.customers[id] = Customer(id, name, total_purchases)

    def delete_customer(self, id: int):
        if id not in self.customers:
            raise ValueError("The customer does not exist.")
        del self.customers[id]

    def get_all_customers(self):
        return sorted(self.customers.values(), key=lambda x: x.total_purchases, reverse=True)

    def update_purchase(self, id: int, purchase: float):
        if id in self.customers:
            self.customers[id].total_purchases += purchase"""

EXAMPLE_STUB = """class Customer:
    def __init__(self, id: int, name: str, total_purchases: float):
        pass

class CustomerDatabase:
    def __init__(self):
        pass

    def add_customer(self, id: int, name: str, total_purchases: float):
        pass

    def delete_customer(self, id: int):
        pass

    def get_all_customers(self):
        pass

    def update_purchase(self, id: int, purchase: float):
        pass"""

EXAMPLE_STUB_WITH_COMMENTS = """class Customer:
    def __init__(self, id: int, name: str, total_purchases: float):
        \"""
        Initialize the customer with the given id, name, and total purchases.

        Parameters:
        - id (int): Unique identifier for the customer.
        - name (str): Name of the customer.
        - total_purchases (float): Total purchases made by the customer.
        \"""
        pass

class CustomerDatabase:
    def __init__(self):
        \"""
        Initialize an empty dictionary to store the customers.
        \"""
        pass

    def add_customer(self, id: int, name: str, total_purchases: float):
        \"""
        Add a new customer to the database.

        Parameters:
        - id (int): Unique identifier for the customer.
        - name (str): Name of the customer.
        - total_purchases (float): Total purchases made by the customer.

        Raises:
        - ValueError: If a customer with the given id already exists.
        - ValueError: If the length of the name is more than 100 characters.
        - ValueError: If the id is more than 10000.
        - ValueError: If the total purchases is not between 0.1 and 1,000,000.
        \"""
        pass

    def delete_customer(self, id: int):
        \"""
        Delete the customer with the given id from the database.

        Parameters:
        - id (int): Unique identifier for the customer to be deleted.

        Raises:
        - ValueError: If no such customer exists.
        \"""
        pass

    def get_all_customers(self):
        \"""
        Return a list of all customers, sorted by their total purchases in descending order.

        Returns:
        - List[Customer]: A list of all customers sorted by total purchases.
        \"""
        pass

    def update_purchase(self, id: int, purchase: float):
        \"""
        Update the total purchases of the customer with the given id by adding the given purchase amount.

        Parameters:
        - id (int): Unique identifier for the customer to be updated.
        - purchase (float): Purchase amount to be added.

        Raises:
        - ValueError: If no such customer exists.
        \"""
        pass"""

CREATE_STUBS_FEW_SHOTS = [
    Message(sender="Human", items=[
        FileItem(file_path=f"{EXAMPLE_EXERCISE_NAME}/instructions.md", content=EXAMPLE_INSTRUCTION, read_only=True),
        FileItem(file_path=f"{EXAMPLE_EXERCISE_NAME}/python/{EXAMPLE_EXERCISE_NAME}.py", content=EXAMPLE_IMPLEMENTATION, read_only=True),
    ]),
    Message(sender="AI", items=[
        FileItem(file_path=f"{EXAMPLE_EXERCISE_NAME}/python/{EXAMPLE_EXERCISE_NAME}.py", content=EXAMPLE_STUB_WITH_COMMENTS),
    ])
]

CREATE_STUBS_SYSTEM_PROMPT = PromptTemplate.from_template("""You are a staff engineer at a large company, you have been given an programming exercise 
with a test suite and a reference implementation. 

The individual who will do the exercise will not have access to these tests, and the verification will be conducted automatically without human intervention.

To assist in this process, you should replace existing files with skeletal code files (also known as a file stubs) from the reference implementation. These files should contain only 
the functions and structures essential for running the tests. All other implementation details should be written by the person doing the exercise.

Please adhere to the following rules:
* There should be no contradictions between the file stub and the instructions.
* The interfaces in the file stub code should clearly specify the types, data structures, etc., needed to run the tests.
{language_specifics}
""")

CREATE_STUBS_PYTHON_RULES = """* Use docstrings to create comments for each method and class."""

CREATE_STUBS_JAVA_RULES = """* Use Javadoc to create comments for each method and class."""

VERIFY_TEST_SYSTEM_PROMPT = """The programming exercise can be found in the file instructions.md. 
Accompanying these instructions is an example implementation and a test suite to verify that the requirements have been implemented correctly.

Please verify the following in the files:
* Each test case should be in its own method. If one test method covers more than one case it should be split into multiple methods.
* There should be no contradictions between the test suite, the implementation and the instructions. Update any of the files if necessary.
* There should be at least one test method for each instruction and constraint. Add any missing test methods. 
* The tests should cover all the requirements, edge cases, and constraints specified in the instructions. Add any missing test methods.
* All test methods must be properly implemented. If a test method cannot be implemented due to missing instructions, the instructions file needs to be updated.
* Update instructions that can't be implemented or tested.

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
