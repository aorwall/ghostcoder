from typing import Optional, Tuple

from tree_sitter import Node

from ghostcoder.codeblocks.codeblocks import CodeBlockType
from ghostcoder.codeblocks.parser.parser import CodeParser, commented_out_keywords, find_type

statement_node_types = [
    "if_statement", "for_statement", "while_statement", "try_statement", "with_statement",
    "expression_statement", "elif_clause", "else_clause", "except_clause", "finally_clause"
]

child_block_types = ["ERROR", "block"]

block_delimiters = [
    ":"
]


class PythonParser(CodeParser):

    def __init__(self):
        super().__init__("python")

    def get_first_child(self, node: Node):
        if node.children:
            return node.children[0]
        return None

    def get_last_child(self, node: Node):
        if node.children:
            return node.children[-1]
        return None

    def find_block_child(self, node: Node) -> Tuple[Optional[Node], Optional[Node]]:
        delimiter = find_type(node, [":"])
        if not delimiter:
            return self.get_first_child(node), self.get_last_child(node)
        if delimiter.next_sibling.type == "block":
            if delimiter.next_sibling.children:
                return delimiter.next_sibling.children[0], delimiter.next_sibling.children[-1]

            # Set indented lines as children, see test case test_python_function_with_only_comment
            next_sibling = node.next_sibling
            while next_sibling and node.next_sibling.start_point[1] > node.start_point[0]:
                if next_sibling.start_point[1] == node.start_point[0]:
                    return node.next_sibling, next_sibling
                next_sibling = next_sibling.next_sibling

            return self.get_first_child(delimiter.next_sibling), self.get_last_child(node)
        else:
            return delimiter.next_sibling, self.get_last_child(node)

    def get_block_definition(self, node: Node) -> Tuple[CodeBlockType, Optional[Node], Optional[Node]]:
        if node.type == "ERROR" or any(child.type == "ERROR" for child in node.children):
            return CodeBlockType.ERROR, None, None

        if node.type == "decorated_definition" and len(node.children) > 1:
            node = node.children[-1]

        if node.type == "block" and node.children:
            node = node.children[0]

        if node.type == "module":
            return CodeBlockType.MODULE, self.get_first_child(node), self.get_last_child(node)

        if node.type == "function_definition":
            first, last = self.find_block_child(node)
            return CodeBlockType.FUNCTION, first, last

        if node.type == "class_definition":
            first, last = self.find_block_child(node)
            return CodeBlockType.CLASS, first, last

        if node.type in ["import_statement", "future_import_statement"]:
            return CodeBlockType.IMPORT, None, None

        if node.type == "import_from_statement":
            return CodeBlockType.IMPORT, find_type(node, ["import"]), self.get_last_child(node)

        if node.type in block_delimiters:
            return CodeBlockType.BLOCK_DELIMITER, None, None

        if "comment" in node.type:
            comment = node.text.decode("utf8").strip()
            if comment.startswith("# ...") or any(keyword in comment.lower() for keyword in commented_out_keywords):
                return CodeBlockType.COMMENTED_OUT_CODE, None, None
            else:
                return CodeBlockType.COMMENT, None, None

        if node.type in statement_node_types:
            first, last = self.find_block_child(node)
            return CodeBlockType.STATEMENT, first, last

        if node.type in ["return_statement"]:
            if len(node.children) > 1:
                return CodeBlockType.CODE, node.children[1], node.children[-1]
            else:
                return CodeBlockType.CODE, None, None

        if node.type == "assignment":
            return CodeBlockType.CODE, find_type(node, ["="]), self.get_last_child(node)

        if node.type == "pair":
            return CodeBlockType.CODE, find_type(node, [":"]), self.get_last_child(node)

        if node.type == "dictionary":
            return CodeBlockType.CODE, find_type(node, ["{"]), self.get_last_child(node)

        return CodeBlockType.CODE, None, None
