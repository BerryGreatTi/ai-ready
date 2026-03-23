"""Installation logger with sensitive data masking."""
from __future__ import annotations

import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path


_MASK_PATTERNS = [
    (re.compile(r"sk-ant-[a-zA-Z0-9_-]+"), "sk-ant-***"),
    (re.compile(r"sk-(?!ant-\*\*\*)[a-zA-Z0-9_-]+"), "sk-***"),
    (re.compile(r"key-[a-zA-Z0-9_-]+"), "key-***"),
]


def _mask_sensitive(text: str) -> str:
    for pattern, replacement in _MASK_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


class InstallLogger:
    def __init__(self, log_dir: Path | None = None):
        if log_dir is None:
            log_dir = Path(tempfile.gettempdir()) / "aiready"
        log_dir.mkdir(parents=True, exist_ok=True)
        self._path = log_dir / "install.log"
        self._path.write_text("", encoding="utf-8")

    @property
    def path(self) -> Path:
        return self._path

    def _write(self, level: str, step: str, message: str) -> None:
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        masked = _mask_sensitive(message)
        line = f"[{ts}] [{level}] [{step}] {masked}\n"
        with open(self._path, "a", encoding="utf-8") as f:
            f.write(line)

    def info(self, step: str, message: str) -> None:
        self._write("INFO", step, message)

    def warn(self, step: str, message: str) -> None:
        self._write("WARN", step, message)

    def error(self, step: str, message: str) -> None:
        self._write("ERROR", step, message)
