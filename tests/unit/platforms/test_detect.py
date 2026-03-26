# tests/unit/platforms/test_detect.py
from unittest.mock import patch
import pytest
from aiready.platforms.detect import detect_platform
from aiready.platforms.base import Platform, UnsupportedPlatformError


class TestDetectPlatform:
    @patch("aiready.platforms.detect.platform_module")
    def test_detect_linux(self, mock_platform):
        mock_platform.system.return_value = "Linux"
        p = detect_platform()
        assert isinstance(p, Platform)

    @patch("aiready.platforms.detect.platform_module")
    def test_detect_darwin(self, mock_platform):
        mock_platform.system.return_value = "Darwin"
        p = detect_platform()
        assert isinstance(p, Platform)

    @patch("aiready.platforms.detect.platform_module")
    def test_detect_windows(self, mock_platform):
        mock_platform.system.return_value = "Windows"
        p = detect_platform()
        assert isinstance(p, Platform)

    @patch("aiready.platforms.detect.platform_module")
    def test_detect_unsupported(self, mock_platform):
        mock_platform.system.return_value = "FreeBSD"
        with pytest.raises(UnsupportedPlatformError):
            detect_platform()
