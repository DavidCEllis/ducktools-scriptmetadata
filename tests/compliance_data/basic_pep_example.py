"""
The original example block from the PEP.
"""

# /// pyproject
# [run]
# requires-python = ">=3.11"
# dependencies = [
#   "requests<3",
#   "rich",
# ]
# ///

import textwrap

output = {
    "pyproject": textwrap.dedent(
        """
        [run]
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
