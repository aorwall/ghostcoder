import logging
from enum import Enum
from typing import List, Union, Optional, Dict, Any

from langchain.callbacks.openai_info import get_openai_token_cost_for_model, MODEL_COST_PER_1K_TOKENS
from marshmallow import ValidationError
from pydantic import BaseModel, Field, validator, root_validator

from ghostcoder.utils import language_by_filename


class Item(BaseModel):
    type: str

    def to_history(self) -> str:
        pass

    def to_prompt(self, style: Optional[str] = None) -> str:
        pass


class TextItem(Item):
    type: str = "text"
    text: str = Field(default="", description="text")
    need_input: bool = Field(default=False, description="if more input is needed")

    def __str__(self) -> str:
        return self.text

    def to_prompt(self, style: Optional[str] = None) -> str:
        return self.text


class CodeItem(Item):
    type: str = "code"
    content: Optional[str] = Field(default=None, description="Code")
    language: Optional[str] = Field(default=None, description="Programming language")

    def to_prompt(self, style: Optional[str] = None) -> str:
        if style == "llama" and self.language:
            return f"[{self.language.upper()}]\n{self.content}\n[/{self.language.upper()}]\n"

        if self.language:
            return f"```{self.language}\n{self.content}\n```"

        return f"```\n{self.content}\n```"


class VerificationFailureItem(Item):
    type: str = "verification_failure"
    test_code: str = Field(default=None, description="Code of the test")
    output: str = Field(description="Output of the verification process")
    test_method: Optional[str] = Field(default=None, description="Test method")
    test_class: Optional[str] = Field(default=None, description="Test class")
    test_file: Optional[str] = Field(default=None, description="Test file")

    def to_prompt(self, style: Optional[str] = None):
        code = "" if not self.test_code else f"```\n{self.test_code}\n```"
        return (f"Test method `{self.test_class}.{self.test_method}` in `{self.test_file}` failed."
                f"\n{code} "
                f"\nOutput:\n```\n{self.output}\n```")


class FileItem(CodeItem):
    type: str = "file"
    file_path: str = Field(default="", description="Path to file")
    readonly: bool = Field(default=False, description="Is the file readonly")
    new: bool = Field(default=False, description="If the file is new and doesn't exist in the repository")

    @root_validator(pre=True)
    def set_language(cls, values):
        file_path = values.get("file_path")
        language = values.get("language")
        if file_path and not language:
            values["language"] = language_by_filename(file_path)

        if not file_path.startswith("/"):
            values["file_path"] = "/" + file_path
        return values

    def __str__(self) -> str:
        return self.to_prompt()

    def to_prompt(self, style: Optional[str] = None):
        readonly_str = ""
        if self.readonly:
            readonly_str = " (readonly)"

        return f"{self.file_path}{readonly_str}\n{super().to_prompt(style=style)}"

    def to_history(self) -> str:
        return f"{self.file_path}"

    def to_log(self):
        details = ""
        if self.language:
            details += f"{self.language}"

        if self.readonly:
            if details:
                details += ", "
            details += "readonly"

        if not self.content:
            if details:
                details += ", "
            details += "new"

        if details:
            return f"{self.file_path} ({details})"

        return f"{self.file_path}"


class UpdatedFileItem(FileItem):
    type: str = "updated_file"
    file_path: str = Field(description="file to update or create")
    error: Optional[str] = Field(default=None, description="error message")
    diff: Optional[str] = Field(default=None, description="diff of the file")
    invalid: str = Field(default=None, description="file is invalid")
    created: bool = Field(default=False, description="file is created")

    def to_prompt(self, style: Optional[str] = None):
        return super().to_prompt(style=style)

    def to_log(self):
        if self.error:
            status = "failed"
        elif self.invalid:
            status = self.invalid
        elif self.created:
            status = "created"
        else:
            status = "updated"

        return f"{self.file_path} ({status})"

    def __str__(self) -> str:
        return self.to_prompt()

    def to_history(self) -> str:
        return str(self)


class ItemHolder(BaseModel):
    items: List[Item] = Field(default=[])

    @validator("items", pre=True)
    def parse_items(cls, items: List[Union[Dict[str, Any], Item]]) -> List[Item]:
        parsed_items = []
        for item in items:
            if isinstance(item, Item):
                parsed_items.append(item)
                continue

            item_type = item.get("type")
            if item_type == "text":
                parsed_items.append(TextItem(**item))
            elif item_type == "code":
                parsed_items.append(CodeItem(**item))
            elif item_type == "file":
                parsed_items.append(FileItem(**item))
            elif item_type == "updated_file":
                parsed_items.append(UpdatedFileItem(**item))
            else:
                raise ValidationError(f"Unknown item type: {item_type}")
        return parsed_items

    class Config:
        json_encoders = {
            TextItem: lambda v: v.dict(),
            FileItem: lambda v: v.dict(),
            UpdatedFileItem: lambda v: v.dict(),
        }


class Stats(BaseModel):
    prompt: str = None
    model_name: str = None
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_cost: float = 0.0
    duration: float = 0.0
    extra: dict = {}
    metrics: dict = {}

    @classmethod
    def from_dict(cls, prompt: str, duration: float, llm_output: dict = {}, extra: dict = {}):
        token_usage = llm_output.get("token_usage", {})
        model_name = llm_output.get("model_name", "unknown")
        prompt_tokens = token_usage.get("prompt_tokens", 0)
        completion_tokens = token_usage.get("completion_tokens", 0)
        total_tokens = token_usage.get("total_tokens", 0)

        total_cost = 0.0

        if model_name in MODEL_COST_PER_1K_TOKENS:
            try:
                completion_cost = get_openai_token_cost_for_model(model_name, completion_tokens, is_completion=True)
                prompt_cost = get_openai_token_cost_for_model(model_name, prompt_tokens, is_completion=False)
                total_cost = completion_cost + prompt_cost
            except ValueError as e:
                logging.info(f"Failed to get cost for model {model_name}: {e}")

        return cls(
            prompt=prompt,
            model_name=model_name,
            total_tokens=total_tokens,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_cost=total_cost,
            duration=duration,
            extra=extra)

    def __add__(self, other):
        sum_usage = Stats(
            prompt=self.prompt,
            model_name=self.model_name,
            total_tokens=self.total_cost + other.total_tokens,
            prompt_tokens=self.prompt_tokens + other.prompt_tokens,
            completion_tokens=self.completion_tokens + other.completion_tokens,
            duration=self.duration + other.duration,
        )

        try:
            completion_cost = get_openai_token_cost_for_model(sum_usage.model_name, sum_usage.completion_tokens, is_completion=True)
            prompt_cost = get_openai_token_cost_for_model(sum_usage.model_name, sum_usage.prompt_tokens, is_completion=False)
            sum_usage.total_cost = completion_cost + prompt_cost
        except ValueError as e:
            """Expect failure"""

        return sum_usage

    def increment(self, key: str, value: int = 1):
        self.metrics[key] = self.metrics.get(key, 0) + value


class Message(ItemHolder):
    sender: str = Field(description="who sent the message", enum=["Human", "AI", "Agent"])
    items: List[Item] = []
    summary: Optional[str] = Field(default=None, description="summary of the message")
    stats: Optional[Stats] = Field(default=None, description="status information about the processing of the message")
    commit_id: Optional[str] = None
    discarded: bool = False
    auto: bool = False

    def to_prompt(self, style: Optional[str] = None) -> str:
        return "\n\n".join([item.to_prompt(style=style) for item in self.items])

    def to_history(self):
        item_str = "\n".join([item.to_history() for item in self.items])
        return f"{item_str}"

    def find_items_by_type(self, item_type: str):
        return [item for item in self.items if item.type == item_type]


class VerificationResult(BaseModel):
    success: bool
    message: str = ""
    verification_count: int = 0
    failures: List[VerificationFailureItem] = []

    def to_prompt(self):
        if self.success:
            return self.message
        else:
            return self.message + "\n" + "\n".join([failure.to_prompt() for failure in self.failures])


class MergeResponse(BaseModel):
    diff: Optional[str]
    answer: Optional[str]
    merged: bool = False


class File(BaseModel):
    path: str
    language: str
    name: str = ""  # TODO: remove this?
    last_modified: float = 0
    staged: bool = False
    untracked: bool = False
    test: bool = False


class Folder(BaseModel):
    name: str
    path: str
    children: List[Union[File, "Folder"]]

    def traverse(self) -> list[File]:
        files = []
        for node in self.children:
            if isinstance(node, File):
                files.append(node)
            elif isinstance(node, Folder):
                files.extend(node.traverse())
        return files

    def find(self, path):
        for child in self.children:
            if child.path == path:
                return child
            elif isinstance(child, Folder):
                result = child.find(path)
                if result is not None:
                    return result
        return None
       
    def tree_string(self, indent=0):
        file_tree = ""
        for child in self.children:
            if isinstance(child, Folder):
                file_tree += " " * indent + child.name + "/\n"
                file_tree += child.tree_string(indent + 2)
            else:
                file_tree += " " * (indent) + child.name + "\n"
        return file_tree


class SaveFilesRequest(BaseModel):
    file_paths: List[str]


class DiscardFilesRequest(BaseModel):
    file_paths: List[str]


class FileContent(BaseModel):
    file_path: str
    content: str

class Difficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
