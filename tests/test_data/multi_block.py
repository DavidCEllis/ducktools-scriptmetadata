# Multiple block descrepency between the regex in the pep
# and the text description.

# /// pyproject
# run.dependencies = [
#     "ducktools-lazyimporter>=0.1.1",
# ]
# ///
#
# Middle Comment
#
# /// newblock
# newblock data
# ///

import textwrap

output = {
    "pyproject":
        textwrap.dedent("""
        run.dependencies = [
            "ducktools-lazyimporter>=0.1.1",
        ]
        """).lstrip(),
    "newblock":
        "newblock data\n",
}

is_error = False

# Internals
strict_error = False
exact_error = None
