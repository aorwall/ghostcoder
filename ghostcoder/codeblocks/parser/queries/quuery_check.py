from pathlib import Path

import tree_sitter_languages
from tree_sitter_languages import get_language


def print_node(node, indent=""):
    print(indent + node.type)
    for child in node.children:
        print_node(child, indent + " ")

content = """class Foo extends Component {
  
  ...
  
  foo = () => {
    return (
      "foo"
    );
  };
};
"""

content_in_bytes = bytes(content, "utf8")
tree_parser = tree_sitter_languages.get_parser("javascript")
language = get_language("javascript")

tree = tree_parser.parse(content_in_bytes)

print_node(tree.root_node)

current_node = tree.root_node.children[0]

query_scm = Path("/home/albert/repos/albert/ghostcoder/ghostcoder/codeblocks/parser/queries/javascript_gpt.scm")

t_query = query_scm.read_text()


query = language.query(t_query)
captures = query.captures(current_node)

print(captures)
captures = list(captures)

for node, tag in captures:
    print(tag + ": " + node.type + " \"" + node.text.decode("utf8") + "\"")
