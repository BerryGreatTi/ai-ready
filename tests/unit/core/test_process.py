# tests/unit/core/test_process.py
from aiready.core.process import run_process
from aiready.core.models import CommandResult


class TestRunProcess:
    def test_simple_command(self):
        result = run_process(["echo", "hello"])
        assert result.succeeded is True
        assert "hello" in result.stdout

    def test_failed_command(self):
        result = run_process(["false"])
        assert result.succeeded is False
        assert result.return_code != 0

    def test_command_not_found(self):
        result = run_process(["nonexistent_command_xyz"])
        assert result.succeeded is False

    def test_timeout(self):
        result = run_process(["sleep", "10"], timeout=1)
        assert result.succeeded is False
        assert "timeout" in result.stderr.lower() or result.return_code != 0

    def test_captures_stderr(self):
        result = run_process(["ls", "/nonexistent_path_xyz"])
        assert result.succeeded is False
        assert len(result.stderr) > 0
