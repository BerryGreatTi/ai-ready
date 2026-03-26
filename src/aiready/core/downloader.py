"""File downloader with retry, checksum validation, and progress callback."""
from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

import requests


@dataclass(frozen=True)
class DownloadResult:
    success: bool
    path: Optional[Path] = None
    error: Optional[str] = None


class Downloader:
    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self._timeout = timeout
        self._max_retries = max_retries

    def download(
        self,
        url: str,
        dest: Path,
        checksum: Optional[str] = None,
        on_progress: Optional[Callable[[int, int], None]] = None,
    ) -> DownloadResult:
        last_error = ""
        for attempt in range(self._max_retries):
            try:
                response = requests.get(url, stream=True, timeout=self._timeout)
                response.raise_for_status()
                total = int(response.headers.get("content-length", 0))
                downloaded = 0
                dest.parent.mkdir(parents=True, exist_ok=True)
                with open(dest, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded += len(chunk)
                        if on_progress:
                            on_progress(downloaded, total)
                if checksum:
                    file_hash = hashlib.sha256(dest.read_bytes()).hexdigest()
                    if file_hash != checksum:
                        dest.unlink(missing_ok=True)
                        return DownloadResult(
                            success=False,
                            error=f"Checksum mismatch: expected {checksum}, got {file_hash}",
                        )
                return DownloadResult(success=True, path=dest)
            except (requests.RequestException, OSError) as e:
                last_error = str(e)
                if attempt < self._max_retries - 1:
                    time.sleep(2**attempt)
        return DownloadResult(
            success=False,
            error=f"Download failed after {self._max_retries} attempts: {last_error}",
        )
