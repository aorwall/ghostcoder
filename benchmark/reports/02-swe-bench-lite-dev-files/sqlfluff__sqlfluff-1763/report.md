# sqlfluff__sqlfluff-1763

| **sqlfluff/sqlfluff** | `a10057635e5b2559293a676486f0b730981f037a` |
| ---- | ---- |
| **No of patches** | 1 |
| **All found context length** | - |
| **Any found context length** | - |
| **Avg pos** | - |
| **Min pos** | - |
| **Max pos** | - |
| **Top file pos** | - |
| **Missing snippets** | 2 |
| **Missing patch files** | 1 |


## Expected patch

```diff
diff --git a/src/sqlfluff/core/linter/linted_file.py b/src/sqlfluff/core/linter/linted_file.py
--- a/src/sqlfluff/core/linter/linted_file.py
+++ b/src/sqlfluff/core/linter/linted_file.py
@@ -7,6 +7,8 @@
 
 import os
 import logging
+import shutil
+import tempfile
 from typing import (
     Any,
     Iterable,
@@ -493,7 +495,24 @@ def persist_tree(self, suffix: str = "") -> bool:
             if suffix:
                 root, ext = os.path.splitext(fname)
                 fname = root + suffix + ext
-            # Actually write the file.
-            with open(fname, "w", encoding=self.encoding) as f:
-                f.write(write_buff)
+            self._safe_create_replace_file(fname, write_buff, self.encoding)
         return success
+
+    @staticmethod
+    def _safe_create_replace_file(fname, write_buff, encoding):
+        # Write to a temporary file first, so in case of encoding or other
+        # issues, we don't delete or corrupt the user's existing file.
+        dirname, basename = os.path.split(fname)
+        with tempfile.NamedTemporaryFile(
+            mode="w",
+            encoding=encoding,
+            prefix=basename,
+            dir=dirname,
+            suffix=os.path.splitext(fname)[1],
+            delete=False,
+        ) as tmp:
+            tmp.file.write(write_buff)
+            tmp.flush()
+            os.fsync(tmp.fileno())
+        # Once the temp file is safely written, replace the existing file.
+        shutil.move(tmp.name, fname)

```

## Expected file changes

| File | Start line | End line | Found on position | Found file position | Context length |
| ---- | ---------- | -------- | ----------------- | ------------------- | -------------- |
| src/sqlfluff/core/linter/linted_file.py | 7 | - | - | - | -
| src/sqlfluff/core/linter/linted_file.py | 496 | 498 | - | - | -


## Problem Statement

```
dbt postgres fix command errors with UnicodeEncodeError and also wipes the .sql file
_If this is a parsing or linting issue, please include a minimal SQL example which reproduces the issue, along with the `sqlfluff parse` output, `sqlfluff lint` output and `sqlfluff fix` output when relevant._

## Expected Behaviour
Violation failure notice at a minimum, without wiping the file. Would like a way to ignore the known error at a minimum as --noqa is not getting past this. Actually would expect --noqa to totally ignore this.

## Observed Behaviour
Reported error: `UnicodeEncodeError: 'charmap' codec can't encode character '\u2192' in position 120: character maps to <undefined>`

## Steps to Reproduce
SQL file:
\`\`\`sql
SELECT
    reacted_table_name_right.descendant_id AS category_id,
    string_agg(redacted_table_name_left.name, ' → ' ORDER BY reacted_table_name_right.generations DESC) AS breadcrumbs -- noqa
FROM {{ ref2('redacted_schema_name', 'redacted_table_name_left') }} AS redacted_table_name_left
INNER JOIN {{ ref2('redacted_schema_name', 'reacted_table_name_right') }} AS reacted_table_name_right
    ON redacted_table_name_left.id = order_issue_category_hierarchies.ancestor_id
GROUP BY reacted_table_name_right.descendant_id
\`\`\`
Running `sqlfluff fix --ignore templating,parsing,lexing -vvvv` and accepting proposed fixes for linting violations.

## Dialect
`postgres`, with `dbt` templater

## Version
`python 3.7.12`
`sqlfluff 0.7.0`
`sqlfluff-templater-dbt 0.7.0`

## Configuration
I've tried a few, here's one:
\`\`\`
[sqlfluff]
verbose = 2
dialect = postgres
templater = dbt
exclude_rules = None
output_line_length = 80
runaway_limit = 10
ignore_templated_areas = True
processes = 3
# Comma separated list of file extensions to lint.

# NB: This config will only apply in the root folder.
sql_file_exts = .sql

[sqlfluff:indentation]
indented_joins = False
indented_using_on = True
template_blocks_indent = True

[sqlfluff:templater]
unwrap_wrapped_queries = True

[sqlfluff:templater:jinja]
apply_dbt_builtins = True

[sqlfluff:templater:jinja:macros]
# Macros provided as builtins for dbt projects
dbt_ref = {% macro ref(model_ref) %}{{model_ref}}{% endmacro %}
dbt_source = {% macro source(source_name, table) %}{{source_name}}_{{table}}{% endmacro %}
dbt_config = {% macro config() %}{% for k in kwargs %}{% endfor %}{% endmacro %}
dbt_var = {% macro var(variable, default='') %}item{% endmacro %}
dbt_is_incremental = {% macro is_incremental() %}True{% endmacro %}

# Common config across rules
[sqlfluff:rules]
tab_space_size = 4
indent_unit = space
single_table_references = consistent
unquoted_identifiers_policy = all

# L001 - Remove trailing whitespace (fix)
# L002 - Single section of whitespace should not contain both tabs and spaces (fix)
# L003 - Keep consistent indentation (fix)
# L004 - We use 4 spaces for indentation just for completeness (fix)
# L005 - Remove space before commas (fix)
# L006 - Operators (+, -, *, /) will be wrapped by a single space each side (fix)

# L007 - Operators should not be at the end of a line
[sqlfluff:rules:L007]  # Keywords
operator_new_lines = after

# L008 - Always use a single whitespace after a comma (fix)
# L009 - Files will always end with a trailing newline

# L010 - All keywords will use full upper case (fix)
[sqlfluff:rules:L010]  # Keywords
capitalisation_policy = upper

# L011 - Always explicitly alias tables (fix)
[sqlfluff:rules:L011]  # Aliasing
aliasing = explicit

# L012 - Do not have to explicitly alias all columns
[sqlfluff:rules:L012]  # Aliasing
aliasing = explicit

# L013 - Always explicitly alias a column with an expression in it (fix)
[sqlfluff:rules:L013]  # Aliasing
allow_scalar = False

# L014 - Always user full lower case for 'quoted identifiers' -> column refs. without an alias (fix)
[sqlfluff:rules:L014]  # Unquoted identifiers
extended_capitalisation_policy = lower

# L015 - Always remove parenthesis when using DISTINCT to be clear that DISTINCT applies to all columns (fix)

# L016 - Lines should be 120 characters of less. Comment lines should not be ignored (fix)
[sqlfluff:rules:L016]
ignore_comment_lines = False
max_line_length = 120

# L017 - There should not be whitespace between function name and brackets (fix)
# L018 - Always align closing bracket of WITH to the WITH keyword (fix)

# L019 - Always use trailing commas / commas at the end of the line (fix)
[sqlfluff:rules:L019]
comma_style = trailing

# L020 - Table aliases will always be unique per statement
# L021 - Remove any use of ambiguous DISTINCT and GROUP BY combinations. Lean on removing the GROUP BY.
# L022 - Add blank lines after common table expressions (CTE) / WITH.
# L023 - Always add a single whitespace after AS in a WITH clause (fix)

[sqlfluff:rules:L026]
force_enable = False

# L027 - Always add references if more than one referenced table or view is used

[sqlfluff:rules:L028]
force_enable = False

[sqlfluff:rules:L029]  # Keyword identifiers
unquoted_identifiers_policy = aliases

[sqlfluff:rules:L030]  # Function names
capitalisation_policy = upper

# L032 - We prefer use of join keys rather than USING
# L034 - We prefer ordering of columns in select statements as (fix):
# 1. wildcards
# 2. single identifiers
# 3. calculations and aggregates

# L035 - Omit 'else NULL'; it is redundant (fix)
# L036 - Move select targets / identifiers onto new lines each (fix)
# L037 - When using ORDER BY, make the direction explicit (fix)

# L038 - Never use trailing commas at the end of the SELECT clause
[sqlfluff:rules:L038]
select_clause_trailing_comma = forbid

# L039 - Remove unnecessary whitespace (fix)

[sqlfluff:rules:L040]  # Null & Boolean Literals
capitalisation_policy = upper

# L042 - Join clauses should not contain subqueries. Use common tables expressions (CTE) instead.
[sqlfluff:rules:L042]
# By default, allow subqueries in from clauses, but not join clauses.
forbid_subquery_in = join

# L043 - Reduce CASE WHEN conditions to COALESCE (fix)
# L044 - Prefer a known number of columns along the path to the source data
# L045 - Remove unused common tables expressions (CTE) / WITH statements (fix)
# L046 - Jinja tags should have a single whitespace on both sides

# L047 - Use COUNT(*) instead of COUNT(0) or COUNT(1) alternatives (fix)
[sqlfluff:rules:L047]  # Consistent syntax to count all rows
prefer_count_1 = False
prefer_count_0 = False

# L048 - Quoted literals should be surrounded by a single whitespace (fix)
# L049 - Always use IS or IS NOT for comparisons with NULL (fix)
\`\`\`


```

## Retrieved code snippets

| Position | File | Start line | End line | Tokens | Sum tokens |
| -------- | ---- | ---------- | -------- | ------ | ---------- |
| 1 | 1 setup.py | 0 | 131| 987 | 987 | 
| 2 | 2 src/sqlfluff/dialects/dialect_tsql.py | 0 | 2159| 13232 | 14219 | 
| 3 | 3 src/sqlfluff/rules/L039.py | 0 | 71| 410 | 14629 | 
| 4 | 3 src/sqlfluff/dialects/dialect_tsql.py | 0 | 2159| 13232 | 27861 | 
| 5 | 3 src/sqlfluff/dialects/dialect_tsql.py | 0 | 2159| 13232 | 41093 | 


## Missing Patch Files

 * 1: src/sqlfluff/core/linter/linted_file.py

### Hint

```
I get a dbt-related error -- can you provide your project file as well? Also, what operating system are you running this on? I tested a simplified (non-dbt) version of your file on my Mac, and it worked okay.

\`\`\`
dbt.exceptions.DbtProjectError: Runtime Error
  no dbt_project.yml found at expected path /Users/bhart/dev/sqlfluff/dbt_project.yml
\`\`\`
Never mind the questions above -- I managed to reproduce the error in a sample dbt project. Taking a look now...
@Tumble17: Have you tried setting the `encoding` parameter in `.sqlfluff`? Do you know what encoding you're using? The default is `autodetect`, and SQLFluff "thinks" the file uses "Windows-1252" encoding, which I assume is incorrect -- that's why SQLFluff is unable to write out the updated file.
I added this line to the first section of your `.sqlfluff`, and now it seems to work. I'll look into changing the behavior of `sqlfluff fix` so it doesn't erase the file when it fails.

\`\`\`
encoding = utf-8
\`\`\`
```

## Patch

```diff
diff --git a/src/sqlfluff/core/linter/linted_file.py b/src/sqlfluff/core/linter/linted_file.py
--- a/src/sqlfluff/core/linter/linted_file.py
+++ b/src/sqlfluff/core/linter/linted_file.py
@@ -7,6 +7,8 @@
 
 import os
 import logging
+import shutil
+import tempfile
 from typing import (
     Any,
     Iterable,
@@ -493,7 +495,24 @@ def persist_tree(self, suffix: str = "") -> bool:
             if suffix:
                 root, ext = os.path.splitext(fname)
                 fname = root + suffix + ext
-            # Actually write the file.
-            with open(fname, "w", encoding=self.encoding) as f:
-                f.write(write_buff)
+            self._safe_create_replace_file(fname, write_buff, self.encoding)
         return success
+
+    @staticmethod
+    def _safe_create_replace_file(fname, write_buff, encoding):
+        # Write to a temporary file first, so in case of encoding or other
+        # issues, we don't delete or corrupt the user's existing file.
+        dirname, basename = os.path.split(fname)
+        with tempfile.NamedTemporaryFile(
+            mode="w",
+            encoding=encoding,
+            prefix=basename,
+            dir=dirname,
+            suffix=os.path.splitext(fname)[1],
+            delete=False,
+        ) as tmp:
+            tmp.file.write(write_buff)
+            tmp.flush()
+            os.fsync(tmp.fileno())
+        # Once the temp file is safely written, replace the existing file.
+        shutil.move(tmp.name, fname)

```

## Test Patch

```diff
diff --git a/test/core/linter_test.py b/test/core/linter_test.py
--- a/test/core/linter_test.py
+++ b/test/core/linter_test.py
@@ -641,3 +641,56 @@ def test__attempt_to_change_templater_warning(caplog):
         assert "Attempt to set templater to " in caplog.text
     finally:
         logger.propagate = original_propagate_value
+
+
+@pytest.mark.parametrize(
+    "case",
+    [
+        dict(
+            name="utf8_create",
+            fname="test.sql",
+            encoding="utf-8",
+            existing=None,
+            update="def",
+            expected="def",
+        ),
+        dict(
+            name="utf8_update",
+            fname="test.sql",
+            encoding="utf-8",
+            existing="abc",
+            update="def",
+            expected="def",
+        ),
+        dict(
+            name="utf8_special_char",
+            fname="test.sql",
+            encoding="utf-8",
+            existing="abc",
+            update="→",  # Special utf-8 character
+            expected="→",
+        ),
+        dict(
+            name="incorrect_encoding",
+            fname="test.sql",
+            encoding="Windows-1252",
+            existing="abc",
+            update="→",  # Not valid in Windows-1252
+            expected="abc",  # File should be unchanged
+        ),
+    ],
+    ids=lambda case: case["name"],
+)
+def test_safe_create_replace_file(case, tmp_path):
+    """Test creating or updating .sql files, various content and encoding."""
+    p = tmp_path / case["fname"]
+    if case["existing"]:
+        p.write_text(case["existing"])
+    try:
+        linter.LintedFile._safe_create_replace_file(
+            str(p), case["update"], case["encoding"]
+        )
+    except:  # noqa: E722
+        pass
+    actual = p.read_text(encoding=case["encoding"])
+    assert case["expected"] == actual

```


## Code snippets

### 1 - setup.py:

```python
#!/usr/bin/env python

"""The script for setting up sqlfluff."""


import sys

if sys.version_info[0] < 3:
    raise Exception("SQLFluff does not support Python 2. Please upgrade to Python 3.")

import configparser
from os.path import dirname
from os.path import join

from setuptools import find_packages, setup


# Get the global config info as currently stated
# (we use the config file to avoid actually loading any python here)
config = configparser.ConfigParser()
config.read(["src/sqlfluff/config.ini"])
version = config.get("sqlfluff", "version")


def read(*names, **kwargs):
    """Read a file and return the contents as a string."""
    return open(
        join(dirname(__file__), *names), encoding=kwargs.get("encoding", "utf8")
    ).read()


setup(
    name="sqlfluff",
    version=version,
    license="MIT License",
    description="The SQL Linter for Humans",
    long_description=read("README.md"),
    # Make sure pypi is expecting markdown!
    long_description_content_type="text/markdown",
    author="Alan Cruickshank",
    author_email="alan@designingoverload.com",
    url="https://github.com/sqlfluff/sqlfluff",
    python_requires=">=3.6",
    keywords=[
        "sqlfluff",
        "sql",
        "linter",
        "formatter",
        "bigquery",
        "exasol",
        "hive",
        "mysql",
        "postgres",
        "redshift",
        "snowflake",
        "spark3",
        "sqlite",
        "teradata",
        "tsql",
        "dbt",
    ],
    project_urls={
        "Homepage": "https://www.sqlfluff.com",
        "Documentation": "https://docs.sqlfluff.com",
        "Changes": "https://github.com/sqlfluff/sqlfluff/blob/main/CHANGELOG.md",
        "Source": "https://github.com/sqlfluff/sqlfluff",
        "Issue Tracker": "https://github.com/sqlfluff/sqlfluff/issues",
        "Twitter": "https://twitter.com/SQLFluff",
        "Chat": "https://github.com/sqlfluff/sqlfluff#sqlfluff-on-slack",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 4 - Beta",
        # 'Development Status :: 5 - Production/Stable',
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Operating System :: POSIX",
        "Operating System :: MacOS",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Utilities",
        "Topic :: Software Development :: Quality Assurance",
    ],
    install_requires=[
        # Core
        "click>=7.1",
        "colorama>=0.3",
        "configparser",
        "oyaml",
        "Jinja2",
        # Used for diffcover plugin
        "diff-cover>=2.5.0",
        # Used for .sqlfluffignore
        "pathspec",
        # Used for finding os-specific application config dirs
        "appdirs",
        # Cached property for performance gains
        "cached-property",
        # dataclasses backport for python 3.6
        "dataclasses; python_version < '3.7'",
        # better type hints for older python versions
        "typing_extensions",
        # We provide a testing library for plugins in sqlfluff.testing
        "pytest",
        # For parsing pyproject.toml
        "toml",
        # For returning exceptions from multiprocessing.Pool.map()
        "tblib",
    ],
    entry_points={
        "console_scripts": [
            "sqlfluff = sqlfluff.cli.commands:cli",
        ],
        "diff_cover": ["sqlfluff = sqlfluff.diff_quality_plugin"],
        "sqlfluff": ["sqlfluff = sqlfluff.core.plugin.lib"],
    },
)

```
### 2 - src/sqlfluff/dialects/dialect_tsql.py:

```python
"""The MSSQL T-SQL dialect.

https://docs.microsoft.com/en-us/sql/t-sql/language-elements/language-elements-transact-sql
"""

from sqlfluff.core.parser import (
    BaseSegment,
    Sequence,
    OneOf,
    Bracketed,
    Ref,
    Anything,
    Nothing,
    RegexLexer,
    CodeSegment,
    RegexParser,
    Delimited,
    Matchable,
    NamedParser,
    OptionallyBracketed,
    Dedent,
    BaseFileSegment,
    Indent,
    AnyNumberOf,
    CommentSegment,
    StringParser,
    SymbolSegment,
    SegmentGenerator,
)

from sqlfluff.core.dialects import load_raw_dialect

from sqlfluff.dialects.dialect_tsql_keywords import (
    RESERVED_KEYWORDS,
    UNRESERVED_KEYWORDS,
)

ansi_dialect = load_raw_dialect("ansi")
tsql_dialect = ansi_dialect.copy_as("tsql")

# Should really clear down the old keywords but some are needed by certain segments
# tsql_dialect.sets("reserved_keywords").clear()
# tsql_dialect.sets("unreserved_keywords").clear()
tsql_dialect.sets("reserved_keywords").update(RESERVED_KEYWORDS)
tsql_dialect.sets("unreserved_keywords").update(UNRESERVED_KEYWORDS)

tsql_dialect.insert_lexer_matchers(
    [
        RegexLexer(
            "atsign",
            r"[@][a-zA-Z0-9_]+",
            CodeSegment,
        ),
        RegexLexer(
            "square_quote",
            r"\[([^\[\]]*)*\]",
            CodeSegment,
        ),
        # T-SQL unicode strings
        RegexLexer("single_quote_with_n", r"N'([^']|'')*'", CodeSegment),
        RegexLexer(
            "hash_prefix",
            r"[#][#]?[a-zA-Z0-9_]+",
            CodeSegment,
        ),
    ],
    before="back_quote",
)

tsql_dialect.patch_lexer_matchers(
    [
        # Patching single_quote to allow for TSQL-style escaped quotes
        RegexLexer("single_quote", r"'([^']|'')*'", CodeSegment),
        # Patching comments to remove hash comments
        RegexLexer(
            "inline_comment",
            r"(--)[^\n]*",
            CommentSegment,
            segment_kwargs={"trim_start": ("--")},
        ),
        # Patching to add !<, !>
        RegexLexer("greater_than_or_equal", ">=|!<", CodeSegment),
        RegexLexer("less_than_or_equal", "<=|!>", CodeSegment),
        RegexLexer(
            "code", r"[0-9a-zA-Z_#@]+", CodeSegment
        ),  # overriding to allow hash mark and at-sign in code
    ]
)

tsql_dialect.add(
    BracketedIdentifierSegment=NamedParser(
        "square_quote", CodeSegment, name="quoted_identifier", type="identifier"
    ),
    HashIdentifierSegment=NamedParser(
        "hash_prefix", CodeSegment, name="hash_identifier", type="identifier"
    ),
    BatchDelimiterSegment=Ref("GoStatementSegment"),
    QuotedLiteralSegmentWithN=NamedParser(
        "single_quote_with_n", CodeSegment, name="quoted_literal", type="literal"
    ),
    NotGreaterThanSegment=StringParser(
        "!>", SymbolSegment, name="less_than_equal_to", type="comparison_operator"
    ),
    NotLessThanSegment=StringParser(
        "!<", SymbolSegment, name="greater_than_equal_to", type="comparison_operator"
    ),
)

tsql_dialect.replace(
    # Overriding to cover TSQL allowed identifier name characters
    # https://docs.microsoft.com/en-us/sql/relational-databases/databases/database-identifiers?view=sql-server-ver15
    NakedIdentifierSegment=SegmentGenerator(
        # Generate the anti template from the set of reserved keywords
        lambda dialect: RegexParser(
            r"[A-Z_][A-Z0-9_@$#]*",
            CodeSegment,
            name="naked_identifier",
            type="identifier",
            anti_template=r"^(" + r"|".join(dialect.sets("reserved_keywords")) + r")$",
        )
    ),
    ComparisonOperatorGrammar=OneOf(
        Ref("EqualsSegment"),
        Ref("GreaterThanSegment"),
        Ref("LessThanSegment"),
        Ref("GreaterThanOrEqualToSegment"),
        Ref("LessThanOrEqualToSegment"),
        Ref("NotEqualToSegment_a"),
        Ref("NotEqualToSegment_b"),
        Ref("LikeOperatorSegment"),
        Ref("NotGreaterThanSegment"),
        Ref("NotLessThanSegment"),
    ),
    SingleIdentifierGrammar=OneOf(
        Ref("NakedIdentifierSegment"),
        Ref("QuotedIdentifierSegment"),
        Ref("BracketedIdentifierSegment"),
        Ref("HashIdentifierSegment"),
        Ref("ParameterNameSegment"),
    ),
    LiteralGrammar=OneOf(
        Ref("QuotedLiteralSegment"),
        Ref("QuotedLiteralSegmentWithN"),
        Ref("NumericLiteralSegment"),
        Ref("BooleanLiteralGrammar"),
        Ref("QualifiedNumericLiteralSegment"),
        # NB: Null is included in the literals, because it is a keyword which
        # can otherwise be easily mistaken for an identifier.
        Ref("NullLiteralSegment"),
        Ref("DateTimeLiteralGrammar"),
    ),
    ParameterNameSegment=RegexParser(
        r"[@][A-Za-z0-9_]+", CodeSegment, name="parameter", type="parameter"
    ),
    FunctionNameIdentifierSegment=RegexParser(
        r"[A-Z][A-Z0-9_]*|\[[A-Z][A-Z0-9_]*\]",
        CodeSegment,
        name="function_name_identifier",
        type="function_name_identifier",
    ),
    DatatypeIdentifierSegment=Ref("SingleIdentifierGrammar"),
    PrimaryKeyGrammar=Sequence(
        "PRIMARY", "KEY", OneOf("CLUSTERED", "NONCLUSTERED", optional=True)
    ),
    # Overriding SelectClauseSegmentGrammar to remove Delimited logic which assumes statements have been delimited
    SelectClauseSegmentGrammar=Sequence(
        "SELECT",
        Ref("SelectClauseModifierSegment", optional=True),
        Indent,
        AnyNumberOf(
            Sequence(
                Ref("SelectClauseElementSegment"),
                Ref("CommaSegment"),
            ),
        ),
        Ref("SelectClauseElementSegment"),
        # NB: The Dedent for the indent above lives in the
        # SelectStatementSegment so that it sits in the right
        # place corresponding to the whitespace.
    ),
    FromClauseTerminatorGrammar=OneOf(
        "WHERE",
        "LIMIT",
        Sequence("GROUP", "BY"),
        Sequence("ORDER", "BY"),
        "HAVING",
        "PIVOT",
        "UNPIVOT",
        Ref("SetOperatorSegment"),
        Ref("WithNoSchemaBindingClauseSegment"),
        Ref("DelimiterSegment"),
    ),
    JoinKeywords=OneOf("JOIN", "APPLY", Sequence("OUTER", "APPLY")),
    # Replace Expression_D_Grammar to remove casting syntax invalid in TSQL
    Expression_D_Grammar=Sequence(
        OneOf(
            Ref("BareFunctionSegment"),
            Ref("FunctionSegment"),
            Bracketed(
                OneOf(
                    # We're using the expression segment here rather than the grammar so
                    # that in the parsed structure we get nested elements.
                    Ref("ExpressionSegment"),
                    Ref("SelectableGrammar"),
                    Delimited(
                        Ref(
                            "ColumnReferenceSegment"
                        ),  # WHERE (a,b,c) IN (select a,b,c FROM...)
                        Ref(
                            "FunctionSegment"
                        ),  # WHERE (a, substr(b,1,3)) IN (select c,d FROM...)
                        Ref("LiteralGrammar"),  # WHERE (a, 2) IN (SELECT b, c FROM ...)
                    ),
                    ephemeral_name="BracketedExpression",
                ),
            ),
            # Allow potential select statement without brackets
            Ref("SelectStatementSegment"),
            Ref("LiteralGrammar"),
            Ref("IntervalExpressionSegment"),
            Ref("ColumnReferenceSegment"),
            Sequence(
                Ref("SimpleArrayTypeGrammar", optional=True), Ref("ArrayLiteralSegment")
            ),
        ),
        Ref("Accessor_Grammar", optional=True),
        allow_gaps=True,
    ),
)


@tsql_dialect.segment(replace=True)
class AliasExpressionSegment(BaseSegment):
    """A reference to an object with an `AS` clause.

    The optional AS keyword allows both implicit and explicit aliasing.
    Overriding ANSI to remove QuotedLiteralSegment
    """

    type = "alias_expression"
    match_grammar = Sequence(
        Ref.keyword("AS", optional=True),
        OneOf(
            Sequence(
                Ref("SingleIdentifierGrammar"),
                # Column alias in VALUES clause
                Bracketed(Ref("SingleIdentifierListSegment"), optional=True),
            ),
        ),
    )


@tsql_dialect.segment(replace=True)
class StatementSegment(ansi_dialect.get_segment("StatementSegment")):  # type: ignore
    """Overriding StatementSegment to allow for additional segment parsing."""

    match_grammar = ansi_dialect.get_segment("StatementSegment").parse_grammar.copy(
        insert=[
            Ref("IfExpressionStatement"),
            Ref("DeclareStatementSegment"),
            Ref("SetStatementSegment"),
            Ref("AlterTableSwitchStatementSegment"),
            Ref("PrintStatementSegment"),
            Ref(
                "CreateTableAsSelectStatementSegment"
            ),  # Azure Synapse Analytics specific
            Ref("RenameStatementSegment"),  # Azure Synapse Analytics specific
            Ref("ExecuteScriptSegment"),
            Ref("DropStatisticsStatementSegment"),
            Ref("UpdateStatisticsStatementSegment"),
        ],
    )

    parse_grammar = match_grammar


@tsql_dialect.segment(replace=True)
class SelectClauseElementSegment(BaseSegment):
    """An element in the targets of a select statement.

    Overriding ANSI to remove GreedyUntil logic which assumes statements have been delimited
    """

    type = "select_clause_element"
    # Important to split elements before parsing, otherwise debugging is really hard.
    match_grammar = OneOf(
        # *, blah.*, blah.blah.*, etc.
        Ref("WildcardExpressionSegment"),
        Sequence(
            Ref("BaseExpressionElementGrammar"),
            Ref("AliasExpressionSegment", optional=True),
        ),
    )


@tsql_dialect.segment(replace=True)
class SelectClauseModifierSegment(BaseSegment):
    """Things that come after SELECT but before the columns."""

    type = "select_clause_modifier"
    match_grammar = OneOf(
        "DISTINCT",
        "ALL",
        Sequence(
            "TOP",
            OptionallyBracketed(Ref("ExpressionSegment")),
            Sequence("PERCENT", optional=True),
            Sequence("WITH", "TIES", optional=True),
        ),
    )


@tsql_dialect.segment(replace=True)
class SelectClauseSegment(BaseSegment):
    """A group of elements in a select target statement.

    Overriding ANSI to remove StartsWith logic which assumes statements have been delimited
    """

    type = "select_clause"
    match_grammar = Ref("SelectClauseSegmentGrammar")


@tsql_dialect.segment(replace=True)
class UnorderedSelectStatementSegment(BaseSegment):
    """A `SELECT` statement without any ORDER clauses or later.

    We need to change ANSI slightly to remove LimitClauseSegment
    and NamedWindowSegment which don't exist in T-SQL.

    We also need to get away from ANSI's use of StartsWith.
    There's not a clean list of terminators that can be used
    to identify the end of a TSQL select statement.  Semi-colon is optional.
    """

    type = "select_statement"
    match_grammar = Sequence(
        Ref("SelectClauseSegment"),
        # Dedent for the indent in the select clause.
        # It's here so that it can come AFTER any whitespace.
        Dedent,
        Ref("IntoTableSegment", optional=True),
        Ref("FromClauseSegment", optional=True),
        Ref("PivotUnpivotStatementSegment", optional=True),
        Ref("WhereClauseSegment", optional=True),
        Ref("GroupByClauseSegment", optional=True),
        Ref("HavingClauseSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
class SelectStatementSegment(BaseSegment):
    """A `SELECT` statement.

    We need to change ANSI slightly to remove LimitClauseSegment
    and NamedWindowSegment which don't exist in T-SQL.

    We also need to get away from ANSI's use of StartsWith.
    There's not a clean list of terminators that can be used
    to identify the end of a TSQL select statement.  Semi-colon is optional.
    """

    type = "select_statement"
    # Remove the Limit and Window statements from ANSI
    match_grammar = UnorderedSelectStatementSegment.match_grammar.copy(
        insert=[
            Ref("OrderByClauseSegment", optional=True),
            Ref("OptionClauseSegment", optional=True),
            Ref("DelimiterSegment", optional=True),
        ]
    )


@tsql_dialect.segment()
class IntoTableSegment(BaseSegment):
    """`INTO` clause within `SELECT`.

    https://docs.microsoft.com/en-us/sql/t-sql/queries/select-into-clause-transact-sql?view=sql-server-ver15
    """

    type = "into_table_clause"
    match_grammar = Sequence("INTO", Ref("ObjectReferenceSegment"))


@tsql_dialect.segment(replace=True)
class WhereClauseSegment(BaseSegment):
    """A `WHERE` clause like in `SELECT` or `INSERT`.

    Overriding ANSI in order to get away from the use of
    StartsWith. There's not a clean list of terminators that can be used
    to identify the end of a TSQL select statement.  Semi-colon is optional.
    """

    type = "where_clause"
    match_grammar = Sequence(
        "WHERE",
        Indent,
        OptionallyBracketed(Ref("ExpressionSegment")),
        Dedent,
    )


@tsql_dialect.segment(replace=True)
class CreateIndexStatementSegment(BaseSegment):
    """A `CREATE INDEX` or `CREATE STATISTICS` statement.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-index-transact-sql?view=sql-server-ver15
    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-statistics-transact-sql?view=sql-server-ver15
    """

    type = "create_index_statement"
    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Sequence("UNIQUE", optional=True),
        OneOf("CLUSTERED", "NONCLUSTERED", optional=True),
        OneOf("INDEX", "STATISTICS"),
        Ref("IfNotExistsGrammar", optional=True),
        Ref("IndexReferenceSegment"),
        "ON",
        Ref("TableReferenceSegment"),
        Sequence(
            Bracketed(
                Delimited(
                    Ref("IndexColumnDefinitionSegment"),
                ),
            )
        ),
        Sequence(
            "INCLUDE",
            Sequence(
                Bracketed(
                    Delimited(
                        Ref("IndexColumnDefinitionSegment"),
                    ),
                )
            ),
            optional=True,
        ),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
class DropIndexStatementSegment(BaseSegment):
    """A `DROP INDEX` statement.

    Overriding ANSI to include required ON clause.
    """

    type = "drop_statement"
    match_grammar = Sequence(
        "DROP",
        "INDEX",
        Ref("IfExistsGrammar", optional=True),
        Ref("IndexReferenceSegment"),
        "ON",
        Ref("TableReferenceSegment"),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment()
class DropStatisticsStatementSegment(BaseSegment):
    """A `DROP STATISTICS` statement."""

    type = "drop_statement"
    # DROP INDEX <Index name> [CONCURRENTLY] [IF EXISTS] {RESTRICT | CASCADE}
    match_grammar = Sequence(
        "DROP",
        OneOf("STATISTICS"),
        Ref("IndexReferenceSegment"),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment()
class UpdateStatisticsStatementSegment(BaseSegment):
    """An `UPDATE STATISTICS` statement.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/update-statistics-transact-sql?view=sql-server-ver15
    """

    type = "update_statistics_statement"
    match_grammar = Sequence(
        "UPDATE",
        "STATISTICS",
        Ref("ObjectReferenceSegment"),
        OneOf(
            Ref("SingleIdentifierGrammar"),
            Bracketed(
                Delimited(
                    Ref("SingleIdentifierGrammar"),
                ),
            ),
            optional=True,
        ),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
class ObjectReferenceSegment(BaseSegment):
    """A reference to an object.

    Update ObjectReferenceSegment to only allow dot separated SingleIdentifierGrammar
    So Square Bracketed identifiers can be matched.
    """

    type = "object_reference"
    # match grammar (allow whitespace)
    match_grammar: Matchable = Sequence(
        Ref("SingleIdentifierGrammar"),
        AnyNumberOf(
            Sequence(
                Ref("DotSegment"),
                Ref("SingleIdentifierGrammar", optional=True),
            ),
            min_times=0,
            max_times=3,
        ),
    )

    ObjectReferencePart = ansi_dialect.get_segment(
        "ObjectReferenceSegment"
    ).ObjectReferencePart

    _iter_reference_parts = ansi_dialect.get_segment(
        "ObjectReferenceSegment"
    )._iter_reference_parts

    iter_raw_references = ansi_dialect.get_segment(
        "ObjectReferenceSegment"
    ).iter_raw_references

    is_qualified = ansi_dialect.get_segment("ObjectReferenceSegment").is_qualified

    qualification = ansi_dialect.get_segment("ObjectReferenceSegment").qualification

    ObjectReferenceLevel = ansi_dialect.get_segment(
        "ObjectReferenceSegment"
    ).ObjectReferenceLevel

    extract_possible_references = ansi_dialect.get_segment(
        "ObjectReferenceSegment"
    ).extract_possible_references

    _level_to_int = staticmethod(
        ansi_dialect.get_segment("ObjectReferenceSegment")._level_to_int
    )


@tsql_dialect.segment(replace=True)
class TableReferenceSegment(ObjectReferenceSegment):
    """A reference to an table, CTE, subquery or alias.

    Overriding to capture TSQL's override of ObjectReferenceSegment
    """

    type = "table_reference"


@tsql_dialect.segment(replace=True)
class SchemaReferenceSegment(ObjectReferenceSegment):
    """A reference to a schema.

    Overriding to capture TSQL's override of ObjectReferenceSegment
    """

    type = "schema_reference"


@tsql_dialect.segment(replace=True)
class DatabaseReferenceSegment(ObjectReferenceSegment):
    """A reference to a database.

    Overriding to capture TSQL's override of ObjectReferenceSegment
    """

    type = "database_reference"


@tsql_dialect.segment(replace=True)
class IndexReferenceSegment(ObjectReferenceSegment):
    """A reference to an index.

    Overriding to capture TSQL's override of ObjectReferenceSegment
    """

    type = "index_reference"


@tsql_dialect.segment(replace=True)
class ExtensionReferenceSegment(ObjectReferenceSegment):
    """A reference to an extension.

    Overriding to capture TSQL's override of ObjectReferenceSegment
    """

    type = "extension_reference"


@tsql_dialect.segment(replace=True)
class ColumnReferenceSegment(ObjectReferenceSegment):
    """A reference to column, field or alias.

    Overriding to capture TSQL's override of ObjectReferenceSegment
    """

    type = "column_reference"


@tsql_dialect.segment(replace=True)
class SequenceReferenceSegment(ObjectReferenceSegment):
    """A reference to a sequence.

    Overriding to capture TSQL's override of ObjectReferenceSegment
    """

    type = "sequence_reference"


@tsql_dialect.segment()
class PivotColumnReferenceSegment(ObjectReferenceSegment):
    """A reference to a PIVOT column to differentiate it from a regular column reference."""

    type = "pivot_column_reference"


@tsql_dialect.segment()
class PivotUnpivotStatementSegment(BaseSegment):
    """Declaration of a variable.

    https://docs.microsoft.com/en-us/sql/t-sql/queries/from-using-pivot-and-unpivot?view=sql-server-ver15
    """

    type = "from_pivot_expression"
    match_grammar = Sequence(
        OneOf(
            Sequence(
                "PIVOT",
                OptionallyBracketed(
                    Sequence(
                        OptionallyBracketed(Ref("FunctionSegment")),
                        "FOR",
                        Ref("ColumnReferenceSegment"),
                        "IN",
                        Bracketed(Delimited(Ref("PivotColumnReferenceSegment"))),
                    )
                ),
            ),
            Sequence(
                "UNPIVOT",
                OptionallyBracketed(
                    Sequence(
                        OptionallyBracketed(Ref("ColumnReferenceSegment")),
                        "FOR",
                        Ref("ColumnReferenceSegment"),
                        "IN",
                        Bracketed(Delimited(Ref("PivotColumnReferenceSegment"))),
                    )
                ),
            ),
        ),
        "AS",
        Ref("TableReferenceSegment"),
    )


@tsql_dialect.segment()
class DeclareStatementSegment(BaseSegment):
    """Declaration of a variable.

    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/declare-local-variable-transact-sql?view=sql-server-ver15
    """

    type = "declare_segment"
    match_grammar = Sequence(
        "DECLARE",
        Ref("ParameterNameSegment"),
        Sequence("AS", optional=True),
        Ref("DatatypeSegment"),
        Sequence(
            Ref("EqualsSegment"),
            Ref("ExpressionSegment"),
            optional=True,
        ),
        AnyNumberOf(
            Ref("CommaSegment"),
            Ref("ParameterNameSegment"),
            Ref("DatatypeSegment"),
            Sequence(
                Ref("EqualsSegment"),
                Ref("ExpressionSegment"),
                optional=True,
            ),
        ),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment()
class GoStatementSegment(BaseSegment):
    """GO signals the end of a batch of Transact-SQL statements to the SQL Server utilities.

    GO statements are not part of the TSQL language. They are used to signal batch statements
    so that clients know in how batches of statements can be executed.
    """

    type = "go_statement"
    match_grammar = Sequence("GO")


@tsql_dialect.segment(replace=True)
class DatatypeSegment(BaseSegment):
    """A data type segment.

    Updated for Transact-SQL to allow bracketed data types with bracketed schemas.
    """

    type = "data_type"
    match_grammar = Sequence(
        # Some dialects allow optional qualification of data types with schemas
        Sequence(
            Ref("SingleIdentifierGrammar"),
            Ref("DotSegment"),
            allow_gaps=False,
            optional=True,
        ),
        OneOf(
            Ref("DatatypeIdentifierSegment"),
            Bracketed(Ref("DatatypeIdentifierSegment"), bracket_type="square"),
        ),
        Bracketed(
            OneOf(
                Delimited(Ref("ExpressionSegment")),
                # The brackets might be empty for some cases...
                optional=True,
            ),
            # There may be no brackets for some data types
            optional=True,
        ),
        Ref("CharCharacterSetSegment", optional=True),
    )


@tsql_dialect.segment()
class NextValueSequenceSegment(BaseSegment):
    """Segment to get next value from a sequence."""

    type = "sequence_next_value"
    match_grammar = Sequence(
        "NEXT",
        "VALUE",
        "FOR",
        Ref("ObjectReferenceSegment"),
    )


@tsql_dialect.segment()
class IfExpressionStatement(BaseSegment):
    """IF-ELSE statement.

    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/if-else-transact-sql?view=sql-server-ver15
    """

    type = "if_then_statement"

    match_grammar = Sequence(
        OneOf(
            Sequence(Ref("IfNotExistsGrammar"), Ref("SelectStatementSegment")),
            Sequence(Ref("IfExistsGrammar"), Ref("SelectStatementSegment")),
            Sequence("IF", Ref("ExpressionSegment")),
        ),
        Indent,
        OneOf(
            Ref("BeginEndSegment"),
            Sequence(
                Ref("StatementSegment"),
                Ref("DelimiterSegment", optional=True),
            ),
        ),
        Dedent,
        Sequence(
            "ELSE",
            Indent,
            OneOf(
                Ref("BeginEndSegment"),
                Sequence(
                    Ref("StatementSegment"),
                    Ref("DelimiterSegment", optional=True),
                ),
            ),
            Dedent,
            optional=True,
        ),
    )


@tsql_dialect.segment(replace=True)
class ColumnConstraintSegment(BaseSegment):
    """A column option; each CREATE TABLE column can have 0 or more."""

    type = "column_constraint_segment"
    # Column constraint from
    # https://www.postgresql.org/docs/12/sql-createtable.html
    match_grammar = Sequence(
        Sequence(
            "CONSTRAINT",
            Ref("ObjectReferenceSegment"),  # Constraint name
            optional=True,
        ),
        OneOf(
            Sequence(Ref.keyword("NOT", optional=True), "NULL"),  # NOT NULL or NULL
            Sequence(  # DEFAULT <value>
                "DEFAULT",
                OneOf(
                    Ref("LiteralGrammar"),
                    Ref("FunctionSegment"),
                    # ?? Ref('IntervalExpressionSegment')
                    OptionallyBracketed(Ref("NextValueSequenceSegment")),
                ),
            ),
            Ref("PrimaryKeyGrammar"),
            "UNIQUE",  # UNIQUE
            "AUTO_INCREMENT",  # AUTO_INCREMENT (MySQL)
            "UNSIGNED",  # UNSIGNED (MySQL)
            Sequence(  # REFERENCES reftable [ ( refcolumn) ]
                "REFERENCES",
                Ref("ColumnReferenceSegment"),
                # Foreign columns making up FOREIGN KEY constraint
                Ref("BracketedColumnReferenceListGrammar", optional=True),
            ),
            Ref("CommentClauseSegment"),
            Ref("IdentityGrammar"),
        ),
    )


@tsql_dialect.segment(replace=True)
class FunctionParameterListGrammar(BaseSegment):
    """The parameters for a function ie. `(@city_name NVARCHAR(30), @postal_code NVARCHAR(15))`.

    Overriding ANSI (1) to optionally bracket and (2) remove Delimited
    """

    type = "function_parameter_list"
    # Function parameter list
    match_grammar = OptionallyBracketed(
        Ref("FunctionParameterGrammar"),
        AnyNumberOf(
            Ref("CommaSegment"),
            Ref("FunctionParameterGrammar"),
        ),
    )


@tsql_dialect.segment(replace=True)
class CreateFunctionStatementSegment(BaseSegment):
    """A `CREATE FUNCTION` statement.

    This version in the TSQL dialect should be a "common subset" of the
    structure of the code for those dialects.

    Updated to include AS after declaration of RETURNS. Might be integrated in ANSI though.

    postgres: https://www.postgresql.org/docs/9.1/sql-createfunction.html
    snowflake: https://docs.snowflake.com/en/sql-reference/sql/create-function.html
    bigquery: https://cloud.google.com/bigquery/docs/reference/standard-sql/user-defined-functions
    tsql/mssql : https://docs.microsoft.com/en-us/sql/t-sql/statements/create-function-transact-sql?view=sql-server-ver15
    """

    type = "create_function_statement"

    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "ALTER", optional=True),
        "FUNCTION",
        Anything(),
    )
    parse_grammar = Sequence(
        "CREATE",
        Sequence("OR", "ALTER", optional=True),
        "FUNCTION",
        Ref("ObjectReferenceSegment"),
        Ref("FunctionParameterListGrammar"),
        Sequence(  # Optional function return type
            "RETURNS",
            Ref("DatatypeSegment"),
            optional=True,
        ),
        Ref("FunctionDefinitionGrammar"),
    )


@tsql_dialect.segment()
class SetStatementSegment(BaseSegment):
    """A Set statement.

    Setting an already declared variable or global variable.
    https://docs.microsoft.com/en-us/sql/t-sql/statements/set-statements-transact-sql?view=sql-server-ver15

    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/set-local-variable-transact-sql?view=sql-server-ver15
    """

    type = "set_segment"
    match_grammar = Sequence(
        "SET",
        OneOf(
            Ref("ParameterNameSegment"),
            "DATEFIRST",
            "DATEFORMAT",
            "DEADLOCK_PRIORITY",
            "LOCK_TIMEOUT",
            "CONCAT_NULL_YIELDS_NULL",
            "CURSOR_CLOSE_ON_COMMIT",
            "FIPS_FLAGGER",
            "IDENTITY_INSERT",
            "LANGUAGE",
            "OFFSETS",
            "QUOTED_IDENTIFIER",
            "ARITHABORT",
            "ARITHIGNORE",
            "FMTONLY",
            "NOCOUNT",
            "NOEXEC",
            "NUMERIC_ROUNDABORT",
            "PARSEONLY",
            "QUERY_GOVERNOR_COST_LIMIT",
            "RESULT CACHING (Preview)",
            "ROWCOUNT",
            "TEXTSIZE",
            "ANSI_DEFAULTS",
            "ANSI_NULL_DFLT_OFF",
            "ANSI_NULL_DFLT_ON",
            "ANSI_NULLS",
            "ANSI_PADDING",
            "ANSI_WARNINGS",
            "FORCEPLAN",
            "SHOWPLAN_ALL",
            "SHOWPLAN_TEXT",
            "SHOWPLAN_XML",
            "STATISTICS IO",
            "STATISTICS XML",
            "STATISTICS PROFILE",
            "STATISTICS TIME",
            "IMPLICIT_TRANSACTIONS",
            "REMOTE_PROC_TRANSACTIONS",
            "TRANSACTION ISOLATION LEVEL",
            "XACT_ABORT",
        ),
        OneOf(
            "ON",
            "OFF",
            Sequence(
                Ref("EqualsSegment"),
                Ref("ExpressionSegment"),
            ),
        ),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
class FunctionDefinitionGrammar(BaseSegment):
    """This is the body of a `CREATE FUNCTION AS` statement.

    Adjusted from ansi as Transact SQL does not seem to have the QuotedLiteralSegmentand Language.
    Futhermore the body can contain almost anything like a function with table output.
    """

    type = "function_statement"
    name = "function_statement"

    match_grammar = Sequence("AS", Sequence(Anything()))


@tsql_dialect.segment()
class CreateProcedureStatementSegment(BaseSegment):
    """A `CREATE OR ALTER PROCEDURE` statement.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-procedure-transact-sql?view=sql-server-ver15
    """

    type = "create_procedure_statement"

    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "ALTER", optional=True),
        OneOf("PROCEDURE", "PROC"),
        Ref("ObjectReferenceSegment"),
        Ref("FunctionParameterListGrammar", optional=True),
        "AS",
        Ref("ProcedureDefinitionGrammar"),
    )


@tsql_dialect.segment()
class ProcedureDefinitionGrammar(BaseSegment):
    """This is the body of a `CREATE OR ALTER PROCEDURE AS` statement."""

    type = "procedure_statement"
    name = "procedure_statement"

    match_grammar = AnyNumberOf(
        OneOf(
            Ref("BeginEndSegment"),
            Ref("StatementSegment"),
        ),
        min_times=1,
    )


@tsql_dialect.segment(replace=True)
class CreateViewStatementSegment(BaseSegment):
    """A `CREATE VIEW` statement.

    Adjusted to allow CREATE OR ALTER instead of CREATE OR REPLACE.
    # https://docs.microsoft.com/en-us/sql/t-sql/statements/create-view-transact-sql?view=sql-server-ver15#examples
    """

    type = "create_view_statement"
    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "ALTER", optional=True),
        "VIEW",
        Ref("ObjectReferenceSegment"),
        "AS",
        Ref("SelectableGrammar"),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
class IntervalExpressionSegment(BaseSegment):
    """An interval expression segment.

    Not present in T-SQL.
    """

    type = "interval_expression"
    match_grammar = Nothing()


@tsql_dialect.segment(replace=True)
class CreateExtensionStatementSegment(BaseSegment):
    """A `CREATE EXTENSION` statement.

    Not present in T-SQL.
    """

    type = "create_extension_statement"
    match_grammar = Nothing()


@tsql_dialect.segment(replace=True)
class CreateModelStatementSegment(BaseSegment):
    """A BigQuery `CREATE MODEL` statement.

    Not present in T-SQL.
    """

    type = "create_model_statement"
    match_grammar = Nothing()


@tsql_dialect.segment(replace=True)
class DropModelStatementSegment(BaseSegment):
    """A `DROP MODEL` statement.

    Not present in T-SQL.
    """

    type = "drop_MODELstatement"
    match_grammar = Nothing()


@tsql_dialect.segment(replace=True)
class OverlapsClauseSegment(BaseSegment):
    """An `OVERLAPS` clause like in `SELECT.

    Not present in T-SQL.
    """

    type = "overlaps_clause"
    match_grammar = Nothing()


@tsql_dialect.segment()
class ConvertFunctionNameSegment(BaseSegment):
    """CONVERT function name segment.

    Need to be able to specify this as type function_name
    so that linting rules identify it properly
    """

    type = "function_name"
    match_grammar = Sequence("CONVERT")


@tsql_dialect.segment()
class CastFunctionNameSegment(BaseSegment):
    """CAST function name segment.

    Need to be able to specify this as type function_name
    so that linting rules identify it properly
    """

    type = "function_name"
    match_grammar = Sequence("CAST")


@tsql_dialect.segment()
class RankFunctionNameSegment(BaseSegment):
    """Rank function name segment.

    Need to be able to specify this as type function_name
    so that linting rules identify it properly
    """

    type = "function_name"
    match_grammar = OneOf("DENSE_RANK", "NTILE", "RANK", "ROW_NUMBER")


@tsql_dialect.segment()
class WithinGroupFunctionNameSegment(BaseSegment):
    """WITHIN GROUP function name segment.

    For aggregation functions that use the WITHIN GROUP clause.
    https://docs.microsoft.com/en-us/sql/t-sql/functions/string-agg-transact-sql?view=sql-server-ver15
    https://docs.microsoft.com/en-us/sql/t-sql/functions/percentile-cont-transact-sql?view=sql-server-ver15
    https://docs.microsoft.com/en-us/sql/t-sql/functions/percentile-disc-transact-sql?view=sql-server-ver15

    Need to be able to specify this as type function_name
    so that linting rules identify it properly
    """

    type = "function_name"
    match_grammar = OneOf(
        "STRING_AGG",
        "PERCENTILE_CONT",
        "PERCENTILE_DISC",
    )


@tsql_dialect.segment()
class WithinGroupClause(BaseSegment):
    """WITHIN GROUP clause.

    For a small set of aggregation functions.
    https://docs.microsoft.com/en-us/sql/t-sql/functions/string-agg-transact-sql?view=sql-server-ver15
    https://docs.microsoft.com/en-us/sql/t-sql/functions/percentile-cont-transact-sql?view=sql-server-ver15
    """

    type = "within_group_clause"
    match_grammar = Sequence(
        "WITHIN",
        "GROUP",
        Bracketed(
            Ref("OrderByClauseSegment"),
        ),
        Sequence(
            "OVER",
            Bracketed(Ref("PartitionByClause")),
            optional=True,
        ),
    )


@tsql_dialect.segment()
class PartitionByClause(BaseSegment):
    """PARTITION BY clause.

    https://docs.microsoft.com/en-us/sql/t-sql/queries/select-over-clause-transact-sql?view=sql-server-ver15#partition-by
    """

    type = "partition_by_clause"
    match_grammar = Sequence(
        "PARTITION",
        "BY",
        Ref("ColumnReferenceSegment"),
    )


@tsql_dialect.segment(replace=True)
class FunctionSegment(BaseSegment):
    """A scalar or aggregate function.

    Maybe in the future we should distinguish between
    aggregate functions and other functions. For now
    we treat them the same because they look the same
    for our purposes.
    """

    type = "function"
    match_grammar = OneOf(
        Sequence(
            Ref("DatePartFunctionNameSegment"),
            Bracketed(
                Delimited(
                    Ref("DatePartClause"),
                    Ref(
                        "FunctionContentsGrammar",
                        # The brackets might be empty for some functions...
                        optional=True,
                        ephemeral_name="FunctionContentsGrammar",
                    ),
                )
            ),
        ),
        Sequence(
            Ref("RankFunctionNameSegment"),
            Bracketed(
                Ref("NumericLiteralSegment", optional=True),
            ),
            "OVER",
            Bracketed(
                Ref("PartitionByClause", optional=True),
                Ref("OrderByClauseSegment"),
            ),
        ),
        Sequence(
            Ref("ConvertFunctionNameSegment"),
            Bracketed(
                Delimited(
                    Ref("DatatypeSegment"),
                    Ref(
                        "FunctionContentsGrammar",
                        # The brackets might be empty for some functions...
                        optional=True,
                        ephemeral_name="FunctionContentsGrammar",
                    ),
                )
            ),
        ),
        Sequence(
            Ref("CastFunctionNameSegment"),
            Bracketed(
                Ref("ExpressionSegment"),
                "AS",
                Ref("DatatypeSegment"),
            ),
        ),
        Sequence(
            Ref("WithinGroupFunctionNameSegment"),
            Bracketed(
                Delimited(
                    Ref(
                        "FunctionContentsGrammar",
                        # The brackets might be empty for some functions...
                        optional=True,
                        ephemeral_name="FunctionContentsGrammar",
                    ),
                ),
            ),
            Ref("WithinGroupClause", optional=True),
        ),
        Sequence(
            OneOf(
                Ref("FunctionNameSegment"),
                exclude=OneOf(
                    # List of special functions handled differently
                    Ref("CastFunctionNameSegment"),
                    Ref("ConvertFunctionNameSegment"),
                    Ref("DatePartFunctionNameSegment"),
                    Ref("WithinGroupFunctionNameSegment"),
                    Ref("RankFunctionNameSegment"),
                ),
            ),
            Bracketed(
                Ref(
                    "FunctionContentsGrammar",
                    # The brackets might be empty for some functions...
                    optional=True,
                    ephemeral_name="FunctionContentsGrammar",
                )
            ),
            Ref("PostFunctionGrammar", optional=True),
        ),
    )


@tsql_dialect.segment(replace=True)
class CreateTableStatementSegment(BaseSegment):
    """A `CREATE TABLE` statement."""

    type = "create_table_statement"
    # https://docs.microsoft.com/en-us/sql/t-sql/statements/create-table-transact-sql?view=sql-server-ver15
    # https://docs.microsoft.com/en-us/sql/t-sql/statements/create-table-azure-sql-data-warehouse?view=aps-pdw-2016-au7
    match_grammar = Sequence(
        "CREATE",
        "TABLE",
        Ref("TableReferenceSegment"),
        OneOf(
            # Columns and comment syntax:
            Sequence(
                Bracketed(
                    Delimited(
                        OneOf(
                            Ref("TableConstraintSegment"),
                            Ref("ColumnDefinitionSegment"),
                        ),
                    )
                ),
                Ref("CommentClauseSegment", optional=True),
            ),
            # Create AS syntax:
            Sequence(
                "AS",
                OptionallyBracketed(Ref("SelectableGrammar")),
            ),
            # Create like syntax
            Sequence("LIKE", Ref("TableReferenceSegment")),
        ),
        Ref(
            "TableDistributionIndexClause", optional=True
        ),  # Azure Synapse Analytics specific
        Ref("FilegroupClause", optional=True),
        Ref("DelimiterSegment", optional=True),
    )

    parse_grammar = match_grammar


@tsql_dialect.segment()
class FilegroupClause(BaseSegment):
    """Filegroup Clause segment.

    https://docs.microsoft.com/en-us/sql/relational-databases/databases/database-files-and-filegroups?view=sql-server-ver15
    """

    type = "filegroup_clause"
    match_grammar = Sequence(
        "ON",
        Ref("SingleIdentifierGrammar"),
    )


@tsql_dialect.segment()
class IdentityGrammar(BaseSegment):
    """`IDENTITY (1,1)` in table schemas.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-table-transact-sql-identity-property?view=sql-server-ver15
    """

    type = "identity_grammar"
    match_grammar = Sequence(
        "IDENTITY",
        # optional (seed, increment) e.g. (1, 1)
        Bracketed(
            Sequence(
                Ref("NumericLiteralSegment"),
                Ref("CommaSegment"),
                Ref("NumericLiteralSegment"),
            ),
            optional=True,
        ),
    )


@tsql_dialect.segment()
class TableDistributionIndexClause(BaseSegment):
    """`CREATE TABLE` distribution / index clause.

    This is specific to Azure Synapse Analytics.
    """

    type = "table_distribution_index_clause"

    match_grammar = Sequence(
        "WITH",
        Bracketed(
            Delimited(
                Ref("TableDistributionClause"),
                Ref("TableIndexClause"),
                Ref("TableLocationClause"),
            ),
        ),
    )


@tsql_dialect.segment()
class TableDistributionClause(BaseSegment):
    """`CREATE TABLE` distribution clause.

    This is specific to Azure Synapse Analytics.
    """

    type = "table_distribution_clause"

    match_grammar = Sequence(
        "DISTRIBUTION",
        Ref("EqualsSegment"),
        OneOf(
            "REPLICATE",
            "ROUND_ROBIN",
            Sequence(
                "HASH",
                Bracketed(Ref("ColumnReferenceSegment")),
            ),
        ),
    )


@tsql_dialect.segment()
class TableIndexClause(BaseSegment):
    """`CREATE TABLE` table index clause.

    This is specific to Azure Synapse Analytics.
    """

    type = "table_index_clause"

    match_grammar = Sequence(
        OneOf(
            "HEAP",
            Sequence(
                "CLUSTERED",
                "COLUMNSTORE",
                "INDEX",
            ),
        ),
    )


@tsql_dialect.segment()
class TableLocationClause(BaseSegment):
    """`CREATE TABLE` location clause.

    This is specific to Azure Synapse Analytics (deprecated) or to an external table.
    """

    type = "table_location_clause"

    match_grammar = Sequence(
        "LOCATION",
        Ref("EqualsSegment"),
        OneOf(
            "USER_DB",  # Azure Synapse Analytics specific
            Ref("QuotedLiteralSegment"),  # External Table
        ),
    )


@tsql_dialect.segment()
class AlterTableSwitchStatementSegment(BaseSegment):
    """An `ALTER TABLE SWITCH` statement."""

    type = "alter_table_switch_statement"
    # https://docs.microsoft.com/en-us/sql/t-sql/statements/alter-table-transact-sql?view=sql-server-ver15
    # T-SQL's ALTER TABLE SWITCH grammar is different enough to core ALTER TABLE grammar to merit its own definition
    match_grammar = Sequence(
        "ALTER",
        "TABLE",
        Ref("ObjectReferenceSegment"),
        "SWITCH",
        Sequence("PARTITION", Ref("NumericLiteralSegment"), optional=True),
        "TO",
        Ref("ObjectReferenceSegment"),
        Sequence(  # Azure Synapse Analytics specific
            "WITH",
            Bracketed("TRUNCATE_TARGET", Ref("EqualsSegment"), OneOf("ON", "OFF")),
            optional=True,
        ),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment()
class CreateTableAsSelectStatementSegment(BaseSegment):
    """A `CREATE TABLE AS SELECT` statement.

    This is specific to Azure Synapse Analytics.
    """

    type = "create_table_as_select_statement"
    # https://docs.microsoft.com/en-us/sql/t-sql/statements/create-table-as-select-azure-sql-data-warehouse?toc=/azure/synapse-analytics/sql-data-warehouse/toc.json&bc=/azure/synapse-analytics/sql-data-warehouse/breadcrumb/toc.json&view=azure-sqldw-latest&preserve-view=true
    match_grammar = Sequence(
        "CREATE",
        "TABLE",
        Ref("TableReferenceSegment"),
        Ref("TableDistributionIndexClause"),
        "AS",
        OptionallyBracketed(Ref("SelectableGrammar")),
        Ref("OptionClauseSegment", optional=True),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
class DatePartClause(BaseSegment):
    """DatePart clause for use within DATEADD() or related functions."""

    type = "date_part"

    match_grammar = OneOf(
        "D",
        "DAY",
        "DAYOFYEAR",
        "DD",
        "DW",
        "DY",
        "HH",
        "HOUR",
        "M",
        "MCS",
        "MI",
        "MICROSECOND",
        "MILLISECOND",
        "MINUTE",
        "MM",
        "MONTH",
        "MS",
        "N",
        "NANOSECOND",
        "NS",
        "Q",
        "QQ",
        "QUARTER",
        "S",
        "SECOND",
        "SS",
        "W",
        "WEEK",
        "WEEKDAY",
        "WK",
        "WW",
        "YEAR",
        "Y",
        "YY",
        "YYYY",
    )


@tsql_dialect.segment(replace=True)
class TransactionStatementSegment(BaseSegment):
    """A `COMMIT`, `ROLLBACK` or `TRANSACTION` statement."""

    type = "transaction_statement"
    match_grammar = OneOf(
        # BEGIN | SAVE TRANSACTION
        # COMMIT [ TRANSACTION | WORK ]
        # ROLLBACK [ TRANSACTION | WORK ]
        # https://docs.microsoft.com/en-us/sql/t-sql/language-elements/begin-transaction-transact-sql?view=sql-server-ver15
        Sequence(
            "BEGIN",
            Sequence("DISTRIBUTED", optional=True),
            "TRANSACTION",
            Ref("SingleIdentifierGrammar", optional=True),
            Sequence("WITH", "MARK", Ref("QuotedIdentifierSegment"), optional=True),
            Ref("DelimiterSegment", optional=True),
        ),
        Sequence(
            OneOf("COMMIT", "ROLLBACK"),
            OneOf("TRANSACTION", "WORK", optional=True),
            Ref("DelimiterSegment", optional=True),
        ),
        Sequence("SAVE", "TRANSACTION", Ref("DelimiterSegment", optional=True)),
    )


@tsql_dialect.segment()
class BeginEndSegment(BaseSegment):
    """A `BEGIN/END` block.

    Encloses multiple statements into a single statement object.
    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/begin-end-transact-sql?view=sql-server-ver15
    """

    type = "begin_end_block"
    match_grammar = Sequence(
        "BEGIN",
        Ref("DelimiterSegment", optional=True),
        Indent,
        AnyNumberOf(
            OneOf(
                Ref("BeginEndSegment"),
                Ref("StatementSegment"),
            ),
            min_times=1,
        ),
        Dedent,
        "END",
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment()
class BatchSegment(BaseSegment):
    """A segment representing a GO batch within a file or script."""

    type = "batch"
    match_grammar = OneOf(
        # Things that can be bundled
        AnyNumberOf(
            OneOf(
                Ref("BeginEndSegment"),
                Ref("StatementSegment"),
            ),
            min_times=1,
        ),
        # Things that can't be bundled
        Ref("CreateProcedureStatementSegment"),
    )


@tsql_dialect.segment(replace=True)
class FileSegment(BaseFileSegment):
    """A segment representing a whole file or script.

    We override default as T-SQL allows concept of several
    batches of commands separated by GO as well as usual
    semicolon-separated statement lines.

    This is also the default "root" segment of the dialect,
    and so is usually instantiated directly. It therefore
    has no match_grammar.
    """

    # NB: We don't need a match_grammar here because we're
    # going straight into instantiating it directly usually.
    parse_grammar = Delimited(
        Ref("BatchSegment"),
        delimiter=Ref("BatchDelimiterSegment"),
        allow_gaps=True,
        allow_trailing=True,
    )


@tsql_dialect.segment(replace=True)
class DeleteStatementSegment(BaseSegment):
    """A `DELETE` statement.

    DELETE FROM <table name> [ WHERE <search condition> ]
    Overriding ANSI to remove StartsWith logic which assumes statements have been delimited
    """

    type = "delete_statement"
    # match grammar. This one makes sense in the context of knowing that it's
    # definitely a statement, we just don't know what type yet.
    match_grammar = Sequence(
        "DELETE",
        Ref("FromClauseSegment"),
        Ref("WhereClauseSegment", optional=True),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
class FromClauseSegment(BaseSegment):
    """A `FROM` clause like in `SELECT`.

    NOTE: this is a delimited set of table expressions, with a variable
    number of optional join clauses with those table expressions. The
    delmited aspect is the higher of the two such that the following is
    valid (albeit unusual):

    ```
    SELECT *
    FROM a JOIN b, c JOIN d
    ```

    Overriding ANSI to remove Delimited logic which assumes statements have been delimited
    """

    type = "from_clause"
    match_grammar = Sequence(
        "FROM",
        AnyNumberOf(
            Sequence(
                Ref("FromExpressionSegment"),
                Ref("CommaSegment"),
            ),
        ),
        Ref("FromExpressionSegment"),
        Ref("DelimiterSegment", optional=True),
    )

    get_eventual_aliases = ansi_dialect.get_segment(
        "FromClauseSegment"
    ).get_eventual_aliases


@tsql_dialect.segment(replace=True)
class GroupByClauseSegment(BaseSegment):
    """A `GROUP BY` clause like in `SELECT`.

    Overriding ANSI to remove Delimited logic which assumes statements have been delimited
    """

    type = "groupby_clause"
    match_grammar = Sequence(
        "GROUP",
        "BY",
        Indent,
        OneOf(
            Ref("ColumnReferenceSegment"),
            # Can `GROUP BY 1`
            Ref("NumericLiteralSegment"),
            # Can `GROUP BY coalesce(col, 1)`
            Ref("ExpressionSegment"),
        ),
        AnyNumberOf(
            Ref("CommaSegment"),
            OneOf(
                Ref("ColumnReferenceSegment"),
                # Can `GROUP BY 1`
                Ref("NumericLiteralSegment"),
                # Can `GROUP BY coalesce(col, 1)`
                Ref("ExpressionSegment"),
            ),
        ),
        Dedent,
    )


@tsql_dialect.segment(replace=True)
class HavingClauseSegment(BaseSegment):
    """A `HAVING` clause like in `SELECT`.

    Overriding ANSI to remove StartsWith with greedy terminator
    """

    type = "having_clause"
    match_grammar = Sequence(
        "HAVING",
        Indent,
        OptionallyBracketed(Ref("ExpressionSegment")),
        Dedent,
    )


@tsql_dialect.segment(replace=True)
class OrderByClauseSegment(BaseSegment):
    """A `ORDER BY` clause like in `SELECT`.

    Overriding ANSI to remove StartsWith logic which assumes statements have been delimited
    """

    type = "orderby_clause"
    match_grammar = Sequence(
        "ORDER",
        "BY",
        Indent,
        Sequence(
            OneOf(
                Ref("ColumnReferenceSegment"),
                # Can `ORDER BY 1`
                Ref("NumericLiteralSegment"),
                # Can order by an expression
                Ref("ExpressionSegment"),
            ),
            OneOf("ASC", "DESC", optional=True),
        ),
        AnyNumberOf(
            Sequence(
                Ref("CommaSegment"),
                Sequence(
                    OneOf(
                        Ref("ColumnReferenceSegment"),
                        # Can `ORDER BY 1`
                        Ref("NumericLiteralSegment"),
                        # Can order by an expression
                        Ref("ExpressionSegment"),
                    ),
                    OneOf("ASC", "DESC", optional=True),
                ),
            ),
        ),
        Dedent,
    )


@tsql_dialect.segment()
class RenameStatementSegment(BaseSegment):
    """`RENAME` statement.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/rename-transact-sql?view=aps-pdw-2016-au7
    Azure Synapse Analytics-specific.
    """

    type = "rename_statement"
    match_grammar = Sequence(
        "RENAME",
        "OBJECT",
        Ref("ObjectReferenceSegment"),
        "TO",
        Ref("SingleIdentifierGrammar"),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
class DropStatementSegment(BaseSegment):
    """A `DROP` statement.

    Overriding ANSI to add optional delimiter.
    """

    type = "drop_statement"
    match_grammar = ansi_dialect.get_segment("DropStatementSegment").match_grammar.copy(
        insert=[
            Ref("DelimiterSegment", optional=True),
        ],
    )


@tsql_dialect.segment(replace=True)
class UpdateStatementSegment(BaseSegment):
    """An `Update` statement.

    UPDATE <table name> SET <set clause list> [ WHERE <search condition> ]
    Overriding ANSI in order to allow for PostTableExpressionGrammar (table hints)
    """

    type = "update_statement"
    match_grammar = Sequence(
        "UPDATE",
        OneOf(Ref("TableReferenceSegment"), Ref("AliasedTableReferenceGrammar")),
        Ref("PostTableExpressionGrammar", optional=True),
        Ref("SetClauseListSegment"),
        Ref("FromClauseSegment", optional=True),
        Ref("WhereClauseSegment", optional=True),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
class SetClauseListSegment(BaseSegment):
    """set clause list.

    Overriding ANSI to remove Delimited
    """

    type = "set_clause_list"
    match_grammar = Sequence(
        "SET",
        Indent,
        Ref("SetClauseSegment"),
        AnyNumberOf(
            Ref("CommaSegment"),
            Ref("SetClauseSegment"),
        ),
        Dedent,
    )


@tsql_dialect.segment(replace=True)
class SetClauseSegment(BaseSegment):
    """Set clause.

    Overriding ANSI to allow for ExpressionSegment on the right
    """

    type = "set_clause"

    match_grammar = Sequence(
        Ref("ColumnReferenceSegment"),
        Ref("EqualsSegment"),
        Ref("ExpressionSegment"),
    )


@tsql_dialect.segment(replace=True)
class DatePartFunctionNameSegment(BaseSegment):
    """DATEADD function name segment.

    Override to support DATEDIFF as well
    """

    type = "function_name"
    match_grammar = OneOf("DATEADD", "DATEDIFF", "DATEDIFF_BIG", "DATENAME")


@tsql_dialect.segment()
class PrintStatementSegment(BaseSegment):
    """PRINT statement segment."""

    type = "print_statement"
    match_grammar = Sequence(
        "PRINT",
        Ref("ExpressionSegment"),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment()
class OptionClauseSegment(BaseSegment):
    """Query Hint clause.

    https://docs.microsoft.com/en-us/sql/t-sql/queries/hints-transact-sql-query?view=sql-server-ver15
    """

    type = "option_clause"
    match_grammar = Sequence(
        Sequence("OPTION", optional=True),
        Bracketed(
            Ref("QueryHintSegment"),
            AnyNumberOf(
                Ref("CommaSegment"),
                Ref("QueryHintSegment"),
            ),
        ),
    )


@tsql_dialect.segment()
class QueryHintSegment(BaseSegment):
    """Query Hint segment.

    https://docs.microsoft.com/en-us/sql/t-sql/queries/hints-transact-sql-query?view=sql-server-ver15
    """

    type = "query_hint_segment"
    match_grammar = OneOf(
        Sequence(  # Azure Synapse Analytics specific
            "LABEL",
            Ref("EqualsSegment"),
            Ref("QuotedLiteralSegment"),
        ),
        Sequence(
            OneOf("HASH", "ORDER"),
            "GROUP",
        ),
        Sequence(OneOf("MERGE", "HASH", "CONCAT"), "UNION"),
        Sequence(OneOf("LOOP", "MERGE", "HASH"), "JOIN"),
        Sequence("EXPAND", "VIEWS"),
        Sequence(
            OneOf(
                "FAST",
                "MAXDOP",
                "MAXRECURSION",
                "QUERYTRACEON",
                Sequence(
                    OneOf(
                        "MAX_GRANT_PERCENT",
                        "MIN_GRANT_PERCENT",
                    ),
                    Ref("EqualsSegment"),
                ),
            ),
            Ref("NumericLiteralSegment"),
        ),
        Sequence("FORCE", "ORDER"),
        Sequence(
            OneOf("FORCE", "DISABLE"),
            OneOf("EXTERNALPUSHDOWN", "SCALEOUTEXECUTION"),
        ),
        Sequence(
            OneOf(
                "KEEP",
                "KEEPFIXED",
                "ROBUST",
            ),
            "PLAN",
        ),
        "IGNORE_NONCLUSTERED_COLUMNSTORE_INDEX",
        "NO_PERFORMANCE_SPOOL",
        Sequence(
            "OPTIMIZE",
            "FOR",
            OneOf(
                "UNKNOWN",
                Bracketed(
                    Ref("ParameterNameSegment"),
                    OneOf(
                        "UNKNOWN", Sequence(Ref("EqualsSegment"), Ref("LiteralGrammar"))
                    ),
                    AnyNumberOf(
                        Ref("CommaSegment"),
                        Ref("ParameterNameSegment"),
                        OneOf(
                            "UNKNOWN",
                            Sequence(Ref("EqualsSegment"), Ref("LiteralGrammar")),
                        ),
                    ),
                ),
            ),
        ),
        Sequence("PARAMETERIZATION", OneOf("SIMPLE", "FORCED")),
        "RECOMPILE",
        Sequence(
            "USE",
            "HINT",
            Bracketed(
                Ref("QuotedLiteralSegment"),
                AnyNumberOf(Ref("CommaSegment"), Ref("QuotedLiteralSegment")),
            ),
        ),
        Sequence(
            "USE",
            "PLAN",
            OneOf(Ref("QuotedLiteralSegment"), Ref("QuotedLiteralSegmentWithN")),
        ),
        Sequence(
            "TABLE",
            "HINT",
            Ref("ObjectReferenceSegment"),
            Ref("TableHintSegment"),
            AnyNumberOf(
                Ref("CommaSegment"),
                Ref("TableHintSegment"),
            ),
        ),
    )


@tsql_dialect.segment(replace=True)
class PostTableExpressionGrammar(BaseSegment):
    """Table Hint clause.  Overloading the PostTableExpressionGrammar to implement.

    https://docs.microsoft.com/en-us/sql/t-sql/queries/hints-transact-sql-table?view=sql-server-ver15
    """

    match_grammar = Sequence(
        Sequence("WITH", optional=True),
        Bracketed(
            Ref("TableHintSegment"),
            AnyNumberOf(
                Ref("CommaSegment"),
                Ref("TableHintSegment"),
            ),
        ),
    )


@tsql_dialect.segment()
class TableHintSegment(BaseSegment):
    """Table Hint segment.

    https://docs.microsoft.com/en-us/sql/t-sql/queries/hints-transact-sql-table?view=sql-server-ver15
    """

    type = "query_hint_segment"
    match_grammar = OneOf(
        "NOEXPAND",
        Sequence(
            "INDEX",
            Bracketed(
                OneOf(Ref("IndexReferenceSegment"), Ref("NumericLiteralSegment")),
                AnyNumberOf(
                    Ref("CommaSegment"),
                    OneOf(
                        Ref("IndexReferenceSegment"),
                        Ref("NumericLiteralSegment"),
                    ),
                ),
            ),
        ),
        Sequence(
            "INDEX",
            Ref("EqualsSegment"),
            Bracketed(
                OneOf(Ref("IndexReferenceSegment"), Ref("NumericLiteralSegment")),
            ),
        ),
        "KEEPIDENTITY",
        "KEEPDEFAULTS",
        Sequence(
            "FORCESEEK",
            Bracketed(
                Ref("IndexReferenceSegment"),
                Bracketed(
                    Ref("SingleIdentifierGrammar"),
                    AnyNumberOf(Ref("CommaSegment"), Ref("SingleIdentifierGrammar")),
                ),
                optional=True,
            ),
        ),
        "FORCESCAN",
        "HOLDLOCK",
        "IGNORE_CONSTRAINTS",
        "IGNORE_TRIGGERS",
        "NOLOCK",
        "NOWAIT",
        "PAGLOCK",
        "READCOMMITTED",
        "READCOMMITTEDLOCK",
        "READPAST",
        "READUNCOMMITTED",
        "REPEATABLEREAD",
        "ROWLOCK",
        "SERIALIZABLE",
        "SNAPSHOT",
        Sequence(
            "SPATIAL_WINDOW_MAX_CELLS",
            Ref("EqualsSegment"),
            Ref("NumericLiteralSegment"),
        ),
        "TABLOCK",
        "TABLOCKX",
        "UPDLOCK",
        "XLOCK",
    )


@tsql_dialect.segment(replace=True)
class SetExpressionSegment(BaseSegment):
    """A set expression with either Union, Minus, Except or Intersect.

    Overriding ANSI to include OPTION clause.
    """

    type = "set_expression"
    # match grammar
    match_grammar = Sequence(
        Ref("NonSetSelectableGrammar"),
        AnyNumberOf(
            Sequence(
                Ref("SetOperatorSegment"),
                Ref("NonSetSelectableGrammar"),
            ),
            min_times=1,
        ),
        Ref("OrderByClauseSegment", optional=True),
        Ref("OptionClauseSegment", optional=True),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment()
class ExecuteScriptSegment(BaseSegment):
    """`EXECUTE` statement.

    Matching segment name and type from exasol.
    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/execute-transact-sql?view=sql-server-ver15
    """

    type = "execute_script_statement"
    match_grammar = Sequence(
        OneOf("EXEC", "EXECUTE"),
        Ref("ObjectReferenceSegment"),
        Sequence(
            Sequence(Ref("ParameterNameSegment"), Ref("EqualsSegment"), optional=True),
            OneOf(
                "DEFAULT",
                Ref("LiteralGrammar"),
                Ref("ParameterNameSegment"),
                Ref("SingleIdentifierGrammar"),
            ),
            Sequence("OUTPUT", optional=True),
            AnyNumberOf(
                Ref("CommaSegment"),
                Sequence(
                    Ref("ParameterNameSegment"), Ref("EqualsSegment"), optional=True
                ),
                OneOf(
                    "DEFAULT",
                    Ref("LiteralGrammar"),
                    Ref("ParameterNameSegment"),
                    Ref("SingleIdentifierGrammar"),
                ),
                Sequence("OUTPUT", optional=True),
            ),
            optional=True,
        ),
        Ref("DelimiterSegment", optional=True),
    )

```
### 3 - src/sqlfluff/rules/L039.py:

```python
"""Implementation of Rule L039."""
from typing import List, Optional

from sqlfluff.core.parser import WhitespaceSegment

from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L039(BaseRule):
    """Unnecessary whitespace found.

    | **Anti-pattern**

    .. code-block:: sql

        SELECT
            a,        b
        FROM foo

    | **Best practice**
    | Unless an indent or preceding a comment, whitespace should
    | be a single space.

    .. code-block:: sql

        SELECT
            a, b
        FROM foo
    """

    def _eval(self, context: RuleContext) -> Optional[List[LintResult]]:
        """Unnecessary whitespace."""
        # For the given segment, lint whitespace directly within it.
        prev_newline = True
        prev_whitespace = None
        violations = []
        for seg in context.segment.segments:
            if seg.is_type("newline"):
                prev_newline = True
                prev_whitespace = None
            elif seg.is_type("whitespace"):
                # This is to avoid indents
                if not prev_newline:
                    prev_whitespace = seg
                # We won't set prev_newline to False, just for whitespace
                # in case there's multiple indents, inserted by other rule
                # fixes (see #1713)
            elif seg.is_type("comment"):
                prev_newline = False
                prev_whitespace = None
            else:
                if prev_whitespace:
                    if prev_whitespace.raw != " ":
                        violations.append(
                            LintResult(
                                anchor=prev_whitespace,
                                fixes=[
                                    LintFix(
                                        "edit",
                                        prev_whitespace,
                                        WhitespaceSegment(),
                                    )
                                ],
                            )
                        )
                prev_newline = False
                prev_whitespace = None
        return violations or None

```
### 4 - src/sqlfluff/dialects/dialect_tsql.py:

```python
"""The MSSQL T-SQL dialect.

https://docs.microsoft.com/en-us/sql/t-sql/language-elements/language-elements-transact-sql
"""

from sqlfluff.core.parser import (
    BaseSegment,
    Sequence,
    OneOf,
    Bracketed,
    Ref,
    Anything,
    Nothing,
    RegexLexer,
    CodeSegment,
    RegexParser,
    Delimited,
    Matchable,
    NamedParser,
    OptionallyBracketed,
    Dedent,
    BaseFileSegment,
    Indent,
    AnyNumberOf,
    CommentSegment,
    StringParser,
    SymbolSegment,
    SegmentGenerator,
)

from sqlfluff.core.dialects import load_raw_dialect

from sqlfluff.dialects.dialect_tsql_keywords import (
    RESERVED_KEYWORDS,
    UNRESERVED_KEYWORDS,
)

ansi_dialect = load_raw_dialect("ansi")
tsql_dialect = ansi_dialect.copy_as("tsql")

# Should really clear down the old keywords but some are needed by certain segments
# tsql_dialect.sets("reserved_keywords").clear()
# tsql_dialect.sets("unreserved_keywords").clear()
tsql_dialect.sets("reserved_keywords").update(RESERVED_KEYWORDS)
tsql_dialect.sets("unreserved_keywords").update(UNRESERVED_KEYWORDS)

tsql_dialect.insert_lexer_matchers(
    [
        RegexLexer(
            "atsign",
            r"[@][a-zA-Z0-9_]+",
            CodeSegment,
        ),
        RegexLexer(
            "square_quote",
            r"\[([^\[\]]*)*\]",
            CodeSegment,
        ),
        # T-SQL unicode strings
        RegexLexer("single_quote_with_n", r"N'([^']|'')*'", CodeSegment),
        RegexLexer(
            "hash_prefix",
            r"[#][#]?[a-zA-Z0-9_]+",
            CodeSegment,
        ),
    ],
    before="back_quote",
)

tsql_dialect.patch_lexer_matchers(
    [
        # Patching single_quote to allow for TSQL-style escaped quotes
        RegexLexer("single_quote", r"'([^']|'')*'", CodeSegment),
        # Patching comments to remove hash comments
        RegexLexer(
            "inline_comment",
            r"(--)[^\n]*",
            CommentSegment,
            segment_kwargs={"trim_start": ("--")},
        ),
        # Patching to add !<, !>
        RegexLexer("greater_than_or_equal", ">=|!<", CodeSegment),
        RegexLexer("less_than_or_equal", "<=|!>", CodeSegment),
        RegexLexer(
            "code", r"[0-9a-zA-Z_#@]+", CodeSegment
        ),  # overriding to allow hash mark and at-sign in code
    ]
)

tsql_dialect.add(
    BracketedIdentifierSegment=NamedParser(
        "square_quote", CodeSegment, name="quoted_identifier", type="identifier"
    ),
    HashIdentifierSegment=NamedParser(
        "hash_prefix", CodeSegment, name="hash_identifier", type="identifier"
    ),
    BatchDelimiterSegment=Ref("GoStatementSegment"),
    QuotedLiteralSegmentWithN=NamedParser(
        "single_quote_with_n", CodeSegment, name="quoted_literal", type="literal"
    ),
    NotGreaterThanSegment=StringParser(
        "!>", SymbolSegment, name="less_than_equal_to", type="comparison_operator"
    ),
    NotLessThanSegment=StringParser(
        "!<", SymbolSegment, name="greater_than_equal_to", type="comparison_operator"
    ),
)

tsql_dialect.replace(
    # Overriding to cover TSQL allowed identifier name characters
    # https://docs.microsoft.com/en-us/sql/relational-databases/databases/database-identifiers?view=sql-server-ver15
    NakedIdentifierSegment=SegmentGenerator(
        # Generate the anti template from the set of reserved keywords
        lambda dialect: RegexParser(
            r"[A-Z_][A-Z0-9_@$#]*",
            CodeSegment,
            name="naked_identifier",
            type="identifier",
            anti_template=r"^(" + r"|".join(dialect.sets("reserved_keywords")) + r")$",
        )
    ),
    ComparisonOperatorGrammar=OneOf(
        Ref("EqualsSegment"),
        Ref("GreaterThanSegment"),
        Ref("LessThanSegment"),
        Ref("GreaterThanOrEqualToSegment"),
        Ref("LessThanOrEqualToSegment"),
        Ref("NotEqualToSegment_a"),
        Ref("NotEqualToSegment_b"),
        Ref("LikeOperatorSegment"),
        Ref("NotGreaterThanSegment"),
        Ref("NotLessThanSegment"),
    ),
    SingleIdentifierGrammar=OneOf(
        Ref("NakedIdentifierSegment"),
        Ref("QuotedIdentifierSegment"),
        Ref("BracketedIdentifierSegment"),
        Ref("HashIdentifierSegment"),
        Ref("ParameterNameSegment"),
    ),
    LiteralGrammar=OneOf(
        Ref("QuotedLiteralSegment"),
        Ref("QuotedLiteralSegmentWithN"),
        Ref("NumericLiteralSegment"),
        Ref("BooleanLiteralGrammar"),
        Ref("QualifiedNumericLiteralSegment"),
        # NB: Null is included in the literals, because it is a keyword which
        # can otherwise be easily mistaken for an identifier.
        Ref("NullLiteralSegment"),
        Ref("DateTimeLiteralGrammar"),
    ),
    ParameterNameSegment=RegexParser(
        r"[@][A-Za-z0-9_]+", CodeSegment, name="parameter", type="parameter"
    ),
    FunctionNameIdentifierSegment=RegexParser(
        r"[A-Z][A-Z0-9_]*|\[[A-Z][A-Z0-9_]*\]",
        CodeSegment,
        name="function_name_identifier",
        type="function_name_identifier",
    ),
    DatatypeIdentifierSegment=Ref("SingleIdentifierGrammar"),
    PrimaryKeyGrammar=Sequence(
        "PRIMARY", "KEY", OneOf("CLUSTERED", "NONCLUSTERED", optional=True)
    ),
    # Overriding SelectClauseSegmentGrammar to remove Delimited logic which assumes statements have been delimited
    SelectClauseSegmentGrammar=Sequence(
        "SELECT",
        Ref("SelectClauseModifierSegment", optional=True),
        Indent,
        AnyNumberOf(
            Sequence(
                Ref("SelectClauseElementSegment"),
                Ref("CommaSegment"),
            ),
        ),
        Ref("SelectClauseElementSegment"),
        # NB: The Dedent for the indent above lives in the
        # SelectStatementSegment so that it sits in the right
        # place corresponding to the whitespace.
    ),
    FromClauseTerminatorGrammar=OneOf(
        "WHERE",
        "LIMIT",
        Sequence("GROUP", "BY"),
        Sequence("ORDER", "BY"),
        "HAVING",
        "PIVOT",
        "UNPIVOT",
        Ref("SetOperatorSegment"),
        Ref("WithNoSchemaBindingClauseSegment"),
        Ref("DelimiterSegment"),
    ),
    JoinKeywords=OneOf("JOIN", "APPLY", Sequence("OUTER", "APPLY")),
    # Replace Expression_D_Grammar to remove casting syntax invalid in TSQL
    Expression_D_Grammar=Sequence(
        OneOf(
            Ref("BareFunctionSegment"),
            Ref("FunctionSegment"),
            Bracketed(
                OneOf(
                    # We're using the expression segment here rather than the grammar so
                    # that in the parsed structure we get nested elements.
                    Ref("ExpressionSegment"),
                    Ref("SelectableGrammar"),
                    Delimited(
                        Ref(
                            "ColumnReferenceSegment"
                        ),  # WHERE (a,b,c) IN (select a,b,c FROM...)
                        Ref(
                            "FunctionSegment"
                        ),  # WHERE (a, substr(b,1,3)) IN (select c,d FROM...)
                        Ref("LiteralGrammar"),  # WHERE (a, 2) IN (SELECT b, c FROM ...)
                    ),
                    ephemeral_name="BracketedExpression",
                ),
            ),
            # Allow potential select statement without brackets
            Ref("SelectStatementSegment"),
            Ref("LiteralGrammar"),
            Ref("IntervalExpressionSegment"),
            Ref("ColumnReferenceSegment"),
            Sequence(
                Ref("SimpleArrayTypeGrammar", optional=True), Ref("ArrayLiteralSegment")
            ),
        ),
        Ref("Accessor_Grammar", optional=True),
        allow_gaps=True,
    ),
)


@tsql_dialect.segment(replace=True)
class AliasExpressionSegment(BaseSegment):
    """A reference to an object with an `AS` clause.

    The optional AS keyword allows both implicit and explicit aliasing.
    Overriding ANSI to remove QuotedLiteralSegment
    """

    type = "alias_expression"
    match_grammar = Sequence(
        Ref.keyword("AS", optional=True),
        OneOf(
            Sequence(
                Ref("SingleIdentifierGrammar"),
                # Column alias in VALUES clause
                Bracketed(Ref("SingleIdentifierListSegment"), optional=True),
            ),
        ),
    )


@tsql_dialect.segment(replace=True)
class StatementSegment(ansi_dialect.get_segment("StatementSegment")):  # type: ignore
    """Overriding StatementSegment to allow for additional segment parsing."""

    match_grammar = ansi_dialect.get_segment("StatementSegment").parse_grammar.copy(
        insert=[
            Ref("IfExpressionStatement"),
            Ref("DeclareStatementSegment"),
            Ref("SetStatementSegment"),
            Ref("AlterTableSwitchStatementSegment"),
            Ref("PrintStatementSegment"),
            Ref(
                "CreateTableAsSelectStatementSegment"
            ),  # Azure Synapse Analytics specific
            Ref("RenameStatementSegment"),  # Azure Synapse Analytics specific
            Ref("ExecuteScriptSegment"),
            Ref("DropStatisticsStatementSegment"),
            Ref("UpdateStatisticsStatementSegment"),
        ],
    )

    parse_grammar = match_grammar


@tsql_dialect.segment(replace=True)
class SelectClauseElementSegment(BaseSegment):
    """An element in the targets of a select statement.

    Overriding ANSI to remove GreedyUntil logic which assumes statements have been delimited
    """

    type = "select_clause_element"
    # Important to split elements before parsing, otherwise debugging is really hard.
    match_grammar = OneOf(
        # *, blah.*, blah.blah.*, etc.
        Ref("WildcardExpressionSegment"),
        Sequence(
            Ref("BaseExpressionElementGrammar"),
            Ref("AliasExpressionSegment", optional=True),
        ),
    )


@tsql_dialect.segment(replace=True)
class SelectClauseModifierSegment(BaseSegment):
    """Things that come after SELECT but before the columns."""

    type = "select_clause_modifier"
    match_grammar = OneOf(
        "DISTINCT",
        "ALL",
        Sequence(
            "TOP",
            OptionallyBracketed(Ref("ExpressionSegment")),
            Sequence("PERCENT", optional=True),
            Sequence("WITH", "TIES", optional=True),
        ),
    )


@tsql_dialect.segment(replace=True)
class SelectClauseSegment(BaseSegment):
    """A group of elements in a select target statement.

    Overriding ANSI to remove StartsWith logic which assumes statements have been delimited
    """

    type = "select_clause"
    match_grammar = Ref("SelectClauseSegmentGrammar")


@tsql_dialect.segment(replace=True)
class UnorderedSelectStatementSegment(BaseSegment):
    """A `SELECT` statement without any ORDER clauses or later.

    We need to change ANSI slightly to remove LimitClauseSegment
    and NamedWindowSegment which don't exist in T-SQL.

    We also need to get away from ANSI's use of StartsWith.
    There's not a clean list of terminators that can be used
    to identify the end of a TSQL select statement.  Semi-colon is optional.
    """

    type = "select_statement"
    match_grammar = Sequence(
        Ref("SelectClauseSegment"),
        # Dedent for the indent in the select clause.
        # It's here so that it can come AFTER any whitespace.
        Dedent,
        Ref("IntoTableSegment", optional=True),
        Ref("FromClauseSegment", optional=True),
        Ref("PivotUnpivotStatementSegment", optional=True),
        Ref("WhereClauseSegment", optional=True),
        Ref("GroupByClauseSegment", optional=True),
        Ref("HavingClauseSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
class SelectStatementSegment(BaseSegment):
    """A `SELECT` statement.

    We need to change ANSI slightly to remove LimitClauseSegment
    and NamedWindowSegment which don't exist in T-SQL.

    We also need to get away from ANSI's use of StartsWith.
    There's not a clean list of terminators that can be used
    to identify the end of a TSQL select statement.  Semi-colon is optional.
    """

    type = "select_statement"
    # Remove the Limit and Window statements from ANSI
    match_grammar = UnorderedSelectStatementSegment.match_grammar.copy(
        insert=[
            Ref("OrderByClauseSegment", optional=True),
            Ref("OptionClauseSegment", optional=True),
            Ref("DelimiterSegment", optional=True),
        ]
    )


@tsql_dialect.segment()
class IntoTableSegment(BaseSegment):
    """`INTO` clause within `SELECT`.

    https://docs.microsoft.com/en-us/sql/t-sql/queries/select-into-clause-transact-sql?view=sql-server-ver15
    """

    type = "into_table_clause"
    match_grammar = Sequence("INTO", Ref("ObjectReferenceSegment"))


@tsql_dialect.segment(replace=True)
class WhereClauseSegment(BaseSegment):
    """A `WHERE` clause like in `SELECT` or `INSERT`.

    Overriding ANSI in order to get away from the use of
    StartsWith. There's not a clean list of terminators that can be used
    to identify the end of a TSQL select statement.  Semi-colon is optional.
    """

    type = "where_clause"
    match_grammar = Sequence(
        "WHERE",
        Indent,
        OptionallyBracketed(Ref("ExpressionSegment")),
        Dedent,
    )


@tsql_dialect.segment(replace=True)
class CreateIndexStatementSegment(BaseSegment):
    """A `CREATE INDEX` or `CREATE STATISTICS` statement.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-index-transact-sql?view=sql-server-ver15
    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-statistics-transact-sql?view=sql-server-ver15
    """

    type = "create_index_statement"
    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Sequence("UNIQUE", optional=True),
        OneOf("CLUSTERED", "NONCLUSTERED", optional=True),
        OneOf("INDEX", "STATISTICS"),
        Ref("IfNotExistsGrammar", optional=True),
        Ref("IndexReferenceSegment"),
        "ON",
        Ref("TableReferenceSegment"),
        Sequence(
            Bracketed(
                Delimited(
                    Ref("IndexColumnDefinitionSegment"),
                ),
            )
        ),
        Sequence(
            "INCLUDE",
            Sequence(
                Bracketed(
                    Delimited(
                        Ref("IndexColumnDefinitionSegment"),
                    ),
                )
            ),
            optional=True,
        ),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
class DropIndexStatementSegment(BaseSegment):
    """A `DROP INDEX` statement.

    Overriding ANSI to include required ON clause.
    """

    type = "drop_statement"
    match_grammar = Sequence(
        "DROP",
        "INDEX",
        Ref("IfExistsGrammar", optional=True),
        Ref("IndexReferenceSegment"),
        "ON",
        Ref("TableReferenceSegment"),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment()
class DropStatisticsStatementSegment(BaseSegment):
    """A `DROP STATISTICS` statement."""

    type = "drop_statement"
    # DROP INDEX <Index name> [CONCURRENTLY] [IF EXISTS] {RESTRICT | CASCADE}
    match_grammar = Sequence(
        "DROP",
        OneOf("STATISTICS"),
        Ref("IndexReferenceSegment"),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment()
class UpdateStatisticsStatementSegment(BaseSegment):
    """An `UPDATE STATISTICS` statement.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/update-statistics-transact-sql?view=sql-server-ver15
    """

    type = "update_statistics_statement"
    match_grammar = Sequence(
        "UPDATE",
        "STATISTICS",
        Ref("ObjectReferenceSegment"),
        OneOf(
            Ref("SingleIdentifierGrammar"),
            Bracketed(
                Delimited(
                    Ref("SingleIdentifierGrammar"),
                ),
            ),
            optional=True,
        ),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
class ObjectReferenceSegment(BaseSegment):
    """A reference to an object.

    Update ObjectReferenceSegment to only allow dot separated SingleIdentifierGrammar
    So Square Bracketed identifiers can be matched.
    """

    type = "object_reference"
    # match grammar (allow whitespace)
    match_grammar: Matchable = Sequence(
        Ref("SingleIdentifierGrammar"),
        AnyNumberOf(
            Sequence(
                Ref("DotSegment"),
                Ref("SingleIdentifierGrammar", optional=True),
            ),
            min_times=0,
            max_times=3,
        ),
    )

    ObjectReferencePart = ansi_dialect.get_segment(
        "ObjectReferenceSegment"
    ).ObjectReferencePart

    _iter_reference_parts = ansi_dialect.get_segment(
        "ObjectReferenceSegment"
    )._iter_reference_parts

    iter_raw_references = ansi_dialect.get_segment(
        "ObjectReferenceSegment"
    ).iter_raw_references

    is_qualified = ansi_dialect.get_segment("ObjectReferenceSegment").is_qualified

    qualification = ansi_dialect.get_segment("ObjectReferenceSegment").qualification

    ObjectReferenceLevel = ansi_dialect.get_segment(
        "ObjectReferenceSegment"
    ).ObjectReferenceLevel

    extract_possible_references = ansi_dialect.get_segment(
        "ObjectReferenceSegment"
    ).extract_possible_references

    _level_to_int = staticmethod(
        ansi_dialect.get_segment("ObjectReferenceSegment")._level_to_int
    )


@tsql_dialect.segment(replace=True)
class TableReferenceSegment(ObjectReferenceSegment):
    """A reference to an table, CTE, subquery or alias.

    Overriding to capture TSQL's override of ObjectReferenceSegment
    """

    type = "table_reference"


@tsql_dialect.segment(replace=True)
class SchemaReferenceSegment(ObjectReferenceSegment):
    """A reference to a schema.

    Overriding to capture TSQL's override of ObjectReferenceSegment
    """

    type = "schema_reference"


@tsql_dialect.segment(replace=True)
class DatabaseReferenceSegment(ObjectReferenceSegment):
    """A reference to a database.

    Overriding to capture TSQL's override of ObjectReferenceSegment
    """

    type = "database_reference"


@tsql_dialect.segment(replace=True)
class IndexReferenceSegment(ObjectReferenceSegment):
    """A reference to an index.

    Overriding to capture TSQL's override of ObjectReferenceSegment
    """

    type = "index_reference"


@tsql_dialect.segment(replace=True)
class ExtensionReferenceSegment(ObjectReferenceSegment):
    """A reference to an extension.

    Overriding to capture TSQL's override of ObjectReferenceSegment
    """

    type = "extension_reference"


@tsql_dialect.segment(replace=True)
class ColumnReferenceSegment(ObjectReferenceSegment):
    """A reference to column, field or alias.

    Overriding to capture TSQL's override of ObjectReferenceSegment
    """

    type = "column_reference"


@tsql_dialect.segment(replace=True)
class SequenceReferenceSegment(ObjectReferenceSegment):
    """A reference to a sequence.

    Overriding to capture TSQL's override of ObjectReferenceSegment
    """

    type = "sequence_reference"


@tsql_dialect.segment()
class PivotColumnReferenceSegment(ObjectReferenceSegment):
    """A reference to a PIVOT column to differentiate it from a regular column reference."""

    type = "pivot_column_reference"


@tsql_dialect.segment()
class PivotUnpivotStatementSegment(BaseSegment):
    """Declaration of a variable.

    https://docs.microsoft.com/en-us/sql/t-sql/queries/from-using-pivot-and-unpivot?view=sql-server-ver15
    """

    type = "from_pivot_expression"
    match_grammar = Sequence(
        OneOf(
            Sequence(
                "PIVOT",
                OptionallyBracketed(
                    Sequence(
                        OptionallyBracketed(Ref("FunctionSegment")),
                        "FOR",
                        Ref("ColumnReferenceSegment"),
                        "IN",
                        Bracketed(Delimited(Ref("PivotColumnReferenceSegment"))),
                    )
                ),
            ),
            Sequence(
                "UNPIVOT",
                OptionallyBracketed(
                    Sequence(
                        OptionallyBracketed(Ref("ColumnReferenceSegment")),
                        "FOR",
                        Ref("ColumnReferenceSegment"),
                        "IN",
                        Bracketed(Delimited(Ref("PivotColumnReferenceSegment"))),
                    )
                ),
            ),
        ),
        "AS",
        Ref("TableReferenceSegment"),
    )


@tsql_dialect.segment()
class DeclareStatementSegment(BaseSegment):
    """Declaration of a variable.

    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/declare-local-variable-transact-sql?view=sql-server-ver15
    """

    type = "declare_segment"
    match_grammar = Sequence(
        "DECLARE",
        Ref("ParameterNameSegment"),
        Sequence("AS", optional=True),
        Ref("DatatypeSegment"),
        Sequence(
            Ref("EqualsSegment"),
            Ref("ExpressionSegment"),
            optional=True,
        ),
        AnyNumberOf(
            Ref("CommaSegment"),
            Ref("ParameterNameSegment"),
            Ref("DatatypeSegment"),
            Sequence(
                Ref("EqualsSegment"),
                Ref("ExpressionSegment"),
                optional=True,
            ),
        ),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment()
class GoStatementSegment(BaseSegment):
    """GO signals the end of a batch of Transact-SQL statements to the SQL Server utilities.

    GO statements are not part of the TSQL language. They are used to signal batch statements
    so that clients know in how batches of statements can be executed.
    """

    type = "go_statement"
    match_grammar = Sequence("GO")


@tsql_dialect.segment(replace=True)
class DatatypeSegment(BaseSegment):
    """A data type segment.

    Updated for Transact-SQL to allow bracketed data types with bracketed schemas.
    """

    type = "data_type"
    match_grammar = Sequence(
        # Some dialects allow optional qualification of data types with schemas
        Sequence(
            Ref("SingleIdentifierGrammar"),
            Ref("DotSegment"),
            allow_gaps=False,
            optional=True,
        ),
        OneOf(
            Ref("DatatypeIdentifierSegment"),
            Bracketed(Ref("DatatypeIdentifierSegment"), bracket_type="square"),
        ),
        Bracketed(
            OneOf(
                Delimited(Ref("ExpressionSegment")),
                # The brackets might be empty for some cases...
                optional=True,
            ),
            # There may be no brackets for some data types
            optional=True,
        ),
        Ref("CharCharacterSetSegment", optional=True),
    )


@tsql_dialect.segment()
class NextValueSequenceSegment(BaseSegment):
    """Segment to get next value from a sequence."""

    type = "sequence_next_value"
    match_grammar = Sequence(
        "NEXT",
        "VALUE",
        "FOR",
        Ref("ObjectReferenceSegment"),
    )


@tsql_dialect.segment()
class IfExpressionStatement(BaseSegment):
    """IF-ELSE statement.

    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/if-else-transact-sql?view=sql-server-ver15
    """

    type = "if_then_statement"

    match_grammar = Sequence(
        OneOf(
            Sequence(Ref("IfNotExistsGrammar"), Ref("SelectStatementSegment")),
            Sequence(Ref("IfExistsGrammar"), Ref("SelectStatementSegment")),
            Sequence("IF", Ref("ExpressionSegment")),
        ),
        Indent,
        OneOf(
            Ref("BeginEndSegment"),
            Sequence(
                Ref("StatementSegment"),
                Ref("DelimiterSegment", optional=True),
            ),
        ),
        Dedent,
        Sequence(
            "ELSE",
            Indent,
            OneOf(
                Ref("BeginEndSegment"),
                Sequence(
                    Ref("StatementSegment"),
                    Ref("DelimiterSegment", optional=True),
                ),
            ),
            Dedent,
            optional=True,
        ),
    )


@tsql_dialect.segment(replace=True)
class ColumnConstraintSegment(BaseSegment):
    """A column option; each CREATE TABLE column can have 0 or more."""

    type = "column_constraint_segment"
    # Column constraint from
    # https://www.postgresql.org/docs/12/sql-createtable.html
    match_grammar = Sequence(
        Sequence(
            "CONSTRAINT",
            Ref("ObjectReferenceSegment"),  # Constraint name
            optional=True,
        ),
        OneOf(
            Sequence(Ref.keyword("NOT", optional=True), "NULL"),  # NOT NULL or NULL
            Sequence(  # DEFAULT <value>
                "DEFAULT",
                OneOf(
                    Ref("LiteralGrammar"),
                    Ref("FunctionSegment"),
                    # ?? Ref('IntervalExpressionSegment')
                    OptionallyBracketed(Ref("NextValueSequenceSegment")),
                ),
            ),
            Ref("PrimaryKeyGrammar"),
            "UNIQUE",  # UNIQUE
            "AUTO_INCREMENT",  # AUTO_INCREMENT (MySQL)
            "UNSIGNED",  # UNSIGNED (MySQL)
            Sequence(  # REFERENCES reftable [ ( refcolumn) ]
                "REFERENCES",
                Ref("ColumnReferenceSegment"),
                # Foreign columns making up FOREIGN KEY constraint
                Ref("BracketedColumnReferenceListGrammar", optional=True),
            ),
            Ref("CommentClauseSegment"),
            Ref("IdentityGrammar"),
        ),
    )


@tsql_dialect.segment(replace=True)
class FunctionParameterListGrammar(BaseSegment):
    """The parameters for a function ie. `(@city_name NVARCHAR(30), @postal_code NVARCHAR(15))`.

    Overriding ANSI (1) to optionally bracket and (2) remove Delimited
    """

    type = "function_parameter_list"
    # Function parameter list
    match_grammar = OptionallyBracketed(
        Ref("FunctionParameterGrammar"),
        AnyNumberOf(
            Ref("CommaSegment"),
            Ref("FunctionParameterGrammar"),
        ),
    )


@tsql_dialect.segment(replace=True)
class CreateFunctionStatementSegment(BaseSegment):
    """A `CREATE FUNCTION` statement.

    This version in the TSQL dialect should be a "common subset" of the
    structure of the code for those dialects.

    Updated to include AS after declaration of RETURNS. Might be integrated in ANSI though.

    postgres: https://www.postgresql.org/docs/9.1/sql-createfunction.html
    snowflake: https://docs.snowflake.com/en/sql-reference/sql/create-function.html
    bigquery: https://cloud.google.com/bigquery/docs/reference/standard-sql/user-defined-functions
    tsql/mssql : https://docs.microsoft.com/en-us/sql/t-sql/statements/create-function-transact-sql?view=sql-server-ver15
    """

    type = "create_function_statement"

    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "ALTER", optional=True),
        "FUNCTION",
        Anything(),
    )
    parse_grammar = Sequence(
        "CREATE",
        Sequence("OR", "ALTER", optional=True),
        "FUNCTION",
        Ref("ObjectReferenceSegment"),
        Ref("FunctionParameterListGrammar"),
        Sequence(  # Optional function return type
            "RETURNS",
            Ref("DatatypeSegment"),
            optional=True,
        ),
        Ref("FunctionDefinitionGrammar"),
    )


@tsql_dialect.segment()
class SetStatementSegment(BaseSegment):
    """A Set statement.

    Setting an already declared variable or global variable.
    https://docs.microsoft.com/en-us/sql/t-sql/statements/set-statements-transact-sql?view=sql-server-ver15

    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/set-local-variable-transact-sql?view=sql-server-ver15
    """

    type = "set_segment"
    match_grammar = Sequence(
        "SET",
        OneOf(
            Ref("ParameterNameSegment"),
            "DATEFIRST",
            "DATEFORMAT",
            "DEADLOCK_PRIORITY",
            "LOCK_TIMEOUT",
            "CONCAT_NULL_YIELDS_NULL",
            "CURSOR_CLOSE_ON_COMMIT",
            "FIPS_FLAGGER",
            "IDENTITY_INSERT",
            "LANGUAGE",
            "OFFSETS",
            "QUOTED_IDENTIFIER",
            "ARITHABORT",
            "ARITHIGNORE",
            "FMTONLY",
            "NOCOUNT",
            "NOEXEC",
            "NUMERIC_ROUNDABORT",
            "PARSEONLY",
            "QUERY_GOVERNOR_COST_LIMIT",
            "RESULT CACHING (Preview)",
            "ROWCOUNT",
            "TEXTSIZE",
            "ANSI_DEFAULTS",
            "ANSI_NULL_DFLT_OFF",
            "ANSI_NULL_DFLT_ON",
            "ANSI_NULLS",
            "ANSI_PADDING",
            "ANSI_WARNINGS",
            "FORCEPLAN",
            "SHOWPLAN_ALL",
            "SHOWPLAN_TEXT",
            "SHOWPLAN_XML",
            "STATISTICS IO",
            "STATISTICS XML",
            "STATISTICS PROFILE",
            "STATISTICS TIME",
            "IMPLICIT_TRANSACTIONS",
            "REMOTE_PROC_TRANSACTIONS",
            "TRANSACTION ISOLATION LEVEL",
            "XACT_ABORT",
        ),
        OneOf(
            "ON",
            "OFF",
            Sequence(
                Ref("EqualsSegment"),
                Ref("ExpressionSegment"),
            ),
        ),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
class FunctionDefinitionGrammar(BaseSegment):
    """This is the body of a `CREATE FUNCTION AS` statement.

    Adjusted from ansi as Transact SQL does not seem to have the QuotedLiteralSegmentand Language.
    Futhermore the body can contain almost anything like a function with table output.
    """

    type = "function_statement"
    name = "function_statement"

    match_grammar = Sequence("AS", Sequence(Anything()))


@tsql_dialect.segment()
class CreateProcedureStatementSegment(BaseSegment):
    """A `CREATE OR ALTER PROCEDURE` statement.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-procedure-transact-sql?view=sql-server-ver15
    """

    type = "create_procedure_statement"

    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "ALTER", optional=True),
        OneOf("PROCEDURE", "PROC"),
        Ref("ObjectReferenceSegment"),
        Ref("FunctionParameterListGrammar", optional=True),
        "AS",
        Ref("ProcedureDefinitionGrammar"),
    )


@tsql_dialect.segment()
class ProcedureDefinitionGrammar(BaseSegment):
    """This is the body of a `CREATE OR ALTER PROCEDURE AS` statement."""

    type = "procedure_statement"
    name = "procedure_statement"

    match_grammar = AnyNumberOf(
        OneOf(
            Ref("BeginEndSegment"),
            Ref("StatementSegment"),
        ),
        min_times=1,
    )


@tsql_dialect.segment(replace=True)
class CreateViewStatementSegment(BaseSegment):
    """A `CREATE VIEW` statement.

    Adjusted to allow CREATE OR ALTER instead of CREATE OR REPLACE.
    # https://docs.microsoft.com/en-us/sql/t-sql/statements/create-view-transact-sql?view=sql-server-ver15#examples
    """

    type = "create_view_statement"
    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "ALTER", optional=True),
        "VIEW",
        Ref("ObjectReferenceSegment"),
        "AS",
        Ref("SelectableGrammar"),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
class IntervalExpressionSegment(BaseSegment):
    """An interval expression segment.

    Not present in T-SQL.
    """

    type = "interval_expression"
    match_grammar = Nothing()


@tsql_dialect.segment(replace=True)
class CreateExtensionStatementSegment(BaseSegment):
    """A `CREATE EXTENSION` statement.

    Not present in T-SQL.
    """

    type = "create_extension_statement"
    match_grammar = Nothing()


@tsql_dialect.segment(replace=True)
class CreateModelStatementSegment(BaseSegment):
    """A BigQuery `CREATE MODEL` statement.

    Not present in T-SQL.
    """

    type = "create_model_statement"
    match_grammar = Nothing()


@tsql_dialect.segment(replace=True)
class DropModelStatementSegment(BaseSegment):
    """A `DROP MODEL` statement.

    Not present in T-SQL.
    """

    type = "drop_MODELstatement"
    match_grammar = Nothing()


@tsql_dialect.segment(replace=True)
class OverlapsClauseSegment(BaseSegment):
    """An `OVERLAPS` clause like in `SELECT.

    Not present in T-SQL.
    """

    type = "overlaps_clause"
    match_grammar = Nothing()


@tsql_dialect.segment()
class ConvertFunctionNameSegment(BaseSegment):
    """CONVERT function name segment.

    Need to be able to specify this as type function_name
    so that linting rules identify it properly
    """

    type = "function_name"
    match_grammar = Sequence("CONVERT")


@tsql_dialect.segment()
class CastFunctionNameSegment(BaseSegment):
    """CAST function name segment.

    Need to be able to specify this as type function_name
    so that linting rules identify it properly
    """

    type = "function_name"
    match_grammar = Sequence("CAST")


@tsql_dialect.segment()
class RankFunctionNameSegment(BaseSegment):
    """Rank function name segment.

    Need to be able to specify this as type function_name
    so that linting rules identify it properly
    """

    type = "function_name"
    match_grammar = OneOf("DENSE_RANK", "NTILE", "RANK", "ROW_NUMBER")


@tsql_dialect.segment()
class WithinGroupFunctionNameSegment(BaseSegment):
    """WITHIN GROUP function name segment.

    For aggregation functions that use the WITHIN GROUP clause.
    https://docs.microsoft.com/en-us/sql/t-sql/functions/string-agg-transact-sql?view=sql-server-ver15
    https://docs.microsoft.com/en-us/sql/t-sql/functions/percentile-cont-transact-sql?view=sql-server-ver15
    https://docs.microsoft.com/en-us/sql/t-sql/functions/percentile-disc-transact-sql?view=sql-server-ver15

    Need to be able to specify this as type function_name
    so that linting rules identify it properly
    """

    type = "function_name"
    match_grammar = OneOf(
        "STRING_AGG",
        "PERCENTILE_CONT",
        "PERCENTILE_DISC",
    )


@tsql_dialect.segment()
class WithinGroupClause(BaseSegment):
    """WITHIN GROUP clause.

    For a small set of aggregation functions.
    https://docs.microsoft.com/en-us/sql/t-sql/functions/string-agg-transact-sql?view=sql-server-ver15
    https://docs.microsoft.com/en-us/sql/t-sql/functions/percentile-cont-transact-sql?view=sql-server-ver15
    """

    type = "within_group_clause"
    match_grammar = Sequence(
        "WITHIN",
        "GROUP",
        Bracketed(
            Ref("OrderByClauseSegment"),
        ),
        Sequence(
            "OVER",
            Bracketed(Ref("PartitionByClause")),
            optional=True,
        ),
    )


@tsql_dialect.segment()
class PartitionByClause(BaseSegment):
    """PARTITION BY clause.

    https://docs.microsoft.com/en-us/sql/t-sql/queries/select-over-clause-transact-sql?view=sql-server-ver15#partition-by
    """

    type = "partition_by_clause"
    match_grammar = Sequence(
        "PARTITION",
        "BY",
        Ref("ColumnReferenceSegment"),
    )


@tsql_dialect.segment(replace=True)
class FunctionSegment(BaseSegment):
    """A scalar or aggregate function.

    Maybe in the future we should distinguish between
    aggregate functions and other functions. For now
    we treat them the same because they look the same
    for our purposes.
    """

    type = "function"
    match_grammar = OneOf(
        Sequence(
            Ref("DatePartFunctionNameSegment"),
            Bracketed(
                Delimited(
                    Ref("DatePartClause"),
                    Ref(
                        "FunctionContentsGrammar",
                        # The brackets might be empty for some functions...
                        optional=True,
                        ephemeral_name="FunctionContentsGrammar",
                    ),
                )
            ),
        ),
        Sequence(
            Ref("RankFunctionNameSegment"),
            Bracketed(
                Ref("NumericLiteralSegment", optional=True),
            ),
            "OVER",
            Bracketed(
                Ref("PartitionByClause", optional=True),
                Ref("OrderByClauseSegment"),
            ),
        ),
        Sequence(
            Ref("ConvertFunctionNameSegment"),
            Bracketed(
                Delimited(
                    Ref("DatatypeSegment"),
                    Ref(
                        "FunctionContentsGrammar",
                        # The brackets might be empty for some functions...
                        optional=True,
                        ephemeral_name="FunctionContentsGrammar",
                    ),
                )
            ),
        ),
        Sequence(
            Ref("CastFunctionNameSegment"),
            Bracketed(
                Ref("ExpressionSegment"),
                "AS",
                Ref("DatatypeSegment"),
            ),
        ),
        Sequence(
            Ref("WithinGroupFunctionNameSegment"),
            Bracketed(
                Delimited(
                    Ref(
                        "FunctionContentsGrammar",
                        # The brackets might be empty for some functions...
                        optional=True,
                        ephemeral_name="FunctionContentsGrammar",
                    ),
                ),
            ),
            Ref("WithinGroupClause", optional=True),
        ),
        Sequence(
            OneOf(
                Ref("FunctionNameSegment"),
                exclude=OneOf(
                    # List of special functions handled differently
                    Ref("CastFunctionNameSegment"),
                    Ref("ConvertFunctionNameSegment"),
                    Ref("DatePartFunctionNameSegment"),
                    Ref("WithinGroupFunctionNameSegment"),
                    Ref("RankFunctionNameSegment"),
                ),
            ),
            Bracketed(
                Ref(
                    "FunctionContentsGrammar",
                    # The brackets might be empty for some functions...
                    optional=True,
                    ephemeral_name="FunctionContentsGrammar",
                )
            ),
            Ref("PostFunctionGrammar", optional=True),
        ),
    )


@tsql_dialect.segment(replace=True)
class CreateTableStatementSegment(BaseSegment):
    """A `CREATE TABLE` statement."""

    type = "create_table_statement"
    # https://docs.microsoft.com/en-us/sql/t-sql/statements/create-table-transact-sql?view=sql-server-ver15
    # https://docs.microsoft.com/en-us/sql/t-sql/statements/create-table-azure-sql-data-warehouse?view=aps-pdw-2016-au7
    match_grammar = Sequence(
        "CREATE",
        "TABLE",
        Ref("TableReferenceSegment"),
        OneOf(
            # Columns and comment syntax:
            Sequence(
                Bracketed(
                    Delimited(
                        OneOf(
                            Ref("TableConstraintSegment"),
                            Ref("ColumnDefinitionSegment"),
                        ),
                    )
                ),
                Ref("CommentClauseSegment", optional=True),
            ),
            # Create AS syntax:
            Sequence(
                "AS",
                OptionallyBracketed(Ref("SelectableGrammar")),
            ),
            # Create like syntax
            Sequence("LIKE", Ref("TableReferenceSegment")),
        ),
        Ref(
            "TableDistributionIndexClause", optional=True
        ),  # Azure Synapse Analytics specific
        Ref("FilegroupClause", optional=True),
        Ref("DelimiterSegment", optional=True),
    )

    parse_grammar = match_grammar


@tsql_dialect.segment()
class FilegroupClause(BaseSegment):
    """Filegroup Clause segment.

    https://docs.microsoft.com/en-us/sql/relational-databases/databases/database-files-and-filegroups?view=sql-server-ver15
    """

    type = "filegroup_clause"
    match_grammar = Sequence(
        "ON",
        Ref("SingleIdentifierGrammar"),
    )


@tsql_dialect.segment()
class IdentityGrammar(BaseSegment):
    """`IDENTITY (1,1)` in table schemas.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-table-transact-sql-identity-property?view=sql-server-ver15
    """

    type = "identity_grammar"
    match_grammar = Sequence(
        "IDENTITY",
        # optional (seed, increment) e.g. (1, 1)
        Bracketed(
            Sequence(
                Ref("NumericLiteralSegment"),
                Ref("CommaSegment"),
                Ref("NumericLiteralSegment"),
            ),
            optional=True,
        ),
    )


@tsql_dialect.segment()
class TableDistributionIndexClause(BaseSegment):
    """`CREATE TABLE` distribution / index clause.

    This is specific to Azure Synapse Analytics.
    """

    type = "table_distribution_index_clause"

    match_grammar = Sequence(
        "WITH",
        Bracketed(
            Delimited(
                Ref("TableDistributionClause"),
                Ref("TableIndexClause"),
                Ref("TableLocationClause"),
            ),
        ),
    )


@tsql_dialect.segment()
class TableDistributionClause(BaseSegment):
    """`CREATE TABLE` distribution clause.

    This is specific to Azure Synapse Analytics.
    """

    type = "table_distribution_clause"

    match_grammar = Sequence(
        "DISTRIBUTION",
        Ref("EqualsSegment"),
        OneOf(
            "REPLICATE",
            "ROUND_ROBIN",
            Sequence(
                "HASH",
                Bracketed(Ref("ColumnReferenceSegment")),
            ),
        ),
    )


@tsql_dialect.segment()
class TableIndexClause(BaseSegment):
    """`CREATE TABLE` table index clause.

    This is specific to Azure Synapse Analytics.
    """

    type = "table_index_clause"

    match_grammar = Sequence(
        OneOf(
            "HEAP",
            Sequence(
                "CLUSTERED",
                "COLUMNSTORE",
                "INDEX",
            ),
        ),
    )


@tsql_dialect.segment()
class TableLocationClause(BaseSegment):
    """`CREATE TABLE` location clause.

    This is specific to Azure Synapse Analytics (deprecated) or to an external table.
    """

    type = "table_location_clause"

    match_grammar = Sequence(
        "LOCATION",
        Ref("EqualsSegment"),
        OneOf(
            "USER_DB",  # Azure Synapse Analytics specific
            Ref("QuotedLiteralSegment"),  # External Table
        ),
    )


@tsql_dialect.segment()
class AlterTableSwitchStatementSegment(BaseSegment):
    """An `ALTER TABLE SWITCH` statement."""

    type = "alter_table_switch_statement"
    # https://docs.microsoft.com/en-us/sql/t-sql/statements/alter-table-transact-sql?view=sql-server-ver15
    # T-SQL's ALTER TABLE SWITCH grammar is different enough to core ALTER TABLE grammar to merit its own definition
    match_grammar = Sequence(
        "ALTER",
        "TABLE",
        Ref("ObjectReferenceSegment"),
        "SWITCH",
        Sequence("PARTITION", Ref("NumericLiteralSegment"), optional=True),
        "TO",
        Ref("ObjectReferenceSegment"),
        Sequence(  # Azure Synapse Analytics specific
            "WITH",
            Bracketed("TRUNCATE_TARGET", Ref("EqualsSegment"), OneOf("ON", "OFF")),
            optional=True,
        ),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment()
class CreateTableAsSelectStatementSegment(BaseSegment):
    """A `CREATE TABLE AS SELECT` statement.

    This is specific to Azure Synapse Analytics.
    """

    type = "create_table_as_select_statement"
    # https://docs.microsoft.com/en-us/sql/t-sql/statements/create-table-as-select-azure-sql-data-warehouse?toc=/azure/synapse-analytics/sql-data-warehouse/toc.json&bc=/azure/synapse-analytics/sql-data-warehouse/breadcrumb/toc.json&view=azure-sqldw-latest&preserve-view=true
    match_grammar = Sequence(
        "CREATE",
        "TABLE",
        Ref("TableReferenceSegment"),
        Ref("TableDistributionIndexClause"),
        "AS",
        OptionallyBracketed(Ref("SelectableGrammar")),
        Ref("OptionClauseSegment", optional=True),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
class DatePartClause(BaseSegment):
    """DatePart clause for use within DATEADD() or related functions."""

    type = "date_part"

    match_grammar = OneOf(
        "D",
        "DAY",
        "DAYOFYEAR",
        "DD",
        "DW",
        "DY",
        "HH",
        "HOUR",
        "M",
        "MCS",
        "MI",
        "MICROSECOND",
        "MILLISECOND",
        "MINUTE",
        "MM",
        "MONTH",
        "MS",
        "N",
        "NANOSECOND",
        "NS",
        "Q",
        "QQ",
        "QUARTER",
        "S",
        "SECOND",
        "SS",
        "W",
        "WEEK",
        "WEEKDAY",
        "WK",
        "WW",
        "YEAR",
        "Y",
        "YY",
        "YYYY",
    )


@tsql_dialect.segment(replace=True)
class TransactionStatementSegment(BaseSegment):
    """A `COMMIT`, `ROLLBACK` or `TRANSACTION` statement."""

    type = "transaction_statement"
    match_grammar = OneOf(
        # BEGIN | SAVE TRANSACTION
        # COMMIT [ TRANSACTION | WORK ]
        # ROLLBACK [ TRANSACTION | WORK ]
        # https://docs.microsoft.com/en-us/sql/t-sql/language-elements/begin-transaction-transact-sql?view=sql-server-ver15
        Sequence(
            "BEGIN",
            Sequence("DISTRIBUTED", optional=True),
            "TRANSACTION",
            Ref("SingleIdentifierGrammar", optional=True),
            Sequence("WITH", "MARK", Ref("QuotedIdentifierSegment"), optional=True),
            Ref("DelimiterSegment", optional=True),
        ),
        Sequence(
            OneOf("COMMIT", "ROLLBACK"),
            OneOf("TRANSACTION", "WORK", optional=True),
            Ref("DelimiterSegment", optional=True),
        ),
        Sequence("SAVE", "TRANSACTION", Ref("DelimiterSegment", optional=True)),
    )


@tsql_dialect.segment()
class BeginEndSegment(BaseSegment):
    """A `BEGIN/END` block.

    Encloses multiple statements into a single statement object.
    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/begin-end-transact-sql?view=sql-server-ver15
    """

    type = "begin_end_block"
    match_grammar = Sequence(
        "BEGIN",
        Ref("DelimiterSegment", optional=True),
        Indent,
        AnyNumberOf(
            OneOf(
                Ref("BeginEndSegment"),
                Ref("StatementSegment"),
            ),
            min_times=1,
        ),
        Dedent,
        "END",
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment()
class BatchSegment(BaseSegment):
    """A segment representing a GO batch within a file or script."""

    type = "batch"
    match_grammar = OneOf(
        # Things that can be bundled
        AnyNumberOf(
            OneOf(
                Ref("BeginEndSegment"),
                Ref("StatementSegment"),
            ),
            min_times=1,
        ),
        # Things that can't be bundled
        Ref("CreateProcedureStatementSegment"),
    )


@tsql_dialect.segment(replace=True)
class FileSegment(BaseFileSegment):
    """A segment representing a whole file or script.

    We override default as T-SQL allows concept of several
    batches of commands separated by GO as well as usual
    semicolon-separated statement lines.

    This is also the default "root" segment of the dialect,
    and so is usually instantiated directly. It therefore
    has no match_grammar.
    """

    # NB: We don't need a match_grammar here because we're
    # going straight into instantiating it directly usually.
    parse_grammar = Delimited(
        Ref("BatchSegment"),
        delimiter=Ref("BatchDelimiterSegment"),
        allow_gaps=True,
        allow_trailing=True,
    )


@tsql_dialect.segment(replace=True)
class DeleteStatementSegment(BaseSegment):
    """A `DELETE` statement.

    DELETE FROM <table name> [ WHERE <search condition> ]
    Overriding ANSI to remove StartsWith logic which assumes statements have been delimited
    """

    type = "delete_statement"
    # match grammar. This one makes sense in the context of knowing that it's
    # definitely a statement, we just don't know what type yet.
    match_grammar = Sequence(
        "DELETE",
        Ref("FromClauseSegment"),
        Ref("WhereClauseSegment", optional=True),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
class FromClauseSegment(BaseSegment):
    """A `FROM` clause like in `SELECT`.

    NOTE: this is a delimited set of table expressions, with a variable
    number of optional join clauses with those table expressions. The
    delmited aspect is the higher of the two such that the following is
    valid (albeit unusual):

    ```
    SELECT *
    FROM a JOIN b, c JOIN d
    ```

    Overriding ANSI to remove Delimited logic which assumes statements have been delimited
    """

    type = "from_clause"
    match_grammar = Sequence(
        "FROM",
        AnyNumberOf(
            Sequence(
                Ref("FromExpressionSegment"),
                Ref("CommaSegment"),
            ),
        ),
        Ref("FromExpressionSegment"),
        Ref("DelimiterSegment", optional=True),
    )

    get_eventual_aliases = ansi_dialect.get_segment(
        "FromClauseSegment"
    ).get_eventual_aliases


@tsql_dialect.segment(replace=True)
class GroupByClauseSegment(BaseSegment):
    """A `GROUP BY` clause like in `SELECT`.

    Overriding ANSI to remove Delimited logic which assumes statements have been delimited
    """

    type = "groupby_clause"
    match_grammar = Sequence(
        "GROUP",
        "BY",
        Indent,
        OneOf(
            Ref("ColumnReferenceSegment"),
            # Can `GROUP BY 1`
            Ref("NumericLiteralSegment"),
            # Can `GROUP BY coalesce(col, 1)`
            Ref("ExpressionSegment"),
        ),
        AnyNumberOf(
            Ref("CommaSegment"),
            OneOf(
                Ref("ColumnReferenceSegment"),
                # Can `GROUP BY 1`
                Ref("NumericLiteralSegment"),
                # Can `GROUP BY coalesce(col, 1)`
                Ref("ExpressionSegment"),
            ),
        ),
        Dedent,
    )


@tsql_dialect.segment(replace=True)
class HavingClauseSegment(BaseSegment):
    """A `HAVING` clause like in `SELECT`.

    Overriding ANSI to remove StartsWith with greedy terminator
    """

    type = "having_clause"
    match_grammar = Sequence(
        "HAVING",
        Indent,
        OptionallyBracketed(Ref("ExpressionSegment")),
        Dedent,
    )


@tsql_dialect.segment(replace=True)
class OrderByClauseSegment(BaseSegment):
    """A `ORDER BY` clause like in `SELECT`.

    Overriding ANSI to remove StartsWith logic which assumes statements have been delimited
    """

    type = "orderby_clause"
    match_grammar = Sequence(
        "ORDER",
        "BY",
        Indent,
        Sequence(
            OneOf(
                Ref("ColumnReferenceSegment"),
                # Can `ORDER BY 1`
                Ref("NumericLiteralSegment"),
                # Can order by an expression
                Ref("ExpressionSegment"),
            ),
            OneOf("ASC", "DESC", optional=True),
        ),
        AnyNumberOf(
            Sequence(
                Ref("CommaSegment"),
                Sequence(
                    OneOf(
                        Ref("ColumnReferenceSegment"),
                        # Can `ORDER BY 1`
                        Ref("NumericLiteralSegment"),
                        # Can order by an expression
                        Ref("ExpressionSegment"),
                    ),
                    OneOf("ASC", "DESC", optional=True),
                ),
            ),
        ),
        Dedent,
    )


@tsql_dialect.segment()
class RenameStatementSegment(BaseSegment):
    """`RENAME` statement.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/rename-transact-sql?view=aps-pdw-2016-au7
    Azure Synapse Analytics-specific.
    """

    type = "rename_statement"
    match_grammar = Sequence(
        "RENAME",
        "OBJECT",
        Ref("ObjectReferenceSegment"),
        "TO",
        Ref("SingleIdentifierGrammar"),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
class DropStatementSegment(BaseSegment):
    """A `DROP` statement.

    Overriding ANSI to add optional delimiter.
    """

    type = "drop_statement"
    match_grammar = ansi_dialect.get_segment("DropStatementSegment").match_grammar.copy(
        insert=[
            Ref("DelimiterSegment", optional=True),
        ],
    )


@tsql_dialect.segment(replace=True)
class UpdateStatementSegment(BaseSegment):
    """An `Update` statement.

    UPDATE <table name> SET <set clause list> [ WHERE <search condition> ]
    Overriding ANSI in order to allow for PostTableExpressionGrammar (table hints)
    """

    type = "update_statement"
    match_grammar = Sequence(
        "UPDATE",
        OneOf(Ref("TableReferenceSegment"), Ref("AliasedTableReferenceGrammar")),
        Ref("PostTableExpressionGrammar", optional=True),
        Ref("SetClauseListSegment"),
        Ref("FromClauseSegment", optional=True),
        Ref("WhereClauseSegment", optional=True),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
class SetClauseListSegment(BaseSegment):
    """set clause list.

    Overriding ANSI to remove Delimited
    """

    type = "set_clause_list"
    match_grammar = Sequence(
        "SET",
        Indent,
        Ref("SetClauseSegment"),
        AnyNumberOf(
            Ref("CommaSegment"),
            Ref("SetClauseSegment"),
        ),
        Dedent,
    )


@tsql_dialect.segment(replace=True)
class SetClauseSegment(BaseSegment):
    """Set clause.

    Overriding ANSI to allow for ExpressionSegment on the right
    """

    type = "set_clause"

    match_grammar = Sequence(
        Ref("ColumnReferenceSegment"),
        Ref("EqualsSegment"),
        Ref("ExpressionSegment"),
    )


@tsql_dialect.segment(replace=True)
class DatePartFunctionNameSegment(BaseSegment):
    """DATEADD function name segment.

    Override to support DATEDIFF as well
    """

    type = "function_name"
    match_grammar = OneOf("DATEADD", "DATEDIFF", "DATEDIFF_BIG", "DATENAME")


@tsql_dialect.segment()
class PrintStatementSegment(BaseSegment):
    """PRINT statement segment."""

    type = "print_statement"
    match_grammar = Sequence(
        "PRINT",
        Ref("ExpressionSegment"),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment()
class OptionClauseSegment(BaseSegment):
    """Query Hint clause.

    https://docs.microsoft.com/en-us/sql/t-sql/queries/hints-transact-sql-query?view=sql-server-ver15
    """

    type = "option_clause"
    match_grammar = Sequence(
        Sequence("OPTION", optional=True),
        Bracketed(
            Ref("QueryHintSegment"),
            AnyNumberOf(
                Ref("CommaSegment"),
                Ref("QueryHintSegment"),
            ),
        ),
    )


@tsql_dialect.segment()
class QueryHintSegment(BaseSegment):
    """Query Hint segment.

    https://docs.microsoft.com/en-us/sql/t-sql/queries/hints-transact-sql-query?view=sql-server-ver15
    """

    type = "query_hint_segment"
    match_grammar = OneOf(
        Sequence(  # Azure Synapse Analytics specific
            "LABEL",
            Ref("EqualsSegment"),
            Ref("QuotedLiteralSegment"),
        ),
        Sequence(
            OneOf("HASH", "ORDER"),
            "GROUP",
        ),
        Sequence(OneOf("MERGE", "HASH", "CONCAT"), "UNION"),
        Sequence(OneOf("LOOP", "MERGE", "HASH"), "JOIN"),
        Sequence("EXPAND", "VIEWS"),
        Sequence(
            OneOf(
                "FAST",
                "MAXDOP",
                "MAXRECURSION",
                "QUERYTRACEON",
                Sequence(
                    OneOf(
                        "MAX_GRANT_PERCENT",
                        "MIN_GRANT_PERCENT",
                    ),
                    Ref("EqualsSegment"),
                ),
            ),
            Ref("NumericLiteralSegment"),
        ),
        Sequence("FORCE", "ORDER"),
        Sequence(
            OneOf("FORCE", "DISABLE"),
            OneOf("EXTERNALPUSHDOWN", "SCALEOUTEXECUTION"),
        ),
        Sequence(
            OneOf(
                "KEEP",
                "KEEPFIXED",
                "ROBUST",
            ),
            "PLAN",
        ),
        "IGNORE_NONCLUSTERED_COLUMNSTORE_INDEX",
        "NO_PERFORMANCE_SPOOL",
        Sequence(
            "OPTIMIZE",
            "FOR",
            OneOf(
                "UNKNOWN",
                Bracketed(
                    Ref("ParameterNameSegment"),
                    OneOf(
                        "UNKNOWN", Sequence(Ref("EqualsSegment"), Ref("LiteralGrammar"))
                    ),
                    AnyNumberOf(
                        Ref("CommaSegment"),
                        Ref("ParameterNameSegment"),
                        OneOf(
                            "UNKNOWN",
                            Sequence(Ref("EqualsSegment"), Ref("LiteralGrammar")),
                        ),
                    ),
                ),
            ),
        ),
        Sequence("PARAMETERIZATION", OneOf("SIMPLE", "FORCED")),
        "RECOMPILE",
        Sequence(
            "USE",
            "HINT",
            Bracketed(
                Ref("QuotedLiteralSegment"),
                AnyNumberOf(Ref("CommaSegment"), Ref("QuotedLiteralSegment")),
            ),
        ),
        Sequence(
            "USE",
            "PLAN",
            OneOf(Ref("QuotedLiteralSegment"), Ref("QuotedLiteralSegmentWithN")),
        ),
        Sequence(
            "TABLE",
            "HINT",
            Ref("ObjectReferenceSegment"),
            Ref("TableHintSegment"),
            AnyNumberOf(
                Ref("CommaSegment"),
                Ref("TableHintSegment"),
            ),
        ),
    )


@tsql_dialect.segment(replace=True)
class PostTableExpressionGrammar(BaseSegment):
    """Table Hint clause.  Overloading the PostTableExpressionGrammar to implement.

    https://docs.microsoft.com/en-us/sql/t-sql/queries/hints-transact-sql-table?view=sql-server-ver15
    """

    match_grammar = Sequence(
        Sequence("WITH", optional=True),
        Bracketed(
            Ref("TableHintSegment"),
            AnyNumberOf(
                Ref("CommaSegment"),
                Ref("TableHintSegment"),
            ),
        ),
    )


@tsql_dialect.segment()
class TableHintSegment(BaseSegment):
    """Table Hint segment.

    https://docs.microsoft.com/en-us/sql/t-sql/queries/hints-transact-sql-table?view=sql-server-ver15
    """

    type = "query_hint_segment"
    match_grammar = OneOf(
        "NOEXPAND",
        Sequence(
            "INDEX",
            Bracketed(
                OneOf(Ref("IndexReferenceSegment"), Ref("NumericLiteralSegment")),
                AnyNumberOf(
                    Ref("CommaSegment"),
                    OneOf(
                        Ref("IndexReferenceSegment"),
                        Ref("NumericLiteralSegment"),
                    ),
                ),
            ),
        ),
        Sequence(
            "INDEX",
            Ref("EqualsSegment"),
            Bracketed(
                OneOf(Ref("IndexReferenceSegment"), Ref("NumericLiteralSegment")),
            ),
        ),
        "KEEPIDENTITY",
        "KEEPDEFAULTS",
        Sequence(
            "FORCESEEK",
            Bracketed(
                Ref("IndexReferenceSegment"),
                Bracketed(
                    Ref("SingleIdentifierGrammar"),
                    AnyNumberOf(Ref("CommaSegment"), Ref("SingleIdentifierGrammar")),
                ),
                optional=True,
            ),
        ),
        "FORCESCAN",
        "HOLDLOCK",
        "IGNORE_CONSTRAINTS",
        "IGNORE_TRIGGERS",
        "NOLOCK",
        "NOWAIT",
        "PAGLOCK",
        "READCOMMITTED",
        "READCOMMITTEDLOCK",
        "READPAST",
        "READUNCOMMITTED",
        "REPEATABLEREAD",
        "ROWLOCK",
        "SERIALIZABLE",
        "SNAPSHOT",
        Sequence(
            "SPATIAL_WINDOW_MAX_CELLS",
            Ref("EqualsSegment"),
            Ref("NumericLiteralSegment"),
        ),
        "TABLOCK",
        "TABLOCKX",
        "UPDLOCK",
        "XLOCK",
    )


@tsql_dialect.segment(replace=True)
class SetExpressionSegment(BaseSegment):
    """A set expression with either Union, Minus, Except or Intersect.

    Overriding ANSI to include OPTION clause.
    """

    type = "set_expression"
    # match grammar
    match_grammar = Sequence(
        Ref("NonSetSelectableGrammar"),
        AnyNumberOf(
            Sequence(
                Ref("SetOperatorSegment"),
                Ref("NonSetSelectableGrammar"),
            ),
            min_times=1,
        ),
        Ref("OrderByClauseSegment", optional=True),
        Ref("OptionClauseSegment", optional=True),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment()
class ExecuteScriptSegment(BaseSegment):
    """`EXECUTE` statement.

    Matching segment name and type from exasol.
    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/execute-transact-sql?view=sql-server-ver15
    """

    type = "execute_script_statement"
    match_grammar = Sequence(
        OneOf("EXEC", "EXECUTE"),
        Ref("ObjectReferenceSegment"),
        Sequence(
            Sequence(Ref("ParameterNameSegment"), Ref("EqualsSegment"), optional=True),
            OneOf(
                "DEFAULT",
                Ref("LiteralGrammar"),
                Ref("ParameterNameSegment"),
                Ref("SingleIdentifierGrammar"),
            ),
            Sequence("OUTPUT", optional=True),
            AnyNumberOf(
                Ref("CommaSegment"),
                Sequence(
                    Ref("ParameterNameSegment"), Ref("EqualsSegment"), optional=True
                ),
                OneOf(
                    "DEFAULT",
                    Ref("LiteralGrammar"),
                    Ref("ParameterNameSegment"),
                    Ref("SingleIdentifierGrammar"),
                ),
                Sequence("OUTPUT", optional=True),
            ),
            optional=True,
        ),
        Ref("DelimiterSegment", optional=True),
    )

```
### 5 - src/sqlfluff/dialects/dialect_tsql.py:

```python
"""The MSSQL T-SQL dialect.

https://docs.microsoft.com/en-us/sql/t-sql/language-elements/language-elements-transact-sql
"""

from sqlfluff.core.parser import (
    BaseSegment,
    Sequence,
    OneOf,
    Bracketed,
    Ref,
    Anything,
    Nothing,
    RegexLexer,
    CodeSegment,
    RegexParser,
    Delimited,
    Matchable,
    NamedParser,
    OptionallyBracketed,
    Dedent,
    BaseFileSegment,
    Indent,
    AnyNumberOf,
    CommentSegment,
    StringParser,
    SymbolSegment,
    SegmentGenerator,
)

from sqlfluff.core.dialects import load_raw_dialect

from sqlfluff.dialects.dialect_tsql_keywords import (
    RESERVED_KEYWORDS,
    UNRESERVED_KEYWORDS,
)

ansi_dialect = load_raw_dialect("ansi")
tsql_dialect = ansi_dialect.copy_as("tsql")

# Should really clear down the old keywords but some are needed by certain segments
# tsql_dialect.sets("reserved_keywords").clear()
# tsql_dialect.sets("unreserved_keywords").clear()
tsql_dialect.sets("reserved_keywords").update(RESERVED_KEYWORDS)
tsql_dialect.sets("unreserved_keywords").update(UNRESERVED_KEYWORDS)

tsql_dialect.insert_lexer_matchers(
    [
        RegexLexer(
            "atsign",
            r"[@][a-zA-Z0-9_]+",
            CodeSegment,
        ),
        RegexLexer(
            "square_quote",
            r"\[([^\[\]]*)*\]",
            CodeSegment,
        ),
        # T-SQL unicode strings
        RegexLexer("single_quote_with_n", r"N'([^']|'')*'", CodeSegment),
        RegexLexer(
            "hash_prefix",
            r"[#][#]?[a-zA-Z0-9_]+",
            CodeSegment,
        ),
    ],
    before="back_quote",
)

tsql_dialect.patch_lexer_matchers(
    [
        # Patching single_quote to allow for TSQL-style escaped quotes
        RegexLexer("single_quote", r"'([^']|'')*'", CodeSegment),
        # Patching comments to remove hash comments
        RegexLexer(
            "inline_comment",
            r"(--)[^\n]*",
            CommentSegment,
            segment_kwargs={"trim_start": ("--")},
        ),
        # Patching to add !<, !>
        RegexLexer("greater_than_or_equal", ">=|!<", CodeSegment),
        RegexLexer("less_than_or_equal", "<=|!>", CodeSegment),
        RegexLexer(
            "code", r"[0-9a-zA-Z_#@]+", CodeSegment
        ),  # overriding to allow hash mark and at-sign in code
    ]
)

tsql_dialect.add(
    BracketedIdentifierSegment=NamedParser(
        "square_quote", CodeSegment, name="quoted_identifier", type="identifier"
    ),
    HashIdentifierSegment=NamedParser(
        "hash_prefix", CodeSegment, name="hash_identifier", type="identifier"
    ),
    BatchDelimiterSegment=Ref("GoStatementSegment"),
    QuotedLiteralSegmentWithN=NamedParser(
        "single_quote_with_n", CodeSegment, name="quoted_literal", type="literal"
    ),
    NotGreaterThanSegment=StringParser(
        "!>", SymbolSegment, name="less_than_equal_to", type="comparison_operator"
    ),
    NotLessThanSegment=StringParser(
        "!<", SymbolSegment, name="greater_than_equal_to", type="comparison_operator"
    ),
)

tsql_dialect.replace(
    # Overriding to cover TSQL allowed identifier name characters
    # https://docs.microsoft.com/en-us/sql/relational-databases/databases/database-identifiers?view=sql-server-ver15
    NakedIdentifierSegment=SegmentGenerator(
        # Generate the anti template from the set of reserved keywords
        lambda dialect: RegexParser(
            r"[A-Z_][A-Z0-9_@$#]*",
            CodeSegment,
            name="naked_identifier",
            type="identifier",
            anti_template=r"^(" + r"|".join(dialect.sets("reserved_keywords")) + r")$",
        )
    ),
    ComparisonOperatorGrammar=OneOf(
        Ref("EqualsSegment"),
        Ref("GreaterThanSegment"),
        Ref("LessThanSegment"),
        Ref("GreaterThanOrEqualToSegment"),
        Ref("LessThanOrEqualToSegment"),
        Ref("NotEqualToSegment_a"),
        Ref("NotEqualToSegment_b"),
        Ref("LikeOperatorSegment"),
        Ref("NotGreaterThanSegment"),
        Ref("NotLessThanSegment"),
    ),
    SingleIdentifierGrammar=OneOf(
        Ref("NakedIdentifierSegment"),
        Ref("QuotedIdentifierSegment"),
        Ref("BracketedIdentifierSegment"),
        Ref("HashIdentifierSegment"),
        Ref("ParameterNameSegment"),
    ),
    LiteralGrammar=OneOf(
        Ref("QuotedLiteralSegment"),
        Ref("QuotedLiteralSegmentWithN"),
        Ref("NumericLiteralSegment"),
        Ref("BooleanLiteralGrammar"),
        Ref("QualifiedNumericLiteralSegment"),
        # NB: Null is included in the literals, because it is a keyword which
        # can otherwise be easily mistaken for an identifier.
        Ref("NullLiteralSegment"),
        Ref("DateTimeLiteralGrammar"),
    ),
    ParameterNameSegment=RegexParser(
        r"[@][A-Za-z0-9_]+", CodeSegment, name="parameter", type="parameter"
    ),
    FunctionNameIdentifierSegment=RegexParser(
        r"[A-Z][A-Z0-9_]*|\[[A-Z][A-Z0-9_]*\]",
        CodeSegment,
        name="function_name_identifier",
        type="function_name_identifier",
    ),
    DatatypeIdentifierSegment=Ref("SingleIdentifierGrammar"),
    PrimaryKeyGrammar=Sequence(
        "PRIMARY", "KEY", OneOf("CLUSTERED", "NONCLUSTERED", optional=True)
    ),
    # Overriding SelectClauseSegmentGrammar to remove Delimited logic which assumes statements have been delimited
    SelectClauseSegmentGrammar=Sequence(
        "SELECT",
        Ref("SelectClauseModifierSegment", optional=True),
        Indent,
        AnyNumberOf(
            Sequence(
                Ref("SelectClauseElementSegment"),
                Ref("CommaSegment"),
            ),
        ),
        Ref("SelectClauseElementSegment"),
        # NB: The Dedent for the indent above lives in the
        # SelectStatementSegment so that it sits in the right
        # place corresponding to the whitespace.
    ),
    FromClauseTerminatorGrammar=OneOf(
        "WHERE",
        "LIMIT",
        Sequence("GROUP", "BY"),
        Sequence("ORDER", "BY"),
        "HAVING",
        "PIVOT",
        "UNPIVOT",
        Ref("SetOperatorSegment"),
        Ref("WithNoSchemaBindingClauseSegment"),
        Ref("DelimiterSegment"),
    ),
    JoinKeywords=OneOf("JOIN", "APPLY", Sequence("OUTER", "APPLY")),
    # Replace Expression_D_Grammar to remove casting syntax invalid in TSQL
    Expression_D_Grammar=Sequence(
        OneOf(
            Ref("BareFunctionSegment"),
            Ref("FunctionSegment"),
            Bracketed(
                OneOf(
                    # We're using the expression segment here rather than the grammar so
                    # that in the parsed structure we get nested elements.
                    Ref("ExpressionSegment"),
                    Ref("SelectableGrammar"),
                    Delimited(
                        Ref(
                            "ColumnReferenceSegment"
                        ),  # WHERE (a,b,c) IN (select a,b,c FROM...)
                        Ref(
                            "FunctionSegment"
                        ),  # WHERE (a, substr(b,1,3)) IN (select c,d FROM...)
                        Ref("LiteralGrammar"),  # WHERE (a, 2) IN (SELECT b, c FROM ...)
                    ),
                    ephemeral_name="BracketedExpression",
                ),
            ),
            # Allow potential select statement without brackets
            Ref("SelectStatementSegment"),
            Ref("LiteralGrammar"),
            Ref("IntervalExpressionSegment"),
            Ref("ColumnReferenceSegment"),
            Sequence(
                Ref("SimpleArrayTypeGrammar", optional=True), Ref("ArrayLiteralSegment")
            ),
        ),
        Ref("Accessor_Grammar", optional=True),
        allow_gaps=True,
    ),
)


@tsql_dialect.segment(replace=True)
class AliasExpressionSegment(BaseSegment):
    """A reference to an object with an `AS` clause.

    The optional AS keyword allows both implicit and explicit aliasing.
    Overriding ANSI to remove QuotedLiteralSegment
    """

    type = "alias_expression"
    match_grammar = Sequence(
        Ref.keyword("AS", optional=True),
        OneOf(
            Sequence(
                Ref("SingleIdentifierGrammar"),
                # Column alias in VALUES clause
                Bracketed(Ref("SingleIdentifierListSegment"), optional=True),
            ),
        ),
    )


@tsql_dialect.segment(replace=True)
class StatementSegment(ansi_dialect.get_segment("StatementSegment")):  # type: ignore
    """Overriding StatementSegment to allow for additional segment parsing."""

    match_grammar = ansi_dialect.get_segment("StatementSegment").parse_grammar.copy(
        insert=[
            Ref("IfExpressionStatement"),
            Ref("DeclareStatementSegment"),
            Ref("SetStatementSegment"),
            Ref("AlterTableSwitchStatementSegment"),
            Ref("PrintStatementSegment"),
            Ref(
                "CreateTableAsSelectStatementSegment"
            ),  # Azure Synapse Analytics specific
            Ref("RenameStatementSegment"),  # Azure Synapse Analytics specific
            Ref("ExecuteScriptSegment"),
            Ref("DropStatisticsStatementSegment"),
            Ref("UpdateStatisticsStatementSegment"),
        ],
    )

    parse_grammar = match_grammar


@tsql_dialect.segment(replace=True)
class SelectClauseElementSegment(BaseSegment):
    """An element in the targets of a select statement.

    Overriding ANSI to remove GreedyUntil logic which assumes statements have been delimited
    """

    type = "select_clause_element"
    # Important to split elements before parsing, otherwise debugging is really hard.
    match_grammar = OneOf(
        # *, blah.*, blah.blah.*, etc.
        Ref("WildcardExpressionSegment"),
        Sequence(
            Ref("BaseExpressionElementGrammar"),
            Ref("AliasExpressionSegment", optional=True),
        ),
    )


@tsql_dialect.segment(replace=True)
class SelectClauseModifierSegment(BaseSegment):
    """Things that come after SELECT but before the columns."""

    type = "select_clause_modifier"
    match_grammar = OneOf(
        "DISTINCT",
        "ALL",
        Sequence(
            "TOP",
            OptionallyBracketed(Ref("ExpressionSegment")),
            Sequence("PERCENT", optional=True),
            Sequence("WITH", "TIES", optional=True),
        ),
    )


@tsql_dialect.segment(replace=True)
class SelectClauseSegment(BaseSegment):
    """A group of elements in a select target statement.

    Overriding ANSI to remove StartsWith logic which assumes statements have been delimited
    """

    type = "select_clause"
    match_grammar = Ref("SelectClauseSegmentGrammar")


@tsql_dialect.segment(replace=True)
class UnorderedSelectStatementSegment(BaseSegment):
    """A `SELECT` statement without any ORDER clauses or later.

    We need to change ANSI slightly to remove LimitClauseSegment
    and NamedWindowSegment which don't exist in T-SQL.

    We also need to get away from ANSI's use of StartsWith.
    There's not a clean list of terminators that can be used
    to identify the end of a TSQL select statement.  Semi-colon is optional.
    """

    type = "select_statement"
    match_grammar = Sequence(
        Ref("SelectClauseSegment"),
        # Dedent for the indent in the select clause.
        # It's here so that it can come AFTER any whitespace.
        Dedent,
        Ref("IntoTableSegment", optional=True),
        Ref("FromClauseSegment", optional=True),
        Ref("PivotUnpivotStatementSegment", optional=True),
        Ref("WhereClauseSegment", optional=True),
        Ref("GroupByClauseSegment", optional=True),
        Ref("HavingClauseSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
class SelectStatementSegment(BaseSegment):
    """A `SELECT` statement.

    We need to change ANSI slightly to remove LimitClauseSegment
    and NamedWindowSegment which don't exist in T-SQL.

    We also need to get away from ANSI's use of StartsWith.
    There's not a clean list of terminators that can be used
    to identify the end of a TSQL select statement.  Semi-colon is optional.
    """

    type = "select_statement"
    # Remove the Limit and Window statements from ANSI
    match_grammar = UnorderedSelectStatementSegment.match_grammar.copy(
        insert=[
            Ref("OrderByClauseSegment", optional=True),
            Ref("OptionClauseSegment", optional=True),
            Ref("DelimiterSegment", optional=True),
        ]
    )


@tsql_dialect.segment()
class IntoTableSegment(BaseSegment):
    """`INTO` clause within `SELECT`.

    https://docs.microsoft.com/en-us/sql/t-sql/queries/select-into-clause-transact-sql?view=sql-server-ver15
    """

    type = "into_table_clause"
    match_grammar = Sequence("INTO", Ref("ObjectReferenceSegment"))


@tsql_dialect.segment(replace=True)
class WhereClauseSegment(BaseSegment):
    """A `WHERE` clause like in `SELECT` or `INSERT`.

    Overriding ANSI in order to get away from the use of
    StartsWith. There's not a clean list of terminators that can be used
    to identify the end of a TSQL select statement.  Semi-colon is optional.
    """

    type = "where_clause"
    match_grammar = Sequence(
        "WHERE",
        Indent,
        OptionallyBracketed(Ref("ExpressionSegment")),
        Dedent,
    )


@tsql_dialect.segment(replace=True)
class CreateIndexStatementSegment(BaseSegment):
    """A `CREATE INDEX` or `CREATE STATISTICS` statement.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-index-transact-sql?view=sql-server-ver15
    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-statistics-transact-sql?view=sql-server-ver15
    """

    type = "create_index_statement"
    match_grammar = Sequence(
        "CREATE",
        Ref("OrReplaceGrammar", optional=True),
        Sequence("UNIQUE", optional=True),
        OneOf("CLUSTERED", "NONCLUSTERED", optional=True),
        OneOf("INDEX", "STATISTICS"),
        Ref("IfNotExistsGrammar", optional=True),
        Ref("IndexReferenceSegment"),
        "ON",
        Ref("TableReferenceSegment"),
        Sequence(
            Bracketed(
                Delimited(
                    Ref("IndexColumnDefinitionSegment"),
                ),
            )
        ),
        Sequence(
            "INCLUDE",
            Sequence(
                Bracketed(
                    Delimited(
                        Ref("IndexColumnDefinitionSegment"),
                    ),
                )
            ),
            optional=True,
        ),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
class DropIndexStatementSegment(BaseSegment):
    """A `DROP INDEX` statement.

    Overriding ANSI to include required ON clause.
    """

    type = "drop_statement"
    match_grammar = Sequence(
        "DROP",
        "INDEX",
        Ref("IfExistsGrammar", optional=True),
        Ref("IndexReferenceSegment"),
        "ON",
        Ref("TableReferenceSegment"),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment()
class DropStatisticsStatementSegment(BaseSegment):
    """A `DROP STATISTICS` statement."""

    type = "drop_statement"
    # DROP INDEX <Index name> [CONCURRENTLY] [IF EXISTS] {RESTRICT | CASCADE}
    match_grammar = Sequence(
        "DROP",
        OneOf("STATISTICS"),
        Ref("IndexReferenceSegment"),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment()
class UpdateStatisticsStatementSegment(BaseSegment):
    """An `UPDATE STATISTICS` statement.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/update-statistics-transact-sql?view=sql-server-ver15
    """

    type = "update_statistics_statement"
    match_grammar = Sequence(
        "UPDATE",
        "STATISTICS",
        Ref("ObjectReferenceSegment"),
        OneOf(
            Ref("SingleIdentifierGrammar"),
            Bracketed(
                Delimited(
                    Ref("SingleIdentifierGrammar"),
                ),
            ),
            optional=True,
        ),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
class ObjectReferenceSegment(BaseSegment):
    """A reference to an object.

    Update ObjectReferenceSegment to only allow dot separated SingleIdentifierGrammar
    So Square Bracketed identifiers can be matched.
    """

    type = "object_reference"
    # match grammar (allow whitespace)
    match_grammar: Matchable = Sequence(
        Ref("SingleIdentifierGrammar"),
        AnyNumberOf(
            Sequence(
                Ref("DotSegment"),
                Ref("SingleIdentifierGrammar", optional=True),
            ),
            min_times=0,
            max_times=3,
        ),
    )

    ObjectReferencePart = ansi_dialect.get_segment(
        "ObjectReferenceSegment"
    ).ObjectReferencePart

    _iter_reference_parts = ansi_dialect.get_segment(
        "ObjectReferenceSegment"
    )._iter_reference_parts

    iter_raw_references = ansi_dialect.get_segment(
        "ObjectReferenceSegment"
    ).iter_raw_references

    is_qualified = ansi_dialect.get_segment("ObjectReferenceSegment").is_qualified

    qualification = ansi_dialect.get_segment("ObjectReferenceSegment").qualification

    ObjectReferenceLevel = ansi_dialect.get_segment(
        "ObjectReferenceSegment"
    ).ObjectReferenceLevel

    extract_possible_references = ansi_dialect.get_segment(
        "ObjectReferenceSegment"
    ).extract_possible_references

    _level_to_int = staticmethod(
        ansi_dialect.get_segment("ObjectReferenceSegment")._level_to_int
    )


@tsql_dialect.segment(replace=True)
class TableReferenceSegment(ObjectReferenceSegment):
    """A reference to an table, CTE, subquery or alias.

    Overriding to capture TSQL's override of ObjectReferenceSegment
    """

    type = "table_reference"


@tsql_dialect.segment(replace=True)
class SchemaReferenceSegment(ObjectReferenceSegment):
    """A reference to a schema.

    Overriding to capture TSQL's override of ObjectReferenceSegment
    """

    type = "schema_reference"


@tsql_dialect.segment(replace=True)
class DatabaseReferenceSegment(ObjectReferenceSegment):
    """A reference to a database.

    Overriding to capture TSQL's override of ObjectReferenceSegment
    """

    type = "database_reference"


@tsql_dialect.segment(replace=True)
class IndexReferenceSegment(ObjectReferenceSegment):
    """A reference to an index.

    Overriding to capture TSQL's override of ObjectReferenceSegment
    """

    type = "index_reference"


@tsql_dialect.segment(replace=True)
class ExtensionReferenceSegment(ObjectReferenceSegment):
    """A reference to an extension.

    Overriding to capture TSQL's override of ObjectReferenceSegment
    """

    type = "extension_reference"


@tsql_dialect.segment(replace=True)
class ColumnReferenceSegment(ObjectReferenceSegment):
    """A reference to column, field or alias.

    Overriding to capture TSQL's override of ObjectReferenceSegment
    """

    type = "column_reference"


@tsql_dialect.segment(replace=True)
class SequenceReferenceSegment(ObjectReferenceSegment):
    """A reference to a sequence.

    Overriding to capture TSQL's override of ObjectReferenceSegment
    """

    type = "sequence_reference"


@tsql_dialect.segment()
class PivotColumnReferenceSegment(ObjectReferenceSegment):
    """A reference to a PIVOT column to differentiate it from a regular column reference."""

    type = "pivot_column_reference"


@tsql_dialect.segment()
class PivotUnpivotStatementSegment(BaseSegment):
    """Declaration of a variable.

    https://docs.microsoft.com/en-us/sql/t-sql/queries/from-using-pivot-and-unpivot?view=sql-server-ver15
    """

    type = "from_pivot_expression"
    match_grammar = Sequence(
        OneOf(
            Sequence(
                "PIVOT",
                OptionallyBracketed(
                    Sequence(
                        OptionallyBracketed(Ref("FunctionSegment")),
                        "FOR",
                        Ref("ColumnReferenceSegment"),
                        "IN",
                        Bracketed(Delimited(Ref("PivotColumnReferenceSegment"))),
                    )
                ),
            ),
            Sequence(
                "UNPIVOT",
                OptionallyBracketed(
                    Sequence(
                        OptionallyBracketed(Ref("ColumnReferenceSegment")),
                        "FOR",
                        Ref("ColumnReferenceSegment"),
                        "IN",
                        Bracketed(Delimited(Ref("PivotColumnReferenceSegment"))),
                    )
                ),
            ),
        ),
        "AS",
        Ref("TableReferenceSegment"),
    )


@tsql_dialect.segment()
class DeclareStatementSegment(BaseSegment):
    """Declaration of a variable.

    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/declare-local-variable-transact-sql?view=sql-server-ver15
    """

    type = "declare_segment"
    match_grammar = Sequence(
        "DECLARE",
        Ref("ParameterNameSegment"),
        Sequence("AS", optional=True),
        Ref("DatatypeSegment"),
        Sequence(
            Ref("EqualsSegment"),
            Ref("ExpressionSegment"),
            optional=True,
        ),
        AnyNumberOf(
            Ref("CommaSegment"),
            Ref("ParameterNameSegment"),
            Ref("DatatypeSegment"),
            Sequence(
                Ref("EqualsSegment"),
                Ref("ExpressionSegment"),
                optional=True,
            ),
        ),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment()
class GoStatementSegment(BaseSegment):
    """GO signals the end of a batch of Transact-SQL statements to the SQL Server utilities.

    GO statements are not part of the TSQL language. They are used to signal batch statements
    so that clients know in how batches of statements can be executed.
    """

    type = "go_statement"
    match_grammar = Sequence("GO")


@tsql_dialect.segment(replace=True)
class DatatypeSegment(BaseSegment):
    """A data type segment.

    Updated for Transact-SQL to allow bracketed data types with bracketed schemas.
    """

    type = "data_type"
    match_grammar = Sequence(
        # Some dialects allow optional qualification of data types with schemas
        Sequence(
            Ref("SingleIdentifierGrammar"),
            Ref("DotSegment"),
            allow_gaps=False,
            optional=True,
        ),
        OneOf(
            Ref("DatatypeIdentifierSegment"),
            Bracketed(Ref("DatatypeIdentifierSegment"), bracket_type="square"),
        ),
        Bracketed(
            OneOf(
                Delimited(Ref("ExpressionSegment")),
                # The brackets might be empty for some cases...
                optional=True,
            ),
            # There may be no brackets for some data types
            optional=True,
        ),
        Ref("CharCharacterSetSegment", optional=True),
    )


@tsql_dialect.segment()
class NextValueSequenceSegment(BaseSegment):
    """Segment to get next value from a sequence."""

    type = "sequence_next_value"
    match_grammar = Sequence(
        "NEXT",
        "VALUE",
        "FOR",
        Ref("ObjectReferenceSegment"),
    )


@tsql_dialect.segment()
class IfExpressionStatement(BaseSegment):
    """IF-ELSE statement.

    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/if-else-transact-sql?view=sql-server-ver15
    """

    type = "if_then_statement"

    match_grammar = Sequence(
        OneOf(
            Sequence(Ref("IfNotExistsGrammar"), Ref("SelectStatementSegment")),
            Sequence(Ref("IfExistsGrammar"), Ref("SelectStatementSegment")),
            Sequence("IF", Ref("ExpressionSegment")),
        ),
        Indent,
        OneOf(
            Ref("BeginEndSegment"),
            Sequence(
                Ref("StatementSegment"),
                Ref("DelimiterSegment", optional=True),
            ),
        ),
        Dedent,
        Sequence(
            "ELSE",
            Indent,
            OneOf(
                Ref("BeginEndSegment"),
                Sequence(
                    Ref("StatementSegment"),
                    Ref("DelimiterSegment", optional=True),
                ),
            ),
            Dedent,
            optional=True,
        ),
    )


@tsql_dialect.segment(replace=True)
class ColumnConstraintSegment(BaseSegment):
    """A column option; each CREATE TABLE column can have 0 or more."""

    type = "column_constraint_segment"
    # Column constraint from
    # https://www.postgresql.org/docs/12/sql-createtable.html
    match_grammar = Sequence(
        Sequence(
            "CONSTRAINT",
            Ref("ObjectReferenceSegment"),  # Constraint name
            optional=True,
        ),
        OneOf(
            Sequence(Ref.keyword("NOT", optional=True), "NULL"),  # NOT NULL or NULL
            Sequence(  # DEFAULT <value>
                "DEFAULT",
                OneOf(
                    Ref("LiteralGrammar"),
                    Ref("FunctionSegment"),
                    # ?? Ref('IntervalExpressionSegment')
                    OptionallyBracketed(Ref("NextValueSequenceSegment")),
                ),
            ),
            Ref("PrimaryKeyGrammar"),
            "UNIQUE",  # UNIQUE
            "AUTO_INCREMENT",  # AUTO_INCREMENT (MySQL)
            "UNSIGNED",  # UNSIGNED (MySQL)
            Sequence(  # REFERENCES reftable [ ( refcolumn) ]
                "REFERENCES",
                Ref("ColumnReferenceSegment"),
                # Foreign columns making up FOREIGN KEY constraint
                Ref("BracketedColumnReferenceListGrammar", optional=True),
            ),
            Ref("CommentClauseSegment"),
            Ref("IdentityGrammar"),
        ),
    )


@tsql_dialect.segment(replace=True)
class FunctionParameterListGrammar(BaseSegment):
    """The parameters for a function ie. `(@city_name NVARCHAR(30), @postal_code NVARCHAR(15))`.

    Overriding ANSI (1) to optionally bracket and (2) remove Delimited
    """

    type = "function_parameter_list"
    # Function parameter list
    match_grammar = OptionallyBracketed(
        Ref("FunctionParameterGrammar"),
        AnyNumberOf(
            Ref("CommaSegment"),
            Ref("FunctionParameterGrammar"),
        ),
    )


@tsql_dialect.segment(replace=True)
class CreateFunctionStatementSegment(BaseSegment):
    """A `CREATE FUNCTION` statement.

    This version in the TSQL dialect should be a "common subset" of the
    structure of the code for those dialects.

    Updated to include AS after declaration of RETURNS. Might be integrated in ANSI though.

    postgres: https://www.postgresql.org/docs/9.1/sql-createfunction.html
    snowflake: https://docs.snowflake.com/en/sql-reference/sql/create-function.html
    bigquery: https://cloud.google.com/bigquery/docs/reference/standard-sql/user-defined-functions
    tsql/mssql : https://docs.microsoft.com/en-us/sql/t-sql/statements/create-function-transact-sql?view=sql-server-ver15
    """

    type = "create_function_statement"

    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "ALTER", optional=True),
        "FUNCTION",
        Anything(),
    )
    parse_grammar = Sequence(
        "CREATE",
        Sequence("OR", "ALTER", optional=True),
        "FUNCTION",
        Ref("ObjectReferenceSegment"),
        Ref("FunctionParameterListGrammar"),
        Sequence(  # Optional function return type
            "RETURNS",
            Ref("DatatypeSegment"),
            optional=True,
        ),
        Ref("FunctionDefinitionGrammar"),
    )


@tsql_dialect.segment()
class SetStatementSegment(BaseSegment):
    """A Set statement.

    Setting an already declared variable or global variable.
    https://docs.microsoft.com/en-us/sql/t-sql/statements/set-statements-transact-sql?view=sql-server-ver15

    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/set-local-variable-transact-sql?view=sql-server-ver15
    """

    type = "set_segment"
    match_grammar = Sequence(
        "SET",
        OneOf(
            Ref("ParameterNameSegment"),
            "DATEFIRST",
            "DATEFORMAT",
            "DEADLOCK_PRIORITY",
            "LOCK_TIMEOUT",
            "CONCAT_NULL_YIELDS_NULL",
            "CURSOR_CLOSE_ON_COMMIT",
            "FIPS_FLAGGER",
            "IDENTITY_INSERT",
            "LANGUAGE",
            "OFFSETS",
            "QUOTED_IDENTIFIER",
            "ARITHABORT",
            "ARITHIGNORE",
            "FMTONLY",
            "NOCOUNT",
            "NOEXEC",
            "NUMERIC_ROUNDABORT",
            "PARSEONLY",
            "QUERY_GOVERNOR_COST_LIMIT",
            "RESULT CACHING (Preview)",
            "ROWCOUNT",
            "TEXTSIZE",
            "ANSI_DEFAULTS",
            "ANSI_NULL_DFLT_OFF",
            "ANSI_NULL_DFLT_ON",
            "ANSI_NULLS",
            "ANSI_PADDING",
            "ANSI_WARNINGS",
            "FORCEPLAN",
            "SHOWPLAN_ALL",
            "SHOWPLAN_TEXT",
            "SHOWPLAN_XML",
            "STATISTICS IO",
            "STATISTICS XML",
            "STATISTICS PROFILE",
            "STATISTICS TIME",
            "IMPLICIT_TRANSACTIONS",
            "REMOTE_PROC_TRANSACTIONS",
            "TRANSACTION ISOLATION LEVEL",
            "XACT_ABORT",
        ),
        OneOf(
            "ON",
            "OFF",
            Sequence(
                Ref("EqualsSegment"),
                Ref("ExpressionSegment"),
            ),
        ),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
class FunctionDefinitionGrammar(BaseSegment):
    """This is the body of a `CREATE FUNCTION AS` statement.

    Adjusted from ansi as Transact SQL does not seem to have the QuotedLiteralSegmentand Language.
    Futhermore the body can contain almost anything like a function with table output.
    """

    type = "function_statement"
    name = "function_statement"

    match_grammar = Sequence("AS", Sequence(Anything()))


@tsql_dialect.segment()
class CreateProcedureStatementSegment(BaseSegment):
    """A `CREATE OR ALTER PROCEDURE` statement.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-procedure-transact-sql?view=sql-server-ver15
    """

    type = "create_procedure_statement"

    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "ALTER", optional=True),
        OneOf("PROCEDURE", "PROC"),
        Ref("ObjectReferenceSegment"),
        Ref("FunctionParameterListGrammar", optional=True),
        "AS",
        Ref("ProcedureDefinitionGrammar"),
    )


@tsql_dialect.segment()
class ProcedureDefinitionGrammar(BaseSegment):
    """This is the body of a `CREATE OR ALTER PROCEDURE AS` statement."""

    type = "procedure_statement"
    name = "procedure_statement"

    match_grammar = AnyNumberOf(
        OneOf(
            Ref("BeginEndSegment"),
            Ref("StatementSegment"),
        ),
        min_times=1,
    )


@tsql_dialect.segment(replace=True)
class CreateViewStatementSegment(BaseSegment):
    """A `CREATE VIEW` statement.

    Adjusted to allow CREATE OR ALTER instead of CREATE OR REPLACE.
    # https://docs.microsoft.com/en-us/sql/t-sql/statements/create-view-transact-sql?view=sql-server-ver15#examples
    """

    type = "create_view_statement"
    match_grammar = Sequence(
        "CREATE",
        Sequence("OR", "ALTER", optional=True),
        "VIEW",
        Ref("ObjectReferenceSegment"),
        "AS",
        Ref("SelectableGrammar"),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
class IntervalExpressionSegment(BaseSegment):
    """An interval expression segment.

    Not present in T-SQL.
    """

    type = "interval_expression"
    match_grammar = Nothing()


@tsql_dialect.segment(replace=True)
class CreateExtensionStatementSegment(BaseSegment):
    """A `CREATE EXTENSION` statement.

    Not present in T-SQL.
    """

    type = "create_extension_statement"
    match_grammar = Nothing()


@tsql_dialect.segment(replace=True)
class CreateModelStatementSegment(BaseSegment):
    """A BigQuery `CREATE MODEL` statement.

    Not present in T-SQL.
    """

    type = "create_model_statement"
    match_grammar = Nothing()


@tsql_dialect.segment(replace=True)
class DropModelStatementSegment(BaseSegment):
    """A `DROP MODEL` statement.

    Not present in T-SQL.
    """

    type = "drop_MODELstatement"
    match_grammar = Nothing()


@tsql_dialect.segment(replace=True)
class OverlapsClauseSegment(BaseSegment):
    """An `OVERLAPS` clause like in `SELECT.

    Not present in T-SQL.
    """

    type = "overlaps_clause"
    match_grammar = Nothing()


@tsql_dialect.segment()
class ConvertFunctionNameSegment(BaseSegment):
    """CONVERT function name segment.

    Need to be able to specify this as type function_name
    so that linting rules identify it properly
    """

    type = "function_name"
    match_grammar = Sequence("CONVERT")


@tsql_dialect.segment()
class CastFunctionNameSegment(BaseSegment):
    """CAST function name segment.

    Need to be able to specify this as type function_name
    so that linting rules identify it properly
    """

    type = "function_name"
    match_grammar = Sequence("CAST")


@tsql_dialect.segment()
class RankFunctionNameSegment(BaseSegment):
    """Rank function name segment.

    Need to be able to specify this as type function_name
    so that linting rules identify it properly
    """

    type = "function_name"
    match_grammar = OneOf("DENSE_RANK", "NTILE", "RANK", "ROW_NUMBER")


@tsql_dialect.segment()
class WithinGroupFunctionNameSegment(BaseSegment):
    """WITHIN GROUP function name segment.

    For aggregation functions that use the WITHIN GROUP clause.
    https://docs.microsoft.com/en-us/sql/t-sql/functions/string-agg-transact-sql?view=sql-server-ver15
    https://docs.microsoft.com/en-us/sql/t-sql/functions/percentile-cont-transact-sql?view=sql-server-ver15
    https://docs.microsoft.com/en-us/sql/t-sql/functions/percentile-disc-transact-sql?view=sql-server-ver15

    Need to be able to specify this as type function_name
    so that linting rules identify it properly
    """

    type = "function_name"
    match_grammar = OneOf(
        "STRING_AGG",
        "PERCENTILE_CONT",
        "PERCENTILE_DISC",
    )


@tsql_dialect.segment()
class WithinGroupClause(BaseSegment):
    """WITHIN GROUP clause.

    For a small set of aggregation functions.
    https://docs.microsoft.com/en-us/sql/t-sql/functions/string-agg-transact-sql?view=sql-server-ver15
    https://docs.microsoft.com/en-us/sql/t-sql/functions/percentile-cont-transact-sql?view=sql-server-ver15
    """

    type = "within_group_clause"
    match_grammar = Sequence(
        "WITHIN",
        "GROUP",
        Bracketed(
            Ref("OrderByClauseSegment"),
        ),
        Sequence(
            "OVER",
            Bracketed(Ref("PartitionByClause")),
            optional=True,
        ),
    )


@tsql_dialect.segment()
class PartitionByClause(BaseSegment):
    """PARTITION BY clause.

    https://docs.microsoft.com/en-us/sql/t-sql/queries/select-over-clause-transact-sql?view=sql-server-ver15#partition-by
    """

    type = "partition_by_clause"
    match_grammar = Sequence(
        "PARTITION",
        "BY",
        Ref("ColumnReferenceSegment"),
    )


@tsql_dialect.segment(replace=True)
class FunctionSegment(BaseSegment):
    """A scalar or aggregate function.

    Maybe in the future we should distinguish between
    aggregate functions and other functions. For now
    we treat them the same because they look the same
    for our purposes.
    """

    type = "function"
    match_grammar = OneOf(
        Sequence(
            Ref("DatePartFunctionNameSegment"),
            Bracketed(
                Delimited(
                    Ref("DatePartClause"),
                    Ref(
                        "FunctionContentsGrammar",
                        # The brackets might be empty for some functions...
                        optional=True,
                        ephemeral_name="FunctionContentsGrammar",
                    ),
                )
            ),
        ),
        Sequence(
            Ref("RankFunctionNameSegment"),
            Bracketed(
                Ref("NumericLiteralSegment", optional=True),
            ),
            "OVER",
            Bracketed(
                Ref("PartitionByClause", optional=True),
                Ref("OrderByClauseSegment"),
            ),
        ),
        Sequence(
            Ref("ConvertFunctionNameSegment"),
            Bracketed(
                Delimited(
                    Ref("DatatypeSegment"),
                    Ref(
                        "FunctionContentsGrammar",
                        # The brackets might be empty for some functions...
                        optional=True,
                        ephemeral_name="FunctionContentsGrammar",
                    ),
                )
            ),
        ),
        Sequence(
            Ref("CastFunctionNameSegment"),
            Bracketed(
                Ref("ExpressionSegment"),
                "AS",
                Ref("DatatypeSegment"),
            ),
        ),
        Sequence(
            Ref("WithinGroupFunctionNameSegment"),
            Bracketed(
                Delimited(
                    Ref(
                        "FunctionContentsGrammar",
                        # The brackets might be empty for some functions...
                        optional=True,
                        ephemeral_name="FunctionContentsGrammar",
                    ),
                ),
            ),
            Ref("WithinGroupClause", optional=True),
        ),
        Sequence(
            OneOf(
                Ref("FunctionNameSegment"),
                exclude=OneOf(
                    # List of special functions handled differently
                    Ref("CastFunctionNameSegment"),
                    Ref("ConvertFunctionNameSegment"),
                    Ref("DatePartFunctionNameSegment"),
                    Ref("WithinGroupFunctionNameSegment"),
                    Ref("RankFunctionNameSegment"),
                ),
            ),
            Bracketed(
                Ref(
                    "FunctionContentsGrammar",
                    # The brackets might be empty for some functions...
                    optional=True,
                    ephemeral_name="FunctionContentsGrammar",
                )
            ),
            Ref("PostFunctionGrammar", optional=True),
        ),
    )


@tsql_dialect.segment(replace=True)
class CreateTableStatementSegment(BaseSegment):
    """A `CREATE TABLE` statement."""

    type = "create_table_statement"
    # https://docs.microsoft.com/en-us/sql/t-sql/statements/create-table-transact-sql?view=sql-server-ver15
    # https://docs.microsoft.com/en-us/sql/t-sql/statements/create-table-azure-sql-data-warehouse?view=aps-pdw-2016-au7
    match_grammar = Sequence(
        "CREATE",
        "TABLE",
        Ref("TableReferenceSegment"),
        OneOf(
            # Columns and comment syntax:
            Sequence(
                Bracketed(
                    Delimited(
                        OneOf(
                            Ref("TableConstraintSegment"),
                            Ref("ColumnDefinitionSegment"),
                        ),
                    )
                ),
                Ref("CommentClauseSegment", optional=True),
            ),
            # Create AS syntax:
            Sequence(
                "AS",
                OptionallyBracketed(Ref("SelectableGrammar")),
            ),
            # Create like syntax
            Sequence("LIKE", Ref("TableReferenceSegment")),
        ),
        Ref(
            "TableDistributionIndexClause", optional=True
        ),  # Azure Synapse Analytics specific
        Ref("FilegroupClause", optional=True),
        Ref("DelimiterSegment", optional=True),
    )

    parse_grammar = match_grammar


@tsql_dialect.segment()
class FilegroupClause(BaseSegment):
    """Filegroup Clause segment.

    https://docs.microsoft.com/en-us/sql/relational-databases/databases/database-files-and-filegroups?view=sql-server-ver15
    """

    type = "filegroup_clause"
    match_grammar = Sequence(
        "ON",
        Ref("SingleIdentifierGrammar"),
    )


@tsql_dialect.segment()
class IdentityGrammar(BaseSegment):
    """`IDENTITY (1,1)` in table schemas.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/create-table-transact-sql-identity-property?view=sql-server-ver15
    """

    type = "identity_grammar"
    match_grammar = Sequence(
        "IDENTITY",
        # optional (seed, increment) e.g. (1, 1)
        Bracketed(
            Sequence(
                Ref("NumericLiteralSegment"),
                Ref("CommaSegment"),
                Ref("NumericLiteralSegment"),
            ),
            optional=True,
        ),
    )


@tsql_dialect.segment()
class TableDistributionIndexClause(BaseSegment):
    """`CREATE TABLE` distribution / index clause.

    This is specific to Azure Synapse Analytics.
    """

    type = "table_distribution_index_clause"

    match_grammar = Sequence(
        "WITH",
        Bracketed(
            Delimited(
                Ref("TableDistributionClause"),
                Ref("TableIndexClause"),
                Ref("TableLocationClause"),
            ),
        ),
    )


@tsql_dialect.segment()
class TableDistributionClause(BaseSegment):
    """`CREATE TABLE` distribution clause.

    This is specific to Azure Synapse Analytics.
    """

    type = "table_distribution_clause"

    match_grammar = Sequence(
        "DISTRIBUTION",
        Ref("EqualsSegment"),
        OneOf(
            "REPLICATE",
            "ROUND_ROBIN",
            Sequence(
                "HASH",
                Bracketed(Ref("ColumnReferenceSegment")),
            ),
        ),
    )


@tsql_dialect.segment()
class TableIndexClause(BaseSegment):
    """`CREATE TABLE` table index clause.

    This is specific to Azure Synapse Analytics.
    """

    type = "table_index_clause"

    match_grammar = Sequence(
        OneOf(
            "HEAP",
            Sequence(
                "CLUSTERED",
                "COLUMNSTORE",
                "INDEX",
            ),
        ),
    )


@tsql_dialect.segment()
class TableLocationClause(BaseSegment):
    """`CREATE TABLE` location clause.

    This is specific to Azure Synapse Analytics (deprecated) or to an external table.
    """

    type = "table_location_clause"

    match_grammar = Sequence(
        "LOCATION",
        Ref("EqualsSegment"),
        OneOf(
            "USER_DB",  # Azure Synapse Analytics specific
            Ref("QuotedLiteralSegment"),  # External Table
        ),
    )


@tsql_dialect.segment()
class AlterTableSwitchStatementSegment(BaseSegment):
    """An `ALTER TABLE SWITCH` statement."""

    type = "alter_table_switch_statement"
    # https://docs.microsoft.com/en-us/sql/t-sql/statements/alter-table-transact-sql?view=sql-server-ver15
    # T-SQL's ALTER TABLE SWITCH grammar is different enough to core ALTER TABLE grammar to merit its own definition
    match_grammar = Sequence(
        "ALTER",
        "TABLE",
        Ref("ObjectReferenceSegment"),
        "SWITCH",
        Sequence("PARTITION", Ref("NumericLiteralSegment"), optional=True),
        "TO",
        Ref("ObjectReferenceSegment"),
        Sequence(  # Azure Synapse Analytics specific
            "WITH",
            Bracketed("TRUNCATE_TARGET", Ref("EqualsSegment"), OneOf("ON", "OFF")),
            optional=True,
        ),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment()
class CreateTableAsSelectStatementSegment(BaseSegment):
    """A `CREATE TABLE AS SELECT` statement.

    This is specific to Azure Synapse Analytics.
    """

    type = "create_table_as_select_statement"
    # https://docs.microsoft.com/en-us/sql/t-sql/statements/create-table-as-select-azure-sql-data-warehouse?toc=/azure/synapse-analytics/sql-data-warehouse/toc.json&bc=/azure/synapse-analytics/sql-data-warehouse/breadcrumb/toc.json&view=azure-sqldw-latest&preserve-view=true
    match_grammar = Sequence(
        "CREATE",
        "TABLE",
        Ref("TableReferenceSegment"),
        Ref("TableDistributionIndexClause"),
        "AS",
        OptionallyBracketed(Ref("SelectableGrammar")),
        Ref("OptionClauseSegment", optional=True),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
class DatePartClause(BaseSegment):
    """DatePart clause for use within DATEADD() or related functions."""

    type = "date_part"

    match_grammar = OneOf(
        "D",
        "DAY",
        "DAYOFYEAR",
        "DD",
        "DW",
        "DY",
        "HH",
        "HOUR",
        "M",
        "MCS",
        "MI",
        "MICROSECOND",
        "MILLISECOND",
        "MINUTE",
        "MM",
        "MONTH",
        "MS",
        "N",
        "NANOSECOND",
        "NS",
        "Q",
        "QQ",
        "QUARTER",
        "S",
        "SECOND",
        "SS",
        "W",
        "WEEK",
        "WEEKDAY",
        "WK",
        "WW",
        "YEAR",
        "Y",
        "YY",
        "YYYY",
    )


@tsql_dialect.segment(replace=True)
class TransactionStatementSegment(BaseSegment):
    """A `COMMIT`, `ROLLBACK` or `TRANSACTION` statement."""

    type = "transaction_statement"
    match_grammar = OneOf(
        # BEGIN | SAVE TRANSACTION
        # COMMIT [ TRANSACTION | WORK ]
        # ROLLBACK [ TRANSACTION | WORK ]
        # https://docs.microsoft.com/en-us/sql/t-sql/language-elements/begin-transaction-transact-sql?view=sql-server-ver15
        Sequence(
            "BEGIN",
            Sequence("DISTRIBUTED", optional=True),
            "TRANSACTION",
            Ref("SingleIdentifierGrammar", optional=True),
            Sequence("WITH", "MARK", Ref("QuotedIdentifierSegment"), optional=True),
            Ref("DelimiterSegment", optional=True),
        ),
        Sequence(
            OneOf("COMMIT", "ROLLBACK"),
            OneOf("TRANSACTION", "WORK", optional=True),
            Ref("DelimiterSegment", optional=True),
        ),
        Sequence("SAVE", "TRANSACTION", Ref("DelimiterSegment", optional=True)),
    )


@tsql_dialect.segment()
class BeginEndSegment(BaseSegment):
    """A `BEGIN/END` block.

    Encloses multiple statements into a single statement object.
    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/begin-end-transact-sql?view=sql-server-ver15
    """

    type = "begin_end_block"
    match_grammar = Sequence(
        "BEGIN",
        Ref("DelimiterSegment", optional=True),
        Indent,
        AnyNumberOf(
            OneOf(
                Ref("BeginEndSegment"),
                Ref("StatementSegment"),
            ),
            min_times=1,
        ),
        Dedent,
        "END",
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment()
class BatchSegment(BaseSegment):
    """A segment representing a GO batch within a file or script."""

    type = "batch"
    match_grammar = OneOf(
        # Things that can be bundled
        AnyNumberOf(
            OneOf(
                Ref("BeginEndSegment"),
                Ref("StatementSegment"),
            ),
            min_times=1,
        ),
        # Things that can't be bundled
        Ref("CreateProcedureStatementSegment"),
    )


@tsql_dialect.segment(replace=True)
class FileSegment(BaseFileSegment):
    """A segment representing a whole file or script.

    We override default as T-SQL allows concept of several
    batches of commands separated by GO as well as usual
    semicolon-separated statement lines.

    This is also the default "root" segment of the dialect,
    and so is usually instantiated directly. It therefore
    has no match_grammar.
    """

    # NB: We don't need a match_grammar here because we're
    # going straight into instantiating it directly usually.
    parse_grammar = Delimited(
        Ref("BatchSegment"),
        delimiter=Ref("BatchDelimiterSegment"),
        allow_gaps=True,
        allow_trailing=True,
    )


@tsql_dialect.segment(replace=True)
class DeleteStatementSegment(BaseSegment):
    """A `DELETE` statement.

    DELETE FROM <table name> [ WHERE <search condition> ]
    Overriding ANSI to remove StartsWith logic which assumes statements have been delimited
    """

    type = "delete_statement"
    # match grammar. This one makes sense in the context of knowing that it's
    # definitely a statement, we just don't know what type yet.
    match_grammar = Sequence(
        "DELETE",
        Ref("FromClauseSegment"),
        Ref("WhereClauseSegment", optional=True),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
class FromClauseSegment(BaseSegment):
    """A `FROM` clause like in `SELECT`.

    NOTE: this is a delimited set of table expressions, with a variable
    number of optional join clauses with those table expressions. The
    delmited aspect is the higher of the two such that the following is
    valid (albeit unusual):

    ```
    SELECT *
    FROM a JOIN b, c JOIN d
    ```

    Overriding ANSI to remove Delimited logic which assumes statements have been delimited
    """

    type = "from_clause"
    match_grammar = Sequence(
        "FROM",
        AnyNumberOf(
            Sequence(
                Ref("FromExpressionSegment"),
                Ref("CommaSegment"),
            ),
        ),
        Ref("FromExpressionSegment"),
        Ref("DelimiterSegment", optional=True),
    )

    get_eventual_aliases = ansi_dialect.get_segment(
        "FromClauseSegment"
    ).get_eventual_aliases


@tsql_dialect.segment(replace=True)
class GroupByClauseSegment(BaseSegment):
    """A `GROUP BY` clause like in `SELECT`.

    Overriding ANSI to remove Delimited logic which assumes statements have been delimited
    """

    type = "groupby_clause"
    match_grammar = Sequence(
        "GROUP",
        "BY",
        Indent,
        OneOf(
            Ref("ColumnReferenceSegment"),
            # Can `GROUP BY 1`
            Ref("NumericLiteralSegment"),
            # Can `GROUP BY coalesce(col, 1)`
            Ref("ExpressionSegment"),
        ),
        AnyNumberOf(
            Ref("CommaSegment"),
            OneOf(
                Ref("ColumnReferenceSegment"),
                # Can `GROUP BY 1`
                Ref("NumericLiteralSegment"),
                # Can `GROUP BY coalesce(col, 1)`
                Ref("ExpressionSegment"),
            ),
        ),
        Dedent,
    )


@tsql_dialect.segment(replace=True)
class HavingClauseSegment(BaseSegment):
    """A `HAVING` clause like in `SELECT`.

    Overriding ANSI to remove StartsWith with greedy terminator
    """

    type = "having_clause"
    match_grammar = Sequence(
        "HAVING",
        Indent,
        OptionallyBracketed(Ref("ExpressionSegment")),
        Dedent,
    )


@tsql_dialect.segment(replace=True)
class OrderByClauseSegment(BaseSegment):
    """A `ORDER BY` clause like in `SELECT`.

    Overriding ANSI to remove StartsWith logic which assumes statements have been delimited
    """

    type = "orderby_clause"
    match_grammar = Sequence(
        "ORDER",
        "BY",
        Indent,
        Sequence(
            OneOf(
                Ref("ColumnReferenceSegment"),
                # Can `ORDER BY 1`
                Ref("NumericLiteralSegment"),
                # Can order by an expression
                Ref("ExpressionSegment"),
            ),
            OneOf("ASC", "DESC", optional=True),
        ),
        AnyNumberOf(
            Sequence(
                Ref("CommaSegment"),
                Sequence(
                    OneOf(
                        Ref("ColumnReferenceSegment"),
                        # Can `ORDER BY 1`
                        Ref("NumericLiteralSegment"),
                        # Can order by an expression
                        Ref("ExpressionSegment"),
                    ),
                    OneOf("ASC", "DESC", optional=True),
                ),
            ),
        ),
        Dedent,
    )


@tsql_dialect.segment()
class RenameStatementSegment(BaseSegment):
    """`RENAME` statement.

    https://docs.microsoft.com/en-us/sql/t-sql/statements/rename-transact-sql?view=aps-pdw-2016-au7
    Azure Synapse Analytics-specific.
    """

    type = "rename_statement"
    match_grammar = Sequence(
        "RENAME",
        "OBJECT",
        Ref("ObjectReferenceSegment"),
        "TO",
        Ref("SingleIdentifierGrammar"),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
class DropStatementSegment(BaseSegment):
    """A `DROP` statement.

    Overriding ANSI to add optional delimiter.
    """

    type = "drop_statement"
    match_grammar = ansi_dialect.get_segment("DropStatementSegment").match_grammar.copy(
        insert=[
            Ref("DelimiterSegment", optional=True),
        ],
    )


@tsql_dialect.segment(replace=True)
class UpdateStatementSegment(BaseSegment):
    """An `Update` statement.

    UPDATE <table name> SET <set clause list> [ WHERE <search condition> ]
    Overriding ANSI in order to allow for PostTableExpressionGrammar (table hints)
    """

    type = "update_statement"
    match_grammar = Sequence(
        "UPDATE",
        OneOf(Ref("TableReferenceSegment"), Ref("AliasedTableReferenceGrammar")),
        Ref("PostTableExpressionGrammar", optional=True),
        Ref("SetClauseListSegment"),
        Ref("FromClauseSegment", optional=True),
        Ref("WhereClauseSegment", optional=True),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment(replace=True)
class SetClauseListSegment(BaseSegment):
    """set clause list.

    Overriding ANSI to remove Delimited
    """

    type = "set_clause_list"
    match_grammar = Sequence(
        "SET",
        Indent,
        Ref("SetClauseSegment"),
        AnyNumberOf(
            Ref("CommaSegment"),
            Ref("SetClauseSegment"),
        ),
        Dedent,
    )


@tsql_dialect.segment(replace=True)
class SetClauseSegment(BaseSegment):
    """Set clause.

    Overriding ANSI to allow for ExpressionSegment on the right
    """

    type = "set_clause"

    match_grammar = Sequence(
        Ref("ColumnReferenceSegment"),
        Ref("EqualsSegment"),
        Ref("ExpressionSegment"),
    )


@tsql_dialect.segment(replace=True)
class DatePartFunctionNameSegment(BaseSegment):
    """DATEADD function name segment.

    Override to support DATEDIFF as well
    """

    type = "function_name"
    match_grammar = OneOf("DATEADD", "DATEDIFF", "DATEDIFF_BIG", "DATENAME")


@tsql_dialect.segment()
class PrintStatementSegment(BaseSegment):
    """PRINT statement segment."""

    type = "print_statement"
    match_grammar = Sequence(
        "PRINT",
        Ref("ExpressionSegment"),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment()
class OptionClauseSegment(BaseSegment):
    """Query Hint clause.

    https://docs.microsoft.com/en-us/sql/t-sql/queries/hints-transact-sql-query?view=sql-server-ver15
    """

    type = "option_clause"
    match_grammar = Sequence(
        Sequence("OPTION", optional=True),
        Bracketed(
            Ref("QueryHintSegment"),
            AnyNumberOf(
                Ref("CommaSegment"),
                Ref("QueryHintSegment"),
            ),
        ),
    )


@tsql_dialect.segment()
class QueryHintSegment(BaseSegment):
    """Query Hint segment.

    https://docs.microsoft.com/en-us/sql/t-sql/queries/hints-transact-sql-query?view=sql-server-ver15
    """

    type = "query_hint_segment"
    match_grammar = OneOf(
        Sequence(  # Azure Synapse Analytics specific
            "LABEL",
            Ref("EqualsSegment"),
            Ref("QuotedLiteralSegment"),
        ),
        Sequence(
            OneOf("HASH", "ORDER"),
            "GROUP",
        ),
        Sequence(OneOf("MERGE", "HASH", "CONCAT"), "UNION"),
        Sequence(OneOf("LOOP", "MERGE", "HASH"), "JOIN"),
        Sequence("EXPAND", "VIEWS"),
        Sequence(
            OneOf(
                "FAST",
                "MAXDOP",
                "MAXRECURSION",
                "QUERYTRACEON",
                Sequence(
                    OneOf(
                        "MAX_GRANT_PERCENT",
                        "MIN_GRANT_PERCENT",
                    ),
                    Ref("EqualsSegment"),
                ),
            ),
            Ref("NumericLiteralSegment"),
        ),
        Sequence("FORCE", "ORDER"),
        Sequence(
            OneOf("FORCE", "DISABLE"),
            OneOf("EXTERNALPUSHDOWN", "SCALEOUTEXECUTION"),
        ),
        Sequence(
            OneOf(
                "KEEP",
                "KEEPFIXED",
                "ROBUST",
            ),
            "PLAN",
        ),
        "IGNORE_NONCLUSTERED_COLUMNSTORE_INDEX",
        "NO_PERFORMANCE_SPOOL",
        Sequence(
            "OPTIMIZE",
            "FOR",
            OneOf(
                "UNKNOWN",
                Bracketed(
                    Ref("ParameterNameSegment"),
                    OneOf(
                        "UNKNOWN", Sequence(Ref("EqualsSegment"), Ref("LiteralGrammar"))
                    ),
                    AnyNumberOf(
                        Ref("CommaSegment"),
                        Ref("ParameterNameSegment"),
                        OneOf(
                            "UNKNOWN",
                            Sequence(Ref("EqualsSegment"), Ref("LiteralGrammar")),
                        ),
                    ),
                ),
            ),
        ),
        Sequence("PARAMETERIZATION", OneOf("SIMPLE", "FORCED")),
        "RECOMPILE",
        Sequence(
            "USE",
            "HINT",
            Bracketed(
                Ref("QuotedLiteralSegment"),
                AnyNumberOf(Ref("CommaSegment"), Ref("QuotedLiteralSegment")),
            ),
        ),
        Sequence(
            "USE",
            "PLAN",
            OneOf(Ref("QuotedLiteralSegment"), Ref("QuotedLiteralSegmentWithN")),
        ),
        Sequence(
            "TABLE",
            "HINT",
            Ref("ObjectReferenceSegment"),
            Ref("TableHintSegment"),
            AnyNumberOf(
                Ref("CommaSegment"),
                Ref("TableHintSegment"),
            ),
        ),
    )


@tsql_dialect.segment(replace=True)
class PostTableExpressionGrammar(BaseSegment):
    """Table Hint clause.  Overloading the PostTableExpressionGrammar to implement.

    https://docs.microsoft.com/en-us/sql/t-sql/queries/hints-transact-sql-table?view=sql-server-ver15
    """

    match_grammar = Sequence(
        Sequence("WITH", optional=True),
        Bracketed(
            Ref("TableHintSegment"),
            AnyNumberOf(
                Ref("CommaSegment"),
                Ref("TableHintSegment"),
            ),
        ),
    )


@tsql_dialect.segment()
class TableHintSegment(BaseSegment):
    """Table Hint segment.

    https://docs.microsoft.com/en-us/sql/t-sql/queries/hints-transact-sql-table?view=sql-server-ver15
    """

    type = "query_hint_segment"
    match_grammar = OneOf(
        "NOEXPAND",
        Sequence(
            "INDEX",
            Bracketed(
                OneOf(Ref("IndexReferenceSegment"), Ref("NumericLiteralSegment")),
                AnyNumberOf(
                    Ref("CommaSegment"),
                    OneOf(
                        Ref("IndexReferenceSegment"),
                        Ref("NumericLiteralSegment"),
                    ),
                ),
            ),
        ),
        Sequence(
            "INDEX",
            Ref("EqualsSegment"),
            Bracketed(
                OneOf(Ref("IndexReferenceSegment"), Ref("NumericLiteralSegment")),
            ),
        ),
        "KEEPIDENTITY",
        "KEEPDEFAULTS",
        Sequence(
            "FORCESEEK",
            Bracketed(
                Ref("IndexReferenceSegment"),
                Bracketed(
                    Ref("SingleIdentifierGrammar"),
                    AnyNumberOf(Ref("CommaSegment"), Ref("SingleIdentifierGrammar")),
                ),
                optional=True,
            ),
        ),
        "FORCESCAN",
        "HOLDLOCK",
        "IGNORE_CONSTRAINTS",
        "IGNORE_TRIGGERS",
        "NOLOCK",
        "NOWAIT",
        "PAGLOCK",
        "READCOMMITTED",
        "READCOMMITTEDLOCK",
        "READPAST",
        "READUNCOMMITTED",
        "REPEATABLEREAD",
        "ROWLOCK",
        "SERIALIZABLE",
        "SNAPSHOT",
        Sequence(
            "SPATIAL_WINDOW_MAX_CELLS",
            Ref("EqualsSegment"),
            Ref("NumericLiteralSegment"),
        ),
        "TABLOCK",
        "TABLOCKX",
        "UPDLOCK",
        "XLOCK",
    )


@tsql_dialect.segment(replace=True)
class SetExpressionSegment(BaseSegment):
    """A set expression with either Union, Minus, Except or Intersect.

    Overriding ANSI to include OPTION clause.
    """

    type = "set_expression"
    # match grammar
    match_grammar = Sequence(
        Ref("NonSetSelectableGrammar"),
        AnyNumberOf(
            Sequence(
                Ref("SetOperatorSegment"),
                Ref("NonSetSelectableGrammar"),
            ),
            min_times=1,
        ),
        Ref("OrderByClauseSegment", optional=True),
        Ref("OptionClauseSegment", optional=True),
        Ref("DelimiterSegment", optional=True),
    )


@tsql_dialect.segment()
class ExecuteScriptSegment(BaseSegment):
    """`EXECUTE` statement.

    Matching segment name and type from exasol.
    https://docs.microsoft.com/en-us/sql/t-sql/language-elements/execute-transact-sql?view=sql-server-ver15
    """

    type = "execute_script_statement"
    match_grammar = Sequence(
        OneOf("EXEC", "EXECUTE"),
        Ref("ObjectReferenceSegment"),
        Sequence(
            Sequence(Ref("ParameterNameSegment"), Ref("EqualsSegment"), optional=True),
            OneOf(
                "DEFAULT",
                Ref("LiteralGrammar"),
                Ref("ParameterNameSegment"),
                Ref("SingleIdentifierGrammar"),
            ),
            Sequence("OUTPUT", optional=True),
            AnyNumberOf(
                Ref("CommaSegment"),
                Sequence(
                    Ref("ParameterNameSegment"), Ref("EqualsSegment"), optional=True
                ),
                OneOf(
                    "DEFAULT",
                    Ref("LiteralGrammar"),
                    Ref("ParameterNameSegment"),
                    Ref("SingleIdentifierGrammar"),
                ),
                Sequence("OUTPUT", optional=True),
            ),
            optional=True,
        ),
        Ref("DelimiterSegment", optional=True),
    )

```