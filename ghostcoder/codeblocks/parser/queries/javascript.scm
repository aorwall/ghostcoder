(program . (_) @child.first @definition.module) @root

(ERROR) @root @definition.error

(comment) @root @definition.comment

(import_statement) @root @definition.import

(export_statement . [
    ;; ("export") @definition.code
    ;; (export_clause) @definition.code
    (_) @check_child
  ]
) @root

(method_definition
  (property_identifier) @identifier
  (statement_block
    ("{") @child.first
  )
) @root @definition.function

(function_declaration
  (identifier) @identifier
  (statement_block
    ("{") @child.first
  )
) @root @definition.function

(lexical_declaration
  (variable_declarator
    [(identifier) @identifier
     (array_pattern) @identifier]
    [
      (arrow_function
        parameters: (formal_parameters) @definition.function
        body: [
          (statement_block
            ("{") @child.first
          )
          (expression) @child.first
        ]
      )
      (call_expression
        (arguments
          (arrow_function
            (formal_parameters) @definition.function
            (statement_block
              ("{") @child.first
            )
          )
        )
      )
    ]
  )
) @root

(expression_statement
  [
    (assignment_expression
      left: [
        (identifier) @identifier
        (member_expression
          property: (property_identifier) @identifier)
      ]
      right: [
        (arrow_function
          (formal_parameters) @definition.function
          (statement_block
              ("{") @child.first
          )
        )
        (object
          ("{") @child.first
        ) @definition.block
      ]
    )
    (call_expression) @check_child
  ]
) @root

(call_expression
  [
    (identifier) @identifier
    (member_expression
      (identifier) @identifier) @definition.block
  ]
  (arguments
    (arrow_function
      (formal_parameters) @definition.function
      (statement_block
        ("{") @child.first
      )
    )
  )
) @root

(for_statement
  body: [
    (statement_block
      ("{") @child.first
      ("}") @child.last
    ) @definition.statement
    (_) @child.first @definition.statement
  ]
) @root

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

(if_statement
  consequence: [
    (statement_block
      ("{") @child.first
      ("}") @child.last
    )
    (_) @child.first
  ]
) @root @definition.statement

(return_statement [
  (parenthesized_expression
    ("(") @child.first
  )
  ]
) @root @definition.statement

;; TODO: Move to opening/closing code in codeblock?
;; ("{") @definition.block_delimiter @root
;; ("}") @definition.block_delimiter @root
;; ("(") @definition.block_delimiter @root
;; (")") @definition.block_delimiter @root
;; (";") @definition.block_delimiter @root