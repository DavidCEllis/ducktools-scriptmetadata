"""
This is upside down because the block is at the end of the file.
"""

output = {}
is_error = False

# Internal
strict_error = True
exact_error = SyntaxError(
    f"Block 'pyproject' not closed correctly. "
    f"A '# ///' block is needed to indicate the end of the block."
)


# /// pyproject
# [run]
# requires-python = ">=3.11"
# dependencies = [
#   "requests<3",
#   "rich",
# ]