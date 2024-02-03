(class_declaration
  [
    (type_identifier) @identifier
    (identifier) @identifier
  ]
  (class_body
    ("{") @child.first
  )
) @root @definition.class

(enum_declaration
  (identifier) @identifier
  (enum_body
    ("{") @child.first
  )
) @root @definition.class

(abstract_class_declaration
  [
    (type_identifier) @identifier
    (identifier) @identifier
  ]
  (class_body
    ("{") @child.first
  )
) @root @definition.class

(interface_declaration
  (type_identifier) @identifier
  (object_type
    ("{") @child.first
  )
) @root @definition.class

(abstract_method_signature
  (property_identifier) @identifier
) @root @definition.function

(type_alias_declaration
  (type_identifier) @identifier
  ("=")
  (object_type
    ("{") @child.first
  )
) @root @definition.class

(type_alias_declaration
  (type_identifier) @identifier
  ("=")
  (_) @child.first
) @root @definition.class

(lexical_declaration
  (variable_declarator
    name: [
      (identifier) @identifier
      ;; (array_pattern) @identifier TODO: Support more than one identifier
    ]
    (type_annotation
      (":")
      (type_identifier) @reference.type
    )?
    value: [
      (arrow_function
        parameters: (formal_parameters
          ("(")
          (
            (required_parameter ;; TODO: Should be a reusable pattern to find parameters and references
              [
                (identifier) @parameter.identifier
                (object_pattern
                  ("{")
                  (
                    [
                      (object_assignment_pattern
                        (shorthand_property_identifier_pattern) @parameter.identifier
                      )
                      (shorthand_property_identifier_pattern) @parameter.identifier
                      (rest_pattern
                        ("...")
                        (identifier) @parameter.identifier
                      )
                    ]
                    (",")?
                  )*
                  ("}")
                )
              ]
              (type_annotation
                (":")
                (_) @parameter.type
              )?
            )
            (",")?
          )*
          (")")
        ) @definition.function
        (type_annotation
          [
            (generic_type
              (type_identifier) @reference.provides
              (type_arguments
                ("<")
                (type_identifier) @reference.provides
                (",")?
                (type_identifier)? @reference.provides
                (">")
              )
            )
          ]
        )?
        body: [
          (statement_block
            ("{") @child.first
          )
          (expression) @child.first
        ]
      )
      (call_expression
        [
          (identifier) @reference.utilizes
          (member_expression) @reference.utilizes
        ]
        (type_arguments
          ("<")
          (type_identifier) @reference.identifier
          (",")?
          (type_identifier)? @reference.identifier
          (">")
        )?
        (arguments
          ("(") @child.first
          (arrow_function
            parameters: (formal_parameters
              ("(")
              (
                (required_parameter
                  [
                    (identifier) @parameter.identifier
                    (object_pattern
                      ("{")
                      (
                        [
                          (object_assignment_pattern
                            (shorthand_property_identifier_pattern) @parameter.identifier
                          )
                          (shorthand_property_identifier_pattern) @parameter.identifier
                          (rest_pattern
                            ("...")
                            (identifier) @parameter.identifier
                          )
                        ]
                        (",")?
                      )*
                      ("}")
                    )
                  ]
                  (type_annotation
                    (":")
                    (_) @parameter.type
                  )?
                )
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
          (")") @child.last
        )
      )
    ]
  )
) @root

(import_statement
  ("import")
  (import_require_clause
    (identifier) @reference.identifier
    ("=")
    (string
      [("\"")("'")]
      (_) @reference.module
      [("\"")("'")]
    )
  )
) @root @definition.import

(property_signature
  (property_identifier) @identifier
  (type_annotation
    (":")
    [
      (generic_type
        (type_identifier) @reference.type
      )
    ]
  )?
) @root @definition.code

(formal_parameters
  ("(")
  (
    (required_parameter
      [
        (identifier) @parameter.identifier
        (object_pattern
          ("{")
          (
            [
              (object_assignment_pattern
                (shorthand_property_identifier_pattern) @parameter.identifier
                )
              (shorthand_property_identifier_pattern) @parameter.identifier
              (rest_pattern
                ("...")
                (identifier) @parameter.identifier
                )
              ]
            (",") ?
            ) *
          ("}")
          )
        ]
      (type_annotation
        (":")
        (_) @parameter.type
        ) ?
      )
    (",") ?
    ) *
  (")")
) @root @definition.function


(jsx_element
  (jsx_opening_element
    (identifier) @reference.identifier
    (type_arguments
      ("<")
      (type_identifier) @reference.identifier
      (",")?
      (">")
    )?
    .
    (jsx_attribute) @child.first @definition.block
  )
  (jsx_closing_element) @child.last
) @root
