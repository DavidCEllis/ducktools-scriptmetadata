# Python Embedded Metadata Compliance Test Data #

This is a set of python scripts containing embedded metadata
and the expected output. This can be used as a python
module.

The output is given as a python dictionary of the form
`{ TYPE: 'contents, ... }` with 'TYPE' as defined by the spec.
If the parser is expected to error, the module will have 
`module.is_error = True`.

Tests can be written using pytest as follows:

```python
import pytest
import compliance_data

# Use your parser here
from ducktools.scriptmetadata import parse_file


@pytest.mark.parametrize("module_name", dir(compliance_data))
def test_compliance(module_name):
    module = getattr(compliance_data, module_name)
    module_path = module.__file__

    try:
        metadata = parse_file(module_path)
    except Exception as e:
        assert module.is_error
    else:
        assert metadata.blocks == module.output
```

To use these tests in other languages the output can be extracted
as JSON by running compliance_data as a module.

`python -m compliance_data`

Will create a json_output folder containing the expected outputs.
