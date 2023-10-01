from ghostcoder.codeblocks.codeblocks import CodeBlockType, CodeBlock
from ghostcoder.codeblocks.parser.python import PythonParser

parser = PythonParser()

code = CodeBlock(content="",
                 type=CodeBlockType.MODULE,
                 children=[CodeBlock(
                     content="public class TreeSitterExample ",
                     type=CodeBlockType.CLASS,
                     pre_code="",
                     children=[
                         CodeBlock(content="{",
                                   type=CodeBlockType.BLOCK_DELIMITER,
                                   pre_code=""),
                         CodeBlock(
                             content="int myVariable = 10;",
                             type=CodeBlockType.CODE,
                             pre_code="\n\n    "),
                         CodeBlock(
                             content="public void myMethod(int parameter) ",
                             type=CodeBlockType.FUNCTION,
                             pre_code="\n\n    ",
                             children=[
                                 CodeBlock(
                                     content="{",
                                     type=CodeBlockType.BLOCK_DELIMITER,
                                     pre_code=""),
                                 CodeBlock(
                                     content="myVariable = parameter;",
                                     type=CodeBlockType.CODE,
                                     pre_code="\n        "),
                                 CodeBlock(
                                     content="}",
                                     pre_code="\n    ",
                                     type=CodeBlockType.BLOCK_DELIMITER)]),
                         CodeBlock(content="}",
                                   type=CodeBlockType.BLOCK_DELIMITER,
                                   pre_code="\n")
                     ])])


def test_to_string():
    assert code.to_string() == """public class TreeSitterExample {

    int myVariable = 10;

    public void myMethod(int parameter) {
        myVariable = parameter;
    }
}"""


def test_find_nested_matching_block():
    find_block = CodeBlock(content="",
                           type=CodeBlockType.MODULE,
                           children=[CodeBlock(
                               content="public void myMethod(int parameter) ",
                               type=CodeBlockType.FUNCTION,
                               pre_code="\n\n    ",
                               children=[
                                   CodeBlock(
                                       content="{",
                                       type=CodeBlockType.BLOCK_DELIMITER,
                                       pre_code=""),
                                   CodeBlock(
                                       content="myVariable = parameter;",
                                       type=CodeBlockType.CODE,
                                       pre_code="\n        "),
                                   CodeBlock(
                                       content="}",
                                       pre_code="\n    ",
                                       type=CodeBlockType.BLOCK_DELIMITER)])])

    assert code.find_nested_matching_block(find_block) == code.children[0].children[2]

def test_trim():
    with open("python/sales_queries_test.py", "r") as f:
        content = f.read()

    code_blocks = parser.parse(content)
    assert code_blocks.to_string() == content

    keep_blocks = [
        CodeBlock(content="setUp(", type=CodeBlockType.FUNCTION),
        CodeBlock(content="test_add_customer(", type=CodeBlockType.FUNCTION),
        CodeBlock(content="test_update_purchase_invalid_amount(", type=CodeBlockType.FUNCTION)
    ]

    trimmed_block = code_blocks.trim(keep_blocks=keep_blocks, keep_level=1, comment_out_str=" ... rest of the code ... ")

    assert trimmed_block.to_string() == """import unittest
import time
from sales_queries import CustomerDatabase

class TestCustomerDatabase(unittest.TestCase):
    def setUp(self):
        self.db = CustomerDatabase()

    def test_add_customer(self):
        self.db.add_customer(1, 'John Doe', 1000.0)
        self.assertEqual(self.db.customers[1].name, 'John Doe')
        self.assertEqual(self.db.customers[1].total_purchases, 1000.0)

    #  ... rest of the code ... 

    def test_update_purchase_invalid_amount(self):
        self.db.add_customer(1, 'John Doe', 1000.0)
        with self.assertRaises(ValueError):
            self.db.update_purchase(1, 1000001.0)

    #  ... rest of the code ... 

if __name__ == '__main__':
    #  ... rest of the code ... """