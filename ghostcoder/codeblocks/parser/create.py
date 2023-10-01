from typing import Optional

from ghostcoder.codeblocks.parser.java import JavaParser
from ghostcoder.codeblocks.parser.parser import CodeParser
from ghostcoder.codeblocks.parser.python import PythonParser
from ghostcoder.codeblocks.parser.typescript import TypeScriptParser


def create_parser(language: str) -> Optional[CodeParser]:
    if language == "java":
        return JavaParser()
    elif language == "python":
        return PythonParser()
    elif language == "typescript" or language == "tsx":
        return TypeScriptParser(language)
    else:
        return CodeParser(language)
