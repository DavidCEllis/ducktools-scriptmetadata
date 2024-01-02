# ducktools: script_metadata_parser #

Parser for embedded metadata in python source files 
as defined in [PEP723](https://peps.python.org/pep-0723/).

Inline script metadata can be extracted from a file path, from a string
or from an iterable of lines (such as an open file).

This module does not attempt to parse the contents of the metadata blocks
in any way.

```python
from pathlib import Path

from ducktools.script_metadata_parser import parse_source, parse_file, parse_iterable

src_path = Path("examples/pep-723-sample.py")

# Parse from a link to a file
metadata = parse_file(src_path, encoding="utf-8")

# Parse from source code as a string
metadata = parse_source(src_path.read_text())

# Parse from an iterable of source code lines
with src_path.open("r") as f:
    metadata = parse_iterable(f, start_line=1)

# Get all metadata blocks and unprocessed text as a dict
metadata.blocks

# View any warnings about potentially malformed blocks
metadata.warnings
```

## Why not use the regex from the PEP? ##

Using the regex would correctly extract blocks that have been defined correctly
it does not provide a way to give additional warnings to users about potentially
malformed blocks.

Importing the python regex module is also slower than parsing the source in this
way.

Python 3.12 on Windows parsing the example file:

```
hyperfine -w3 -r100 "python -c \"import re\"" "python perf\ducktools_parse.py" "python perf\regex_parse.py"

Benchmark 1: python -c "import re"
  Time (mean ± σ):      29.6 ms ±   0.9 ms    [User: 14.9 ms, System: 14.7 ms]
  Range (min … max):    28.3 ms …  32.8 ms    100 runs

Benchmark 2: python perf\ducktools_parse.py
  Time (mean ± σ):      24.4 ms ±   0.5 ms    [User: 11.1 ms, System: 14.4 ms]
  Range (min … max):    23.4 ms …  26.4 ms    100 runs

Benchmark 3: python perf\regex_parse.py
  Time (mean ± σ):      30.5 ms ±   0.6 ms    [User: 12.2 ms, System: 14.9 ms]
  Range (min … max):    29.5 ms …  32.7 ms    100 runs

Summary
  python perf\ducktools_parse.py ran
    1.21 ± 0.05 times faster than python -c "import re"
    1.25 ± 0.04 times faster than python perf\regex_parse.py
```