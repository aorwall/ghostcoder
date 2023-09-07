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
from ghostcoder.llm.phind import PhindLLMWrapper
from ghostcoder.schema import Message, TextItem, FileItem, Stats


@pytest.fixture
def mock_llm_wrapper():
    return Mock(spec=LLMWrapper)

@pytest.fixture
def mock_llm():
    return Mock(spec=BaseLanguageModel)


def test_two_code_blocks(mock_llm_wrapper):
    verify_execute(mock_llm_wrapper, "two_code_blocks", "linked_list.py")


def test_no_file_path(mock_llm_wrapper):
    verify_execute(mock_llm_wrapper, "no_file_path", "roman_numerals.py")


def test_no_file_path_and_hallucinations(mock_llm_wrapper):
    verify_execute(mock_llm_wrapper, "no_file_path_and_hallucinations", "series.py")


def test_square_bracket_fence(mock_llm_wrapper):
    verify_execute(mock_llm_wrapper, "llama_fence", "roman_numerals.py")


def test_file_path_with_line_break(mock_llm_wrapper):
    verify_execute(mock_llm_wrapper, "file_path_with_line_break", "diamond.py")


def test_crlf_line_breaks(mock_llm_wrapper):
    verify_execute(mock_llm_wrapper, "crlf_line_breaks", "sum_of_multiples.py")


def test_not_similar_blocks(mock_llm_wrapper):
    verify_execute(mock_llm_wrapper, "not_similar_blocks", "precision_cut.py")


def test_updated_content_is_invalid(mock_llm):
    with open(f"resources/invalid_content/response.txt", 'r') as f:
        response = f.read()

    with open(f"resources/invalid_content/response2.txt", 'r') as f:
        response2 = f.read()

    with tempfile.TemporaryDirectory() as tmpdir:
        repository = FileRepository(repo_path=tmpdir, use_git=False)
        full_path = tmpdir + "/" + "proverb.py"
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(f"resources/invalid_content/proverb.py", 'r') as f:
            content = f.read()
            with open(full_path, 'w') as nf:
                nf.write(content)

        mock_llm.predict.side_effect = [
            response,
            response2
        ]

        prompt = WriteCodeAction(llm=PhindLLMWrapper(mock_llm), repository=repository, auto_mode=True)

        response = prompt.execute(Message(
            sender="Human",
            items=[TextItem(text=""), FileItem(file_path="proverb.py")]))

        first_call_args = mock_llm.predict.call_args_list[0]
        assert mock_llm.predict.call_count == 2

        print(first_call_args)

        with open(f"resources/invalid_content/expected.py", 'r') as f:
            expected = f.read()
            with open(full_path, 'r') as nf:
                content = nf.read()
                assert content == expected


def test_not_closed_code_block(mock_llm):
    with open(f"resources/not_closed_code_block/response.txt", 'r') as f:
        response = f.read()
    with open(f"resources/not_closed_code_block/response2.txt", 'r') as f:
        response2 = f.read()

    with tempfile.TemporaryDirectory() as tmpdir:
        repository = FileRepository(repo_path=tmpdir, use_git=False)
        full_path = tmpdir + "/" + "circular_buffer.py"
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(f"resources/not_closed_code_block/circular_buffer.py", 'r') as f:
            content = f.read()
            with open(full_path, 'w') as nf:
                nf.write(content)

        mock_llm.predict.side_effect = [
            response,
            response2
        ]

        prompt = WriteCodeAction(llm=PhindLLMWrapper(mock_llm), repository=repository, auto_mode=True)

        response = prompt.execute(Message(
            sender="Human",
            items=[TextItem(text=""), FileItem(file_path="circular_buffer.py")]))

        first_call_args = mock_llm.predict.call_args_list[0]
        assert mock_llm.predict.call_count == 2

        print(first_call_args)

        with open(f"resources/not_closed_code_block/expected.py", 'r') as f:
            expected = f.read()
            with open(full_path, 'r') as nf:
                content = nf.read()
                assert content == expected

def test_update_with_non_code_block_in_input(mock_llm_wrapper): # and test merge...
    with open(f"resources/non_code_file_in_input/response.txt", 'r') as f:
        response = f.read()

    with tempfile.TemporaryDirectory() as tmpdir:
        repository = FileRepository(repo_path=tmpdir, use_git=False)
        instructions_temp_path = tmpdir + "/instructions.md"
        code_temp_path = tmpdir + "/precision_cut_test.py"
        os.makedirs(os.path.dirname(instructions_temp_path), exist_ok=True)

        with open(f"resources/non_code_file_in_input/instructions.md", 'r') as f:
            content = f.read()
            with open(instructions_temp_path, 'w') as nf:
                nf.write(content)

        with open(f"resources/non_code_file_in_input/precision_cut_test.py", 'r') as f:
            content = f.read()
            with open(code_temp_path, 'w') as nf:
                nf.write(content)

        mock_llm_wrapper.generate.return_value = response, Stats()

        prompt = WriteCodeAction(llm=mock_llm_wrapper, repository=repository, auto_mode=True)

        response = prompt.execute(Message(
            sender="Human",
            items=[
                FileItem(file_path="instructions.md"),
                FileItem(file_path="precision_cut_test.py")
            ]))

        # TODO: Verify response

        with open(f"resources/non_code_file_in_input/expected.py", 'r') as f:
            expected = f.read()
            with open(code_temp_path, 'r') as nf:
                content = nf.read()
                assert content == expected



def verify_execute(mock_llm, test_dir, code_file):
    with open(f"resources/{test_dir}/response.txt", 'r') as f:
        response = f.read()

    with tempfile.TemporaryDirectory() as tmpdir:
        repository = FileRepository(repo_path=tmpdir, use_git=False)
        full_path = tmpdir + "/" + code_file
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(f"resources/{test_dir}/{code_file}", 'r') as f:
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
