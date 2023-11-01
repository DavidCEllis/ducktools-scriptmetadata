from ducktools.pep723parser import (
    metadata_from_string,
    metadata_from_path,
    _is_valid_type,
)
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

pep_723_run_requirements_text = pep_723_ex_extracted_dict["run"]

pep_723_run_requirements = {
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
        return metadata_from_path(test_file)

    @property
    def str_parser(self):
        test_file = example_folder / "pep-723-sample.py"
        test_text = test_file.read_text()
        return metadata_from_string(test_text)

    @pytest.mark.parametrize("parser_type", ["file_parser", "str_parser"])
    def test_pep_example_file_toml(self, parser_type):
        parser = getattr(self, parser_type)
        output = parser.pyproject_toml
        assert output == pep_723_ex_extracted_dict

    @pytest.mark.parametrize("parser_type", ["file_parser", "str_parser"])
    def test_pep_example_run_requirements_text(self, parser_type):
        parser = getattr(self, parser_type)
        output = parser.run_requirements_text
        assert output == pep_723_run_requirements_text

    @pytest.mark.parametrize("parser_type", ["file_parser", "str_parser"])
    def test_pep_example_run_requirements(self, parser_type):
        parser = getattr(self, parser_type)
        output = parser.run_requirements
        assert output == pep_723_run_requirements


class TestRaises:
    def test_new_block_without_close(self):
        test_file = example_folder / "valid_but_errors_double_block.py"
        parser = metadata_from_path(test_file)

        # Fails TOML parse
        with pytest.raises(tomllib.TOMLDecodeError):
            _ = parser.pyproject_toml

    def test_block_not_closed(self):
        test_file = example_folder / "pep-723-sample-noclose.py"
        parser = metadata_from_path(test_file)
        assert len(parser.warnings) > 0
        assert "Potential unclosed block" in parser.warnings[0]

    def test_block_not_closed_eof(self):
        test_file = example_folder / "pep-723-sample-noclose-eof.py"
        parser = metadata_from_path(test_file)

        assert len(parser.warnings) > 0
        assert "Potential unclosed block" in parser.warnings[0]

    def test_repeated_block(self):
        test_file = example_folder / "invalid_repeated_block.py"

        with pytest.raises(ValueError):
            _ = metadata_from_path(test_file)


class TestMissing:
    @property
    def parser(self):
        test_file = example_folder / "example_no_pyproject_block.py"
        return metadata_from_path(test_file)

    def test_missing_none(self):
        parser = self.parser

        assert parser.pyproject_text is None
        assert parser.pyproject_toml == {}

    def test_missing_empty(self):
        parser = self.parser

        assert parser.run_requirements == {
            "requires-python": None,
            "dependencies": [],
        }


class TestSpec:
    # Test that matches the updated spec
    def test_multi_block(self):
        test_file = example_folder / "multi_block_discrepency.py"
        parser = metadata_from_path(test_file)

        output_text_pyproject = (
            'run.dependencies = [\n'
            '    "ducktools-lazyimporter>=0.1.1",\n'
            ']\n'
            '///\n'
            '\n'
            'Middle Comment\n'
            '\n'
            '/// newblock\n'
            'newblock data\n'
        )

        assert parser.pyproject_text == output_text_pyproject


def test_toml_extension_warning():
    test_file = example_folder / "toml_warning.py"
    parser = metadata_from_path(test_file)

    assert "'pyproject.toml' block found, should be 'pyproject'." in parser.warnings[0]


def test_valid_types():
    assert _is_valid_type("pyproject")
    assert _is_valid_type("test-example123")
    assert _is_valid_type("123test-example")
    assert not _is_valid_type("example_with_underscores")
    assert not _is_valid_type("pyproject.toml")
    assert not _is_valid_type("random$extra!characters")
    assert not _is_valid_type("\"internalquotes\"")