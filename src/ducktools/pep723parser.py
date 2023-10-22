"""
Lazy PEP723 format parser.
"""

import sys
import io

from ducktools.lazyimporter import LazyImporter, ModuleImport, FromImport


__version__ = "v0.0.1"

if sys.version_info >= (3, 11):  # pragma: no cover
    _toml_import = ModuleImport("tomllib")
else:  # pragma: no cover
    _toml_import = ModuleImport("tomli", asname="tomllib")

# Lazily import tomllib and packaging
_laz = LazyImporter(
    [
        _toml_import,
        FromImport("packaging.specifiers", "SpecifierSet"),
        FromImport("packaging.requirements", "Requirement"),
    ]
)


def _removeprefix(txt, prefix):
    # Python 3.8 has no remove_prefix method on str
    # Copied from the PEP that added it with 'self' changed to 'txt'
    if txt.startswith(prefix):
        return txt[len(prefix):]  # fmt: skip
    else:
        return txt[:]  # pragma: no cover


class PEP723Parser:
    """
    Parse PEP723 metadata blocks.

    This provides methods and properties to assist in handling
    PEP723 metadata blocks.

    get_* methods will raise a KeyError exception if the block is not found
    properties will instead return None if the block is not found
    """

    PYTHON_VERSION_KEY = "requires-python"
    DEPENDENCIES_KEY = "dependencies"

    __slots__ = ("src", "src_path", "encoding", "possible_errors")

    def __init__(self, *, src=None, src_path=None, encoding="utf-8"):
        if src and src_path:
            raise ValueError("Provide only one of 'src' and 'src_path'")
        elif not (src or src_path):
            raise ValueError("Must provide one of 'src' and 'src_path'")

        self.src = src
        self.src_path = src_path
        self.encoding = encoding

        self.possible_errors = []

    @classmethod
    def from_path(cls, src_path, encoding="utf-8"):
        """
        Create a PEP723Parser instance given the path to a source file

        :param src_path: path to a python source file to search for PEP723 metadata
        :type src_path: str | os.PathLike
        :param encoding: encoding to use when opening the file.
        :type encoding: str
        :return: PEP723Parser instance
        """
        return cls(src_path=src_path, encoding=encoding)

    @classmethod
    def from_string(cls, src):
        """
        Create a PEP723Parser instance given source code as a string

        :param src: source code to search for PEP723 metadata.
        :type src: str
        :return: PEP723Parser instance
        """
        return cls(src=src)

    def _parse_source_blocks(self, iterable_src):
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

        consumed_blocks = set()

        # Reset possible error block to avoid repetition
        self.possible_errors = []

        for line in iterable_src:
            if in_block:
                if not line.startswith("#"):
                    raise SyntaxError(
                        f"Block {block_name} not closed correctly. "
                        f"A '# ///' block is needed to indicate the end of the block."
                    )

                line = _removeprefix(_removeprefix(line, "#"), " ")
                if line.strip() == "///":
                    block_text = "".join(block_data)

                    yield block_name, block_text

                    # Reset blocks
                    in_block = False
                    block_name, block_data = None, []
                elif line.startswith("/// "):
                    # Possibly an unclosed block. Make note.
                    invalid_block_name = line[3:].strip()
                    self.possible_errors.append(
                        f"New {invalid_block_name!r} block encountered before "
                        f"block {block_name!r} closed."
                    )
                    # Append anyway to match reference behaviour
                    block_data.append(line)
                else:
                    block_data.append(line)
            else:
                if line.startswith("#"):
                    line = _removeprefix(line, "#").strip()
                    if line.startswith("///"):
                        block_name = line[3:].strip()
                        if block_name in consumed_blocks:
                            raise ValueError(f"Multiple {block_name!r} blocks found.")
                        consumed_blocks.add(block_name)
                        in_block = True

        if in_block:
            raise SyntaxError(
                f"Block {block_name} not closed correctly. "
                f"A '# ///' block is needed to indicate the end of the block."
            )

    def iter_raw_metadata_blocks(self):
        """
        Iterator that returns raw PEP723 metadata blocks.

        :yield: block_name, block_text pairs
        :ytype: tuple[str, str]
        """
        if self.src:
            data = io.StringIO(self.src)
            yield from self._parse_source_blocks(data)
        elif self.src_path:
            with open(self.src_path, "r", encoding=self.encoding) as data:
                yield from self._parse_source_blocks(data)

    def get_first_metadata_block(self, name):
        """
        Get the text of the first metadata block that matches the 'TYPE' block
        given by 'name'

        :param name: name of the 'TYPE' block to extract: eg 'pyproject'
        :type name: str
        :return: text of the metadata block
        :rtype: str
        """
        for block_name, block_text in self.iter_raw_metadata_blocks():
            if block_name == name:
                return block_text
        raise KeyError(f"{name!r} block not found in file.")

    @property
    def metadata_blocks(self):
        """
        Get the text of the metadata blocks as a dictionary.

        :return: Dictionary of block name: toml_text
        :rtype: dict[str, str]
        """
        return {
            block_name: raw_toml
            for block_name, raw_toml in self.iter_raw_metadata_blocks()
        }

    def get_pyproject_raw(self):
        """
        Get the text of the pyproject block.

        If no block is found, raise a KeyError.

        Use this if you want to use an external TOML parser for the block or
        for caching on the text of the block.

        :return: pyproject metadata block text
        :rtype: str
        :raises: KeyError if no pyproject block found
        """
        return self.get_first_metadata_block("pyproject")

    def get_pyproject_toml(self):
        """
        Get the parsed pyproject block.

        If no block is found, raise a KeyError.

        Use this if you wish to make use of the full 'pyproject' TOML data.

        :return: pyproject toml block parsed into a dict
        :rtype: dict
        :raises: KeyError if no pyproject block found
        """
        try:
            return _laz.tomllib.loads(self.get_pyproject_raw())
        except _laz.tomllib.TOMLDecodeError as e:
            if self.possible_errors:
                errs = ",".join(self.possible_errors)
                raise _laz.tomllib.TOMLDecodeError(
                    f"{e}; Possible PEP723 Errors: {errs}"
                )
            else:
                raise

    @property
    def pyproject_raw(self):
        """
        Get the text of the pyproject block

        If no block is found, return None.

        Use this if you want to use an external TOML parser for the block or
        if caching on the text of the block.

        :return: pyproject metadata block text or None
        :rtype: str | None
        """
        try:
            return self.get_pyproject_raw()
        except KeyError:
            return None

    @property
    def pyproject_toml(self):
        """
        Get the parsed pyproject block.

        If no block is found, return None.

        Use this if you wish to make use of the full 'pyproject' TOML data.

        :return: pyproject toml block parsed into a dict
        :rtype: dict | None
        """
        try:
            return self.get_pyproject_toml()
        except KeyError:
            return None

    @property
    def plain_script_dependencies(self):
        """
        Get the [run] block from the 'pyproject' metadata.

        If there is no pyproject block or [run] table,
        return None for the python version and an empty list of dependencies.

        Use this if you wish to use a tool other than 'packaging' to handle
        version specifiers and requirements or if you are caching based on
        the text of the specified requirements.

        :return: pyproject 'run' table
        :rtype: dict
        """
        try:
            dep_data = self.get_pyproject_toml()
        except KeyError:
            run_block = {}
        else:
            run_block = dep_data.get("run", {})

        if self.PYTHON_VERSION_KEY not in run_block:
            run_block[self.PYTHON_VERSION_KEY] = None
        if self.DEPENDENCIES_KEY not in run_block:
            run_block[self.DEPENDENCIES_KEY] = []

        return run_block

    @property
    def script_dependencies(self):
        """
        Get the requirements as packaging Version and Requirement objects.

        If there is no pyproject block this will return None for the python version
        and an empty list of dependencies.

        :return: pyproject 'run' table with requires-python and dependencies values
                 parsed into SpecifierSet and Requirement objects respectively.
        :rtype: dict
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

            deps = run_block.pop(self.DEPENDENCIES_KEY, [])
            if deps:
                dependencies = [_laz.Requirement(spec) for spec in deps]

        run_block[self.PYTHON_VERSION_KEY] = requires_python
        run_block[self.DEPENDENCIES_KEY] = dependencies

        return run_block
