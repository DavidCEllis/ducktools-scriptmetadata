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

pep_723_script_dependencies = {
    "requires-python": SpecifierSet(">=3.11"),
    "dependencies": [
        Requirement("requests<3"),
        Requirement("rich"),
    ]
}


def test_pep_example_file_raw():
    test_file = example_folder / "pep-723-sample.py"

    parser = PEP723Parser.from_path(test_file)
    output = parser.get_pyproject_raw().strip()
    assert output == pep_723_ex_extracted


def test_pep_example_file_toml():
    test_file = example_folder / "pep-723-sample.py"
    parser = PEP723Parser.from_path(test_file)
    output = parser.get_pyproject_toml()

    assert output == pep_723_ex_extracted_dict


def test_pep_example_file_script_dependencies():
    test_file = example_folder / "pep-723-sample.py"
    parser = PEP723Parser.from_path(test_file)
    output = parser.script_dependencies

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
