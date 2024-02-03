(class_declaration
  (identifier) @identifier
  (class_heritage
    ("extends")
    (identifier) @reference.identifier @reference.type
  )?
  (class_body
    ("{") @child.first
  )
) @root @definition.class

(field_definition
  (property_identifier) @identifier
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
) @root
