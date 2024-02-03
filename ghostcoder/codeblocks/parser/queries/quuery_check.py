from pathlib import Path

import tree_sitter_languages
from tree_sitter_languages import get_language


def print_node(node, indent=""):
    print(indent + node.type)
    for child in node.children:
        print_node(child, indent + " ")

def run_query(language, query, content):
    content_in_bytes = bytes(content, "utf8")
    tree_parser = tree_sitter_languages.get_parser(language)
    language = get_language(language)

    tree = tree_parser.parse(content_in_bytes)

    print_node(tree.root_node)

    current_node = tree.root_node.children[0]

    query = language.query(query)
    captures = query.captures(tree.root_node)

    print(captures)
    captures = list(captures)

    for node, tag in captures:
        print(tag + ": " + str(node) + " \"" + node.text.decode("utf8") + "\"")

content = """class FooForm extends Component {
    isContactFormValid = () =>
        isValidPhone(this.state.mobileNumber) && this.validEmail(this.state.email);
}"""

content = """
export const useDeleteUser = ({ config }: UseDeleteUserOptions = {}) => {
  const { addNotification } = useNotificationStore();

  return useMutation({
    onMutate: async (deletedUser) => {
      await queryClient.cancelQueries('users');
      return { previousUsers };
    }
  });
};"""


t_query = """
(lexical_declaration
  (variable_declarator
    name: [
      (identifier) @identifier
      (array_pattern) @identifier
    ]
    value: [
      (arrow_function
        parameters: (formal_parameters
          ("(")
          (
            (identifier) @parameter.identifier
            (",")?
          )*
          (")")
        ) @definition.function
        body: [
          (statement_block
            ("{") @child.first
          )
          (expression) @child.first
          (parenthesized_expression
            ("(") @child.first
          )
        ]
      )
      (call_expression
        (arguments
          (arrow_function
            (formal_parameters
              ("(")
              (
                (identifier) @reference.identifier
                (",")?
              )*
              (")")
            )?
            [
              (statement_block
                ("{") @child.first @definition.block
              )
              (parenthesized_expression
                ("(") @child.first  @definition.block
              )
            ]
          )
        )
      )
    ]
  )
) @root
"""

content = """
export const getUsers = (): Promise<User[]> => {
  return axios.get(`/users`);
};
"""

query_scm = Path("/home/albert/repos/albert/ghostcoder/ghostcoder/codeblocks/parser/queries/javascript.scm")
t_query = query_scm.read_text()


run_query("tsx", t_query, content)