import os.path

from ducktools.script_metadata_parser import parse_file

pth = os.path.realpath(f"{os.path.dirname(__file__)}/../examples/pep-723-sample.py")

data = parse_file(pth)

print(data.blocks)
