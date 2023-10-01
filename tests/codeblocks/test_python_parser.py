import json

from ghostcoder.codeblocks import CodeBlockType
from ghostcoder.codeblocks.parser.python import PythonParser

parser = PythonParser()

def test_python_calculator():
    with open("python/calculator.py", "r") as f:
        content = f.read()

    code_blocks = parser.parse(content)

    print(code_blocks.to_tree(include_tree_sitter_type=True))

    print(code_blocks.to_string())

    assert code_blocks.to_string() == content

def test_python_with_comment():
    with open("python/calculator_insert1.py", "r") as f:
        content = f.read()

    code_blocks = parser.parse(content)

    print(code_blocks.to_tree(include_tree_sitter_type=True))

    assert code_blocks.to_string() == content

def test_python_with_comment_2():
    with open("python/calculator_insert2.py", "r") as f:
        content = f.read()

    code_blocks = parser.parse(content)

    print(code_blocks.to_tree(include_tree_sitter_type=True))

    assert code_blocks.to_string() == content



def test_python_function_with_only_comment():
    content = """def foo():\n    # ... rest of the code\ni = 0"""

    code_blocks = parser.parse(content)

    print(code_blocks.to_tree(include_tree_sitter_type=True))

    assert code_blocks.to_string() == content


def test_python_function_followed_by_unintended_comment():
    content = """def foo():\n# ... rest of the code"""

    code_blocks = parser.parse(content)

    print(code_blocks.to_tree(include_tree_sitter_type=True))

    assert code_blocks.to_string() == content

def test_python_example():
    with open("python/example.py", "r") as f:
        content = f.read()

    code_blocks = parser.parse(content)

    print(code_blocks.to_tree(include_tree_sitter_type=True))

    assert code_blocks.to_string() == content

def test_python_all_treesitter_types():
    with open("python/treesitter_types.py", "r") as f:
        content = f.read()
    with open("python/treesitter_types_expected.txt", "r") as f:
        expected_tree = f.read()

    code_blocks = parser.parse(content)

    print(code_blocks.to_tree(include_tree_sitter_type=False))

    assert code_blocks.to_tree() == expected_tree
    assert code_blocks.to_string() == content


def test_expression_list():
    code_blocks = parser.parse("1, 2, 3")
    assert code_blocks.to_tree() == """ 0 module ``
  1 code `1`
  1 code `,`
  1 code `2`
  1 code `,`
  1 code `3`
"""


def test_outer_inner_def():
    codeblocks = parser.parse("""def outer():
    x = 10
    def inner():
        nonlocal x
        x = 20
    inner()
    print(x)
""")
    print(codeblocks.to_tree(include_tree_sitter_type=True))


def test_python_has_error_blocks():
    with open("python/dsl_dsl_find_update.py", "r") as f:
        content = f.read()

    code_blocks = parser.parse(content)

    print(code_blocks.to_tree(include_tree_sitter_type=True))
    print(code_blocks.find_errors()[0].to_string())

    assert len(code_blocks.find_errors()) == 1
    assert code_blocks.find_errors()[0].to_string() == """for item in data:
    # ...
    elif item[0] == EDGE:
        if len(item) != 3 or not isinstance(item[1], str) or not isinstance(item[2], str) or not isinstance(item[3], dict):
            raise ValueError("Edge is malformed")
        self.edges.append(Edge(item[1], item[2], item[3]))"""



def test_python_has_two_error_blocks():
    with open("python/proverb_replace.py", "r") as f:
        content = f.read()

    code_blocks = parser.parse(content)

    print(code_blocks.to_tree(include_tree_sitter_type=True))

    assert len(code_blocks.find_errors()) == 2
    assert code_blocks.find_errors()[0].to_string() == """
    for i in reversed(range(len(len(input_list)):
        result.append(f"For {qualifier} of a {input_list[i]}")"""
    assert code_blocks.find_errors()[1].to_string() == """
    return "."""

    print(code_blocks.find_errors()[0].copy_with_trimmed_parents().root().to_string())

def test_python_if_and_indentation_parsing_2():
    with open("python/if_clause.py", "r") as f:
        content = f.read()

    code_blocks = parser.parse(content)

    print(code_blocks.to_tree())

    assert code_blocks.to_string() == content


def test_python_two_classes():
    with open("python/binary_search.py", "r") as f:
        content = f.read()

    code_blocks = parser.parse(content)

    print(code_blocks.to_tree())

    assert code_blocks.to_string() == content


def test_python_comments():
    with open("python/word_search_update.py", "r") as f:
        content = f.read()

    code_blocks = parser.parse(content)

    print(code_blocks.to_tree())

    assert code_blocks.to_string() == content



def test_python_sublist():
    with open("python/sublist.py", "r") as f:
        content = f.read()

    code_blocks = parser.parse(content)

    print(code_blocks.to_tree())

    assert code_blocks.to_string() == content

def test_python_indentation_empty_lines():
    with open("python/circular_buffer.py", "r") as f:
        content = f.read()

    code_blocks = parser.parse(content)

    print(code_blocks.to_tree())

    assert code_blocks.to_string() == content
