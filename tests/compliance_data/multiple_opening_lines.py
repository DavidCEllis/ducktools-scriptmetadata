# /// script
# dependencies = ["requests"]
# /// script
# requires-python = ">=3.11"
# ///

import textwrap

output = {
    "script": textwrap.dedent(
        """
        dependencies = ["requests"]
        /// script
        requires-python = ">=3.11"
        """
    ).lstrip()
}

is_error = False

# Internals
exact_error = None
