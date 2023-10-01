from typing import List, Tuple

import tree_sitter_languages
from tree_sitter import Node

from ghostcoder.codeblocks.codeblocks import CodeBlock, CodeBlockType
from ghostcoder.codeblocks.parser.comment import get_comment_symbol

commented_out_keywords = ["rest of the code", "existing code", "other code"]
child_block_types = ["ERROR", "block"]
module_types = ["program", "module"]


def _find_type(node: Node, type: str):
    for i, child in enumerate(node.children):
        if child.type == type:
            return i, child
    return None, None


def find_type(node: Node, types: List[str]):
    for child in node.children:
        if child.type in types:
            return child
    return None


def find_nested_type(node: Node, type: str):
    if node.type == type:
        return node
    for child in node.children:
        found_node = find_nested_type(child, type)
        if found_node:
            return found_node
    return None


class CodeParser:

    def __init__(self, language: str, encoding: str = "utf8"):
        try:
            self.tree_parser = tree_sitter_languages.get_parser(language)
        except Exception as e:
            print(f"Could not get parser for language {language}.")
            raise e
        self.encoding = encoding
        self.language = language

    def is_commented_out_code(self, node: Node):
        comment = node.text.decode("utf8").strip()
        return (comment.startswith(f"{get_comment_symbol(self.language)} ...") or
                any(keyword in comment.lower() for keyword in commented_out_keywords))

    def get_block_definition(self, node: Node):
        if node.children:
            return CodeBlockType.CODE, node.children[0]
        return None, None

    def parse_code(self, content_bytes: bytes, node: Node, start_byte: int = 0) -> Tuple[CodeBlock, Node]:
        pre_code = content_bytes[start_byte:node.start_byte].decode(self.encoding)
        block_type, first_child, last_child = self.get_block_definition(node)

        children = []

        if first_child:
            end_byte = self.get_previous(first_child, node)
        else:
            end_byte = node.end_byte

        end_line = node.end_point[0]

        code = content_bytes[node.start_byte:end_byte].decode(self.encoding)
        next_node = first_child
        while next_node:
            child_block, child_last_node = self.parse_code(content_bytes, next_node, start_byte=end_byte)
            if not child_block.content:
                if child_block.children:
                    child_block.children[0].pre_code = child_block.pre_code + child_block.children[0].pre_code
                    child_block.children[0].__post_init__()  # FIXME
                    children.extend(child_block.children)
            else:
                children.append(child_block)

            if child_last_node:
                next_node = child_last_node

            end_byte = next_node.end_byte

            if next_node == last_child:
                break

            if next_node.next_sibling:
                next_node = next_node.next_sibling
            else:
                next_node = self.get_parent_next(next_node, node)

        if not node.parent and node.end_byte > end_byte:
            children.append(CodeBlock(
                type=CodeBlockType.SPACE,
                pre_code=content_bytes[end_byte:node.end_byte].decode(self.encoding),
                start_line=end_line,
                end_line=node.end_point[0],
                content="",
            ))

        return CodeBlock(
            type=block_type,
            tree_sitter_type=node.type,
            start_line=node.start_point[0],
            end_line=end_line,
            pre_code=pre_code,
            content=code,
            children=children,
            language=self.language
        ), next_node

    def get_previous(self, node: Node, origin_node: Node):
        if node == origin_node:
            return node.start_byte
        if node.prev_sibling:
            return node.prev_sibling.end_byte
        elif node.parent:
            return self.get_previous(node.parent, origin_node)
        else:
            return node.start_byte

    def get_parent_next(self, node: Node, orig_node: Node):
        if node != orig_node:
            if node.next_sibling:
                return node.next_sibling
            else:
                return self.get_parent_next(node.parent, orig_node)
        return None

    def parse(self, content: str) -> CodeBlock:
        tree = self.tree_parser.parse(bytes(content, self.encoding))
        codeblock, _ = self.parse_code(content.encode(self.encoding), tree.walk().node)
        codeblock.language = self.language
        return codeblock
