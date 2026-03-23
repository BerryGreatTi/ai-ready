from unittest.mock import MagicMock
from aiready.core.prereqs import PrerequisiteChecker
from aiready.core.models import Prerequisite, PrereqCheckResult, CommandInfo


class TestPrerequisiteChecker:
    def _make_platform(self, check_result=None):
        platform = MagicMock()
        platform.check_command.return_value = check_result
        return platform

    def test_not_installed(self):
        platform = self._make_platform(check_result=None)
        checker = PrerequisiteChecker(platform)
        prereq = Prerequisite(name="nodejs", min_version="22.16", check_command="node --version")
        result = checker.check(prereq)
        assert result.installed is False
        assert result.current_version is None

    def test_installed_version_ok(self):
        platform = self._make_platform(CommandInfo(path="/usr/bin/node", version="v24.1.0"))
        checker = PrerequisiteChecker(platform)
        prereq = Prerequisite(name="nodejs", min_version="22.16", check_command="node --version")
        result = checker.check(prereq)
        assert result.installed is True
        assert result.needs_upgrade is False

    def test_installed_needs_upgrade(self):
        platform = self._make_platform(CommandInfo(path="/usr/bin/node", version="v18.0.0"))
        checker = PrerequisiteChecker(platform)
        prereq = Prerequisite(name="nodejs", min_version="22.16", check_command="node --version")
        result = checker.check(prereq)
        assert result.installed is True
        assert result.needs_upgrade is True

    def test_installed_no_version_info(self):
        platform = self._make_platform(CommandInfo(path="/usr/bin/node", version=None))
        checker = PrerequisiteChecker(platform)
        prereq = Prerequisite(name="nodejs", min_version="22.16", check_command="node --version")
        result = checker.check(prereq)
        assert result.installed is True
        assert result.needs_upgrade is True

    def test_check_all(self):
        platform = self._make_platform(None)
        checker = PrerequisiteChecker(platform)
        prereqs = [
            Prerequisite(name="nodejs", min_version="22.16", check_command="node --version"),
            Prerequisite(name="git", min_version="2.0", check_command="git --version"),
        ]
        results = checker.check_all(prereqs)
        assert len(results) == 2
        assert all(not r.installed for r in results)
