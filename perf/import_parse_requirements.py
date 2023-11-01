import os.path

from ducktools.pep723parser import EmbeddedMetadataParser

pth = os.path.realpath(f"{os.path.dirname(__file__)}/../examples/pep-723-sample.py")

data = EmbeddedMetadataParser.from_path(pth)

output = data.script_dependencies
