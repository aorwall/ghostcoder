import copy
import logging
import re
from enum import Enum
from typing import List, Optional, Callable, Tuple

from pydantic import BaseModel, validator, Field, root_validator

from ghostcoder import utils
from ghostcoder.codeblocks.parser.comment import get_comment_symbol
from ghostcoder.utils import count_tokens, Colors


class CodeBlockType(str, Enum):
    DECLARATION = "Declaration"
    IDENTIFIER = "Identifier"
    PARAMETER = "Parameter"

    MODULE = "Module"
    CLASS = "Class"
    FUNCTION = "Function"
    CONSTRUCTOR = "Constructor"

    TEST_SUITE = "TestSuite"
    TEST_CASE = "TestCase"

    IMPORT = "Import"
    STATEMENT = "Statement"
    BLOCK = "Block"
    ASSIGNMENT = "Assignment"
    CALL = "Call"
    CODE = "Code"
    BLOCK_DELIMITER = "BlockDelimiter"

    COMMENT = "Comment"
    COMMENTED_OUT_CODE = "CommentedOutCode"

    SPACE = "Space"
    ERROR = "Error"

    @classmethod
    def from_string(cls, tag: str) -> Optional['CodeBlockType']:
        if not tag.startswith("definition"):
            return None

        tag_to_block_type = {
            "definition.assignment": cls.ASSIGNMENT,
            "definition.block": cls.BLOCK,
            "definition.block_delimiter": cls.BLOCK_DELIMITER,
            "definition.call": cls.CALL,
            "definition.class": cls.CLASS,
            "definition.code": cls.CODE,
            "definition.comment": cls.COMMENT,
            "definition.constructor": cls.CONSTRUCTOR,
            "definition.error": cls.ERROR,
            "definition.function": cls.FUNCTION,
            "definition.import": cls.IMPORT,
            "definition.module": cls.MODULE,
            "definition.statement": cls.STATEMENT,
            "definition.test_suite": cls.TEST_SUITE,
            "definition.test_case": cls.TEST_CASE,
        }
        return tag_to_block_type.get(tag)

NON_CODE_BLOCKS = [
    CodeBlockType.BLOCK_DELIMITER,
    CodeBlockType.COMMENT,
    CodeBlockType.COMMENTED_OUT_CODE,
    CodeBlockType.IMPORT,
    CodeBlockType.ERROR,
    CodeBlockType.SPACE
]

class ReferenceScope(str, Enum):
    EXTERNAL = "external"
    DEPENDENCY = "dependency"  # External dependency
    FILE = "file"  # File in repository
    PROJECT = "project"
    CLASS = "class"
    LOCAL = "local"
    GLOBAL = "global"


class RelationshipType(str, Enum):
    UTILIZES = "utilizes"
    USES = "uses"
    DEFINED_BY = "defined_by"
    IS_A = "is_a"
    PROVIDES = "provides"
    IMPORTS = "imports"
    CALLS = "calls"
    DEPENDENCY = "dependency"
    TYPE = "type"


class MergeAction(BaseModel):
    action: str
    original_block: Optional["CodeBlock"] = None
    updated_block: Optional["CodeBlock"] = None

    def __str__(self):
        original_id = self.original_block.identifier if self.original_block else 'None'
        updated_id = self.updated_block.identifier if self.updated_block else 'None'
        return f"{self.action}: {original_id or '[]'} -> {updated_id or '[]'}"


class Relationship(BaseModel):
    scope: ReferenceScope = Field(description="The scope of the reference.")
    identifier: Optional[str] = Field(default=None, description="ID")
    type: RelationshipType = Field(default=RelationshipType.USES, description="The type of the reference.")
    external_path: List[str] = Field(default=[], description="The path to the referenced parent code block.")
    resolved_path: List[str] = Field(default=[], description="The path to the file with the referenced code block.")
    path: List[str] = Field(default=[], description="The path to the referenced code block.")

    @root_validator(pre=True)
    def validate_path(cls, values):
        external_path = values.get("external_path")
        path = values.get("path")
        if not external_path and not path:
            raise ValueError("Cannot create Reference without external_path or path.")
        return values

    def __hash__(self):
        return hash((self.scope, tuple(self.path)))

    def __eq__(self, other):
        return (self.scope, self.path) == (other.scope, other.path)

    def full_path(self):
        return self.external_path + self.path

    def __str__(self):
        if self.identifier:
            start_node = self.identifier
        else:
            start_node = ""

        end_node = ""
        if self.external_path:
            end_node = "/".join(self.external_path)
        if self.path:
            if self.external_path:
                end_node += "/"
            end_node += ".".join(self.path)

        return f"({start_node})-[:{self.type.name} {{scope: {self.scope.value}}}]->({end_node})"


class Parameter(BaseModel):
    identifier: str = Field(description="The identifier of the parameter.")
    type: Optional[str] = Field(description="The type of the parameter.")


class Visibility(str, Enum):
    EVERYTHING = "everything"  # Show all blocks
    CODE = "code"  # Only show code but comment out function and class definitions
    NOTHING = "nothing"  # Comment out everything


class ShowBlock(BaseModel):
    visibility: Visibility = Field(default=Visibility.EVERYTHING, description="The visibility of the block.")
    tree: dict[str, "ShowBlock"] = Field(default={}, description="Child blocks")


class CodeBlock(BaseModel):
    content: str
    type: CodeBlockType
    file_path: str = None  # TODO: Move to Module sub class
    identifier: Optional[str] = None
    parameters: List[Parameter] = []  # TODO: Move to Function sub class
    references: List[Relationship] = []
    content_lines: List[str] = []
    start_line: int = 0
    end_line: int = 0
    properties: dict = {}
    pre_code: str = ""
    pre_lines: int = 0
    indentation: str = ""
    language: Optional[str] = None
    merge_history: List[MergeAction] = []
    children: List["CodeBlock"] = []
    parent: Optional["CodeBlock"] = None

    @validator('type', pre=True, always=True)
    def validate_type(cls, v):
        if v is None:
            raise ValueError("Cannot create CodeBlock without type.")
        return v

    def __init__(self, **data):
        super().__init__(**data)
        for child in self.children:
            child.parent = self

        if self.pre_code.strip():
            raise ValueError(f"Failed to parse code block with type {self.type} and content `{self.content}`. "
                             f"Expected pre_code to only contain spaces and line breaks. Got `{self.pre_code}`")

        if self.pre_code and not self.indentation and not self.pre_lines:
            pre_code_lines = self.pre_code.split("\n")
            self.pre_lines = len(pre_code_lines) - 1
            if self.pre_lines > 0:
                self.indentation = pre_code_lines[-1]
            else:
                self.indentation = self.pre_code

        self.content_lines = self.content.split("\n")
        if self.indentation and self.pre_lines:
            self.content_lines[1:] = [line[len(self.indentation):] for line in self.content_lines[1:]]

    def insert_child(self, index: int, child: "CodeBlock"):
        if index == 0 and self.children[0].pre_lines == 0:
            self.children[0].pre_lines = 1

        self.children.insert(index, child)
        child.parent = self

    def insert_children(self, index: int, children: List["CodeBlock"]):
        for child in children:
            self.insert_child(index, child)
            index += 1

    def append_child(self, child: "CodeBlock"):
        self.children.append(child)
        child.parent = self

    def append_children(self, children: List["CodeBlock"]):
        for child in children:
            self.append_child(child)

    def replace_child(self, index: int, child: "CodeBlock"):
        self.children[index] = child
        child.parent = self

    def replace_children(self, index: int, children: List["CodeBlock"]):
        for child in children:
            self.replace_child(index, child)
            index += 1

    def remove_child(self, index: int):
        del self.children[index]

    def has_equal_definition(self, other: "CodeBlock") -> bool:
        # TODO: should be replaced an expression that checks the actual identifier and parameters
        return other.content in self.content and other.type == self.type

    def __str__(self):
        return self.to_string()

    def to_string(self):
        return self._to_context_string()

    def _insert_into_tree(self, node, path):
        if not path:
            return
        if path[0] not in node:
            node[path[0]] = {}
        self._insert_into_tree(node[path[0]], path[1:])

    def _replace_in_tree(self, node, path):
        if not path:
            return
        if len(path) == 1:
            node[path[0]] = {}
            return
        if path[0] not in node:
            node[path[0]] = {}
        self._replace_in_tree(node[path[0]], path[1:])

    def build_reference_tree(self):
        tree = {}

        if self.type == CodeBlockType.MODULE:
            return tree

        if self.type == CodeBlockType.CLASS:
            references = [self._fix_reference_path(reference) for reference in self.get_all_references(exclude_types=[CodeBlockType.FUNCTION, CodeBlockType.TEST_CASE]) if
                          reference and reference.scope != ReferenceScope.EXTERNAL]  # FIXME skip _fix_reference_path?
        else:
            references = [self._fix_reference_path(reference) for reference in self.get_all_references() if
                          reference and reference.scope != ReferenceScope.EXTERNAL]  # FIXME skip _fix_reference_path?

        for ref in references:
            self._insert_into_tree(tree, ref.path)
        return tree

    def build_external_reference_tree(self):
        tree = {}

        references = [self._fix_reference_path(reference) for reference in self.get_all_references() if
                      reference is not None and reference.scope != ReferenceScope.EXTERNAL]
        for ref in references:
            external_path = tuple(ref.external_path)
            if external_path not in tree:
                tree[external_path] = {}

            self._insert_into_tree(tree[external_path], ref.path)
        return tree

    def _to_context_string(self,
                           path_tree: dict = None,
                           show_commented_out_code_comment: bool = True,
                           exclude_types: List[CodeBlockType] = None) -> str:
        if self.pre_lines:
            contents = "\n" * (self.pre_lines - 1)
            for line in self.content_lines:
                if line:
                    contents += "\n" + self.indentation + line
                else:
                    contents += "\n"
        else:
            contents = self.pre_code + self.content

        # assume invalid reference in path_tree if there are no child blocks with an identifier
        if path_tree and any(child.identifier for child in self.children):
            outcommented_types = set()
            for child in self.children:
                reference_match = any(ref.identifier in path_tree for ref in child.references)
                if reference_match or child.identifier in path_tree:
                    if show_commented_out_code_comment and outcommented_types:
                        # TODO: print by type
                        contents += child.create_commented_out_block()._to_context_string()
                        outcommented_types.clear()
                    contents += child._to_context_string(
                        path_tree=path_tree.get(child.identifier, None),
                        show_commented_out_code_comment=show_commented_out_code_comment,
                        exclude_types=exclude_types)
                else:
                    outcommented_types.add(child.type)

            if show_commented_out_code_comment and outcommented_types and child:
                # TODO: print by type
                contents += child.create_commented_out_block()._to_context_string()
        else:
            contents += "".join([
                child._to_context_string(
                    exclude_types=exclude_types,
                    show_commented_out_code_comment=show_commented_out_code_comment)
                for child in self.children
                if not exclude_types or child.type not in exclude_types])

        return contents

    # TODO: Move to Module sub class
    def to_string_with_blocks(self, block_paths: List[str], include_references: bool) -> str:
        path_tree = {}

        if self.parent:
            raise ValueError("Cannot call to_string_with_blocks on non root block.")

        for block_path in block_paths:
            if block_path:
                path = block_path.split(".")

                block = self.find_by_path(path)
                if block and include_references:
                    if self.type == CodeBlockType.CLASS:
                        references = [self._fix_reference_path(reference) for reference in self.get_all_references(
                            exclude_types=[CodeBlockType.FUNCTION, CodeBlockType.TEST_CASE]) if
                                      reference and reference.scope != ReferenceScope.EXTERNAL]  # FIXME skip _fix_reference_path?
                    else:
                        references = [self._fix_reference_path(reference) for reference in self.get_all_references() if
                                      reference and reference.scope != ReferenceScope.EXTERNAL]  # FIXME skip _fix_reference_path?

                    for ref in references:
                        self._insert_into_tree(path_tree, ref.path)

                self._replace_in_tree(path_tree, path)

        exclude_types = [CodeBlockType.FUNCTION, CodeBlockType.CLASS, CodeBlockType.TEST_SUITE, CodeBlockType.TEST_CASE]
        return self._to_context_string(path_tree, show_commented_out_code_comment=True, exclude_types=exclude_types)

    def to_context_string(self,
                          include_references: bool = False,
                          show_commented_out_code_comment: bool = True,
                          max_tokens: int = 0) -> str:
        path_tree = {}
        if include_references:
            path_tree = self.build_reference_tree()

        exclude_types = [CodeBlockType.FUNCTION, CodeBlockType.CLASS, CodeBlockType.TEST_SUITE, CodeBlockType.TEST_CASE]
        self._replace_in_tree(path_tree, self.full_path())
        content = self.root()._to_context_string(path_tree, show_commented_out_code_comment=show_commented_out_code_comment, exclude_types=exclude_types)

        if include_references and 0 < max_tokens < count_tokens(content):
            path_tree = {}
            self._replace_in_tree(path_tree, self.full_path())
            content = self.root()._to_context_string(path_tree, show_commented_out_code_comment=show_commented_out_code_comment, exclude_types=exclude_types)

        return content

    def to_tree(self,
                indent: int = 0,
                only_identifiers: bool = True,
                show_tokens: bool = False,
                debug: bool = False,
                include_types: List[CodeBlockType] = None,
                include_parameters: bool = False,
                include_block_delimiters: bool = False,
                include_references: bool = False,
                include_merge_history: bool = False,
                color: bool = False):

        if not include_merge_history and self.type == CodeBlockType.BLOCK_DELIMITER:
            return ""

        child_tree = "".join([
            child.to_tree(indent=indent + 1,
                          only_identifiers=only_identifiers,
                          debug=debug,
                          include_types=include_types,
                          include_merge_history=include_merge_history,
                          include_parameters=include_parameters,
                          include_references=include_references,
                          include_block_delimiters=include_block_delimiters,
                          show_tokens=show_tokens)
            for child in self.children if not include_types or child.type in include_types])
        indent_str = " " * indent

        extra = ""
        if show_tokens:
            tokens = utils.count_tokens(str(self))
            extra += f" ({tokens} tokens)"

        if include_references and self.references:
            extra += " references: " + ", ".join([str(ref) for ref in self.references])

        content = Colors.YELLOW + (self.content.strip().replace("\n", "\\n") or "") + Colors.RESET

        if only_identifiers and self.identifier:
            content = Colors.GREEN
            if include_parameters and self.parameters:
                content += f"{self.identifier}({', '.join([param.identifier for param in self.parameters])})"
            else:
                content += self.identifier

            content += Colors.RESET

        if debug and self.properties:
            extra += f" properties: {self.properties}"

        if include_merge_history and self.merge_history:
            extra += " merge_history: " + ", ".join([str(action) for action in self.merge_history])

        return f"{indent_str} {indent} {Colors.BLUE}{self.type.value}{Colors.RESET} `{content}`{extra}\n{child_tree}"

    def __eq__(self, other):
        if not isinstance(other, CodeBlock):
            return False
        return self.to_dict() == other.to_dict()

    def dict(self, **kwargs):
        # TODO: Add **kwargs to dict call
        return super().dict(exclude={"parent", "merge_history"})

    # TODO: Remove
    def to_dict(self):
        return {
            "code": self.content,
            "type": self.type,
            "tree_sitter_type": self.tree_sitter_type,
            "pre_code": self.pre_code,
            # "is_nested": self.is_nested,
            "children": [child.to_dict() for child in self.children]
        }

    def path_string(self):
        return ".".join(self.full_path())

    def full_path(self):
        path = []
        if self.parent:
            path.extend(self.parent.full_path())

        if self.identifier:
            path.append(re.sub(r"[/. ]", "-", self.identifier))
        elif self.parent:
            path.append(str(self.type.value.lower()))

        return path

    def root(self):
        if self.parent:
            return self.parent.root()
        return self

    def get_blocks(self, has_identifier: bool, include_types: List[CodeBlockType] = None) -> List["CodeBlock"]:
        blocks = [self]
        for child in self.children:
            if has_identifier and not child.identifier:
                continue

            if include_types and child.type not in include_types:
                continue

            blocks.extend(child.get_indexable_blocks())
        return blocks

    def find_reference(self, ref_path: [str]) -> Optional[Relationship]:
        for child in self.children:
            if child.type == CodeBlockType.IMPORT:
                for reference in child.references:
                    if reference.path[len(reference.path) - len(ref_path):] == ref_path:
                        return reference

            child_path = child.full_path()

            if child_path[len(child_path) - len(ref_path):] == ref_path:
                if self.type == CodeBlockType.CLASS:
                    return Relationship(scope=ReferenceScope.CLASS, path=child_path)
                if self.type == CodeBlockType.MODULE:
                    return Relationship(scope=ReferenceScope.GLOBAL, path=child_path)

                return Relationship(scope=ReferenceScope.LOCAL, path=child_path)

        if self.parent:
            reference = self.parent.find_reference(ref_path)
            if reference:
                return reference

        return None

    def get_all_references(self, exclude_types: List[CodeBlockType] =[]) -> List[Relationship]:
        references = []
        references.extend(self.references)
        for childblock in self.children:
            if not exclude_types or childblock.type not in exclude_types:
                references.extend(childblock.get_all_references(exclude_types=exclude_types))

        return references

    def _fix_reference_path(self, reference: Relationship):
        if reference.scope == ReferenceScope.CLASS:
            if self.type == CodeBlockType.CLASS:
                return Relationship(scope=reference.scope, path=[self.identifier] + reference.path)
            elif self.parent:
                return self.parent._fix_reference_path(reference)

        return reference

    def is_complete(self):
        if self.type == CodeBlockType.COMMENTED_OUT_CODE:
            return False
        for child in self.children:
            if not child.is_complete():
                return False
        return True

    def find_errors(self) -> List["CodeBlock"]:
        errors = []
        if self.children:
            for child in self.children:
                errors.extend(child.find_errors())

        if self.type == CodeBlockType.ERROR:
            errors.append(self)

        return errors

    def create_commented_out_block(self, comment_out_str: str = "..."):
        return CodeBlock(
            type=CodeBlockType.COMMENTED_OUT_CODE,
            indentation=self.indentation,
            pre_lines=1,
            content=self.create_comment(comment_out_str))

    def create_comment(self, comment: str) -> str:
        symbol = get_comment_symbol(self.root().language)
        return f"{symbol} {comment}"

    def add_indentation(self, indentation: str):
        if self.pre_lines:
            self.indentation += indentation
        for child in self.children:
            child.add_indentation(indentation)

    def find_equal_parent(self, check_block: "CodeBlock") -> Optional["CodeBlock"]:
        if not self.parent:
            return None

        if self.parent == check_block:
            return self

        return self.parent.find_equal_parent(check_block)

    def _get_matching_content(self, other_children: List["CodeBlock"], start_original: int) -> List["CodeBlock"]:
        original_contents = [child.content for child in self.children[start_original:]]
        return [other_child for other_child in other_children if other_child.content in original_contents]

    def get_matching_blocks(self, other_block: "CodeBlock") -> List["CodeBlock"]:
        matching_children = self._get_matching_content(other_block.children, 0)
        if matching_children:
            return matching_children

        nested_match = self.find_nested_matching_block(other_block)
        if nested_match:
            return [nested_match]

        return []

    def has_any_matching_child(self, other_children: List["CodeBlock"]) -> bool:
        return self._check_matching(other_children, any)

    def has_all_matching_children(self, other_children: List["CodeBlock"]) -> bool:
        if len(self.children) != len(other_children):
            return False
        return self._check_matching(other_children, all)

    def _check_matching(self, other_children: List["CodeBlock"], operation: Callable) -> bool:
        original_identifiers = [child.identifier for child in self.children if child.identifier]
        updated_identifiers = [child.identifier for child in other_children if child.identifier]
        return operation(ub_content in original_identifiers for ub_content in updated_identifiers)

    def find_next_matching_child_block(self, children_start, other_child_block):
        i = children_start
        while i < len(self.children):
            check_original_block = self.children[i]
            if (check_original_block.content
                    and check_original_block.content == other_child_block.content
                    and check_original_block.type == other_child_block.type):
                return i
            i += 1
        return None

    def find_nested_matching_block(self, other: "CodeBlock", start_original: int = 0) -> Optional["CodeBlock"]:
        for child_block in self.children[start_original:]:
            if child_block.children:
                for other_child_block in other.children:
                    if child_block.content == other_child_block.content and child_block.type == other_child_block.type:
                        return child_block

                nested_match = child_block.find_nested_matching_block(other)
                if nested_match:
                    return nested_match
        return None

    def find_by_path(self, path: List[str]) -> Optional["CodeBlock"]:
        if not path:
            return None

        for child in self.children:
            if child.identifier == path[0]:
                if len(path) == 1:
                    return child
                else:
                    return child.find_by_path(path[1:])

        return None

    def find_blocks_with_identifier(self, identifier: str) -> List["CodeBlock"]:
        blocks = []
        for child_block in self.children:
            if child_block.identifier and identifier and child_block.identifier == identifier:
                blocks.append(child_block)
        return blocks

    def find_incomplete_blocks_with_type(self, block_type: CodeBlockType):
        return self.find_incomplete_blocks_with_types([block_type])

    def find_incomplete_blocks_with_types(self, block_types: [CodeBlockType]):
        matching_blocks = []
        for child_block in self.children:
            if child_block.type in block_types and not child_block.is_complete():
                matching_blocks.append(child_block)

            if child_block.children:
                matching_blocks.extend(child_block.find_incomplete_blocks_with_types(block_types))

        return matching_blocks

    def find_blocks_with_types(self, block_types: List[CodeBlockType]) -> List["CodeBlock"]:
        matching_blocks = []
        if self.type in block_types:
            matching_blocks.append(self)
        for child_block in self.children:
            matching_blocks.extend(child_block.find_blocks_with_types(block_types=block_types))
        return matching_blocks

    def find_blocks_with_type(self, block_type: CodeBlockType) -> List["CodeBlock"]:
        return self.find_blocks_with_types([block_type])

    def find_nested_matching_blocks(self, blocks: List["CodeBlock"], start_original: int = 0) -> List["CodeBlock"]:
        matching_blocks = []
        for child_block in self.children[start_original:]:
            if any(child_block.has_equal_definition(block) for block in blocks):
                matching_blocks.append(child_block)
            elif child_block.children:
                matching_blocks.extend(child_block.find_nested_matching_blocks(blocks))
        return matching_blocks

    def has_any_similarity(self, updated_block: "CodeBlock"):
        if self.has_any_matching_child(updated_block.children):
            return True
        elif self.find_nested_matching_block(updated_block):
            return True
        return False

    def has_nested_matching_block(self, other: Optional["CodeBlock"], start_original: int = 0) -> bool:
        if not other:
            return False
        return self.find_nested_matching_block(other, start_original)

    def has_nested_blocks_with_types(self, find_types: Optional[List["CodeBlock"]], start_original: int = 0) -> bool:
        if not find_types:
            return False
        for child_block in self.children[start_original:]:
            if child_block.type in find_types:
                return True
            if child_block.has_nested_blocks_with_types(find_types):
                return True
        return False

    def find_next_commented_out(self, start):
        i = start
        while i < len(self.children):
            if self.children[i].type == CodeBlockType.COMMENTED_OUT_CODE:
                return i
            i += 1
        return None

    def find_next_matching_block(self, other_block: "CodeBlock", start_original: int, start_updated: int):
        original_blocks = self.children
        other_blocks = other_block.children

        i = start_original

        next_updated_incomplete = None
        j = start_updated
        while j < len(other_blocks):
            if not other_blocks[j].is_complete() and other_blocks[j].type != CodeBlockType.COMMENTED_OUT_CODE:
                next_updated_incomplete = j
                break
            j += 1

        max_j = len(other_blocks) if next_updated_incomplete is None else next_updated_incomplete
        while i < len(original_blocks):
            j = start_updated
            while j < max_j:
                if original_blocks[i].content == other_blocks[j].content:
                    return i, j
                j += 1
            i += 1

        # try to find similar block if there are incomplete update blocks
        if next_updated_incomplete:
            similar_block = self.most_similar_block(other_blocks[next_updated_incomplete], start_original)
            if similar_block:
                logging.debug(f"Will return index for similar block `{self.children[similar_block].content}`")
                return similar_block, next_updated_incomplete

        return len(original_blocks), len(other_blocks)

    def most_similar_block(self,
                           other_block: "CodeBlock",
                           start_original: int):
        """Naive solution for finding similar blocks."""
        # TODO: Check identifier and parameters

        max_similarity = 0
        max_i = None

        i = start_original
        while i < len(self.children):
            if self.children[i].type == other_block.type:
                common_chars = sum(
                    c1 == c2 for c1, c2 in zip(self.children[i].content, other_block.content))
                if common_chars > max_similarity:
                    max_similarity = common_chars
                    max_i = i
            i += 1
        return max_i

    def find_matching_pairs(self, other_block: "CodeBlock") -> List[Tuple["CodeBlock", "CodeBlock"]]:
        matching_pairs = []

        for child_block in other_block.children:
            if child_block.type in NON_CODE_BLOCKS:
                continue
            matching_children = self.find_blocks_with_identifier(child_block.identifier)
            if len(matching_children) == 1:
                logging.debug(f"Found matching child block `{child_block.identifier}` in `{self.identifier}`")
                matching_pairs.append((matching_children[0], child_block))
            else:
                return []

        return matching_pairs

    def find_nested_matching_pairs(self, other_block: "CodeBlock") -> List[Tuple["CodeBlock", "CodeBlock"]]:
        for child_block in self.children:
            matching_children = child_block.find_matching_pairs(other_block)
            if matching_children:
                return matching_children

            matching_children = child_block.find_nested_matching_pairs(other_block)
            if matching_children:
                return matching_children

        return []

    def merge(self, updated_block: "CodeBlock"):
        logging.debug(f"Merging block `{self.type.value}: {self.identifier}` ({len(self.children)} children) with "
                      f"`{updated_block.type.value}: {updated_block.identifier}` ({len(updated_block.children)} children)")

        # If there are no matching child blocks on root level expect separate blocks to update on other levels
        has_identifier = any(child.identifier for child in self.children)
        no_matching_identifiers = has_identifier and not self.has_any_matching_child(updated_block.children)
        if no_matching_identifiers:
            update_pairs = self.find_nested_matching_pairs(updated_block)
            if update_pairs:
                for original_child, updated_child in update_pairs:
                    original_indentation_length = len(original_child.indentation) + len(self.indentation)
                    updated_indentation_length = len(updated_child.indentation) + len(updated_block.indentation)
                    if original_indentation_length > updated_indentation_length:
                        additional_indentation = ' ' * (original_indentation_length - updated_indentation_length)
                        updated_child.add_indentation(additional_indentation)

                    self.merge_history.append(MergeAction(action="find_nested_block", original_block=original_child, updated_block=updated_child))
                    original_child._merge(updated_child)
                return

            raise ValueError(f"Didn't find matching blocks in `{self.identifier}``")
        else:
            self._merge(updated_block)

    def _merge(self, updated_block: "CodeBlock"):
        logging.debug(f"Merging block `{self.type.value}: {self.identifier}` ({len(self.children)} children) with "
                      f"`{updated_block.type.value}: {updated_block.identifier}` ({len(updated_block.children)} children)")

        # Just replace if there are no code blocks in original block
        if len(self.children) == 0 or all(child.type in NON_CODE_BLOCKS for child in self.children):
            self.children = updated_block.children
            self.merge_history.append(MergeAction(action="replace_non_code_blocks"))

        # Find and replace if all children are matching
        update_pairs = self.find_matching_pairs(updated_block)
        if update_pairs:
            self.merge_history.append(
                MergeAction(action="all_children_match", original_block=self, updated_block=updated_block))

            for original_child, updated_child in update_pairs:
                original_child._merge(updated_child)

            return

        # Replace if block is complete
        if updated_block.is_complete():
            self.children = updated_block.children
            self.merge_history.append(MergeAction(action="replace_complete", original_block=self, updated_block=updated_block))

        self._merge_block_by_block(updated_block)

    def _merge_block_by_block(self, updated_block: "CodeBlock"):
        i = 0
        j = 0
        while j < len(updated_block.children):
            if i >= len(self.children):
                self.children.extend(updated_block.children[j:])
                return

            original_block_child = self.children[i]
            updated_block_child = updated_block.children[j]

            if original_block_child == updated_block_child:
                original_block_child.merge_history.append(MergeAction(action="is_same"))
                i += 1
                j += 1
            elif updated_block_child.type == CodeBlockType.COMMENTED_OUT_CODE:
                j += 1
                orig_next, update_next = self.find_next_matching_block(updated_block, i, j)

                for commented_out_child in self.children[i:orig_next]:
                    commented_out_child.merge_history.append(MergeAction(action="commented_out", original_block=commented_out_child, updated_block=None))

                i = orig_next
                if update_next > j:
                    #  Clean up commented out code at the end
                    last_updated_child = updated_block.children[update_next-1]
                    if last_updated_child.type == CodeBlockType.COMMENTED_OUT_CODE:
                        update_next -= 1

                    self.children[i:i] = updated_block.children[j:update_next]
                    i += update_next - j

                j = update_next
            elif (original_block_child.content == updated_block_child.content and
                  original_block_child.children and updated_block_child.children):
                original_block_child._merge(updated_block_child)
                i += 1
                j += 1
            elif original_block_child.content == updated_block_child.content:
                self.children[i] = updated_block_child
                i += 1
                j += 1
            elif updated_block_child:
                # we expect to update a block when the updated block is incomplete
                # and will try the find the most similar block.
                if not updated_block_child.is_complete():
                    similar_original_block = self.most_similar_block(updated_block_child, i)
                    logging.debug(f"Updated block with definition `{updated_block_child.content}` is not complete")
                    if similar_original_block == i:
                        self.merge_history.append(
                            MergeAction(action="replace_similar", original_block=original_block_child,
                                        updated_block=updated_block_child))

                        original_block_child = CodeBlock(
                            content=updated_block_child.content,
                            identifier=updated_block_child.identifier,
                            pre_code=updated_block_child.pre_code,
                            type=updated_block_child.type,
                            parent=self.parent,
                            children=original_block_child.children
                        )

                        self.children[i] = original_block_child

                        logging.debug(
                            f"Will replace similar original block definition: `{original_block_child.content}`")
                        original_block_child._merge(updated_block_child)
                        i += 1
                        j += 1

                        continue
                    elif not similar_original_block:
                        logging.debug(f"No most similar original block found to `{original_block_child.content}")
                    else:
                        logging.debug(f"Expected most similar original block to be `{original_block_child.content}, "
                                      f"but was {self.children[similar_original_block].content}`")

                next_original_match = self.find_next_matching_child_block(i, updated_block_child)
                next_updated_match = updated_block.find_next_matching_child_block(j, original_block_child)
                next_commented_out = updated_block.find_next_commented_out(j)

                if next_original_match:
                    self.merge_history.append(
                        MergeAction(action="next_original_match_replace", original_block=self.children[next_original_match],
                                    updated_block=updated_block_child))

                    # if it's not on the first level we expect the blocks to be replaced
                    self.children = self.children[:i] + self.children[next_original_match:]
                elif next_commented_out is not None and (
                        not next_updated_match or next_commented_out < next_updated_match):
                    # if there is commented out code after the updated block,
                    # we will insert the lines before the commented out block in the original block
                    self.merge_history.append(
                        MergeAction(action="next_commented_out_insert",
                                    original_block=original_block_child,
                                    updated_block=updated_block.children[next_commented_out]))

                    self.insert_children(i, updated_block.children[j:next_commented_out])
                    i += next_commented_out - j
                    j = next_commented_out
                elif next_updated_match:
                    # if there is a match in the updated block, we expect this to be an addition
                    # and insert the lines before in the original block
                    self.merge_history.append(
                        MergeAction(action="next_original_match_insert",
                                    original_block=original_block_child,
                                    updated_block=updated_block.children[next_updated_match]))

                    self.insert_children(i, updated_block.children[j:next_updated_match])
                    diff = next_updated_match - j
                    i += diff
                    j = next_updated_match
                else:
                    self.children.pop(i)
            else:
                self.insert_child(i, updated_block_child)
                j += 1
                i += 1

    def copy_with_trimmed_parents(self):
        block_copy = CodeBlock(
            type=self.type,
            identifier=self.identifier,
            content=self.content,
            indentation=self.indentation,
            pre_lines=self.pre_lines,
            start_line=self.start_line,
            tree_sitter_type=self.tree_sitter_type,
            children=self.children
        )

        if self.parent:
            block_copy.parent = self.parent.trim_code_block(block_copy)
        return block_copy

    def trim_code_block(self, keep_child: "CodeBlock"):
        children = []
        for child in self.children:
            if child.type == CodeBlockType.BLOCK_DELIMITER and child.pre_lines > 0:
                children.append(child)
            elif child.content != keep_child.content:  # TODO: Fix ID to compare to
                if (child.type not in NON_CODE_BLOCKS and
                        (not children or children[-1].type != CodeBlockType.COMMENTED_OUT_CODE)):
                    children.append(child.create_commented_out_block())
            else:
                children.append(keep_child)

        trimmed_block = CodeBlock(
            content=self.content,
            identifier=self.identifier,
            indentation=self.indentation,
            pre_lines=self.pre_lines,
            type=self.type,
            start_line=self.start_line,
            children=children
        )

        if trimmed_block.parent:
            trimmed_block.parent = self.parent.trim_code_block(trimmed_block)

        return trimmed_block

    def get_indexable_blocks(self) -> List["CodeBlock"]:
        """
        Returns a list of blocks that can be indexed.
        """
        splitted_blocks = []
        splitted_blocks.append(self)
        for child in self.children:
            if child.type in [CodeBlockType.CLASS, CodeBlockType.FUNCTION, CodeBlockType.CONSTRUCTOR, CodeBlockType.TEST_SUITE, CodeBlockType.TEST_CASE]:
                splitted_blocks.extend(child.get_indexable_blocks())

        return splitted_blocks

    def trim(self,
             keep_blocks: List["CodeBlock"] = [],
             keep_level: int = 0,
             include_types: List[CodeBlockType] = None,
             exclude_types: List[CodeBlockType] = None,
             first_level_types: List[CodeBlockType] = None,
             keep_the_rest: bool = False,
             comment_out_str: str = "..."):
        children = []
        for child in self.children:
            if keep_level:
                if child.children:
                    children.append(
                        child.trim(keep_blocks=keep_blocks, keep_level=keep_level - 1, comment_out_str=comment_out_str))
                else:
                    children.append(child)
            elif child.type == CodeBlockType.BLOCK_DELIMITER and child.pre_lines > 0:
                children.append(child)
            elif any(child.has_equal_definition(block) for block in keep_blocks):
                children.append(child)
            elif first_level_types and child.type in first_level_types:
                children.append(child.trim(keep_blocks, comment_out_str=comment_out_str))
            elif (child.find_nested_matching_blocks(keep_blocks)
                  or (include_types and child.type in include_types)):
                children.append(child.trim(keep_blocks, keep_the_rest=keep_the_rest, comment_out_str=comment_out_str))
            elif keep_the_rest and (not exclude_types or child.type not in exclude_types):
                children.append(child.trim(keep_blocks, keep_the_rest=keep_the_rest, exclude_types=exclude_types, comment_out_str=comment_out_str))
            elif (child.type not in NON_CODE_BLOCKS and
                  (not children or children[-1].type != CodeBlockType.COMMENTED_OUT_CODE)):
                children.append(child.create_commented_out_block(comment_out_str))

        trimmed_block = CodeBlock(
            content=self.content,
            identifier=self.identifier,
            pre_code=self.pre_code,
            indentation=self.indentation,
            pre_lines=self.pre_lines,
            type=self.type,
            start_line=self.start_line,
            children=children,
            parent=self.parent
        )

        return trimmed_block

    def trim_with_types(self, show_block: "CodeBlock" = None, include_types: List[CodeBlockType] = None):
        children = []
        for child in self.children:
            if child.type == CodeBlockType.BLOCK_DELIMITER:
                children.append(copy.copy(child))
            elif self == show_block or (include_types and child.type in include_types):
                children.append(child.trim_with_types(show_block, include_types))
            elif child.has_nested_matching_block(show_block) or child.has_nested_blocks_with_types(include_types):
                children.append(child.trim_with_types(show_block, include_types))
            elif not children or children[-1].type != CodeBlockType.COMMENTED_OUT_CODE:
                children.append(child.create_commented_out_block())

        return CodeBlock(
            content=self.content,
            identifier=self.identifier,
            pre_code=self.pre_code,
            type=self.type,
            parent=self.parent,
            children=children
        )
