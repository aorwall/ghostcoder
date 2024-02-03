import re
from typing import Optional

import tiktoken

comment_marker_pattern = r"^[ \t]*(//|#|--|<!--)\s*"

incomplete_code_marker_patterns = [
    r"\(?(rest of|existing code|other code)",
    r"\.\.\.\s*\(?rest of code|existing code|other code\)?\s*",
    r"^\.\.\.\s*"
]

file_extension_mapping = {
    "sh": "bash",
    "c": "c",
    "cs": "c-sharp",
    "lisp": "commonlisp",
    "cpp": "cpp",
    "css": "css",
    "dot": "dot",
    "el": "elisp",
    "ex": "elixir",
    "elm": "elm",
    "hbs": "embedded-template",
    "erl": "erlang",
    "f": "fixed-form-fortran",
    "f90": "fortran",
    "go": "go",
    "mod": "go-mod",
    "hack": "hack",
    "hs": "haskell",
    "hcl": "hcl",
    "html": "html",
    "java": "java",
    "js": "javascript",
    "jsx": "javascript",
    #"jsdoc": "jsdoc",
    #"json": "json",
    "jl": "julia",
    "kt": "kotlin",
    "lua": "lua",
    "mk": "make",
    "m": "objc",
    "ml": "ocaml/ocaml",
    "pl": "perl",
    "php": "php",
    "py": "python",
    "ql": "ql",
    "r": "r",
    #"regex": "regex",
    "rst": "rst",
    "rb": "ruby",
    "rs": "rust",
    "scala": "scala",
    "sql": "sql",
    "sqlite": "sqlite",
    #"toml": "toml",
    "tf": "hcl",
    "tsq": "tsq",
    "ts": "typescript",
    "tsx": "typescript",
    #"yaml": "yaml"
}


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

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'

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
    if filename:
        extension = filename.split(".")[-1]
        return file_extension_mapping.get(extension)
    else:
        return None


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


def remove_unnecessary_spaces(content: str):
    words = content.split()
    return ' '.join(words)


PATTERN = re.compile(r"\s*([=+\-*/<>{}();,])\s*")

def remove_unnecessary_spaces_in_code(code: str) -> str:
    code = remove_unnecessary_spaces(code)

    def replacer(match: re.Match[str]) -> str:
        return match.group(1)

    return re.sub(PATTERN, replacer, code)
