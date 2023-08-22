comment_symbols = {
    "ada": "--",
    "agda": "--",
    "apex": "//",
    "bash": "#",
    "beancount": ";",
    "cap’n proto": "#",
    "c": "//",
    "c++": "//",
    "c#": "//",
    "clojure": ";",
    "cmake": "#",
    "common lisp": ";",
    "css": "/* ",  # TDOO ... */
    "cuda": "//",
    "dart": "//",
    "d": "//",
    "dockerfile": "#",
    "dot": "//",
    "elixir": "#",
    "elm": "--",
    "emacs lisp": ";",
    "erb / ejs": "<%# ... %>",
    "erlang": "%",
    "fish": "#",
    "fortran": "!",
    "gitattributes": "#",
    "gitignore": "#",
    "gleam": "//",
    "go": "//",
    "graphql": "#",
    "haskell": "--",
    "html": "<!--",  # TODO:  ... -->
    "java": "//",
    "javascript": "//",
    "json5": "//",
    "julia": "#",
    "kotlin": "//",
    "latex": "%",
    "lua": "--",
    "make": "#",
    "motorola 68000 assembly": ";",
    "nix": "#",
    "objective-c": "//",
    "ocaml": "(*", # TODO ... *)
    "pascal": "{", # TODO ... }
    "perl": "#",
    "php": "//",
    "powershell": "#",
    "protocol buffers": "//",
    "python": "#",
    "racket": ";",
    "rego": "#",
    "restructuredtext": "..",
    "r": "#",
    "ruby": "#",
    "rust": "//",
    "scala": "//",
    "scheme": ";",
    "scss": "//",
    "s-expressions": ";",
    "sql": "--",
    "swift": "//",
    "toml": "#",
    "typescript": "//",
    "tsx": "//",
    "verilog": "//",
    "vhdl": "--",
    "vue": "<!-- ",  # TODO ... -->
    "yaml": "#",
    "zig": "//"
}


def get_comment_symbol(language):
    if language:
        return comment_symbols.get(language.lower(), None)
    return "//"

