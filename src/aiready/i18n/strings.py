"""Internationalization string loader with interpolation and fallback."""

from __future__ import annotations

import json
from pathlib import Path


class I18n:
    _SUPPORTED = ("en", "ko")
    _DIR = Path(__file__).parent

    def __init__(self, language: str = "en"):
        self._strings: dict[str, dict[str, str]] = {}
        for lang in self._SUPPORTED:
            path = self._DIR / f"{lang}.json"
            if path.exists():
                self._strings[lang] = json.loads(path.read_text(encoding="utf-8"))
        self._language = language if language in self._SUPPORTED else "en"

    @property
    def language(self) -> str:
        return self._language

    def set_language(self, language: str) -> None:
        if language in self._SUPPORTED:
            self._language = language

    def get(self, key: str, **kwargs: str) -> str:
        value = self._strings.get(self._language, {}).get(key)
        if value is None:
            value = self._strings.get("en", {}).get(key)
        if value is None:
            return key
        if kwargs:
            try:
                value = value.format(**kwargs)
            except KeyError:
                pass
        return value
