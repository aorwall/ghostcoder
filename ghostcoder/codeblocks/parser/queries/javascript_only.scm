(class_declaration
  (identifier) @identifier
  (class_body
    ("{") @child.first
  )
) @definition.class @root

(field_definition
  (property_identifier) @identifier
  (arrow_function
    parameters: (formal_parameters) @definition.function
    body: [
      (statement_block
        ("{") @child.first
      )
      (expression) @child.first
    ]
  )
) @root
