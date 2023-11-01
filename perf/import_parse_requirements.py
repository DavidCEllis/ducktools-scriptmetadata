import os.path

from ducktools.pep723parser import EmbeddedMetadata

pth = os.path.realpath(f"{os.path.dirname(__file__)}/../examples/pep-723-sample.py")

data = EmbeddedMetadata.from_path(pth)

output = data.run_requirements
