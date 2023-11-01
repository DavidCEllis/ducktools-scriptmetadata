from ducktools.pep723parser import EmbeddedMetadataParser, _is_valid_type
from pathlib import Path
from packaging.specifiers import SpecifierSet
from packaging.requirements import Requirement

try:
    import tomllib
except ImportError:
    import tomli as tomllib

import pytest

example_folder = Path(__file__).parent / "example_files"


pep_723_ex_extracted_dict = {
    "run": {
        "requires-python": ">=3.11",
        "dependencies": [
            "requests<3",
            "rich",
        ],
    }
}

pep_723_plain_script_dependencies = pep_723_ex_extracted_dict["run"]

pep_723_script_dependencies = {
    "requires-python": SpecifierSet(">=3.11"),
    "dependencies": [
        Requirement("requests<3"),
        Requirement("rich"),
    ],
}


class TestParsePEPExample:
    @property
    def file_parser(self):
        test_file = example_folder / "pep-723-sample.py"
        return EmbeddedMetadataParser.from_path(test_file)

    @property
    def str_parser(self):
        test_file = example_folder / "pep-723-sample.py"
        test_text = test_file.read_text()
        return EmbeddedMetadataParser.from_string(test_text)

    @pytest.mark.parametrize("parser_type", ["file_parser", "str_parser"])
    def test_pep_example_file_toml(self, parser_type):
        parser = getattr(self, parser_type)
        output = parser.get_pyproject_toml()
        assert output == pep_723_ex_extracted_dict

    @pytest.mark.parametrize("parser_type", ["file_parser", "str_parser"])
    def test_pep_example_file_plain_script_dependencies(self, parser_type):
        parser = getattr(self, parser_type)
        output = parser.plain_script_dependencies
        assert output == pep_723_plain_script_dependencies

    @pytest.mark.parametrize("parser_type", ["file_parser", "str_parser"])
    def test_pep_example_file_script_dependencies(self, parser_type):
        parser = getattr(self, parser_type)
        output = parser.script_dependencies
        assert output == pep_723_script_dependencies


class TestRaises:
    def test_new_block_without_close(self):
        test_file = example_folder / "valid_but_errors_double_block.py"
        parser = EmbeddedMetadataParser.from_path(test_file)

        # Fails TOML parse
        with pytest.raises(tomllib.TOMLDecodeError):
            _ = parser.pyproject_toml

    def test_block_not_closed(self):
        test_file = example_folder / "pep-723-sample-noclose.py"
        parser = EmbeddedMetadataParser.from_path(test_file)
        with pytest.warns(UserWarning):
            _ = parser.script_dependencies

    def test_block_not_closed_eof(self):
        test_file = example_folder / "pep-723-sample-noclose-eof.py"
        parser = EmbeddedMetadataParser.from_path(test_file)
        with pytest.warns(UserWarning):
            _ = parser.script_dependencies

    def test_repeated_block(self):
        test_file = example_folder / "invalid_repeated_block.py"
        parser = EmbeddedMetadataParser.from_path(test_file)

        with pytest.raises(ValueError):
            _ = parser.metadata_blocks

        with pytest.raises(ValueError):
            _ = list(parser.iter_raw_metadata_blocks())


class TestMissing:
    @property
    def parser(self):
        test_file = example_folder / "example_no_pyproject_block.py"
        return EmbeddedMetadataParser.from_path(test_file)

    def test_missing_errors(self):
        parser = self.parser

        with pytest.raises(KeyError):
            _ = parser.get_first_metadata_block("Missing")

        with pytest.raises(KeyError):
            _ = parser.get_pyproject_raw()

        with pytest.raises(KeyError):
            _ = parser.get_pyproject_toml()

    def test_missing_none(self):
        parser = self.parser

        assert parser.pyproject_raw is None
        assert parser.pyproject_toml is None

    def test_missing_empty(self):
        parser = self.parser

        assert parser.script_dependencies == {
            "requires-python": None,
            "dependencies": [],
        }


class TestSpec:
    # Test that matches the text of the spec but not the regex
    # as of 23-Oct-2023
    def test_multi_block(self):
        test_file = example_folder / "multi_block_discrepency.py"
        parser = EmbeddedMetadataParser.from_path(test_file)

        output_text_pyproject = (
            "run.dependencies = [\n" '    "ducktools-lazyimporter>=0.1.1",\n' "]\n"
        )
        output_text_newblock = "newblock data\n"

        assert parser.metadata_blocks["pyproject"] == output_text_pyproject
        assert parser.metadata_blocks["newblock"] == output_text_newblock


def test_toml_extension_warning():
    test_file = example_folder / "toml_warning.py"
    parser = EmbeddedMetadataParser.from_path(test_file)

    with pytest.warns(
            UserWarning,
            match="'pyproject.toml' block found, should be 'pyproject'."
    ):
        _ = parser.metadata_blocks


def test_invalid_parser_init():
    with pytest.raises(ValueError):
        _ = EmbeddedMetadataParser()

    with pytest.raises(ValueError):
        _ = EmbeddedMetadataParser(src="Code", src_path="path/to/file")


def test_valid_types():
    assert _is_valid_type("pyproject")
    assert _is_valid_type("test-example123")
    assert _is_valid_type("123test-example")
    assert not _is_valid_type("example_with_underscores")
    assert not _is_valid_type("pyproject.toml")
    assert not _is_valid_type("random$extra!characters")
    assert not _is_valid_type("\"internalquotes\"")
