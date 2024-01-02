# ducktools: script_metadata_parser #

Parser for embedded metadata in python source files 
as defined in [PEP723](https://peps.python.org/pep-0723/).

Inline script metadata can be extracted from a file path, from a string
or from an iterable of lines (such as an open file).

This module does not attempt to parse the contents of the metadata blocks
in any way.

```python
from pathlib import Path

from ducktools.script_metadata_parser import ScriptMetadata

src_path = Path("examples/pep-723-sample.py")

# Create a parser from a path to a source file
metadata = ScriptMetadata.from_path(src_path, encoding="utf-8")

# Create a parser from source code as a string
metadata = ScriptMetadata.from_string(src_path.read_text())

# Get all metadata blocks and unprocessed text as a dict
metadata.blocks

# View any warnings about potentially malformed blocks
metadata.warnings
```
