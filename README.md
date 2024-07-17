# ducktools: scriptmetadata #

Parser for embedded metadata in python source files 
originally defined in [PEP-723](https://peps.python.org/pep-0723/) 
and 
[specified on packaging.python.org](https://packaging.python.org/en/latest/specifications/inline-script-metadata/#inline-script-metadata).

Inline script metadata can be extracted from a file path, from a string
or from an iterable of lines (such as an open file).

This module does not attempt to parse the contents of the metadata blocks
in any way.

## How to Install ##

Install this module via PyPI

`python -m pip install ducktools-scriptmetadata`

```python
from pathlib import Path

from ducktools.scriptmetadata import parse_source, parse_file, parse_iterable

src_path = Path("examples/pep-723-sample.py")

# Parse from a link to a file
metadata = parse_file(src_path, encoding="utf-8")

# Parse from source code as a string
metadata = parse_source(src_path.read_text())

# Parse from an iterable of source code lines
with src_path.open("r") as f:
    metadata = parse_iterable(f, start_line=1)

# Get all metadata block names and plaintext content as a dict
metadata.blocks

# Get a list of warnings about potentially malformed blocks
metadata.warnings
```

## Inputs and Outputs ##

### PEP-723 Example Input ###

```
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests<3",
#   "rich",
# ]
# ///
```

**metadata.blocks**:
```
{'script': 'requires-python = ">=3.11"\ndependencies = [\n  "requests<3",\n  "rich",\n]\n'}
```

**metadata.warnings**:
```
[]
```

### Incomplete block ###

```
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests<3",
#   "rich",
# ]
```

**metadata.blocks**:
```
{}
```

**metadata.warnings**:
```
[MetadataWarning(line_number=7, message="Potential unclosed block 'script' detected. A '# ///' block is needed to indicate the end of the block.")]
```

## Example of usage with toml parsing/validation ##

An example script using `tomllib`/`tomli` to parse TOML and `packaging` to handle version and dependency specifiers.

```python
import warnings
from pathlib import Path
try:
    import tomllib
except ImportError:
    import tomli as tomllib
    
from packaging.specifiers import SpecifierSet
from packaging.requirements import Requirement

from ducktools.scriptmetadata import parse_file

def parse_requirements(f):
    data = parse_file(f)
    
    if script_block := data.blocks.get("script"):
        deps = tomllib.loads(script_block)
        requires_python = SpecifierSet(deps["requires-python"]) if "requires-python" in deps else None
        dependencies = [Requirement(dep) for dep in deps.get("dependencies", [])]
    else:
        requires_python = None
        dependencies = []
        
    if data.warnings:
        for message in data.warnings:
            warnings.warn(str(message))
    
    return {
        "requires-python": requires_python,
        "dependencies": dependencies,
    }

example_success = Path("examples/pep-723-sample.py")
example_warning = Path("examples/incomplete_example.py")

print("Valid metadata block output:")
print(parse_requirements(example_success))
print()
print("Incomplete metadata block output:")
print(parse_requirements(example_warning))
```

Output:
```
Valid metadata block output:
{'requires-python': <SpecifierSet('>=3.11')>, 'dependencies': [<Requirement('requests<3')>, <Requirement('rich')>]}

Incomplete metadata block output:
{'requires-python': None, 'dependencies': []}
<Source Location>: UserWarning: Line 7: Potential unclosed block 'script' detected. A '# ///' block is needed to indicate the end of the block.
  warnings.warn(message)
```

## Why not include the TOML/requirements parsing in this module ##

I wanted to provide a parser that purely handled the *new* format for metadata.
TOML parsing and validation of version specifiers can then be handled by whichever
library the user prefers.

For example: If someone wanted to add inline metadata support to an existing tool
that used `rtoml` to handle other toml parsing duties then it would make sense
for the toml parsing to be handled by that package instead of making the choice
to use `tomllib` (and incurring the import cost).

## Why not use the regex from the PEP/Specification page? ##

While using the regex would correctly extract valid metadata blocks it does not 
provide a way to give additional warnings to users about potential issues with 
incorrect block formatting.

This parser will collect warnings if it encounters an unclosed block, if it
detects multiple valid header lines within a block, and if a potential block 
name contains an invalid character.
It will raise an exception if multiple blocks with the same name are encountered.

Importing the python regex module is also slower than parsing the source in this
way.

Python 3.12 on Windows parsing the example file:

`hyperfine -w3 -r100 "python -c \"import re\"" "python perf\ducktools_parse.py" "python perf\regex_parse.py"`

```
Benchmark 1: python -c "import re"
  Time (mean ± σ):      30.0 ms ±   0.6 ms    [User: 15.1 ms, System: 11.7 ms]
  Range (min … max):    29.0 ms …  33.5 ms    100 runs

Benchmark 2: python perf\ducktools_parse.py
  Time (mean ± σ):      25.9 ms ±   0.8 ms    [User: 11.8 ms, System: 13.4 ms]
  Range (min … max):    24.9 ms …  30.0 ms    100 runs

Benchmark 3: python perf\regex_parse.py
  Time (mean ± σ):      31.6 ms ±   1.6 ms    [User: 16.7 ms, System: 13.9 ms]
  Range (min … max):    29.9 ms …  40.5 ms    100 runs

Summary
  python perf\ducktools_parse.py ran
    1.16 ± 0.04 times faster than python -c "import re"
    1.22 ± 0.07 times faster than python perf\regex_parse.py
```