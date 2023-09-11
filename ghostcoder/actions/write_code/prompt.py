from typing import Optional

from ghostcoder.schema import Message, TextItem, FileItem, UpdatedFileItem

ROLE_PROMPT = """Act as a helpful Senior Developer helping a Human to write code."""

DEFAULT_PROMPT = """You can both update the existing files and add new ones if needed. 
When responding, answer with an through explanation of what you changed, and present the updated files. 
Please exclude files that have not been updated.   

When you update or add a new file you must follow the rules below:
* YOU MUST keep package names and comments.
* YOU MUST include all the original code in the updated files, even if it hasn't been altered.  
* YOU SHOULD avoid adding any comments to the new code sections you are proposing.

ALL files should be presented in the following format:

file.py
```python
# ... code  
```
"""

WIZARD_CODER_INSTRUCT_PROMPT = """Below is an instruction that describes a task, paired with an input that
provides further context. Write a response that appropriately completes
the request."""

FEW_SHOT_PYTHON_1 = [
    Message(sender="Human", items=[
        TextItem(text="Update the function factorial to calculate the factorial of a given integer."),
        FileItem(file_path="factorial.py",
                 content="""def factorial(n):
    pass""")
    ]),
    Message(sender="AI", items=[
    #    TextItem(text="""Explanation:
#In the factorial function, we initialize a variable result with the value 1, and then use a for-loop to multiply result by each integer from 2 up to n. The final value of result is returned as the factorial of n."""),
        UpdatedFileItem(file_path="factorial.py",
                 content="""def factorial(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result""")])
]

FEW_SHOT_PYTHON_2 = [
    Message(sender="Human", items=[
        TextItem(text="Create a function named is_palindrome that checks if a given string is a palindrome."),
        FileItem(file_path="palindrome_checker.py",
                 content="""def is_palindrome(s):
    pass""")
    ]),
    Message(sender="AI", items=[
        #TextItem(text="""Explanation:
#In the is_palindrome function, we first convert the string to lowercase and remove spaces to make the check case and space insensitive. Then we compare the string with its reverse to determine if it's a palindrome."""),
        UpdatedFileItem(file_path="palindrome_checker.py",
                 content="""def is_palindrome(s):
    s = s.lower().replace(" ", "")
    return s == s[::-1]""")])
]

FEW_SHOT_PYTHON_3 = [
    Message(sender="Human", items=[
        TextItem(text="Add a new method named area to the class Rectangle that calculates and returns the area of the rectangle."),
        FileItem(file_path="shapes/shapes.py",
                 content="""class Rectangle:
    def __init__(self, length, width):
        self.length = length
        self.width = width""")
    ]),
    Message(sender="AI", items=[
        #TextItem(text="""Explanation:
#In the Rectangle class, the area method calculates the area of the rectangle by multiplying its length and width, and returns the result."""),
        UpdatedFileItem(file_path="shapes/shapes.py",
                 content="""class Rectangle:
    def __init__(self, length, width):
        self.length = length
        self.width = width

    def area(self):
        return self.length * self.width""")])
]

FEW_SHOTS_PYTHON = FEW_SHOT_PYTHON_1 + FEW_SHOT_PYTHON_2 + FEW_SHOT_PYTHON_3

EXPECT_INCOMPLETE = """You can both update the existing files and add new ones if needed. 

When responding, answer with an through explanation of what you changed, and present the updated or added files. 
Please exclude files that have not been updated.   

* YOU MUST keep package names and comments.
* YOU MUST avoid adding any comments to the new code sections you are proposing.
* YOU MUST provide valid code 

When updating existing files:
* YOU MUST only print out updated or added lines. 
* YOU MUST replace unchanged lines with a comment. 
* YOU MUST include the definitions of parent classes and functions.

ALL files should be presented in the following format:

file.py
```python
# ... code  
```
"""

NO_PROMPT = """
"""

prompts = {
    "default": DEFAULT_PROMPT,
    "expect_incomplete": EXPECT_INCOMPLETE,
    "wizardcoder": WIZARD_CODER_INSTRUCT_PROMPT,
    "no_prompt": NO_PROMPT
}


def get_implement_prompt(name: Optional[str] = None) -> str:
    if name is None:
        return DEFAULT_PROMPT
    return prompts[name]
