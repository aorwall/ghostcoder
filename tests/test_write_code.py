import logging
import os
import tempfile
from unittest.mock import Mock

import pytest
from langchain.schema import LLMResult
from langchain.schema.language_model import BaseLanguageModel

from ghostcoder import FileRepository
from ghostcoder.actions.write_code.base import  WriteCodeAction
from ghostcoder.llm import LLMWrapper
from ghostcoder.schema import Message, TextItem, FileItem, Stats


@pytest.fixture
def mock_llm_wrapper():
    return Mock(spec=LLMWrapper)


def test_two_code_blocks(mock_llm_wrapper):
    with open("resources/two_code_blocks/response.txt", 'r') as f:
        response = f.read()

    with tempfile.TemporaryDirectory() as tmpdir:
        repository = FileRepository(repo_path=tmpdir, use_git=False)
        full_path = tmpdir + "/linked_list.py"
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open("resources/two_code_blocks/linked_list.py", 'r') as f:
            content = f.read()
            with open(full_path, 'w') as nf:
                nf.write(content)

        mock_llm_wrapper.generate.return_value = response, Stats()

        prompt = WriteCodeAction(llm=mock_llm_wrapper, repository=repository)

        response = prompt.execute(Message(
            sender="Human",
            items=[TextItem(text=""), FileItem(file_path="linked_list.py")]))

        with open("resources/two_code_blocks/expected.py", 'r') as f:
            expected = f.read()
            with open(full_path, 'r') as nf:
                content = nf.read()
                assert content == expected


def test_no_file_path_and_hallucinations(mock_llm_wrapper):
    with open("resources/no_file_path_and_hallucinations/response.txt", 'r') as f:
        response = f.read()

    with tempfile.TemporaryDirectory() as tmpdir:
        repository = FileRepository(repo_path=tmpdir, use_git=False)
        full_path = tmpdir + "/series.py"
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open("resources/no_file_path_and_hallucinations/series.py", 'r') as f:
            content = f.read()
            with open(full_path, 'w') as nf:
                nf.write(content)

        mock_llm_wrapper.generate.return_value = response, Stats()

        prompt = WriteCodeAction(llm=mock_llm_wrapper, repository=repository)

        response = prompt.execute(Message(
            sender="Human",
            items=[TextItem(text=""), FileItem(file_path="series.py")]))

        with open("resources/no_file_path_and_hallucinations/expected.py", 'r') as f:
            expected = f.read()
            with open(full_path, 'r') as nf:
                content = nf.read()
                assert content == expected


def test_square_bracket_fence(mock_llm_wrapper):
    verify_execute(mock_llm_wrapper, "llama_fence", "roman_numerals.py")




def verify_execute(mock_llm, test_dir, code_file):
    with open(f"resources/{test_dir}/response.txt", 'r') as f:
        response = f.read()

    with tempfile.TemporaryDirectory() as tmpdir:
        repository = FileRepository(repo_path=tmpdir, use_git=False)
        full_path = tmpdir + "/" + code_file
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(f"resources//{test_dir}/{code_file}", 'r') as f:
            content = f.read()
            with open(full_path, 'w') as nf:
                nf.write(content)

        mock_llm.generate.return_value = response, Stats()

        prompt = WriteCodeAction(llm=mock_llm, repository=repository)

        response = prompt.execute(Message(
            sender="Human",
            items=[TextItem(text=""), FileItem(file_path=code_file)]))

        with open(f"resources/{test_dir}/expected.py", 'r') as f:
            expected = f.read()
            with open(full_path, 'r') as nf:
                content = nf.read()
                assert content == expected
