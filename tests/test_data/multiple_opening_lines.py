# /// pyproject
# [run]
# dependencies = ["requests"]
# /// pyproject
# requires-python = ">=3.11"
# ///

import textwrap

output = {
    "pyproject": textwrap.dedent(
        """
        [run]
        dependencies = ["requests"]
        /// pyproject
        requires-python = ">=3.11"
        """
    ).lstrip()
}

is_error = False

# Internals
exact_error = None
