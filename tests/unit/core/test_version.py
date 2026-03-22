# tests/unit/core/test_version.py
from aiready.core.version import version_gte, parse_version


class TestParseVersion:
    def test_simple(self):
        assert parse_version("1.2.3") == (1, 2, 3)

    def test_with_v_prefix(self):
        assert parse_version("v24.1.0") == (24, 1, 0)

    def test_two_parts(self):
        assert parse_version("22.16") == (22, 16)

    def test_single(self):
        assert parse_version("5") == (5,)

    def test_strips_extra(self):
        assert parse_version("v18.0.0-lts") == (18, 0, 0)

    def test_empty_gives_zero(self):
        assert parse_version("") == ()


class TestVersionGte:
    def test_equal(self):
        assert version_gte("22.16.0", "22.16") is True

    def test_greater(self):
        assert version_gte("24.1.0", "22.16") is True

    def test_less(self):
        assert version_gte("18.0.0", "22.16") is False

    def test_with_v_prefix(self):
        assert version_gte("v24.1.0", "22.16") is True

    def test_patch_comparison(self):
        assert version_gte("22.16.1", "22.16.0") is True
        assert version_gte("22.15.9", "22.16.0") is False

    def test_same_version(self):
        assert version_gte("22.16", "22.16") is True
