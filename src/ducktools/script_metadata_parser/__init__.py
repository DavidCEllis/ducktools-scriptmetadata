# MIT License
#
# Copyright (c) 2023 David C Ellis
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Embedded Python metadata format parser.
"""
# Allow use of syntax not supported natively in Python 3.8
from __future__ import annotations

import io
import os

try:
    # Faster
    from _collections_abc import Iterable
except ImportError:
    from collections.abc import Iterable

__version__ = "v0.0.2"


# The string library imports 're' so some extra manual work here
def _is_valid_type(txt: str) -> bool:
    """
    The specification requires TYPE be alphanumeric + hyphens

    :param txt: the block name/TYPE
    :return: True if the text given is a valid TYPE, False otherwise
    """
    ascii_lowercase = "abcdefghijklmnopqrstuvwxyz"
    ascii_uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    digits = "0123456789"
    extra_characters = "-"
    valid_type = ascii_lowercase + ascii_uppercase + digits + extra_characters

    return all(c in valid_type for c in txt)


class ScriptMetadata:
    """
    Embedded metadata extracted from a python source file
    """

    blocks: dict[str, str]
    warnings: list[str]

    def __init__(self, blocks: dict[str, str], *, warnings: list[str] = None):
        """

        :param blocks: Metadata dict extracted from python source
        :param warnings: Possible errors found during parsing
        """
        self.blocks = blocks
        self.warnings = warnings

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"blocks={self.blocks!r}, "
            f"warnings={self.warnings!r}"
            f")"
        )

    def __eq__(self, other) -> bool:
        if self.__class__ is other.__class__:
            return (self.blocks, self.warnings) == (other.blocks, other.warnings)
        return False

    @classmethod
    def from_iterable(cls, iterable_src: Iterable[str]) -> ScriptMetadata:
        """
        Iterate over source and return embedded metadata.

        :param iterable_src: an iterable of source code: eg an open file
        :return: EmbeddedMetadata containing data from the source
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
                if line.rstrip() == "# ///":
                    # End block
                    block_data.extend("".join(partial_block_data))
                    end_seen = True

                    # reset partial data - add this line
                    partial_block_data = [line[2:]]

                elif line.rstrip() == "#" or line.startswith("# "):
                    # Metadata line
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
                    # Metadata block has ended
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

            else:
                if line.startswith("#"):
                    line = line.rstrip()

                    if line != "# ///" and line.startswith("# /// "):
                        block_name = line[6:].strip()

                        if _is_valid_type(block_name):
                            if block_name in metadata:
                                raise ValueError(
                                    f"Line {line_no}: Duplicate {block_name!r} block found."
                                )
                            in_block = True
                        else:
                            message = (
                                f"Line {line_no}: "
                                f"{block_name!r} is not a valid block name. "
                                f"Block names must consist of alphanumeric characters and '-' only."
                            )
                            warnings_list.append(message)
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

        return cls(blocks=metadata, warnings=warnings_list)

    @classmethod
    def from_path(
        cls,
        source_path: str | os.PathLike,
        encoding: str = "utf-8",
    ) -> ScriptMetadata:
        """
        Extract embedded metadata from a given python source file path

        :param source_path: Path to the python source file
        :param encoding: text encoding of source file
        :return: metadata block
        """
        with open(source_path, encoding=encoding) as src_file:
            metadata = cls.from_iterable(src_file)
        return metadata

    @classmethod
    def from_string(cls, source_string: str) -> ScriptMetadata:
        """
        Extract embedded metadata from python source code given as a string

        :param source_string: Python source code as string
        :return: metadata block
        """
        return cls.from_iterable(io.StringIO(source_string))
