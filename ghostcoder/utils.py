import re
from typing import Optional

import tiktoken

comment_marker_pattern = r"^[ \t]*(//|#|--|<!--)\s*"

incomplete_code_marker_patterns = [
    r"\(?(rest of|existing code|other code)",
    r"\.\.\.\s*\(?rest of code|existing code|other code\)?\s*",
    r"^\.\.\.\s*"
]

#  TODO: Uncomment language when we have support for it
language_extensions = {
    "python": [".py"],
    "java": [".java"],
    "javascript": [".js", ".jsx"],
#    "c": [".c"],
#    "cpp": [".cpp"],
#    "css": [".css", ".scss"],
#    "go": [".go"],
#    "html": [".html", ".htm"],
#    "ruby": [".rb"],
#    "swift": [".swift"],
#    "kotlin": [".kt"],
    "typescript": [".ts", ".tsx"],
#    "json": [".json"],
#    "sql": [".sql"],
#    "yaml": [".yaml", ".yml"],
#    "xml": [".xml"]
}

test_file_path_patterns = {
    "javascript": ["__tests__", "__mocks__"],
    "typescript": ["__tests__", "__mocks__"],
    "java": ["src/test"],
}

def get_purpose_by_filepath(language, file_path):  # TODO: Check content in file also
    if not language:
        return "file"

    if language in test_file_path_patterns:
        for pattern in test_file_path_patterns[language]:
            if pattern in file_path:
                return "test"
    return "code"


def get_extension(language: str) -> Optional[str]:
    for lang, exts in language_extensions.items():
        if lang == language:
            return exts[0]
    return None

def is_complete(content: str):
    lines = content.split('\n')

    for i, line in enumerate(lines, start=1):
        if re.search(comment_marker_pattern, line):
            rest_of_line = re.sub(comment_marker_pattern, '', line)

            if any(re.search(pattern, rest_of_line, re.DOTALL | re.IGNORECASE) for pattern in
                   incomplete_code_marker_patterns):
                print("Not complete: Matched marker on line {}: {}".format(i, line))
                return False
    return True


def extract_code_from_text(text):
    pattern = r"```(?:\w*\n)?(.*?)```"
    matches = re.findall(pattern, text, re.DOTALL)
    if len(matches) == 1:
        return matches[0].strip()
    else:
        return None


def language_by_filename(filename: str) -> str:
    for lang, exts in language_extensions.items():
        for ext in exts:
            if filename.endswith(ext):
                return lang
    return ""


def wrap_code_in_markdown(filename: str = ""):
    language = language_by_filename(filename)

    def _wrap_code_in_markdown(code: str) -> str:
        if language:
            return "```{}\n{}\n```".format(language, code)
        else:
            return "```\n{}\n```".format(code)
    return _wrap_code_in_markdown

def count_tokens(content: str, model_name = "gpt-4"):
    enc = tiktoken.encoding_for_model(model_name)
    tokens = enc.encode(content)
    return len(tokens)
