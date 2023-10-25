import pytest

import test_data

from ducktools.pep723parser import PEP723Parser


@pytest.mark.parametrize('module_name', dir(test_data))
def test_compliance(module_name):
    module = getattr(test_data, module_name)
    parser = PEP723Parser.from_path(module.__file__)
    try:
        metadata = parser.metadata_blocks
    except Exception as e:
        assert module.is_error or module.strict_error
        assert type(e) is type(module.exact_error) and e.args == module.exact_error.args
    else:
        assert metadata == module.output
