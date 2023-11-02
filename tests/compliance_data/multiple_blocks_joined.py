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
    "pyproject": textwrap.dedent(
        """
        run.dependencies = [
            "ducktools-lazyimporter>=0.1.1",
        ]
        ///
        
        Middle Comment
        
        /// newblock
        newblock data
        """
    ).lstrip(),
}

is_error = False

# Internals
exact_error = None
