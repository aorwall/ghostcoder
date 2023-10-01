from ghostcoder.codeblocks.parser.javascript import JavaScriptParser

parser = JavaScriptParser("javascript")


def test_javascript_treesitter_types():
    with open("javascript/treesitter_types.js", "r") as f:
        content = f.read()
    with open("javascript/treesitter_types.txt", "r") as f:
        expected_tree = f.read()

    codeblock = parser.parse(content)
    print(codeblock.to_tree(include_tree_sitter_type=True))

    assert codeblock.to_tree() == expected_tree
    assert codeblock.to_string() == content


def test_javascript_async_function():
    with open("javascript/async_function.js", "r") as f:
        content = f.read()
    with open("javascript/async_function.txt", "r") as f:
        expected_tree = f.read()

    codeblock = parser.parse(content)
    print(codeblock.to_tree(include_tree_sitter_type=False))

    assert codeblock.to_tree() == expected_tree
    assert codeblock.to_string() == content


def test_javascript_object_literal():
    content = """const obj = {
  key: 'value',
  method() {
    return 'This is a method';
  }
};
"""
    codeblock = parser.parse(content)
    print(codeblock.to_tree(include_tree_sitter_type=True))

