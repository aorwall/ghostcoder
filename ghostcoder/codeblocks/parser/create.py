from typing import Optional

from ghostcoder.codeblocks.parser.java import JavaParser
from ghostcoder.codeblocks.parser.javascript import JavaScriptParser
from ghostcoder.codeblocks.parser.parser import CodeParser
from ghostcoder.codeblocks.parser.python import PythonParser
from ghostcoder.codeblocks.parser.typescript import TypeScriptParser


def create_parser(language: str, **kwargs) -> Optional[CodeParser]:
    #if language == "java":
    #    return JavaParser(**kwargs)
    if language == "python":
        return PythonParser(**kwargs)
    elif language == "typescript":
        return TypeScriptParser("tsx", **kwargs)
    elif language == "javascript":
        return JavaScriptParser(language, **kwargs)
    else:
        raise NotImplementedError(f"Language {language} is not supported.")
