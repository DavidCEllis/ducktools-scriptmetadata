# /// pyproject
# [run]
# requires-python = ">=3.11"
# dependencies = [
#   "requests<3",
#   "rich",
# ]
# ///

# /// pyproject
# [run]
# requires-python = ">=3.11"
# dependencies = [
#   "requests<3",
#   "rich",
# ]
# ///

output = {}
is_error = True

# Internal
strict_error = True
exact_error = ValueError(f"Multiple 'pyproject' blocks found.")
