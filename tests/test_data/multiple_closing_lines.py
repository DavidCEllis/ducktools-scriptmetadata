# /// pyproject
# [run]
# dependencies = ["requests"]
# ///
# Additional comment
# ///

import textwrap

output = {
    "pyproject":
        textwrap.dedent("""
        [run]
        dependencies = ["requests"]
        """).lstrip()
}

is_error = False

# Internals
strict_error = False
exact_error = None
