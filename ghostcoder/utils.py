import re
from typing import Optional

comment_marker_pattern = r"^[ \t]*(//|#|--|<!--)\s*"

incomplete_code_marker_patterns = [
    r"\(?(rest of|existing code|other code)",
    r"\.\.\.\s*\(?rest of code|existing code|other code\)?\s*",
    r"^\.\.\.\s*"
]

language_extensions = {
    "python": [".py"],
    "java": [".java"],
    "javascript": [".js"],
    "c": [".c"],
    "cpp": [".cpp"],
    "css": [".css", ".scss"],
    "go": [".go"],
    "html": [".html", ".htm"],
    "ruby": [".rb"],
    "swift": [".swift"],
    "kotlin": [".kt"],
    "typescript": [".ts", ".tsx"],
    "json": [".json"],
    "sql": [".sql"],
    "yaml": [".yaml", ".yml"],
    "xml": [".xml"]
}

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
