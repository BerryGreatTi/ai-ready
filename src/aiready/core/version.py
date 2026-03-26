"""Semantic version parsing and comparison."""

from __future__ import annotations

import re


def parse_version(version_str: str) -> tuple[int, ...]:
    # Find the first version-like pattern (e.g., "2.53.0" in "git version 2.53.0.windows.2")
    match = re.search(r"(\d+(?:\.\d+)*)", version_str)
    if not match:
        return ()
    parts = match.group(1).split(".")
    return tuple(int(p) for p in parts if p)


def version_gte(current: str, minimum: str) -> bool:
    cur = parse_version(current)
    min_ = parse_version(minimum)
    max_len = max(len(cur), len(min_))
    cur_padded = cur + (0,) * (max_len - len(cur))
    min_padded = min_ + (0,) * (max_len - len(min_))
    return cur_padded >= min_padded
