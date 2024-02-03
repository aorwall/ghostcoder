import logging
import os
from typing import List, Optional, Tuple

from tree_sitter import Node

from ghostcoder.codeblocks.codeblocks import CodeBlockType, CodeBlock, Relationship, Parameter, ReferenceScope, \
    RelationshipType
from ghostcoder.codeblocks.parser.parser import CodeParser, commented_out_keywords, find_type, NodeMatch

child_block_types = ["ERROR", "block"]

block_delimiters = [
    ":"
]

logger = logging.getLogger(__name__)


class PythonParser(CodeParser):

    def __init__(self, **kwargs):
        super().__init__("python", **kwargs)

        self.queries = []
        self.queries.extend(self._build_queries("python.scm"))

        if self.apply_gpt_tweaks:
            self.queries.extend(self._build_queries("python_gpt.scm"))

    def process_match(self, node_match: NodeMatch, node: Node, content_bytes: bytes):
        if self.apply_gpt_tweaks:
            # Fix function with commented out content
            if (node.type == "function_definition"
                    and node_match.block_type != CodeBlockType.FUNCTION
                    and node.next_sibling and node.next_sibling.type == "comment"
                    and self.is_outcommented_code(node.next_sibling.text.decode("utf8"))):
                self.debug_log(f"Ignore function with commented out content: {node.text}")

                node_match.block_type = CodeBlockType.COMMENTED_OUT_CODE
                node_match.first_child = node.next_sibling
                node_match.last_child = node.next_sibling

        if node_match.block_type == CodeBlockType.COMMENT and self.is_outcommented_code(node.text.decode("utf8")):
            node_match.block_type = CodeBlockType.COMMENTED_OUT_CODE

        return node_match

    def pre_process(self, codeblock: CodeBlock):
        if codeblock.type == CodeBlockType.FUNCTION and codeblock.identifier == "__init__":
            codeblock.type = CodeBlockType.CONSTRUCTOR

    def post_process(self, codeblock: CodeBlock):
        if codeblock.type == CodeBlockType.ASSIGNMENT:
            for reference in codeblock.references:
                reference.type = RelationshipType.TYPE

        new_references = []
        for reference in codeblock.references:
            if reference.path and reference.path[0] == "self":
                reference.scope = ReferenceScope.CLASS
                if len(reference.path) > 1:
                    reference.path = reference.path[1:]
                    reference.identifier = codeblock.identifier
            elif codeblock.identifier and codeblock.identifier.startswith("self"):
                reference.scope = ReferenceScope.CLASS
                reference.identifier = codeblock.identifier[5:]

            if (reference.path
                    and reference.path[0] in self.reference_index
                    and reference.scope in [ReferenceScope.CLASS, ReferenceScope.LOCAL]):
                existing_reference = self.reference_index[reference.path[0]]
                if len(reference.path) > 1 and codeblock.type == CodeBlockType.CALL:
                    # add new full reference to the called function
                    new_full_reference = Relationship(
                        scope=existing_reference.scope,
                        identifier=reference.identifier,
                        path=existing_reference.path + reference.path[1:],
                        external_path=existing_reference.external_path
                    )
                    new_references.append(new_full_reference)
                    reference.path = reference.path[:1]

        codeblock.references.extend(new_references)

        if codeblock.type == CodeBlockType.CLASS:
            # the class block should refer to instance variables initiated from the constructor
            constructor_blocks = [block for block in codeblock.children if block.type == CodeBlockType.CONSTRUCTOR]
            if constructor_blocks:
                init_block = constructor_blocks[0]
                for reference in init_block.get_all_references():
                    if reference.scope == ReferenceScope.CLASS:
                        codeblock.references.append(reference)

    def is_outcommented_code(self, comment):
        return comment.startswith("# ...") or any(keyword in comment.lower() for keyword in commented_out_keywords)
