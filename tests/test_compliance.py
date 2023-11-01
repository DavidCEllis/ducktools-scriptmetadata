from pathlib import Path

import pytest

from ducktools.pep723parser import EmbeddedMetadata
import test_data


def get_parser(path, parse_type):
    path = Path(path)
    if parse_type == "string":
        return EmbeddedMetadata.from_string(path.read_text())
    elif parse_type == "path":
        return EmbeddedMetadata.from_path(path)


@pytest.mark.parametrize("parser_type", ["string", "path"])
@pytest.mark.parametrize("module_name", dir(test_data))
def test_compliance(parser_type, module_name):
    module = getattr(test_data, module_name)
    try:
        parser = get_parser(module.__file__, parser_type)
    except Exception as e:
        assert module.is_error
        assert type(e) is type(module.exact_error) and e.args == module.exact_error.args
    else:
        metadata = parser.blocks
        assert metadata == module.output
