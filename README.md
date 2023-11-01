# ducktools: pep723parser #

Lazy parser for PEP723 embedded TOML data.

## Example ##

```python
from ducktools.pep723parser import EmbeddedMetadataParser
from pprint import pprint

parser = EmbeddedMetadataParser.from_path("examples/pep-723-sample.py")

pprint(parser.script_dependencies)
```

Output:
```
{'dependencies': [<Requirement('requests<3')>, <Requirement('rich')>],
 'requires-python': <SpecifierSet('>=3.11')>}
```

## Available Methods ##

To create a PEP723Parser there are 2 class methods provided

```python
# Create a parser from a path to a source file
parser = PEP723Parser.from_path(src_path, encoding="utf-8")

# Create a parser from source code as a string
parser = PEP723Parser.from_source(src)
```

The resulting parser objects provide the following methods.

```python
# iter_raw_metadata_blocks to iterate over the metadata blocks
# yield the block name (type) and its contents as tuples
# Note: this will raise a ValueError if a block with the same
#       block_name is encountered multiple times.
parser.iter_raw_metadata_blocks()

# Scan through the file and return the text of the first
# metadata block encountered with the specified block_name
# raise a KeyError if not found.
parser.get_first_metadata_block("pyproject")

# Get all metadata blocks and unprocessed text as a dict
parser.metadata_blocks

# Get the unprocessed pyproject text or raise a KeyError 
# if there is no block
parser.get_pyproject_raw()

# Return the unprocessed pyproject text or None if there is no block
parser.pyproject_raw

# Get the pyproject block processed by tomllib/tomli
# or raise a KeyError if there is no block
parser.get_pyproject_toml()

# Return the pyproject block processed by tomllib/tomli
# or return None if there is no block
parser.pyproject_toml

# Return the [run] block from the pyproject block
# requires-python and dependencies values will exist
# as empty data even if not defined in the block
parser.plain_script_dependencies

# Return the [run] block from the pyproject block
# with requires-python and dependencies values processed
# by packaging into SpecifierSet and Requirement objects
parser.script_dependencies
```