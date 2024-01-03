from . import (
    basic_pep_example,
    basic_pep_example_eof,
    multiple_blocks_joined,
    multiple_closing_lines,
    multiple_opening_lines,
    no_block,
    repeated_block_error,
    unclosed_block_example,
    unclosed_block_eof,
    invalid_block_name,
)

__all__ = [
    "basic_pep_example",
    "basic_pep_example_eof",
    "multiple_blocks_joined",
    "multiple_closing_lines",
    "multiple_opening_lines",
    "no_block",
    "repeated_block_error",
    "unclosed_block_example",
    "unclosed_block_eof",
    "invalid_block_name",
]


def __dir__():
    return __all__
