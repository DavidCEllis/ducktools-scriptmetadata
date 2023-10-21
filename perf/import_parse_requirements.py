import os.path

from ducktools.pep723parser import PEP723Parser

pth = os.path.realpath(f"{os.path.dirname(__file__)}/../examples/pep-723-sample.py")

data = PEP723Parser.from_path(pth)

output = data.script_dependencies
