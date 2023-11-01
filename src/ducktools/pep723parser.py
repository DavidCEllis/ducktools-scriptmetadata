"""
Embedded Python metadata format parser.
"""

import sys
import io
import warnings

from ducktools.lazyimporter import LazyImporter, TryExceptImport, FromImport


__version__ = "v0.0.1"

# Lazily import tomllib and packaging as _laz attributes
_laz = LazyImporter(
    [
        TryExceptImport("tomllib", "tomli", "tomllib"),
        FromImport("packaging.specifiers", "SpecifierSet"),
        FromImport("packaging.requirements", "Requirement"),
    ]
)


# The string library imports 're' so some extra manual work here
def _is_valid_type(txt):
    """
    The specification requires TYPE be alphanumeric + hyphens

    :param txt: the block name/TYPE
    :type txt: str
    :return: True if the text given is a valid TYPE, False otherwise
    :rtype: bool
    """
    ascii_lowercase = "abcdefghijklmnopqrstuvwxyz"
    ascii_uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    digits = "0123456789"
    extra_characters = "-"
    valid_type = ascii_lowercase + ascii_uppercase + digits + extra_characters

    return all(c in valid_type for c in txt)


class EmbeddedMetadata:
    """
    Embedded metadata extracted from a python source file
    """

    PYTHON_VERSION_KEY = "requires-python"
    DEPENDENCIES_KEY = "dependencies"

    def __init__(self, blocks, *, warnings=None):
        """

        :param blocks: Metadata dict extracted from python source
        :type blocks: dict[str, str]
        :param warnings: Possible errors found during parsing
        :type warnings: list[str]
        """
        self.blocks = blocks
        self.warnings = warnings

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"blocks={self.blocks!r}, "
            f"warnings={self.warnings!r}"
            f")"
        )

    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return (self.blocks, self.warnings) == (other.blocks, other.warnings)

    @property
    def pyproject_text(self):
        """
        Get the raw text from a 'pyproject' metadata block.
        :return: text source from pyproject block
        :rtype: str
        """
        return self.blocks.get("pyproject", None)

    @property
    def pyproject_toml(self):
        """
        The parsed 'TOML' data from a 'pyproject' metadata block

        :return: Dictionary of keys and data from the 'pyproject' toml block
        :rtype: dict
        """
        if self.pyproject_text is None:
            return {}
        else:
            try:
                return _laz.tomllib.loads(self.pyproject_text)
            except _laz.tomllib.TOMLDecodeError as e:
                if self.warnings:
                    warns = ",".join(self.warnings)
                    raise _laz.tomllib.TOMLDecodeError(
                        f"{e}; Possible Metadata Issues: {warns}"
                    )
                else:
                    raise

    @property
    def run_requirements_text(self):
        """
        Requirements data from toml block
        :return:
        """

        run_block = self.pyproject_toml.get("run", {})
        run_block[self.PYTHON_VERSION_KEY] = run_block.get(self.PYTHON_VERSION_KEY, None)
        run_block[self.DEPENDENCIES_KEY] = run_block.get(self.DEPENDENCIES_KEY, [])

        return run_block

    @property
    def run_requirements(self):
        """
        Requirements data from toml block
        :return:
        """

        requires_python = None
        dependencies = []

        run_block = self.pyproject_toml.get("run", {})

        pyver = run_block.pop(self.PYTHON_VERSION_KEY, None)
        if pyver:
            requires_python = _laz.SpecifierSet(pyver)

        deps = run_block.pop(self.DEPENDENCIES_KEY, None)
        if deps:
            dependencies = [_laz.Requirement(spec) for spec in deps]

        run_block[self.PYTHON_VERSION_KEY] = requires_python
        run_block[self.DEPENDENCIES_KEY] = dependencies

        return run_block


def _parse_metadata_iterable(iterable_src):
    """
    Iterate over source and return embedded metadata.

    :param iterable_src: an iterable of source code: eg an open file
    :type iterable_src: Iterable[str]
    :return: EmbeddedMetadata containing data from the source
    :rtype: EmbeddedMetadata
    """

    # Is the parser within a potential metadata block
    in_block = False

    # Has a potential closing '# ///' line been seen for
    # the current metadata block
    end_seen = False

    block_name = None
    block_data = []
    partial_block_data = []

    metadata = {}
    warnings_list = []

    for line_no, line in enumerate(iterable_src, start=1):
        if in_block:
            if not (line.rstrip() == "#" or line.startswith("# ")):
                if end_seen:
                    metadata[block_name] = "".join(block_data)
                else:
                    # Warn about potentially unclosed block
                    message = (
                        f"Line {line_no}: "
                        f"Potential unclosed block {block_name!r} detected. "
                        f"A '# ///' block is needed to indicate the end of the block."
                    )
                    warnings_list.append(message)

                # Reset
                in_block = False
                block_name, block_data = None, []
                end_seen = False

            elif line.rstrip() == "# ///":
                block_data.extend("".join(partial_block_data))
                end_seen = True

                # reset partial data - add this line
                partial_block_data = [line[2:]]

            else:
                if line.startswith("# /// "):
                    # Possibly an unclosed block. Make note.
                    invalid_block_name = line[6:].strip()
                    warnings_list.append(
                        f"Line {line_no}: "
                        f"New {invalid_block_name!r} block encountered before "
                        f"block {block_name!r} closed."
                    )

                # Remove '# ' or '#' prefix
                line = line[2:] if line.startswith("# ") else line[1:]
                partial_block_data.append(line)
        else:
            if line.startswith("#"):
                line = line.rstrip()

                if line != "# ///" and line.startswith("# /// "):
                    block_name = line[6:].strip()

                    # Fair chance people will try to call the block
                    # 'pyproject.toml', warn in that case
                    if block_name == "pyproject.toml":
                        warnings_list.append(
                            f"Line {line_no}: "
                            f"{block_name!r} block found, should be 'pyproject'."
                        )

                    if _is_valid_type(block_name):
                        if block_name in metadata:
                            raise ValueError(f"Line {line_no}: Duplicate {block_name!r} block found.")
                        in_block = True
                    else:
                        # Not valid type, remove block name
                        block_name = None
    if in_block:
        if end_seen:
            metadata[block_name] = "".join(block_data)
        else:
            warnings_list.append(
                f"End of File: "
                f"Potential unclosed block {block_name!r} detected. "
                f"A '# ///' block is needed to indicate the end of the block."
            )

    return EmbeddedMetadata(blocks=metadata, warnings=warnings_list)


def metadata_from_path(source_path, encoding="utf-8"):
    """
    Extract embedded metadata from a given python source file path

    :param source_path: Path to the python source file
    :type source_path: str | os.PathLike
    :param encoding: text encoding of source file
    :type encoding: str
    :return: metadata block
    :rtype: EmbeddedMetadata
    """
    with open(source_path, encoding=encoding) as src_file:
        metadata = _parse_metadata_iterable(src_file)
    return metadata


def metadata_from_string(source_string):
    """
    Extract embedded metadata from python source code given as a string

    :param source_string: Python source code as string
    :type source_string: str
    :return: metadata block
    :rtype: EmbeddedMetadata
    """
    return _parse_metadata_iterable(io.StringIO(source_string))
