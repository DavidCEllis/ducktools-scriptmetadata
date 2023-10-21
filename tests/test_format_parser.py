from ducktools.pep723parser import PEP723Parser
from pathlib import Path
from packaging.specifiers import SpecifierSet
from packaging.requirements import Requirement

import pytest

example_folder = Path(__file__).parent / "example_files"

pep_723_ex_raw = """
# /// pyproject
# [run]
# requires-python = ">=3.11"
# dependencies = [
#   "requests<3",
#   "rich",
# ]
# ///
"""

pep_723_ex_extracted = """
[run]
requires-python = ">=3.11"
dependencies = [
  "requests<3",
  "rich",
]
""".strip()

pep_723_ex_extracted_dict = {
    "run": {
        "requires-python": ">=3.11",
        "dependencies": [
            "requests<3",
            "rich",
        ]
    }
}

pep_723_plain_script_dependencies = pep_723_ex_extracted_dict["run"]

pep_723_script_dependencies = {
    "requires-python": SpecifierSet(">=3.11"),
    "dependencies": [
        Requirement("requests<3"),
        Requirement("rich"),
    ]
}

class TestParseOutputFile:
    @property
    def parser(self):
        test_file = example_folder / "pep-723-sample.py"
        return PEP723Parser.from_path(test_file)

    def test_pep_example_file_raw(self):
        output = self.parser.get_pyproject_raw().strip()
        assert output == pep_723_ex_extracted


    def test_pep_example_file_toml(self):
        output = self.parser.get_pyproject_toml()

        assert output == pep_723_ex_extracted_dict

    def test_pep_example_file_plain_script_dependencies(self):
        output = self.parser.plain_script_dependencies
        assert output == pep_723_plain_script_dependencies

    def test_pep_example_file_script_dependencies(self):
        output = self.parser.script_dependencies
        assert output == pep_723_script_dependencies


def test_pep_example_text_raw():
    parser = PEP723Parser.from_string(pep_723_ex_raw)
    output = parser.get_pyproject_raw().strip()
    assert output == pep_723_ex_extracted


def test_pep_example_text_toml():
    parser = PEP723Parser.from_string(pep_723_ex_raw)
    output = parser.get_pyproject_toml()
    assert output == pep_723_ex_extracted_dict


def test_pep_example_text_script_dependencies():
    parser = PEP723Parser.from_string(pep_723_ex_raw)
    output = parser.script_dependencies
    assert output == pep_723_script_dependencies


class TestRaises:
    def test_new_block_without_close(self):
        test_file = example_folder / "invalid_double_block.py"
        parser = PEP723Parser.from_path(test_file)
        with pytest.raises(SyntaxError):
            _ = parser.script_dependencies

    def test_block_not_closed(self):
        test_file = example_folder / "pep-723-sample-noclose.py"
        parser = PEP723Parser.from_path(test_file)
        with pytest.raises(SyntaxError):
            _ = parser.script_dependencies

    def test_block_not_closed_eof(self):
        test_file = example_folder / "pep-723-sample-noclose-eof.py"
        parser = PEP723Parser.from_path(test_file)
        with pytest.raises(SyntaxError):
            _ = parser.script_dependencies

    def test_repeated_block(self):
        test_file = example_folder / "invalid_repeated_block.py"
        parser = PEP723Parser.from_path(test_file)

        with pytest.raises(ValueError):
            _ = parser.metadata_blocks

        with pytest.raises(ValueError):
            _ = list(parser.iter_raw_metadata_blocks())


class TestMissing:

    @property
    def parser(self):
        test_file = example_folder / "example_no_pyproject_block.py"
        return PEP723Parser.from_path(test_file)

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
            "dependencies": []
        }


def test_invalid_parser_init():
    with pytest.raises(ValueError):
        _ = PEP723Parser()

    with pytest.raises(ValueError):
        _ = PEP723Parser(src="Code", src_path="path/to/file")
