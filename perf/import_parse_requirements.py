import os.path

from ducktools.pep723parser import metadata_from_path

pth = os.path.realpath(f"{os.path.dirname(__file__)}/../examples/pep-723-sample.py")

data = metadata_from_path(pth)

output = data.run_requirements
