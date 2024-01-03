"""
The original example block from the PEP. Modified to have the closing block at EOF.
"""

import textwrap

output = {
    "script": textwrap.dedent(
        """
        requires-python = ">=3.11"
        dependencies = [
          "requests<3",
          "rich",
        ]
        """
    ).lstrip()
}

is_error = False

# Internal
exact_error = None

# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests<3",
#   "rich",
# ]
# ///