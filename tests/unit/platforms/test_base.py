# tests/unit/platforms/test_base.py
import pytest
from aiready.platforms.base import Platform


class TestPlatformABC:
    def test_cannot_instantiate(self):
        with pytest.raises(TypeError):
            Platform()

    def test_has_all_abstract_methods(self):
        expected_methods = [
            "get_os_info",
            "check_command",
            "install_prerequisite",
            "verify_prerequisite",
            "add_to_path",
            "request_elevation",
            "run_command",
            "get_temp_dir",
            "open_browser",
            "get_shell_type",
        ]
        for method in expected_methods:
            assert hasattr(Platform, method), f"Platform missing method: {method}"
