from ghostcoder.codeblocks.parser.typescript import TypeScriptParser


def test_typescript_treesitter_types():
    with open("typescript/treesitter_types.ts", "r") as f:
        content = f.read()
    with open("typescript/treesitter_types_expected.txt", "r") as f:
        expected_tree = f.read()

    parser = TypeScriptParser()
    codeblock = parser.parse(content)

    print(codeblock.to_tree(include_tree_sitter_type=True))

    assert codeblock.to_tree() == expected_tree


def test_react_tsx():
    with open("typescript/react_component.tsx", "r") as f:
        content = f.read()
    with open("typescript/react_component_expected.txt", "r") as f:
        expected_tree = f.read()

    parser = TypeScriptParser("tsx")
    codeblock = parser.parse(content)

    print(codeblock.to_tree(include_tree_sitter_type=True))

    assert codeblock.to_tree() == expected_tree
    assert codeblock.to_string() == content


def test_lexical_declaration():
    parser = TypeScriptParser()
    codeblock = parser.parse("let myVariable: number;")
    assert codeblock.to_tree() == """ 0 module ``
  1 code `let myVariable: number`
   2 block_delimiter `;`
"""

    codeblock_assigned = parser.parse("let myVariable: number = 5;")
    assert codeblock_assigned.to_tree() == """ 0 module ``
  1 code `let myVariable: number`
   2 code `=`
   2 code `5`
   2 block_delimiter `;`
"""