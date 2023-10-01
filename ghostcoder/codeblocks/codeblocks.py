import copy
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Callable

from ghostcoder.codeblocks.parser.comment import get_comment_symbol


class CodeBlockType(str, Enum):
    DECLARATION = "declaration"
    IDENTIFIER = "identifier"
    PARAMETER = "parameter"

    MODULE = "module"
    CLASS = "class"
    FUNCTION = "function"

    IMPORT = "import"
    STATEMENT = "statement"
    CODE = "code"
    BLOCK_DELIMITER = "block_delimiter"

    COMMENT = "comment"
    COMMENTED_OUT_CODE = "commented_out_code"

    SPACE = "space"
    ERROR = "error"


non_code_blocks = [CodeBlockType.BLOCK_DELIMITER, CodeBlockType.COMMENTED_OUT_CODE, CodeBlockType.SPACE]


@dataclass
class CodeBlock:
    content: str
    type: CodeBlockType
    content_lines: List[str] = field(default_factory=list)
    start_line: int = 0
    end_line: int = 0
    tree_sitter_type: Optional[str] = None
    pre_code: str = ""
    pre_lines: int = 0
    indentation: str = ""
    language: str = None

    children: List["CodeBlock"] = field(default_factory=list)
    parent: Optional["CodeBlock"] = field(default=None)

    def __post_init__(self):
        for child in self.children:
            child.parent = self

        if self.pre_code.strip():
            raise ValueError("Expected pre_code to only contain spaces and line breaks. Got ", self.pre_code)

        pre_code_lines = self.pre_code.split("\n")
        self.pre_lines = len(pre_code_lines) - 1
        if self.pre_lines > 0:
            self.indentation = pre_code_lines[-1]

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
        return str(self.to_dict())

    def trim_code_block(self, show_block: "CodeBlock" = None, include_types: List[CodeBlockType] = None):
        children = []
        for child in self.children:
            if child.type == CodeBlockType.BLOCK_DELIMITER:
                children.append(copy.copy(child))
            elif self == show_block or (include_types and self.type in include_types):
                children.append(child.trim_code_block(show_block, include_types))
            elif child.has_nested_matching_block(show_block) or child.has_nested_blocks_with_types(include_types):
                children.append(child.trim_code_block(show_block, include_types))
            elif not children or children[-1].type != CodeBlockType.COMMENTED_OUT_CODE:
                children.append(child.create_commented_out_block())

        return CodeBlock(
            content=self.content,
            pre_code=self.pre_code,
            type=self.type,
            parent=self.parent,
            children=children
        )

    def length_without_whitespace(self):
        string_without_whitespace = re.sub(r'\s', '', self.to_string())
        return len(string_without_whitespace)

    def to_string(self, include_types: List[CodeBlockType] = None):
        child_code = ""
        if include_types:
            for child in self.children:
                if child.type in include_types:
                    child_code += child.to_string(include_types)
                else:
                    child_code += self.create_commented_out_block().to_string()
        else:
            child_code = "".join([child.to_string() for child in self.children])

        if self.pre_lines:
            linebreaks = "\n" * self.pre_lines
            content = linebreaks + "\n".join(self.indentation + line for line in self.content_lines)
        else:
            content = self.pre_code + self.content

        return f"{content}{child_code}"

    def to_tree(self, indent: int = 0, include_tree_sitter_type: bool = False):
        child_tree = "".join([
            child.to_tree(indent=indent + 1, include_tree_sitter_type=include_tree_sitter_type)
            for child in self.children])
        indent_str = " " * indent

        tree_sitter_type = ""
        if include_tree_sitter_type and self.tree_sitter_type:
            tree_sitter_type = f" ({self.tree_sitter_type})"

        content = self.content.strip().replace("\n", "\\n")
        return f"{indent_str} {indent} {self.type.value} `{content}`{tree_sitter_type}\n{child_tree}"

    def __eq__(self, other):
        if not isinstance(other, CodeBlock):
            return False
        return self.to_dict() == other.to_dict()

    def to_dict(self):
        return {
            "code": self.content,
            "type": self.type,
            "tree_sitter_type": self.tree_sitter_type,
            "pre_code": self.pre_code,
            # "is_nested": self.is_nested,
            "children": [child.to_dict() for child in self.children]
        }

    def root(self):
        if self.parent:
            return self.parent.root()
        return self

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
            pre_code=self.pre_code,
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

    def _check_matching(self, other_children: List["CodeBlock"], start_original: int, operation: Callable) -> bool:
        original_contents = [child.content for child in self.children[start_original:]]
        updated_contents = [child.content for child in other_children]
        return operation(ub_content in original_contents for ub_content in updated_contents)

    def get_matching_blocks(self, other_block: "CodeBlock") -> List["CodeBlock"]:
        matching_children = self._get_matching_content(other_block.children, 0)
        if matching_children:
            return matching_children

        nested_match = self.find_nested_matching_block(other_block)
        if nested_match:
            return [nested_match]

        return []

    def has_any_matching_child(self, other_children: List["CodeBlock"], start_original: int = 0) -> bool:
        return self._check_matching(other_children, start_original, any)

    def has_all_matching_children(self, other_children: List["CodeBlock"], start_original: int = 0) -> bool:
        if len(self.children[start_original:]) != len(other_children):
            return False
        return self._check_matching(other_children, start_original, all)

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

    def find_nested_matching_blocks(self, blocks: List["CodeBlock"], start_original: int = 0) -> List["CodeBlock"]:
        matching_blocks = []
        for child_block in self.children[start_original:]:
            if any(child_block.has_equal_definition(block) for block in blocks):
                matching_blocks.append(child_block)
            elif child_block.children:
                matching_blocks.extend(child_block.find_nested_matching_blocks(blocks))
        return matching_blocks

    def has_any_similarity(self, updated_block: "CodeBlock"):
        if self.has_any_matching_child(updated_block.children, 0):
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


    def merge(self, updated_block: "CodeBlock", first_level: bool = False) -> List[str]:
        logging.debug(f"Merging block `{self.type.value}: {self.content}` ({len(self.children)} children) with "
              f"`{updated_block.type.value}: {updated_block.content}` ({len(updated_block.children)} children)")

        if first_level and not self.has_any_matching_child(updated_block.children, 0):
            matching_block = self.find_nested_matching_block(updated_block)
            if matching_block:
                logging.debug(
                    f"Found matching children in original block `{self.type.value}: {self.content}`, "
                    f"will merge with updated children")
                indentation = matching_block.indentation
                updated_block.add_indentation(indentation)

                child_tweaks = matching_block.parent.merge(updated_block, first_level=True)
                return child_tweaks + ["find_nested"]
            else:
                logging.debug(
                    f"No matching children in original block `{self.type.value}: {self.content}`, "
                    f"will replace contents")
                self.children = updated_block.children
                return ["replace"]
        if self.has_all_matching_children(updated_block.children, 0) and updated_block.is_complete():
            logging.debug(
                "All updated children match the original ones, and updated content is complete. Will merge updated blocks.")
            self.children = updated_block.children
            return []

        merge_tweaks = []

        i = 0
        j = 0
        while j < len(updated_block.children):
            if i >= len(self.children):
                self.children.extend(updated_block.children[j:])
                return []

            original_block_child = self.children[i]
            updated_block_child = updated_block.children[j]

            if original_block_child == updated_block_child:
                i += 1
                j += 1
            elif updated_block_child.type == CodeBlockType.COMMENTED_OUT_CODE:
                j += 1
                orig_next, update_next = self.find_next_matching_block(updated_block, i, j)

                i = orig_next
                if update_next > j:
                    self.children[i:i] = updated_block.children[j:update_next]
                    i += update_next - j

                j = update_next
                merge_tweaks.append("commented_out")
            elif (original_block_child.content == updated_block_child.content and
                  original_block_child.children and updated_block_child.children):
                child_tweaks = original_block_child.merge(updated_block_child)
                if updated_block_child.indentation or updated_block_child.pre_lines:
                    original_block_child.indentation = updated_block_child.indentation
                    original_block_child.pre_lines = updated_block_child.pre_lines

                merge_tweaks.extend(child_tweaks)
                i += 1
                j += 1
            elif original_block_child.content == updated_block_child.content:
                self.children[i] = updated_block_child
                i += 1
                j += 1
            elif updated_block_child and self:
                # we expect to update a block when the updated block is incomplete
                # and will try the find the most similar block.
                if not updated_block_child.is_complete():
                    similar_original_block = self.most_similar_block(updated_block_child, i)
                    logging.debug(f"Updated block with definition `{updated_block_child.content}` is not complete")
                    if similar_original_block == i:
                        merge_tweaks.append("replace_similar")

                        original_block_child = CodeBlock(
                            content=updated_block_child.content,
                            pre_code=updated_block_child.pre_code,
                            type=updated_block_child.type,
                            parent=self.parent,
                            children=original_block_child.children
                        )

                        self.children[i] = original_block_child

                        logging.debug(f"Will replace similar original block definition: `{original_block_child.content}`")
                        child_tweaks = original_block_child.merge(updated_block_child)
                        merge_tweaks.extend(child_tweaks)
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
                    if first_level:
                        merge_tweaks.append("next_original_match_keep")
                        # if the there is a match on the first level, we will keep the original blocks until that line
                        i = next_original_match
                    else:
                        merge_tweaks.append("next_original_match_replace")
                        # if it's not on the first level we expect the blocks to be replaced
                        self.children = self.children[:i] + self.children[next_original_match:]
                elif next_commented_out is not None and (
                        not next_updated_match or next_commented_out < next_updated_match):
                    # if there is commented out code after the updated block,
                    # we will insert the lines before the commented out block in the original block
                    merge_tweaks.append("next_commented_out_insert")
                    self.insert_children(i, updated_block.children[j:next_commented_out])
                    i += next_commented_out - j
                    j = next_commented_out
                elif next_updated_match:
                    # if there is a match in the updated block, we expect this to be an addition
                    # and insert the lines before in the original block
                    merge_tweaks.append("next_original_match_insert")

                    self.insert_children(i, updated_block.children[j:next_updated_match])
                    diff = next_updated_match - j
                    i += diff
                    j = next_updated_match
                elif first_level:
                    self.insert_child(i, updated_block_child)
                    i += 1
                    j += 1
                else:
                    self.children.pop(i)
            else:
                self.insert_child(i, updated_block_child)
                j += 1
                i += 1

        return merge_tweaks

    def copy_with_trimmed_parents(self):
        block_copy = CodeBlock(
            type=self.type,
            content=self.content,
            pre_code=self.pre_code,
            tree_sitter_type=self.tree_sitter_type,
            children=self.children
        )

        if self.parent:
            block_copy.parent = self.parent.trim_code_block(block_copy)
        return block_copy

    def trim_code_block(self, keep_child: "CodeBlock"):
        children = []
        for child in self.children:
            if child.type == CodeBlockType.BLOCK_DELIMITER:
                children.append(child)
            elif child.content != keep_child.content: # TODO: Fix ID to compare to
                if (child.type not in non_code_blocks and
                        (not children or children[-1].type != CodeBlockType.COMMENTED_OUT_CODE)):
                    children.append(child.create_commented_out_block())
            else:
                children.append(keep_child)

        trimmed_block = CodeBlock(
            content=self.content,
            pre_code=self.pre_code,
            type=self.type,
            children=children
        )

        if trimmed_block.parent:
            trimmed_block.parent = self.parent.trim_code_block(trimmed_block)

        return trimmed_block

    def trim(self, keep_blocks: List["CodeBlock"], keep_level: int = 0, comment_out_str: str = "..."):
        children = []
        for child in self.children:
            if keep_level:
                if child.children:
                    children.append(child.trim(keep_blocks=keep_blocks, keep_level=keep_level-1, comment_out_str=comment_out_str))
                else:
                    children.append(child)
            elif child.type == CodeBlockType.BLOCK_DELIMITER:
                children.append(child)
            elif any(child.has_equal_definition(block) for block in keep_blocks):
                children.append(child)
            elif child.find_nested_matching_blocks(keep_blocks):
                children.append(child.trim(keep_blocks, comment_out_str=comment_out_str))
            elif (child.type not in non_code_blocks and
                  (not children or children[-1].type != CodeBlockType.COMMENTED_OUT_CODE)):
                children.append(child.create_commented_out_block(comment_out_str))

        trimmed_block = CodeBlock(
            content=self.content,
            pre_code=self.pre_code,
            type=self.type,
            children=children
        )

        return trimmed_block
