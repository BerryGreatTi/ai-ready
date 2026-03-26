from unittest.mock import MagicMock
from aiready.core.permissions import PermissionManager, ELEVATED_OPERATIONS


class TestPermissionManager:
    def test_needs_elevation_for_install_package(self):
        pm = PermissionManager(MagicMock())
        assert pm.needs_elevation("install_package") is True

    def test_no_elevation_for_check_version(self):
        pm = PermissionManager(MagicMock())
        assert pm.needs_elevation("check_version") is False

    def test_no_elevation_for_download(self):
        pm = PermissionManager(MagicMock())
        assert pm.needs_elevation("download") is False

    def test_no_elevation_for_modify_user_path(self):
        pm = PermissionManager(MagicMock())
        assert pm.needs_elevation("modify_user_path") is False

    def test_request_if_needed_no_elevation(self):
        platform = MagicMock()
        pm = PermissionManager(platform)
        assert pm.request_if_needed("download", "reason") is True
        platform.request_elevation.assert_not_called()

    def test_request_if_needed_with_elevation_granted(self):
        platform = MagicMock()
        platform.request_elevation.return_value = True
        pm = PermissionManager(platform)
        assert pm.request_if_needed("install_package", "reason") is True

    def test_request_if_needed_with_elevation_denied(self):
        platform = MagicMock()
        platform.request_elevation.return_value = False
        pm = PermissionManager(platform)
        assert pm.request_if_needed("install_package", "reason") is False

    def test_elevated_operations_is_frozenset(self):
        assert isinstance(ELEVATED_OPERATIONS, frozenset)
