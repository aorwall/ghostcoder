from ghostcoder.codeblocks.parser.javascript import JavaScriptParser


class TypeScriptParser(JavaScriptParser):

    def __init__(self, language: str = "typescript", **kwargs):
        super().__init__("tsx", **kwargs)
