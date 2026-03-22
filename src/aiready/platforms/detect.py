# src/aiready/platforms/detect.py
"""Auto-detect the current platform and return appropriate Platform instance."""

from __future__ import annotations

import platform as platform_module

from aiready.platforms.base import Platform, UnsupportedPlatformError


def detect_platform() -> Platform:
    system = platform_module.system()
    if system == "Linux":
        from aiready.platforms.linux import LinuxPlatform
        return LinuxPlatform()
    elif system == "Darwin":
        from aiready.platforms.macos import MacOSPlatform
        return MacOSPlatform()
    elif system == "Windows":
        from aiready.platforms.windows import WindowsPlatform
        return WindowsPlatform()
    raise UnsupportedPlatformError(f"Unsupported platform: {system}")
