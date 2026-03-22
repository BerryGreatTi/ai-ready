"""Semantic version parsing and comparison."""

from __future__ import annotations

import re


def parse_version(version_str: str) -> tuple[int, ...]:
    cleaned = version_str.strip().lstrip("v")
    cleaned = re.split(r"[^0-9.]", cleaned)[0]
    parts = cleaned.split(".")
    return tuple(int(p) for p in parts if p)


def version_gte(current: str, minimum: str) -> bool:
    cur = parse_version(current)
    min_ = parse_version(minimum)
    max_len = max(len(cur), len(min_))
    cur_padded = cur + (0,) * (max_len - len(cur))
    min_padded = min_ + (0,) * (max_len - len(min_))
    return cur_padded >= min_padded
