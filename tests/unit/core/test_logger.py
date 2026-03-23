"""Tests for InstallLogger with sensitive data masking."""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from aiready.core.logger import InstallLogger


@pytest.fixture
def log_dir(tmp_path: Path) -> Path:
    return tmp_path / "logs"


@pytest.fixture
def logger(log_dir: Path) -> InstallLogger:
    return InstallLogger(log_dir=log_dir)


class TestLogFileCreation:
    def test_log_creates_file(self, log_dir: Path) -> None:
        logger = InstallLogger(log_dir=log_dir)
        assert logger.path.exists()
        assert logger.path.name == "install.log"

    def test_log_creates_directory_if_missing(self, tmp_path: Path) -> None:
        nested = tmp_path / "a" / "b" / "c"
        logger = InstallLogger(log_dir=nested)
        assert logger.path.exists()


class TestLogFormat:
    def test_log_format(self, logger: InstallLogger) -> None:
        logger.info("setup", "Installing dependencies")
        content = logger.path.read_text(encoding="utf-8")
        # Expected: [2024-01-01 12:00:00] [INFO] [setup] Installing dependencies
        assert re.search(
            r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\] \[INFO\] \[setup\] Installing dependencies",
            content,
        )

    def test_log_levels(self, logger: InstallLogger) -> None:
        logger.info("step1", "Info message")
        logger.warn("step2", "Warn message")
        logger.error("step3", "Error message")
        content = logger.path.read_text(encoding="utf-8")
        assert "[INFO]" in content
        assert "[WARN]" in content
        assert "[ERROR]" in content


class TestSensitiveMasking:
    def test_masks_api_keys(self, logger: InstallLogger) -> None:
        logger.info("auth", "key sk-ant-api03-abc123xyz")
        content = logger.path.read_text(encoding="utf-8")
        assert "sk-ant-api03-abc123xyz" not in content
        assert "sk-ant-***" in content

    def test_masks_generic_keys(self, logger: InstallLogger) -> None:
        logger.info("auth", "key sk-proj-abc")
        content = logger.path.read_text(encoding="utf-8")
        assert "sk-proj-abc" not in content
        assert "sk-***" in content


class TestTruncateOnNewRun:
    def test_truncates_on_new_run(self, log_dir: Path) -> None:
        first = InstallLogger(log_dir=log_dir)
        first.info("step1", "First run message")
        assert "First run message" in log_dir.joinpath("install.log").read_text()

        second = InstallLogger(log_dir=log_dir)
        content = second.path.read_text(encoding="utf-8")
        assert "First run message" not in content
