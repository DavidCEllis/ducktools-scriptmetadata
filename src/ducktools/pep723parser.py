"""
Lazy PEP723 format parser.
"""

import sys
import io

from ducktools.lazyimporter import LazyImporter, ModuleImport, FromImport


__version__ = "v0.0.1"

if sys.version_info >= (3, 11):
    _toml_import = ModuleImport("tomllib")
else:
    _toml_import = ModuleImport("tomli", asname="tomllib")

_laz = LazyImporter(
    [
        _toml_import,
        FromImport("packaging.specifiers", "SpecifierSet"),
        FromImport("packaging.requirements", "Requirement"),
    ]
)


class PEP723Parser:
    PYTHON_VERSION_KEY = "requires-python"
    DEPENDENCIES_KEY = "dependencies"

    def __init__(self, *, src=None, src_path=None):
        if src and src_path:
            raise ValueError("Provide only one of 'src' and 'src_path'")
        elif not (src or src_path):
            raise ValueError("Must provide one of 'src' and 'src_path'")

        self.src = src
        self.src_path = src_path

        self._raw_toml_blocks = None
        self._toml_blocks = None

    @classmethod
    def from_path(cls, src_path):
        return cls(src_path=src_path)

    @classmethod
    def from_string(cls, src):
        return cls(src=src)

    @staticmethod
    def _parse_source_blocks(iterable_src):
        """
        Iterate over source and yield raw toml source as the blocks occur.

        :param iterable_src: an iterable of source code: eg an open file
        :type iterable_src: Iterable[str]
        :yield: tuples of (block_name, toml_data)
        :ytype: tuple[str, str]
        """
        in_block = False
        block_name = None
        block_data = []

        for line in iterable_src:
            if in_block:
                if not line.startswith("#"):
                    raise SyntaxError(f"Block {block_name!r} not closed correctly.")

                line = line.removeprefix("#").removeprefix(" ")
                if line.strip() == "///":
                    block_text = "".join(block_data)

                    yield block_name, block_text

                    # Reset blocks
                    in_block = False
                    block_name, block_data = None, []
                elif line.startswith("/// "):
                    invalid_block_name = line[3:].strip()
                    raise SyntaxError(
                        f"New block {invalid_block_name!r} encountered before "
                        f"block {block_name!r} closed."
                    )
                else:
                    block_data.append(line)
            else:
                if line.startswith("#"):
                    line = line.removeprefix("#").strip()
                    if line.startswith("///"):
                        block_name = line[3:].strip()
                        in_block = True

        if in_block:
            raise SyntaxError(f"Block {block_name} not closed correctly.")

    def iter_raw_toml_blocks(self):
        if self.src:
            data = io.StringIO(self.src)
            yield from self._parse_source_blocks(data)
        elif self.src_path:
            with open(self.src_path, 'r', encoding="utf8") as data:
                yield from self._parse_source_blocks(data)

    def iter_toml_blocks(self):
        for block_name, raw_data in self.iter_raw_toml_blocks():
            yield block_name, _laz.tomllib.loads(raw_data)

    def get_first_raw_toml(self, name):
        for block_name, block_text in self.iter_raw_toml_blocks():
            if block_name == name:
                return block_text
        raise KeyError(f"{name!r} block not found in file.")

    def get_first_toml_block(self, name):
        raw_toml = self.get_first_raw_toml(name)
        return _laz.tomllib.loads(raw_toml)

    @property
    def raw_toml_blocks(self):
        """
        Get the raw toml text blocks as a dictionary.

        This is cached after first reading all blocks.

        :return: Dictionary of block name: toml_text
        :rtype: dict[str, str]
        """
        if self._raw_toml_blocks is None:
            raw_blocks = {}
            for block_name, raw_toml in self.iter_raw_toml_blocks():
                if block_name in raw_blocks:
                    raise ValueError(f"Multiple {block_name!r} blocks found.")
                raw_blocks[block_name] = raw_toml
            self._raw_toml_blocks = raw_blocks
        return self._raw_toml_blocks

    @property
    def toml_blocks(self):
        """
        Get processed toml blocks as a dictionary.

        This is cached after first reading all blocks.

        :return: Dictionary of block name: parsed_toml
        """
        if self._toml_blocks is None:
            toml_blocks = {}
            for block_name, toml_data in self.raw_toml_blocks.items():
                if block_name in toml_blocks:
                    raise ValueError(f"Multiple {block_name!r} blocks found.")
                toml_blocks[block_name] = toml_data
            self._toml_blocks = toml_blocks
        return self._toml_blocks

    def get_pyproject_raw(self):
        """
        Get the raw pyproject block.

        :return: pyproject block string
        :raises: KeyError if no pyproject block found
        """
        if self._raw_toml_blocks:
            block = self._raw_toml_blocks.get("pyproject", None)
        else:
            block = self.get_first_raw_toml("pyproject")
        return block

    def get_pyproject_toml(self):
        """
        Get the parsed pyproject block.

        :return: pyproject toml block parsed into a dict
        :raises: KeyError if no pyproject block found
        """
        if self._toml_blocks:
            block = self._toml_blocks.get("pyproject", None)
        else:
            block = _laz.tomllib.loads(self.get_pyproject_raw())
        return block

    @property
    def script_dependencies(self):
        """
        Get the requirements as packaging Version and Requirement objects.

        If there is no pyproject block this will return None for the python version
        and an empty list of dependencies.

        :return:
        """
        requires_python = None
        dependencies = []

        try:
            block = self.get_pyproject_toml()
        except KeyError:
            run_block = {}
        else:
            run_block = block.get("run", {})

            pyver = run_block.pop(self.PYTHON_VERSION_KEY, None)
            if pyver:
                requires_python = _laz.SpecifierSet(pyver)
            deps = run_block.pop(self.DEPENDENCIES_KEY, None)
            if deps:
                dependencies = [
                    _laz.Requirement(spec) for spec in deps
                ]

        run_block[self.PYTHON_VERSION_KEY] = requires_python
        run_block[self.DEPENDENCIES_KEY] = dependencies

        return run_block
