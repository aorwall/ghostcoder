from pathlib import Path

import tree_sitter_languages
from tree_sitter_languages import get_language


def print_node(node, indent=""):
    print(indent + node.type)
    for child in node.children:
        print_node(child, indent + " ")

content = """
import java.utils;

public class TreeSitterTypes implements ExampleInterface {

    // This is a single line comment.

    private int value;

    public static String CONSTANT = "foo"

    public TreeSitterTypes(int value) {
        if (value == 5) {
            System.out.println("Five");
        } else if (value == 6) {
            System.out.println("Six");
        } else {
            System.out.println("Other");
        }

        try (AutoCloseable ac = () -> {}) {
            System.out.println("In try");
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            System.out.println("In finally");
        }
    }



}

"""

content_in_bytes = bytes(content, "utf8")
tree_parser = tree_sitter_languages.get_parser("java")
language = get_language("java")

tree = tree_parser.parse(content_in_bytes)

print_node(tree.root_node)

current_node = tree.root_node.children[0]

query_scm = Path("/home/albert/repos/albert/ghostcoder/ghostcoder/codeblocks/parser/queries/java.scm")

t_query = query_scm.read_text()


query = language.query(t_query)
captures = query.captures(tree.root_node)

print(captures)
captures = list(captures)

for node, tag in captures:
    print(tag + ": " + node.type + " \"" + node.text.decode("utf8") + "\"")
