from ducktools.script_metadata_parser import (
    _is_valid_type,
    parse_file,
    parse_source,
    ScriptMetadata,
)
from pathlib import Path


import pytest

example_folder = Path(__file__).parent / "example_files"


class TestParsePEPExample:
    @property
    def file_parser(self):
        test_file = example_folder / "pep-723-sample.py"
        return parse_file(test_file)

    def test_metadata_repr_eq(self):
        parser = self.file_parser

        rebuilt_parser = eval(
            repr(parser),
            {"ScriptMetadata": ScriptMetadata}
        )

        assert parser == rebuilt_parser


def test_eq_true():
    ex_1 = example_folder / "pep-723-sample.py"

    data_1 = parse_file(ex_1)
    data_2 = parse_file(ex_1)

    assert data_1 == data_2


def test_eq_false():
    ex_1 = example_folder / "pep-723-sample.py"
    ex_2 = example_folder / "basic_alternate_example.py"

    data_1 = parse_file(ex_1)
    data_2 = parse_file(ex_2)

    assert data_1 != data_2


def test_eq_othertype():
    ex_1 = example_folder / "pep-723-sample.py"

    data_1 = parse_file(ex_1)

    non_data = "Not Data"

    assert data_1 != non_data


class TestErrors:

    def test_block_not_closed(self):
        test_file = example_folder / "pep-723-sample-noclose.py"
        metadata = parse_file(test_file)
        assert len(metadata.warnings) > 0
        assert "Potential unclosed block" in metadata.warnings[0]

    def test_block_not_closed_eof(self):
        test_file = example_folder / "pep-723-sample-noclose-eof.py"
        metadata = parse_file(test_file)

        assert len(metadata.warnings) > 0
        assert "Potential unclosed block" in metadata.warnings[0]

    def test_repeated_block(self):
        test_file = example_folder / "invalid_repeated_block.py"

        with pytest.raises(ValueError):
            _ = parse_file(test_file)


def test_valid_types():
    assert _is_valid_type("pyproject")
    assert _is_valid_type("test-example123")
    assert _is_valid_type("123test-example")
    assert not _is_valid_type("example_with_underscores")
    assert not _is_valid_type("pyproject.toml")
    assert not _is_valid_type("random$extra!characters")
    assert not _is_valid_type("\"internalquotes\"")
