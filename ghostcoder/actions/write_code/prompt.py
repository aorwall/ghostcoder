from typing import Optional

from ghostcoder.schema import Message, TextItem, FileItem, UpdatedFileItem

ROLE_PROMPT = """Act as a helpful Senior Developer helping a Human to write code."""

DEFAULT_PROMPT = ROLE_PROMPT + """\n\nYou can both update the existing files and add new ones if needed. 
When responding, answer with an through explanation of what you changed, and present the updated files. 
Please exclude files that have not been updated.   

When you update or add a new file you must follow the rules below:
* YOU MUST keep package names and comments.
* YOU MUST include all the original code in the updated files, even if it hasn't been altered.  
* YOU SHOULD avoid adding any comments to the new code sections you are proposing.

ALL files should be presented in the following format:
Filepath: path/to/file
```language
code 
```
"""

FEW_SHOT_PYTHON_1 = [
    Message(sender="Human", items=[
        TextItem(text="Update the function factorial to calculate the factorial of a given integer."),
        FileItem(file_path="factorial.py",
                 content="""def factorial(n):
    pass""")
    ]),
    Message(sender="AI", items=[
        TextItem(text="""Explanation:
In the factorial function, we initialize a variable result with the value 1, and then use a for-loop to multiply result by each integer from 2 up to n. The final value of result is returned as the factorial of n."""),
        UpdatedFileItem(file_path="factorial.py",
                 content="""def factorial(n):
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result""")])
]

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
Filepath: path/to/file
```language
code 
```
"""

NO_PROMPT = """
"""

prompts = {
    "default": DEFAULT_PROMPT,
    "expect_incomplete": EXPECT_INCOMPLETE,
    "no_prompt": NO_PROMPT
}


def get_implement_prompt(name: Optional[str] = None) -> str:
    if name is None:
        return DEFAULT_PROMPT
    return prompts[name]
