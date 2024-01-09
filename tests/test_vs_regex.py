import pytest

from ducktools.scriptmetadata import parse_file
import compliance_data

# REGEX IMPLEMENTATION #
import re

REGEX = r"(?m)^# /// (?P<type>[a-zA-Z0-9-]+)$\s(?P<content>(^#(| .*)$\s)+)^# ///$"


# From the PEP
def _stream(script):
    for match in re.finditer(REGEX, script):
        yield match.group("type"), "".join(
            line[2:] if line.startswith("# ") else line[1:]
            for line in match.group("content").splitlines(keepends=True)
        )


def _get_blocks(pth):
    with open(pth, "r") as f:
        src = f.read()

    return {name: content for name, content in _stream(src)}


@pytest.mark.parametrize("module_name", dir(compliance_data))
def test_matches_regex(module_name):
    module = getattr(compliance_data, module_name)
    try:
        metadata = parse_file(module.__file__)
    except Exception as e:
        assert module.is_error
        assert type(e) is type(module.exact_error) and e.args == module.exact_error.args
    else:
        assert metadata.blocks == _get_blocks(module.__file__)
