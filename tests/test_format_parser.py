from ducktools.pep723parser import PEP723Parser
from pathlib import Path

example_folder = Path(__file__).parent / "example_files"

pep_723_ex_raw = """

"""


pep_723_ex_extracted = """
[run]
requires-python = ">=3.11"
dependencies = [
  "requests<3",
  "rich",
]
""".strip()


def test_pep_example_parse_text():
    test_file = example_folder / "pep-723-sample.py"

    parser = PEP723Parser.from_path(test_file)
    output = parser.get_first_raw_toml("pyproject").strip()

    assert output == pep_723_ex_extracted
