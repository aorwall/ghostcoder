from typing import List, Optional, Tuple

from tree_sitter import Node

from ghostcoder.codeblocks.codeblocks import CodeBlockType, CodeBlock
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

    def __init__(self, **kwargs):
        super().__init__("python", **kwargs)

        query_contents = self._read_query("python.scm")
        query_list = query_contents.strip().split("\n\n")
        self.queries = [self.tree_language.query(q) for q in query_list]

        if self.apply_gpt_tweaks:
            self.gpt_queries = self._build_queries(self._read_query("python_gpt.scm"))

    def get_block_definition(self, node: Node, content_bytes: bytes, start_byte: int = 0) -> Tuple[Optional[CodeBlock], Optional[Node], Optional[Node]]:
        if node.type == "ERROR" or any(child.type == "ERROR" for child in node.children):
            block_type = CodeBlockType.ERROR
            first_child, identifier_node, last_child = None, None, None
            self.debug_log(f"Found error node {node.type}")
        else:
            block_type, first_child, identifier_node, last_child = self.find_in_tree(node)
            if block_type:
                self.debug_log(f"Found match on node type {node.type} with block type {block_type}")
            else:
                self.debug_log(f"Found no match on node type {node.type} set block type {CodeBlockType.CODE}")
                block_type = CodeBlockType.CODE

        pre_code = content_bytes[start_byte:node.start_byte].decode(self.encoding)
        end_line = node.end_point[0]

        if first_child:
            end_byte = self.get_previous(first_child, node)
        else:
            end_byte = node.end_byte

        code = content_bytes[node.start_byte:end_byte].decode(self.encoding)

        if identifier_node:
            identifier = content_bytes[identifier_node.start_byte:identifier_node.end_byte].decode(self.encoding)
        else:
            identifier = None

        if self.apply_gpt_tweaks:
            # Fix function with commented out content
            if (node.type == "function_definition"
                    and block_type != CodeBlockType.FUNCTION
                    and node.next_sibling and node.next_sibling.type == "comment"
                    and self.is_outcommented_code(node.next_sibling.text.decode("utf8"))):
                self.debug_log(f"Ignore function with commented out content: {node.text}")

                block_type = CodeBlockType.COMMENTED_OUT_CODE
                first_child = node.next_sibling
                last_child = node.next_sibling

        if block_type == CodeBlockType.COMMENT and self.is_outcommented_code(node.text.decode("utf8")):
            block_type = CodeBlockType.COMMENTED_OUT_CODE

        code_block = CodeBlock(
                type=block_type,
                identifier=identifier,
                tree_sitter_type=node.type,
                start_line=node.start_point[0],
                end_line=end_line,
                pre_code=pre_code,
                content=code,
                language=self.language,
                children=[]
            )

        return code_block, first_child, last_child

    def is_outcommented_code(self, comment):
        return comment.startswith("# ...") or any(keyword in comment.lower() for keyword in commented_out_keywords)
