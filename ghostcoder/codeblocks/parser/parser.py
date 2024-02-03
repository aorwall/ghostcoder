import logging
import re
from dataclasses import dataclass, field
from importlib import resources
from typing import List, Tuple, Optional

import tree_sitter_languages
from pydantic import BaseModel, ConfigDict
from tree_sitter import Node

from ghostcoder.codeblocks.codeblocks import CodeBlock, CodeBlockType, Relationship, ReferenceScope, Parameter, \
    RelationshipType
from ghostcoder.codeblocks.parser.comment import get_comment_symbol

commented_out_keywords = ["rest of the code", "existing code", "other code"]
child_block_types = ["ERROR", "block"]
module_types = ["program", "module"]

logger = logging.getLogger(__name__)

@dataclass
class NodeMatch:
    block_type: CodeBlockType = None
    identifier_node: Node = None
    first_child: Node = None
    last_child: Node = None
    parameters: List[Tuple[Node, Optional[Node]]] = field(default_factory=list)
    references: List[Tuple[Node, str]] = field(default_factory=list)
    query: str = None


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


def find_nested_type(node: Node, type: str, levels: int = -1):
    if levels == 0:
        return None
    if node.type == type:
        return node
    for child in node.children:
        found_node = find_nested_type(child, type, levels-1)
        if found_node:
            return found_node
    return None


class CodeParser:

    def __init__(self, language: str, encoding: str = "utf8", apply_gpt_tweaks: bool = False, debug: bool = False):
        try:
            self.tree_parser = tree_sitter_languages.get_parser(language)
            self.tree_language = tree_sitter_languages.get_language(language)
        except Exception as e:
            print(f"Could not get parser for language {language}.")
            raise e
        self.apply_gpt_tweaks = apply_gpt_tweaks
        self.debug = debug
        self.encoding = encoding
        self.language = language
        self.gpt_queries = []
        self.queries = []
        self.reference_index = {}

    def _extract_node_type(self, query: str):
        pattern = r'\(\s*(\w+)'
        match = re.search(pattern, query)
        if match:
            return match.group(1)
        else:
            return None

    def _build_queries(self, query_file: str):
        with resources.open_text("ghostcoder.codeblocks.parser.queries", query_file) as file:
            query_list = file.read().strip().split("\n\n")
            parsed_queries = []
            for i, query in enumerate(query_list):
                try:
                    node_type = self._extract_node_type(query)
                    parsed_queries.append((f"{query_file}:{i+1}", node_type, self.tree_language.query(query)))
                except Exception as e:
                    logging.error(f"Could not parse query {query}:{i+1}")
                    raise e
            return parsed_queries



    def parse_code(self, content_bytes: bytes, node: Node, start_byte: int = 0, level: int = 0) -> Tuple[CodeBlock, Node]:
        if node.type == "ERROR" or any(child.type == "ERROR" for child in node.children):
            node_match = NodeMatch(block_type=CodeBlockType.ERROR)
            self.debug_log(f"Found error node {node.type}")
        else:
            node_match = self.find_in_tree(node)

        node_match = self.process_match(node_match, node, content_bytes)

        pre_code = content_bytes[start_byte:node.start_byte].decode(self.encoding)
        end_line = node.end_point[0]

        if node_match.first_child:
            end_byte = self.get_previous(node_match.first_child, node)
        else:
            end_byte = node.end_byte

        code = content_bytes[node.start_byte:end_byte].decode(self.encoding)

        if node_match.identifier_node:
            identifier = content_bytes[node_match.identifier_node.start_byte:
                                       node_match.identifier_node.end_byte].decode(self.encoding)
        else:
            identifier = None

        self.process_match(node_match, node, content_bytes)

        references = self.create_references(code, content_bytes, identifier, node_match)
        parameters = self.create_parameters(content_bytes, node_match, references)

        code_block = CodeBlock(
            type=node_match.block_type,
            identifier=identifier,
            parameters=parameters,
            references=references,
            start_line=node.start_point[0],
            end_line=end_line,
            pre_code=pre_code,
            content=code,
            language=self.language,
            children=[],
            properties={
                "query": node_match.query,
                "tree_sitter_type": node.type,
            }
        )

        self.pre_process(code_block)

        # Workaround to get the module root object when we get invalid content from GPT
        wrong_level_mode = self.apply_gpt_tweaks and level == 0 and not node.parent and code_block.type != CodeBlockType.MODULE
        if wrong_level_mode:
            self.debug_log(f"wrong_level_mode: block_type: {code_block.type}")

            code_block = CodeBlock(
                type=CodeBlockType.MODULE,
                identifier=None,
                properties={
                    "query": "wrong_level_mode",
                    "tree_sitter_type": node.type,
                },
                start_line=node.start_point[0],
                end_line=end_line,
                content="",
                language=self.language
            )
            end_byte = start_byte
            next_node = node
        else:
            next_node = node_match.first_child

        self.debug_log(f"""block_type: {code_block.type} 
    node_type: {node.type}
    next_node: {next_node.type if next_node else "none"}
    wrong_level_mode: {wrong_level_mode}
    first_child: {node_match.first_child}
    last_child: {node_match.last_child}
    start_byte: {start_byte}
    node.start_byte: {node.start_byte}
    node.end_byte: {node.end_byte}""")

        #l = last_child.type if last_child else "none"
        #print(f"start [{level}]: {code_block.content} (last child {l}, end byte {end_byte})")

        while next_node:
            #if next_node.children and next_node.type == "block":  # TODO: This should be handled in get_block_definition
            #    next_node = next_node.children[0]

            self.debug_log(f"next  [{level}]: -> {next_node.type} - {next_node.start_byte}")

            child_block, child_last_node = self.parse_code(content_bytes, next_node, start_byte=end_byte, level=level+1)
            if not child_block.content:
                if child_block.children:
                    child_block.children[0].pre_code = child_block.pre_code + child_block.children[0].pre_code
                    code_block.append_children(child_block.children)
            else:
                code_block.append_child(child_block)

            if child_last_node:
                self.debug_log(f"next  [{level}]: child_last_node -> {child_last_node}")
                next_node = child_last_node

            end_byte = next_node.end_byte

            self.debug_log(f"""next  [{level}]
    wrong_level_mode -> {wrong_level_mode}
    last_child -> {node_match.last_child}
    next_node -> {next_node}
    next_node.next_sibling -> {next_node.next_sibling}
    end_byte -> {end_byte}
""")
            if not wrong_level_mode and next_node == node_match.last_child:
                break
            elif next_node.next_sibling:
                next_node = next_node.next_sibling
            else:
                next_node = self.get_parent_next(next_node, node)

        self.debug_log(f"end   [{level}]: {code_block.content}")

        self.post_process(code_block)

        self.add_to_reference_index(code_block)

        if level == 0 and not node.parent and node.end_byte > end_byte:
            code_block.append_child(CodeBlock(
                type=CodeBlockType.SPACE,
                identifier=None,
                pre_code=content_bytes[end_byte:node.end_byte].decode(self.encoding),
                start_line=end_line,
                end_line=node.end_point[0],
                content="",
            ))

        return code_block, next_node

    def is_commented_out_code(self, node: Node):
        comment = node.text.decode("utf8").strip()
        return (comment.startswith(f"{get_comment_symbol(self.language)} ...") or
                any(keyword in comment.lower() for keyword in commented_out_keywords))

    def find_in_tree(self, node: Node) -> Optional[NodeMatch]:
        if self.apply_gpt_tweaks:
            match = self.find_match(node, True)
            if match:
                self.debug_log(f"GPT match: {match.block_type} on {node}")
                return match

        match = self.find_match(node)
        if match:
            self.debug_log(f"Found match on node type {node.type} with block type {match.block_type}")
            return match
        else:
            self.debug_log(f"Found no match on node type {node.type} set block type {CodeBlockType.CODE}")
            return NodeMatch(block_type=CodeBlockType.CODE)

    def find_match(self, node: Node, gpt_tweaks: bool = False) -> Optional[NodeMatch]:
        queries = gpt_tweaks and self.gpt_queries or self.queries
        for label, node_type, query in queries:
            if node_type and node.type != node_type:
                continue
            match = self._find_match(node, query, label)
            if match:
                if not match.query:
                    match.query = label
                return match

        return None

    def _find_match(self, node: Node, query, label: str) -> Optional[NodeMatch]:
        captures = query.captures(node)

        node_match = NodeMatch()

        if not captures:
            return None

        root_node = None

        for found_node, tag in captures:
            self.debug_log(f"[{label}] Found tag {tag} on node {found_node}")

            if tag == "root" and node != found_node:
                self.debug_log(f"[{label}] Expect first hit to be root match for {node}, got {tag} on {found_node}")
                break

            if tag == "root" and not root_node:
                self.debug_log(f"[{label}] Root node {found_node}")
                root_node = found_node

            if tag == "check_child":
                return self.find_match(found_node)

            if tag == "parse_child":
                child_match = self.find_match(found_node)
                if child_match:
                    if child_match.references:
                        self.debug_log(f"[{label}] Found {len(child_match.references)} references on child {found_node}")
                        node_match.references = child_match.references
                    if child_match.parameters:
                        self.debug_log(f"[{label}] Found {len(child_match.parameters)} parameters on child {found_node}")
                        node_match.parameters.extend(child_match.parameters)
                    if child_match.first_child:
                        node_match.first_child = child_match.first_child

            if tag == "identifier":
                node_match.identifier_node = found_node

            if tag == "child.first":
                node_match.first_child = found_node

            if tag == "child.last":
                node_match.last_child = found_node

            if tag == "parameter.identifier":
                node_match.parameters.append((found_node, None))

            if tag == "parameter.type":
                node_match.parameters[-1] = (node_match.parameters[-1][0], found_node)

            if root_node and tag.startswith("reference"):
                node_match.references.append((found_node, tag))

            if not node_match.block_type:
                node_match.block_type = CodeBlockType.from_string(tag)

        if node_match.block_type:
            self.debug_log(f"[{label}] Return match with type {node_match.block_type} for node {node}")
            return node_match

        return None

    def create_references(self, code, content_bytes, identifier, node_match):
        references = []
        if node_match.block_type == CodeBlockType.IMPORT and node_match.references:
            module_nodes = [ref for ref in node_match.references if ref[1] == "reference.module"]
            if module_nodes:
                module_reference_id = self.get_content(module_nodes[0][0], content_bytes)
                if len(node_match.references) > 1:
                    for ref_node in node_match.references:
                        if ref_node == module_nodes[0]:
                            continue
                        elif ref_node[1] == "reference.alias":
                            reference_id = self.get_content(ref_node[0], content_bytes)
                            references.append(
                                Relationship(scope=ReferenceScope.EXTERNAL,
                                             type=RelationshipType.IMPORTS,
                                             identifier=reference_id,
                                             path=[],
                                             external_path=[module_reference_id]))
                        else:
                            reference_id = self.get_content(ref_node[0], content_bytes)
                            references.append(
                                Relationship(scope=ReferenceScope.EXTERNAL,
                                             type=RelationshipType.IMPORTS,
                                             identifier=reference_id,
                                             path=[reference_id],
                                             external_path=[module_reference_id]))
                else:
                    references.append(
                        Relationship(scope=ReferenceScope.EXTERNAL,
                                     type=RelationshipType.IMPORTS,
                                     identifier=module_reference_id,
                                     external_path=[module_reference_id]))
        else:
            for reference in node_match.references:
                reference_id = self.get_content(reference[0], content_bytes)

                reference_id_path = reference_id.split(".")

                if not reference_id_path:
                    logger.warning(
                        f"Empty reference_id_path ({reference_id_path}) for code `{code}` in reference node {reference} with value {reference_id}")
                    continue

                if reference[1] == "reference.utilizes":
                    if node_match.block_type in [CodeBlockType.FUNCTION, CodeBlockType.CLASS]:
                        relationship_type = RelationshipType.DEFINED_BY
                    else:
                        relationship_type = RelationshipType.UTILIZES
                elif reference[1] == "reference.provides":
                    relationship_type = RelationshipType.PROVIDES
                elif reference[1] == "reference.calls":
                    relationship_type = RelationshipType.CALLS
                elif reference[1] == "reference.type":
                    relationship_type = RelationshipType.IS_A
                else:
                    relationship_type = RelationshipType.USES

                references.append(
                    Relationship(scope=ReferenceScope.LOCAL,
                                 type=relationship_type,
                                 identifier=identifier,
                                 path=reference_id_path))
        return references

    def create_parameters(self, content_bytes, node_match, references):
        parameters = []
        for parameter in node_match.parameters:
            parameter_type = self.get_content(parameter[1], content_bytes) if parameter[1] else None
            parameter_id = self.get_content(parameter[0], content_bytes)

            parameters.append(
                Parameter(identifier=parameter_id,
                          type=parameter_type))

            if parameter_type:
                parameter_type = parameter_type.replace("\"", "")

                type_split = parameter_type.split(".")

                reference = Relationship(scope=ReferenceScope.LOCAL, identifier=parameter_id, path=type_split)
                references.append(reference)
        return parameters

    def process_match(self, node_match: NodeMatch, node: Node, content_bytes: bytes):
        return node_match

    def add_to_reference_index(self, codeblock: CodeBlock):
        for reference in codeblock.references:
            if reference.identifier:
                if reference.path and reference.path[0] in self.reference_index:
                    self.reference_index[reference.identifier] = self.reference_index[reference.path[0]]
                else:
                    self.reference_index[reference.identifier] = reference

    def pre_process(self, codeblock: CodeBlock):
        pass

    def post_process(self, codeblock: CodeBlock):
        pass

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
        self.debug_log(f"get_parent_next: {node.type} - {orig_node.type}")
        if node != orig_node:
            if node.next_sibling:
                self.debug_log(f"get_parent_next: node.next_sibling -> {node.next_sibling}")
                return node.next_sibling
            else:
                return self.get_parent_next(node.parent, orig_node)
        return None

    def has_error(self, node: Node):
        if node.type == "ERROR":
            return True
        if node.children:
            return any(self.has_error(child) for child in node.children)
        return False

    def parse(self, content) -> CodeBlock:
        if isinstance(content, str):
            content_in_bytes = bytes(content, self.encoding)
        elif isinstance(content, bytes):
            content_in_bytes = content
        else:
            raise ValueError("Content must be either a string or bytes")

        tree = self.tree_parser.parse(content_in_bytes)
        codeblock, _ = self.parse_code(content_in_bytes, tree.walk().node)
        codeblock.language = self.language
        return codeblock

    def get_content(self, node: Node, content_bytes: bytes) -> str:
        return content_bytes[node.start_byte:node.end_byte].decode(self.encoding)

    def debug_log(self, message: str):
        if self.debug:
            logger.debug(message)
