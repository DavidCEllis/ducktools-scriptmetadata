from . import (
    basic_pep_example,
    multi_block,
    unclosed_block_example,
    unclosed_block_eof,
)

__all__ = [
    "basic_pep_example",
    "multi_block",
    "unclosed_block_example",
    "unclosed_block_eof",
]


def __dir__():
    return __all__
