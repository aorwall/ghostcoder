import json

from tree_sitter import Parser

from ghostcoder.codeblocks import CodeBlockType, CodeParser
from ghostcoder.codeblocks.parser.java import JavaParser


def test_json():
    content = """
{
    "name": "John",
    "age": 30,
    "cars": [
        {
            "name": "Ford"
        },
        {
            "name": "BMW"
        }
    ]
}
"""

    parser = CodeParser("json")
    code_blocks = parser.parse(content)
    assert code_blocks.to_string() == content
