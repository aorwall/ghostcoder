import difflib
import logging
import os
from pathlib import Path
from typing import List, Optional

import tiktoken
from git import Repo, Tree

from ghostcoder.schema import Folder, File, SaveFilesRequest, DiscardFilesRequest, FileItem
from ghostcoder.utils import language_by_filename, get_extension


class FileRepository:

    def __init__(self,
                 repo_path: Path,
                 use_git: bool = True,
                 repo: Optional[Repo] = None,
                 exclude_dirs: Optional[List[str]] = None):
        super().__init__()
        self.repo_path = repo_path

        if use_git:
            self.repo = repo if repo else Repo(path=repo_path)
            if not self.repo.heads:
                raise Exception("Git repository has no heads, you need to do an initial commit.")
        else:
            self.repo = None

        self.enc = tiktoken.get_encoding("cl100k_base")

        self.exclude_dirs = [".gcoder"]
        if exclude_dirs:
            self.exclude_dirs.extend(exclude_dirs)

    def file_tree(self, file_suffix: str = None) -> Folder:
        return self._generate_file_tree(file_suffix=file_suffix)

    def _generate_file_tree(self, file_suffix: str = None) -> Folder:
        children = self.__generate_file_tree(tree=self.repo.tree(), file_suffix=file_suffix)

        name = self.repo_path.name
        root_dir = Folder(
            name=name,
            path="",
            children=children)

        untracked_files = [item.a_path for item in self.repo.index.diff(None)]
        for path in self.repo.untracked_files + untracked_files:
            self.add_file_to_tree(root_dir, path, False)

        staged_files = [item.a_path for item in self.repo.index.diff("HEAD")]
        for path in staged_files:
            self.add_file_to_tree(root_dir, path, True)

        return root_dir

    def __generate_file_tree(self, tree: Tree, file_suffix: str = None) -> list[File | Folder]:
        if tree is None:
            return []

        nodes = []
        for item in tree:
            if item.type == "blob":
                full_path = os.path.join(self.repo_path, item.path)
                if file_suffix and not item.path.endswith(file_suffix):
                    continue
                if not os.path.exists(full_path):
                    continue
                if self._is_binary(full_path):
                    continue

                language = language_by_filename(item.path)
                nodes.append(File(name=item.name, path=item.path, language=language))
            elif item.type == "tree":
                if item.name in self.exclude_dirs:
                    continue
                folder = Folder(
                    name=item.name,
                    path=item.path,
                    children=self.__generate_file_tree(tree=item))
                nodes.append(folder)
        nodes.sort(key=lambda x: x.name)
        return nodes

    def add_file_to_tree(self, root: Folder, path: str, staged: bool):
        full_path = os.path.join(self.repo_path, path)
        if not os.path.exists(full_path):
            return
        if self._is_binary(full_path):
            return
        language = language_by_filename(path)

        p = Path(path)
        path_parts = p.parts
        current_folder = root

        for part in path_parts[:-1]:
            if part in self.exclude_dirs:
                return

            new_folder_path = str(Path(current_folder.path) / part)
            folder = current_folder.find(new_folder_path)

            if folder is None:
                folder = Folder(name=part, path=new_folder_path, children=[])
                current_folder.children.append(folder)

            current_folder = folder

        file_path = str(p)
        file = current_folder.find(file_path)

        if file is None:
            file = File(path="/" + file_path, language=language, name=path_parts[-1], untracked=not staged, staged=staged)
            current_folder.children.append(file)
        else:
            file.staged = staged
            file.untracked = not staged

    def _new_files(self, dir_path: str, files: list[str]) -> list[File]:
        return [
            File(name=os.path.basename(file), path=os.path.join(dir_path, file), language=language_by_filename(file),
                 untracked=True)
            for file in files]

    def _is_binary(self, file_path: str):
        with open(file_path, 'rb') as file:
            chunk = file.read(8192)
            return b'\0' in chunk

    def as_retriever(self, top_k: int):
        return self._index.as_retriever(similarity_top_k=top_k)

    def get_files_by_suffix(self, file_suffixes: List[str]) -> list[str]:
        return [file.path
                for file in self.file_tree().traverse()
                if any(file.path.endswith(suffix) for suffix in file_suffixes)]

    def get_source_files(self, language: str, directory: str = None, include_test_files: bool = False):
        language_test_suffix = {  # TODO: Move to utils
            "python": "_test.py",
            "java": "Test.java"
        }

        full_dir_path = self.repo_path / directory if directory else self.repo_path

        file_pattern = f"*{get_extension(language)}"
        all_files = list(full_dir_path.rglob(file_pattern))
        file_paths = [
            file
            for file in all_files
            if file.is_file() and not any(part.startswith('.') for part in file.parts)
               and (include_test_files or not (file.name.endswith(language_test_suffix[language])))
        ]

        return [
            FileItem(file_path="/" + str(file.relative_to(self.repo_path)), content=file.read_text())
            for file in file_paths
        ]

    def get_file_content(self, file_path: str) -> Optional[str]:
        if file_path.startswith("/"):
            file_path = file_path[1:]

        if not os.path.exists(os.path.join(self.repo_path, file_path)):
            return None

        with open(os.path.join(self.repo_path, file_path), 'r') as f:
            return f.read()

    def file_tokens(self, file_path: str) -> int:
        file = self.get_file_content(file_path)
        if file is not None:
            tokens = self.enc.encode(file)
            return len(tokens)

    def checkout(self, branch_name: str):
        if branch_name not in self.repo.heads:
            new_branch = self.repo.create_head(branch_name)
        else:
            new_branch = self.repo.heads[branch_name]

        new_branch.checkout()

    def update_file(self, file_path: str, content: str):
        if file_path.startswith("/"):
            file_path = file_path[1:]

        """Write file content to disk and stage the file for commit. """
        full_path = self.repo_path / file_path

        is_new = not full_path.exists()
        untracked = is_new or self.repo is None or file_path in self.repo.untracked_files

        if is_new:
            parent_path = os.path.split(full_path)[0]
            os.makedirs(parent_path, exist_ok=True)
            old_content = []
        else:
            with open(full_path, 'r') as f:
                old_content = f.readlines()

        with open(full_path, 'w') as f:
            f.write(content)

        if untracked:
            file_name = full_path.name
            new_content = content.splitlines(True)
            diff = ''.join(
                difflib.unified_diff(old_content, new_content, fromfile=file_name, tofile=file_name, lineterm='\n'))
        elif self.repo is not None:
            diff = self.repo.git.diff(file_path)
        return diff

    def get_diff(self):
        return self.repo.git.diff('--staged')

    def save_files(self, request: SaveFilesRequest):
        """Stage the files for commit."""

        if request.file_paths:
            for file_path in request.file_paths:
                self.save_file(file_path)
        else:
            self.save_all_files()

    def save_file(self, file_path: str):
        logging.info(f"Staging file {file_path} to commit.")
        self.repo.git.add(file_path)
        self.repo.index.write()

    def save_all_files(self):
        logging.info(f"Stage all files to commit.")
        self.repo.git.add("-A")
        self.repo.index.write()

    def discard_files(self, request: DiscardFilesRequest):
        """Discards the changes by resetting the file to HEAD."""

        if request.file_paths:
            for file_path in request.file_paths:
                self.discard_file(file_path)
        else:
            self.discard_all_files()

    def discard_file(self, file_path: str):
        """Discards the changes by resetting the file to HEAD."""

        if file_path in self.repo.untracked_files:
            logging.info(f"Discard file {file_path} by running clean -df")
            self.repo.git.clean('-df', file_path)
        else:
            logging.info(f"Discard file {file_path} by running reset HEAD")
            self.repo.git.reset("HEAD", file_path)
            self.repo.git.checkout("HEAD", file_path)

    def discard_all_files(self):
        """Discards all changes by resetting the file to HEAD."""

        logging.info(f"Discard all files by running clean -df and reset HEAD")
        self.repo.git.clean('-df')
        self.repo.git.reset("HEAD")
        self.repo.git.checkout("HEAD")

    def commit(self, message: str):
        self.repo.git.commit('-m', message)
