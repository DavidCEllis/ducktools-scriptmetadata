# MIT License
#
# Copyright (c) 2023-2024 David C Ellis
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
# Allow use of typing syntax not supported natively in Python 3.8/3.9
from __future__ import annotations

import io
import os

from ducktools.classbuilder import slotclass, Field, SlotFields

from ._version import __version__

try:
    # Faster
    from _collections_abc import Iterable, Iterator
except ImportError:  # pragma: nocover
    from collections.abc import Iterable, Iterator

__all__ = [
    "parse_source",
    "parse_file",
    "parse_iterable",
    "ScriptMetadata",
    "iter_parse",
    "MetadataWarning",
]


@slotclass
class MetadataWarning:
    __slots__ = SlotFields(line_number=Field(), message=Field())
    line_number: int
    message: str

    def __str__(self):
        return f"Line {self.line_number}: {self.message}"


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


# noinspection PyArgumentList
def iter_parse(
    script_data: Iterable[str],
    *,
    start_line: int = 1,
) -> Iterator[tuple[str | None, str | None, list[MetadataWarning]]]:
    """
    Iterate over source and yield embedded metadata.

    This function implements the actual parsing logic. If a user wishes
    to implement early exit or raising warnings directly this can be used.

    :param script_data: an iterable of source code: eg an open file
    :param start_line: line number to start iterating from
    :yields: tuples of block_name, block_text, warnings
             will yield a None block_name if there are unused warnings at EOF
    """

    # Is the parser within a potential metadata block
    in_block = False

    # Has a potential closing '# ///' line been seen for
    # the current metadata block
    end_seen = False

    block_name = None
    block_data = []
    partial_block_data = []

    used_blocks = set()
    warnings_list = []

    line_no = 0  # Make sure line number is defined even if there is no data

    for line_no, line in enumerate(script_data, start=start_line):
        if in_block:
            if line.rstrip() == "# ///":
                # Potential end block
                # Block doesn't definitely end until an invalid line is encountered or EOF
                # So extend the block data with everything up to now and reset partial data.
                block_data.extend("".join(partial_block_data))
                end_seen = True

                # reset partial data - add this line
                partial_block_data = [line[2:]]

            elif line.rstrip() == "#" or line.startswith("# "):
                # Metadata line
                if line.startswith("# /// "):
                    # Possibly an unclosed block. Make note.
                    invalid_block_name = line[6:].strip()
                    message = MetadataWarning(
                        line_no,
                        (
                            f"New {invalid_block_name!r} block encountered "
                            f"before block {block_name!r} closed."
                        ),
                    )

                    warnings_list.append(message)

                # Remove '# ' or '#' prefix
                line = line[2:] if line.startswith("# ") else line[1:]
                partial_block_data.append(line)

            else:
                # Metadata block has ended
                if end_seen:
                    # Block was closed with "# ///" at some point.
                    block_data_str = "".join(block_data)
                    yield block_name, block_data_str, warnings_list
                    warnings_list = []
                else:
                    # Warn about potentially unclosed block
                    message = MetadataWarning(
                        line_no,
                        (
                            f"Potential unclosed block {block_name!r} detected. "
                            "A '# ///' block is needed to indicate the end of the block."
                        ),
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
                        if block_name in used_blocks:
                            raise ValueError(
                                f"Line {line_no}: Duplicate {block_name!r} block found."
                            )
                        used_blocks.add(block_name)
                        in_block = True
                    else:
                        message = MetadataWarning(
                            line_no,
                            (
                                f"{block_name!r} is not a valid block name. "
                                "Block names must consist of alphanumeric characters and '-' only."
                            ),
                        )
                        warnings_list.append(message)
                        # Not valid type, remove block name
                        block_name = None

    if in_block:
        if end_seen:
            block_data_str = "".join(block_data)
            yield block_name, block_data_str, warnings_list
            warnings_list = []

        else:
            message = MetadataWarning(
                line_no,
                (
                    f"Potential unclosed block {block_name!r} detected. "
                    "A '# ///' block is needed to indicate the end of the block."
                ),
            )
            warnings_list.append(message)

    if warnings_list:
        yield None, None, warnings_list


@slotclass
class ScriptMetadata:
    """
    Embedded metadata extracted from a python source file

    :param blocks: Metadata dict extracted from python source
                   Keys are block names and values the raw text of block data.
    :param warnings: Possible errors found during parsing
    """
    __slots__ = SlotFields(blocks=Field(), warnings=Field())
    blocks: dict[str, str]
    warnings: list[MetadataWarning]


def parse_iterable(
    iterable_data: Iterable[str],
    *,
    start_line: int = 1,
) -> ScriptMetadata:
    """
    Given an iterable of strings (lines of code), parse the object for inline metadata
    blocks.

    :param iterable_data: Iterable of lines of code
    :param start_line: Line number where file parsing starts - used for warnings
    :return: Embedded metadata object with blocks and warnings
    """

    blocks = {}
    warnings = []

    for block_name, block_text, warning_list in iter_parse(
        iterable_data, start_line=start_line
    ):
        if block_name:
            blocks[block_name] = block_text

        warnings.extend(warning_list)

    # noinspection PyArgumentList
    return ScriptMetadata(blocks, warnings)


def parse_source(
    script_text: str,
    *,
    start_line: int = 1,
) -> ScriptMetadata:
    """
    Parse a source code string for inline metadata blocks

    :param script_text: Source of python script as string
    :param start_line: Line number where file parsing starts - used for warnings
    :return: Embedded metadata object with blocks and warnings
    """
    data = io.StringIO(script_text)
    return parse_iterable(data, start_line=start_line)


def parse_file(
    file_path: str | bytes | os.PathLike,
    *,
    encoding: str = "utf-8",
) -> ScriptMetadata:
    """
    Parse a python source file for inline metadata blocks

    :param file_path: Path to the python source
    :param encoding: Text encoding of the file
    :return: Embedded metadata object with blocks and warnings
    """
    with open(file_path, mode="r", encoding=encoding) as f:
        metadata = parse_iterable(f)

    return metadata
