# src/aiready/platforms/linux.py
"""Linux platform stub - full implementation in Task 7."""

from aiready.platforms.base import Platform


class LinuxPlatform(Platform):
    """Stub - full implementation in Task 7."""

    def get_os_info(self):
        raise NotImplementedError

    def check_command(self, command):
        raise NotImplementedError

    def install_prerequisite(self, prereq):
        raise NotImplementedError

    def verify_prerequisite(self, prereq):
        raise NotImplementedError

    def add_to_path(self, path):
        raise NotImplementedError

    def request_elevation(self, reason_key):
        raise NotImplementedError

    def run_command(self, cmd, elevated=False):
        raise NotImplementedError

    def get_temp_dir(self):
        raise NotImplementedError

    def open_browser(self, url):
        raise NotImplementedError

    def get_shell_type(self):
        raise NotImplementedError
