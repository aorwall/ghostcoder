from typing import Optional, Tuple

from tree_sitter import Node

from ghostcoder.codeblocks.codeblocks import CodeBlockType, CodeBlock
from ghostcoder.codeblocks.parser.parser import CodeParser, find_type, find_nested_type

class_node_types = [
    "annotation_type_declaration",
    "class_declaration",
    "enum_declaration",
    "interface_declaration",
    "record_declaration"
]

function_node_types = [
    "method_declaration",
    "constructor_declaration",
    "compact_constructor_declaration"
]

statement_node_types = [
    "static_initializer",
    "instance_initializer",
    "if_statement",
    "for_statement",
    "enhanced_for_statement",
    "while_statement",
    "do_statement",
    "synchronized_statement",
    "try_statement",
    "try_with_resources_statement",
    "switch_expression"
]

block_delimiters = [
    "{",
    "}"
]


class JavaParser(CodeParser):

    def __init__(self, **kwargs):
        super().__init__("java", **kwargs)

        query_contents = self._read_query("java.scm")
        query_list = query_contents.strip().split("\n\n")
        self.queries = [self.tree_language.query(q) for q in query_list]

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

    def get_block_definition_old(self, node: Node) -> Tuple[CodeBlockType, Optional[Node], Optional[Node]]:
        if node.type == "program":
            # TODO: module_declaration?
            package_declaration = find_type(node, ["package_declaration"])
            if package_declaration:
                return CodeBlockType.MODULE, package_declaration.next_sibling, None
            return CodeBlockType.MODULE, node.children[0], node.children[-1]

        if node.type in function_node_types:
            block_delimiter = find_nested_type(node, "{")
            return CodeBlockType.FUNCTION, block_delimiter, node.children[-1]

        if node.type in class_node_types:
            block_delimiter = find_nested_type(node, "{")
            return CodeBlockType.CLASS, block_delimiter, node.children[-1]

        if node.type in statement_node_types:
            block_delimiter = find_nested_type(node, "{")
            return CodeBlockType.STATEMENT, block_delimiter, node.children[-1]

        if node.type in block_delimiters:
            return CodeBlockType.BLOCK_DELIMITER, None, None

        if node.type == "import_declaration":
            return CodeBlockType.IMPORT, None, None # TODO: Separate def import and parameter

        if "comment" in node.type:
            if "..." in node.text.decode("utf8"):
                return CodeBlockType.COMMENTED_OUT_CODE, None, None
            else:
                return CodeBlockType.COMMENT, None, None

        if node.type in ["local_variable_declaration", "variable_declarator"]:
            identifier = find_nested_type(node, "identifier")
            return CodeBlockType.CODE, identifier.next_sibling, node.children[-1]

        if node.type == "expression_statement":
            return CodeBlockType.CODE, find_nested_type(node, "="), node.children[-1]

        if node.type == "switch_rule":
            delimiter = find_type(node, ["->"])
            return CodeBlockType.CODE, delimiter, node.children[-1]

        if node.type == "block":
            block = node
        else:
            block = find_type(node, ["block"])
        if block:
            return CodeBlockType.CODE, block.children[0], node.children[-1]

        if node.type == "ERROR":
            return CodeBlockType.ERROR, None, None

        return CodeBlockType.CODE, None, None
