"""Tests for Downloader with retry, checksum validation, and progress callback."""
from __future__ import annotations

import hashlib
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest
import requests

from aiready.core.downloader import DownloadResult, Downloader


@pytest.fixture
def tmp_dest(tmp_path: Path) -> Path:
    return tmp_path / "download" / "file.bin"


def _make_response(content: bytes, status_code: int = 200) -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.headers = {"content-length": str(len(content))}
    response.iter_content.return_value = [content]
    response.raise_for_status.return_value = None
    return response


class TestDownloadSuccess:
    def test_download_success(self, tmp_dest: Path) -> None:
        content = b"hello world"
        response = _make_response(content)

        with patch("aiready.core.downloader.requests.get", return_value=response) as mock_get:
            downloader = Downloader()
            result = downloader.download("https://example.com/file.bin", tmp_dest)

        assert result.success is True
        assert result.path == tmp_dest
        assert result.error is None
        assert tmp_dest.read_bytes() == content
        mock_get.assert_called_once()


class TestDownloadRetry:
    def test_download_retry_on_failure(self, tmp_dest: Path) -> None:
        content = b"retry content"
        success_response = _make_response(content)
        fail_exc = requests.ConnectionError("connection refused")

        with patch("aiready.core.downloader.requests.get") as mock_get, \
             patch("aiready.core.downloader.time.sleep") as mock_sleep:
            mock_get.side_effect = [fail_exc, fail_exc, success_response]
            downloader = Downloader(max_retries=3)
            result = downloader.download("https://example.com/file.bin", tmp_dest)

        assert result.success is True
        assert mock_get.call_count == 3
        assert mock_sleep.call_count == 2

    def test_download_all_retries_fail(self, tmp_dest: Path) -> None:
        fail_exc = requests.ConnectionError("connection refused")

        with patch("aiready.core.downloader.requests.get") as mock_get, \
             patch("aiready.core.downloader.time.sleep"):
            mock_get.side_effect = [fail_exc, fail_exc, fail_exc]
            downloader = Downloader(max_retries=3)
            result = downloader.download("https://example.com/file.bin", tmp_dest)

        assert result.success is False
        assert result.path is None
        assert "3 attempts" in (result.error or "")
        assert mock_get.call_count == 3


class TestChecksumValidation:
    def test_checksum_validation_pass(self, tmp_dest: Path) -> None:
        content = b"validated content"
        checksum = hashlib.sha256(content).hexdigest()
        response = _make_response(content)

        with patch("aiready.core.downloader.requests.get", return_value=response):
            downloader = Downloader()
            result = downloader.download(
                "https://example.com/file.bin", tmp_dest, checksum=checksum
            )

        assert result.success is True

    def test_checksum_validation_fail(self, tmp_dest: Path) -> None:
        content = b"some content"
        wrong_checksum = "a" * 64
        response = _make_response(content)

        with patch("aiready.core.downloader.requests.get", return_value=response):
            downloader = Downloader()
            result = downloader.download(
                "https://example.com/file.bin", tmp_dest, checksum=wrong_checksum
            )

        assert result.success is False
        assert "Checksum mismatch" in (result.error or "")
        assert not tmp_dest.exists()


class TestProgressCallback:
    def test_progress_callback_called(self, tmp_dest: Path) -> None:
        content = b"progress content"
        response = _make_response(content)
        calls: list[tuple[int, int]] = []

        def on_progress(downloaded: int, total: int) -> None:
            calls.append((downloaded, total))

        with patch("aiready.core.downloader.requests.get", return_value=response):
            downloader = Downloader()
            result = downloader.download(
                "https://example.com/file.bin", tmp_dest, on_progress=on_progress
            )

        assert result.success is True
        assert len(calls) >= 1
        downloaded, total = calls[-1]
        assert downloaded == len(content)
        assert total == len(content)


class TestTimeoutHandling:
    def test_timeout_handling(self, tmp_dest: Path) -> None:
        with patch("aiready.core.downloader.requests.get") as mock_get, \
             patch("aiready.core.downloader.time.sleep"):
            mock_get.side_effect = requests.Timeout("timed out")
            downloader = Downloader(max_retries=3)
            result = downloader.download("https://example.com/file.bin", tmp_dest)

        assert result.success is False
        assert result.error is not None
        assert mock_get.call_count == 3
