;; 1
(program . (_) @child.first @definition.module) @root

;; 2
(ERROR) @root @definition.error

;; 3
(comment) @root @definition.comment

;; 4
(import_statement
  ("import")
  (import_clause
    (
      [
        (identifier) @reference.identifier
        (named_imports
          (
            (import_specifier
              . [
                (
                  (identifier) @reference.identifier
                  ("as")
                  (identifier) ;; TODO: Support alias
                )
                (identifier) @reference.identifier
              ] .
            )
            (",")?
          )*
        )
        (namespace_import
           (identifier) @reference.alias
        )
      ]
      (",")?
    )*
  )
  ("from")
  (string
      [("\"")("'")]
      (_) @reference.module
      [("\"")("'")]
  )
) @root @definition.import

;; 5
(export_statement . [
    ;; ("export") @definition.code
    ;; (export_clause) @definition.code
    (_) @check_child
  ]
) @root

;; 6
(method_definition
  (property_identifier) @identifier
  (formal_parameters
    ("(")
    (
      (identifier) @parameter.identifier
      (",")?
    )*
    (")")
    )?
  (statement_block
    ("{") @child.first
  )
) @root @definition.function

;; 7
(function_declaration
  (identifier) @identifier
  (statement_block
    ("{") @child.first
  )
) @root @definition.function

;; 8
(lexical_declaration
  (variable_declarator
    name: [
      (identifier) @identifier
      ;; (array_pattern) @identifier TODO: Support more than one identifier
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
        ]
      )
      (call_expression) @child.first @definition.assignment
    ]
  )
) @root

;; 9
(lexical_declaration
  (variable_declarator
    name: [
      (identifier) @identifier
      (array_pattern) ;; TODO: Support more than one identifier
      (object_pattern
        (shorthand_property_identifier_pattern) @identifier
      )
    ]
    value: (_) @child.first @definition.assignment
  )
) @root

;; 10
(expression_statement
  (_) @check_child
) @root

;; 11
(await_expression
  ("await")
  [
    (assignment_expression) @check_child
    (call_expression) @check_child
  ]
) @root

;; 12
(assignment_expression
  left: [
    ;; TODO: Not perfect as is can result in duplicated identifications
    (identifier) @identifier
    (member_expression) @identifier
  ]
  right: [
    (arrow_function
      (formal_parameters
        ("(")
        (
          (identifier) @parameter.identifier
          (",")?
        )*
        (")")
      ) @definition.function
      body: (statement_block
          ("{") @child.first
      )
    )
  ]?
) @root

;; 13
(assignment_expression
  left: [
    (identifier) @reference.identifier
    (member_expression) @reference.identifier
  ]
  right: [
    (identifier) @reference.identifier @reference.dependency @definition.assignment
    (member_expression) @reference.identifier @reference.dependency @definition.assignment
    (object
      ("{") @child.first
    ) @definition.assignment
  ]?
) @root

;; 14 Handle Jest test suites
(call_expression
  ((identifier) @function-name
    (#match? @function-name "^(describe)$")) @definition.test_suite
  (arguments
    ("(") @baaa
    (string
      [("\"")("'")]
      (_) @identifier
      [("\"")("'")]
    )
    (",")
    (arrow_function
      body: (statement_block
        ("{") @child.first
      )
    )
  )
) @root

;; 15 Handle Jest test cases
(call_expression
  ((identifier) @function-name
    (#match? @function-name "^(it|fit|xit|test|xtest)$")) @definition.test_case
  (arguments
    ("(")
    (string
      [("\"")("'")]
      (_) @identifier
      [("\"")("'")]
    )
    (",")
    (arrow_function
      body: (statement_block
        ("{") @child.first
      )
    )
  )
) @root

;; 17
(call_expression
  [
    (identifier) @reference.utilizes
    (member_expression) @reference.utilizes
  ]
  (arguments
    [
      (arrow_function
        (formal_parameters
          ("(")
          (
            (identifier) @parameter.identifier
            (",")?
          )*
          (")")
        ) @definition.call
        body: [
          (statement_block
            ("{") @child.first
          )
          (parenthesized_expression
            ("(") @child.first
          )
        ]
      )
      (
        ("(")
        (
          [
            (identifier) @reference.uses
            (member_expression) @reference.uses
            (object
              ("{") @child.first
            )
          ] @definition.call
        (",")?
        )*
        (")")
      )
    ]
  )
) @root

;; 18
(call_expression
  [
    (identifier) @reference.utilizes
    (member_expression) @reference.utilizes
  ]
  (arguments
    [
      (arrow_function
        (formal_parameters
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
          (parenthesized_expression
            ("(") @child.first
          )
        ]
      )
      (
        ("(")
        (
          [
            (identifier) @reference.uses
            (member_expression) @reference.uses
            (call_expression
              [
                (identifier) @reference.utilizes
                (member_expression) @reference.utilizes
              ]
            )
          ] @definition.call
        (",")?
        )*
        (")")
      )
    ]
  )
) @root

;; 19
(call_expression
  [
    (identifier) @reference.utilizes
    (member_expression) @reference.utilizes
  ]
  (arguments
    . ("(") @child.first
    . (_) @definition.call
    (")") @child.last .
  )
) @root

;; 19
(for_statement
  body: [
    (statement_block
      ("{") @child.first
      ("}") @child.last
    ) @definition.statement
    (_) @child.first @definition.statement
  ]
) @root

;; 20
(switch_statement
  body: (switch_body ("{") @child.first)
)  @root @definition.statement

(else_clause
  ("else") @else2
  [
    (statement_block
      ("{") @child.first
      ("}") @child.last
    )
    (if_statement) @check_child
    (_) @child.first
  ]
)  @root @definition.statement @else

;; 21
(if_statement
  consequence: [
    (statement_block
      ("{") @child.first
      ("}") @child.last
    )
    (_) @child.first
  ]
) @root @definition.statement

;; 22
(return_statement
  [
    (parenthesized_expression
      ("(") @child.first
    )
    (object
      (shorthand_property_identifier) @reference.provides
    )
  ]
) @root @definition.statement

;; 23
(return_statement
  . (_) @child.first
) @root @definition.statement

;; 24
(pair
  (property_identifier) @identifier
  (arrow_function
    (formal_parameters) @definition.function @parse_child
    body: [
      (statement_block
        ("{") @child.first
      )
      (parenthesized_expression
        ("(") @child.first
      )
    ]
  )
) @root

(pair
  (property_identifier) @identifier
  (":")
  (_) @child.first  @definition.assignment
) @root

;; 25
(template_string
  (template_substitution
    [
    (identifier) @reference.identifier @reference.dependency
    (member_expression) @reference.identifier @reference.dependency
   ]
  )
) @root @definition.code

;; 26
(jsx_self_closing_element
  (identifier) @reference.identifier @definition.block
  .
  (jsx_attribute)? @child.first
) @root

;; 27
(jsx_fragment
  . ("<")
  . (">")
  . (_) @child.first  @definition.block
) @root


;; 29
(jsx_element
  (jsx_opening_element
    (identifier) @reference.identifier
  )
  (_) @child.first  @definition.block
  (jsx_closing_element) @child.last
) @root

;; 30
(jsx_attribute
  (property_identifier) @identifier
  ("=")
  (jsx_expression
    ("{")
    (arrow_function) @parse_child @definition.function
    ("}")
  )
) @root

(jsx_attribute
  (property_identifier) @identifier
  (
    ("=") @definition.assignment
    (jsx_expression)? @child.first
  )?
) @root

(jsx_expression
  ("{")
  [
    (identifier) @reference.identifier
    (member_expression) @reference.identifier
    (arrow_function) @child.first
    (jsx_element) @child.first
    (call_expression) @child.first
  ]
  ("}")
) @root @definition.block

(jsx_closing_element) @root @definition.block_delimiter

;; TODO: Move to opening/closing code in codeblock?
;; ("{") @definition.block_delimiter @root
;; ("}") @definition.block_delimiter @root
;; ("(") @definition.block_delimiter @root
;; (")") @definition.block_delimiter @root
;; (";") @definition.block_delimiter @root

(object
  ("{") @child.first @definition.block
) @root

;; 31
(arrow_function
  parameters: (formal_parameters) @parse_child @definition.function
  body: [
    (statement_block
      ("{") @child.first
    )
    (parenthesized_expression
      ("(") @child.first
    )
    (expression) @child.first
  ]
) @root

(formal_parameters
  ("(")
  (
    (identifier) @parameter.identifier
    (",")?
  )*
  (")")
)