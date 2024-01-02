import os.path

from ducktools.script_metadata_parser import ScriptMetadata

pth = os.path.realpath(f"{os.path.dirname(__file__)}/../examples/pep-723-sample.py")

data = ScriptMetadata.from_path(pth)

output = data.run_requirements_text
