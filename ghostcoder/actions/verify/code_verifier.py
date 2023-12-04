import logging
import os
from itertools import groupby
from pathlib import Path
from typing import List

from ghostcoder.codeblocks import CodeBlockType, CodeBlock, create_parser
from ghostcoder.filerepository import FileRepository
from ghostcoder.schema import Message, TextItem, VerificationFailureItem, FileItem
from ghostcoder.test_tools import TestTool, JavaMvnUnit5TestTool
from ghostcoder.test_tools.verify_python_pytest import PythonPytestTestTool


class CodeVerifier:

    def __init__(self,
                 repository: FileRepository,
                 test_tool: TestTool = None,
                 callback=None,  # FIXME
                 language: str = "python"):
        self.repository = repository

        if test_tool:
            self.test_tool = test_tool
        elif language == "java":
            self.test_tool = JavaMvnUnit5TestTool(current_dir=self.repository.repo_path, callback=callback)
        elif language == "python":
            self.test_tool = PythonPytestTestTool(current_dir=self.repository.repo_path, callback=callback)
        else:
            raise Exception(f"Unsupported language: {language}")

    def execute(self) -> Message:
        # TODO: Figure out language to use

        # TODO: Do static code analysis and try to compile before testing

        verification_result = self.test_tool.run_tests()

        result_input = TextItem(text=verification_result.message)

        if not verification_result.success:
            test_files = self.get_test_files(failures=verification_result.failures)
            return Message(
                sender="Ghostcoder",
                items=[result_input] + verification_result.failures + test_files,
            )
        else:
            return Message(
                sender="Ghostcoder",
                items=[result_input],
            )

    def get_test_files(self, failures: List[VerificationFailureItem], language: str = "python"):
        parser = create_parser(language=language)
        test_files = []

        sorted_failures = sorted(failures, key=lambda x: x.test_file)

        for test_file_path, grouped_failures in groupby(sorted_failures, key=lambda x: x.test_file):
            if test_file_path is None:
                continue

            file_contents = self.repository.get_file_content(test_file_path)
            if not file_contents:
                logging.warning(f"Test file not found: {test_file_path}")
                continue

            test_file_block = parser.parse(file_contents)

            keep_blocks = []

            for failure in grouped_failures:
                if failure.test_method and not failure.test_code:
                    keep_blocks.append(CodeBlock(content=failure.test_method + "(", type=CodeBlockType.FUNCTION))

            trimmed_block = test_file_block.trim(keep_blocks=keep_blocks, keep_level=1,
                                                 comment_out_str=" ... rest of the code ... ")

            if keep_blocks:
                if language == "python":
                    keep_blocks.append(
                        CodeBlock(content="setUp(", type=CodeBlockType.FUNCTION),  # TODO: Not only python unittest
                    )

                test_files.append(FileItem(file_path=test_file_path, content=trimmed_block.to_string(), readonly=True))

        return test_files


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    path = os.getcwd()
    repository = FileRepository(repo_path=Path(path), use_git=False)
    verifier = CodeVerifier(repository=repository, language="java")

    message = verifier.execute()
    print(message.to_prompt())
