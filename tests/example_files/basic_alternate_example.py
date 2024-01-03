"""
Example with different data to the PEP example
"""

# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "attrs",
#   "cattrs",
# ]
# ///

import textwrap

output = {
    "script": textwrap.dedent(
        """
        requires-python = ">=3.12"
        dependencies = [
          "attrs",
          "cattrs",
        ]
        """
    ).lstrip()
}

is_error = False

# Internal
exact_error = None
