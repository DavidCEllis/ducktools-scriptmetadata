# ducktools: pep723parser #

Lazy parser for PEP723 embedded TOML data.

## Example ##

```python
from ducktools.pep723parser import PEP723Parser
from pprint import pprint

parser = PEP723Parser.from_path("examples/pep-723-sample.py")

pprint(parser.script_dependencies)
```

Output:
```
{'dependencies': [<Requirement('requests<3')>, <Requirement('rich')>],
 'requires-python': <SpecifierSet('>=3.11')>}
```
