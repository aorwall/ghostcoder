import logging
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest
from langchain.schema import LLMResult
from langchain.schema.language_model import BaseLanguageModel

from ghostcoder import FileRepository
from ghostcoder.actions.write_code.base import CodeWriter, extract_response_parts, CodeBlock
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


# TODO: Might be false positive
def test_crlf_line_breaks(mock_llm_wrapper):
    verify_execute(mock_llm_wrapper, "crlf_line_breaks", "hello_world.py")


def test_not_similar_blocks(mock_llm_wrapper):
    verify_execute(mock_llm_wrapper, "not_similar_blocks", "precision_cut.py")

def test_new_file_many_blocks(mock_llm_wrapper):
    verify_execute(mock_llm_wrapper, "new_file_many_blocks", "battleship.py")


def test_expect_one_file(mock_llm_wrapper):
    prompt = CodeWriter(llm=mock_llm_wrapper, expect_one_file=True)
    verify_execute(mock_llm_wrapper, "expect_one_file", "hello_world.py", prompt=prompt)

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
            with open(full_path, "w") as nf:
                nf.write(content)

        mock_llm.predict.side_effect = [
            response,
            response2
        ]

        prompt = CodeWriter(llm=PhindLLMWrapper(mock_llm), repository=repository, auto_mode=True)

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
        full_path = tmpdir + "/" + "hello_world.py"
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(f"resources/not_closed_code_block/hello_world.py", 'r') as f:
            content = f.read()
            with open(full_path, 'w') as nf:
                nf.write(content)

        mock_llm.predict.side_effect = [
            response,
            response2
        ]

        prompt = CodeWriter(llm=PhindLLMWrapper(mock_llm), repository=repository, auto_mode=True)

        response = prompt.execute(Message(
            sender="Human",
            items=[TextItem(text=""), FileItem(file_path="hello_world.py")]))

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

        prompt = CodeWriter(llm=mock_llm_wrapper, repository=repository, auto_mode=True)

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



def verify_execute(mock_llm, test_dir, code_file, prompt: CodeWriter = None):
    with open(f"resources/{test_dir}/response.txt", 'r') as f:
        response = f.read()

    with tempfile.TemporaryDirectory() as tmpdir:
        repository = FileRepository(repo_path=Path(tmpdir), use_git=False)
        full_path = tmpdir + "/" + code_file
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        with open(f"resources/{test_dir}/{code_file}", 'r') as f:
            content = f.read()
            with open(full_path, 'w') as nf:
                nf.write(content)

        mock_llm.generate.return_value = response, Stats()

        if prompt is None:
            prompt = CodeWriter(llm=mock_llm, repository=repository)
        else:
            prompt.repository = repository

        response = prompt.execute([Message(
            sender="Human",
            items=[TextItem(text=""), FileItem(file_path=code_file)])])

        with open(f"resources/{test_dir}/expected.py", 'r') as f:
            expected = f.read()
            with open(full_path, 'r') as nf:
                content = nf.read()
                assert content == expected


def test_extract_response_parts_code_block_with_file_path():
    response = """
Here's the updated code. 

file.py
```python
def my_function():
    print("Hello World")
```

I hope this helps!
"""

    verify_extract_response_parts(response, [
        "Here's the updated code.",
        CodeBlock(content="def my_function():\n    print(\"Hello World\")", file_path="file.py", language="python"),
        "I hope this helps!"
    ])


def test_extract_response_parts_code_block_with_file_path_and_dir():
    response = """
Here's the updated code. 

path/to/file.py
```python
def my_function():
    print("Hello World")
```
"""

    verify_extract_response_parts(response, [
        "Here's the updated code.",
        CodeBlock(file_path="path/to/file.py", content="def my_function():\n    print(\"Hello World\")", language="python")
    ])


def test_extract_response_parts_code_block_with_no_language():
    response = """
Here's the updated code. 

file.py
```
def my_function():
    print("Hello World")
```
"""

    verify_extract_response_parts(response, [
        "Here's the updated code.",
        CodeBlock(content="def my_function():\n    print(\"Hello World\")", file_path="file.py")
    ])


def test_extract_response_parts_code_block_line_breaks_after_file():
    response = """
file.py

```
def my_function():
    print("Hello World")
```
"""

    verify_extract_response_parts(response, [
        CodeBlock(content="def my_function():\n    print(\"Hello World\")", file_path="file.py")
    ])


def test_extract_response_parts_code_block():
    response = """
Here's the updated code. 

```python
def my_function():
    print("Hello World")
```
"""

    verify_extract_response_parts(response, [
        "Here's the updated code.",
        CodeBlock(content="def my_function():\n    print(\"Hello World\")", language="python")
    ])

def test_extract_response_parts_code_block_with_file_path_in_sentence():
    response = """
I updated `file.py` with the following code:

```python
def my_function():
    print("Hello World")
```
"""

    verify_extract_response_parts(response, [
        "I updated `file.py` with the following code:",
        CodeBlock(file_path="file.py", content="def my_function():\n    print(\"Hello World\")", language="python")
    ])

def test_extract_response_parts_code_block_with_backticks_word():
    response = """
I use `python` in the following code:

```python
def my_function():
    print("Hello World")
```
"""

    verify_extract_response_parts(response, [
        "I use `python` in the following code:",
        CodeBlock(content="def my_function():\n    print(\"Hello World\")", language="python")
    ])

def test_extract_response_parts_code_block_with_file_path_and_dir_in_sentence():
    response = """
I updated `path/to/file.py` with the following code:

```python
def my_function():
    print("Hello World")
```"""

    verify_extract_response_parts(response, [
        "I updated `path/to/file.py` with the following code:",
        CodeBlock(file_path="path/to/file.py", content="def my_function():\n    print(\"Hello World\")", language="python")
    ])

def test_extract_response_parts_code_block_two_files_and_a_method_call_mentioned():
    response = """Another file `another.py` was updated. And here's the updated code for `file.py`. If it was called from a class it would be called like this: `my_class.my_function()`.

```python
def my_function():
    print("Hello World")
```
"""

    verify_extract_response_parts(response, [
        "Another file `another.py` was updated. And here's the updated code for `file.py`. If it was called from a class it would be called like this: `my_class.my_function()`.",
        CodeBlock(file_path="file.py", content="def my_function():\n    print(\"Hello World\")", language="python")
    ])


def test_extract_response_parts_code_block_with_backticks_file_path():
    response = """
`file.py`
```python
def my_function():
    print("Hello World")
```
"""

    verify_extract_response_parts(response, [
        CodeBlock(file_path="file.py", content="def my_function():\n    print(\"Hello World\")", language="python")
    ])


def test_extract_response_parts_not_closed_code_block():
    response = """Here's the updated code.

```python
def my_function():
    print("Hello World")"""

    verify_extract_response_parts(response, [
        response
    ])

def test_extract_response_parts_quoted_file_path():
    response = """"file.py"
```python
def my_function():
    print("Hello World")
```"""

    verify_extract_response_parts(response, [
        CodeBlock(file_path="file.py", content="def my_function():\n    print(\"Hello World\")", language="python")
    ])

def verify_extract_response_parts(response, expected):
    blocks = extract_response_parts(response)

    assert len(blocks) == len(expected)
    for i in range(len(blocks)):
        assert blocks[i] == expected[i]