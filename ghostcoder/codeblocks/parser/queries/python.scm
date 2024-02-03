(module . (_) @child.first @definition.module) @root

(decorated_definition [
    (function_definition) @check_child
    (class_definition) @check_child
  ]
) @root

(class_definition
  (identifier) @identifier
  (comment) @child.first @definition.class
  .
  (block (_) @child.last .)
) @root

(class_definition
  (identifier) @identifier
  (block . (_) @child.first)
) @root @definition.class

(function_definition
  (identifier) @identifier
  (parameters
    ("(")
    (
      [
        (identifier)  @parameter.identifier
        (_
          (identifier) @parameter.identifier
          (":")
          (type
            [
              (identifier) @parameter.type
              (string) @parameter.type
            ]
          )
        )
      ]
      (",")?
    )*
    (")")
  )
  (
    ("->")
    (type
      [
        (identifier) @reference.identifier
        (subscript) @reference.identifier ; TODO: Extract identifiers
      ]
    )
  )?
  (":")
  .
  [
    (
      (comment) ? @child.first
      (block
        (_) @child.last .
      )
    )
    (
      (block
        . (_) @child.first
        (_) ? @child.last .
      )
    )
  ]
) @root @definition.function

(comment) @root @definition.comment

(import_statement [
  (aliased_import
    (dotted_name) @reference.identifier
    (identifier) @identifier
  )
  (dotted_name) @reference.identifier @identifier
  ]
) @root @definition.import

(import_from_statement
  ("from")
  .
  (relative_import) @reference.module
  ("import")
  (dotted_name) @reference.identifier @identifier @reference.type
) @root @definition.import

(import_from_statement
  ("from")
  .
  (dotted_name) @reference.module
  ("import")
  (
    (dotted_name) @reference.identifier
    (",")*
  )*
) @root @definition.import

(future_import_statement) @root @definition.import
(import_from_statement) @root @definition.import

(assignment
  left: [
    (identifier) @identifier
    (attribute) @identifier
  ]
  (
    (":")
    (type
      [
        (identifier) @reference.identifier @reference.type
        (subscript .
          (identifier) @reference.identifier @reference.type
        )
      ]
    )
  )?
  right: [
    (identifier) @reference.identifier @reference.dependency
    (attribute) @reference.identifier @reference.dependency
    (_) @child.first
  ]?
) @root @definition.assignment

(call
  [
    (identifier) @reference.identifier
    (attribute) @reference.identifier
  ]
  (argument_list
    (
      [
        (identifier) @reference.identifier
        (attribute) @reference.identifier
        (keyword_argument
          (attribute) @reference.identifier
        )
      ]
      (",")?
    )*
  )
) @root @definition.call

(expression_statement
  (_) @check_child
) @root

(return_statement
  ("return")
  (_) @child.first
) @root @definition.statement

(block
  (_) @check_child
) @root

(_
  (block . (_) @child.first)
) @root @definition.statement
