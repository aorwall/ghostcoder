from ghostcoder.codeblocks.parser.parser import CodeParser


class JavaParser(CodeParser):

    def __init__(self, **kwargs):
        super().__init__("java", **kwargs)
        self.queries = self._build_queries("java.scm")
        self.gpt_queries = []
