from . import (
    basic_pep_example,
    multiple_blocks_joined,
    multiple_closing_lines,
    multiple_opening_lines,
    no_block,
    repeated_block_error,
    unclosed_block_example,
    unclosed_block_eof,
)

__all__ = [
    "basic_pep_example",
    "multiple_blocks_joined",
    "multiple_closing_lines",
    "multiple_opening_lines",
    "no_block",
    "repeated_block_error",
    "unclosed_block_example",
    "unclosed_block_eof",
]


def __dir__():
    return __all__
