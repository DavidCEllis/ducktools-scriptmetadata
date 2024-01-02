from __future__ import annotations

import os.path
import re


try:
    from _collections_abc import Iterator
except ImportError:
    from collections.abc import Iterator

sample_path = os.path.realpath(f"{os.path.dirname(__file__)}/../examples/pep-723-sample.py")

REGEX = r'(?m)^# /// (?P<type>[a-zA-Z0-9-]+)$\s(?P<content>(^#(| .*)$\s)+)^# ///$'


def stream(script: str) -> Iterator[tuple[str, str]]:
    for match in re.finditer(REGEX, script):
        yield match.group('type'), ''.join(
            line[2:] if line.startswith('# ') else line[1:]
            for line in match.group('content').splitlines(keepends=True)
        )


def get_blocks(pth: str):
    with open(pth, 'r') as f:
        src = f.read()

    return {name: content for name, content in stream(src)}


print(get_blocks(sample_path))
