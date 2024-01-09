import os.path

from ducktools.scriptmetadata import parse_file

pth = os.path.realpath(f"{os.path.dirname(__file__)}/../examples/pep-723-sample.py")

data = parse_file(pth)

print(data.blocks)
