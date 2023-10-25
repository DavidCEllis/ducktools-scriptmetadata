# /// pyproject
# [run]
# requires-python = ">=3.11"
# dependencies = [
#   "requests<3",
#   "rich",
# ]


output = {}
is_error = False

# Internal
strict_error = True
exact_error = SyntaxError(
    f"Block 'pyproject' not closed correctly. "
    f"A '# ///' block is needed to indicate the end of the block."
)
