import json
import logging
from typing import Optional, Tuple

from tree_sitter import Node

from ghostcoder.codeblocks.codeblocks import CodeBlockType, CodeBlock, Relationship, ReferenceScope, RelationshipType
from ghostcoder.codeblocks.parser.parser import CodeParser, NodeMatch

block_delimiters = [
    "{",
    "}",
    ";",
    "(",
    ")"
]

logger = logging.getLogger(__name__)

class JavaScriptParser(CodeParser):

    def __init__(self, language: str = "javascript", **kwargs):
        super().__init__(language, **kwargs)

        self.queries = []

        if language in ["tsx", "typescript"]:
            self.queries.extend(self._build_queries("typescript.scm"))
        else:
            self.queries.extend(self._build_queries("javascript_only.scm"))

        self.queries.extend(self._build_queries("javascript.scm"))

        if self.apply_gpt_tweaks:
            self.queries.extend(self._build_queries("javascript_gpt.scm"))

    def process_match(self, node_match: NodeMatch, node: Node, content_bytes: bytes):
        if node.type in block_delimiters:  # TODO: Move to query
            node_match = NodeMatch(block_type=CodeBlockType.BLOCK_DELIMITER)

        return node_match

    def pre_process(self, codeblock: CodeBlock):
        if codeblock.type == CodeBlockType.FUNCTION and codeblock.identifier == "constructor":
            codeblock.type = CodeBlockType.CONSTRUCTOR

        if codeblock.type == CodeBlockType.COMMENT and "..." in codeblock.content:
            codeblock.type = CodeBlockType.COMMENTED_OUT_CODE

        # Expect class on components with an identifier starting with upper case
        if codeblock.type == CodeBlockType.FUNCTION and codeblock.identifier and codeblock.identifier[0].isupper():
            codeblock.type = CodeBlockType.CLASS

        # Handle JSX closing elements as block delimiters
        if codeblock.content in ["/", ">"]:
            codeblock.type = CodeBlockType.BLOCK_DELIMITER

    def post_process(self, codeblock: CodeBlock):
        new_references = []
        for reference in codeblock.references:
            if reference.path and reference.path[0] == "this":
                reference.scope = ReferenceScope.CLASS
                if len(reference.path) > 1:
                    reference.path = reference.path[1:]
                    reference.identifier = codeblock.identifier
            elif codeblock.identifier and codeblock.identifier.startswith("this"):
                reference.scope = ReferenceScope.CLASS
                reference.identifier = codeblock.identifier[5:]

            # Add a new relationship to the external module and point the existing to existing one.
            if (reference.path
                    and reference.path[0] in self.reference_index
                    and reference.scope in [ReferenceScope.CLASS, ReferenceScope.LOCAL]):
                existing_reference = self.reference_index[reference.path[0]]

                new_full_reference = Relationship(
                    scope=existing_reference.scope,
                    type=reference.type,
                    identifier=reference.identifier,
                    path=existing_reference.path + reference.path[1:],
                    external_path=existing_reference.external_path
                )

                new_references.append(new_full_reference)

                reference.type = RelationshipType.USES

                if len(reference.path) > 1:
                    reference.path = reference.path[:1]

        codeblock.references.extend(new_references)