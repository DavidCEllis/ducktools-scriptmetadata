# /// script
# dependencies = ["requests"]
# ///
# Additional comment
# ///

import textwrap

output = {
    "script": textwrap.dedent(
        """
        dependencies = ["requests"]
        ///
        Additional comment
        """
    ).lstrip()
}

is_error = False

# Internals
exact_error = None
