import logging
from pathlib import Path
from typing import Optional, List

from git import Repo

from ghostcoder import FileRepository
from ghostcoder.codeblocks import create_parser, CodeBlockType
from ghostcoder.schema import CodeFile, File
from ghostcoder.utils import language_by_filename, get_purpose_by_filepath

logger = logging.getLogger(__name__)

class CodeRepository(FileRepository):

    def __init__(self,
                 repo_path: Path,
                 use_git: bool = True,
                 exclude_dirs: Optional[List[str]] = None):
        super().__init__(repo_path=repo_path, use_git=use_git, exclude_dirs=exclude_dirs)
        self.parsers = {}

    def _build_file(self, file_path: str, staged: bool = False) -> File:
        language = language_by_filename(file_path)
        if language:
            purpose = get_purpose_by_filepath(language, file_path)
            parser = self._get_parser(language)
            code_blocks = []
            if parser:
                contents = self.get_file_content(file_path)
                if contents:
                    code_block = parser.parse(file_path)
                    if code_block and code_block.type == CodeBlockType.MODULE:
                        code_blocks = code_block.code_blocks
                    elif code_block:
                        code_blocks = [code_block]
            return CodeFile(
                path=file_path,
                staged=staged,
                language=language,
                purpose=purpose,
                code_blocks=code_blocks
            )
        else:
            return super()._build_file(file_path, staged)

    def _get_parser(self, language: str):
        if language not in self.parsers:
            try:
                self.parsers[language] = create_parser(language)
            except Exception as e:
                logger.error(f"Failed to create parser for {language}: {e}")
                self.parsers[language] = None
        elif self.parsers[language] is None:
            return None

        return self.parsers[language]

