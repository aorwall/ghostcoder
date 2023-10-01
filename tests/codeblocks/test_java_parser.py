import json

from ghostcoder.codeblocks import CodeBlockType
from ghostcoder.codeblocks.parser.java import JavaParser

parser = JavaParser()

def test_java_class():
    with open("java/Example.java", "r") as f:
        content = f.read()

    code_blocks = parser.parse(content)
    assert code_blocks.to_string() == content


def test_all_type_sitter_types():
    with open("java/TreeSitterTypes.java", "r") as f:
        content = f.read()
    with open("java/TreeSitterTypes_expected.txt", "r") as f:
        expected_tree = f.read()

    code_blocks = parser.parse(content)
    print(code_blocks.to_tree(include_tree_sitter_type=False))
    assert code_blocks.to_string() == content
    assert code_blocks.to_tree() == expected_tree

def test_java_invalid():
    with open("java/Book_invalid_update.java", "r") as f:
        content = f.read()

    code_blocks = parser.parse(content)

    print(code_blocks.to_tree())
    assert len(code_blocks.find_errors()) == 3

def test_java_class_2():
    with open("java/CoffeeMachineProgram.java", "r") as f:
        content = f.read()

    code_blocks = parser.parse(content)

    print(code_blocks.to_tree(include_tree_sitter_type=False))
    assert code_blocks.to_string() == content
