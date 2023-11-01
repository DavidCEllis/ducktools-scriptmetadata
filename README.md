# ducktools: pep723parser #

Parser for embedded metadata in python source files 
as defined in [PEP723](https://peps.python.org/pep-0723/).

## Example ##

```python
from ducktools.pep723parser import metadata_from_path
from pprint import pprint

metadata = metadata_from_path("examples/pep-723-sample.py")

pprint(metadata.run_requirements)
```

Output:
```
{'dependencies': [<Requirement('requests<3')>, <Requirement('rich')>],
 'requires-python': <SpecifierSet('>=3.11')>}
```

## Available Methods ##

To create a PEP723Parser there are 2 class methods provided

```python
from pathlib import Path

from ducktools.pep723parser import (
    metadata_from_path,
    metadata_from_string,
)

src_path = Path("examples/pep-723-sample.py")

# Create a parser from a path to a source file
metadata = metadata_from_path(src_path, encoding="utf-8")

# Create a parser from source code as a string
metadata = metadata_from_string(src_path.read_text())

# Get all metadata blocks and unprocessed text as a dict
metadata.blocks

# Return the unprocessed pyproject block text or None 
# if there is no block
metadata.pyproject_text

# Return the pyproject block processed by tomllib/tomli
# or return an empty dict if there is no block
metadata.pyproject_toml

# Return the [run] block from the pyproject block
# requires-python and dependencies values will exist
# as empty data even if not defined in the block
metadata.run_requirements_text

# Return the [run] block from the pyproject block
# with requires-python and dependencies values processed
# by packaging into SpecifierSet and Requirement objects
metadata.run_requirements
```
