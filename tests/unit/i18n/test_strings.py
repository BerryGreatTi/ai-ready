import json
from pathlib import Path

import pytest

from aiready.i18n.strings import I18n

I18N_DIR = Path(__file__).resolve().parents[3] / "src" / "aiready" / "i18n"


class TestI18n:
    def test_load_english(self):
        i18n = I18n("en")
        assert i18n.get("app.title") == "AIReady - AI Tool Setup Helper"

    def test_load_korean(self):
        i18n = I18n("ko")
        assert "AIReady" in i18n.get("app.title")

    def test_missing_key_returns_key(self):
        i18n = I18n("en")
        assert i18n.get("nonexistent.key") == "nonexistent.key"

    def test_interpolation(self):
        i18n = I18n("en")
        result = i18n.get("error.version_mismatch", required="22.16", current="18.0")
        assert "22.16" in result
        assert "18.0" in result

    def test_change_language(self):
        i18n = I18n("en")
        assert i18n.language == "en"
        i18n.set_language("ko")
        assert i18n.language == "ko"

    def test_unsupported_language_falls_back_to_en(self):
        i18n = I18n("fr")
        assert i18n.language == "en"
        assert i18n.get("app.title") == "AIReady - AI Tool Setup Helper"

    def test_interpolation_missing_placeholder_returns_template(self):
        i18n = I18n("en")
        result = i18n.get("error.version_mismatch")
        assert "{required}" in result or "required" in result


class TestI18nKeyParity:
    def test_all_en_keys_exist_in_ko(self):
        en = json.loads((I18N_DIR / "en.json").read_text(encoding="utf-8"))
        ko = json.loads((I18N_DIR / "ko.json").read_text(encoding="utf-8"))
        missing = set(en.keys()) - set(ko.keys())
        assert missing == set(), f"Keys missing in ko.json: {missing}"

    def test_all_ko_keys_exist_in_en(self):
        en = json.loads((I18N_DIR / "en.json").read_text(encoding="utf-8"))
        ko = json.loads((I18N_DIR / "ko.json").read_text(encoding="utf-8"))
        extra = set(ko.keys()) - set(en.keys())
        assert extra == set(), f"Extra keys in ko.json not in en.json: {extra}"

    def test_no_empty_values_in_en(self):
        en = json.loads((I18N_DIR / "en.json").read_text(encoding="utf-8"))
        empty = [k for k, v in en.items() if not v.strip()]
        assert empty == [], f"Empty values in en.json: {empty}"

    def test_no_empty_values_in_ko(self):
        ko = json.loads((I18N_DIR / "ko.json").read_text(encoding="utf-8"))
        empty = [k for k, v in ko.items() if not v.strip()]
        assert empty == [], f"Empty values in ko.json: {empty}"
