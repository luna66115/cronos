"""
tests/test_i18n.py – Unit tests for the internationalisation module.
"""

import os
import pytest
from i18n import tr, set_language, get_language, detect_system_language


def test_tr_german():
    set_language("de")
    assert tr("btn_add") == "＋ Hinzufügen"
    assert tr("btn_delete") == "✕ Löschen"
    assert tr("section_jobs") == "GEPLANTE AUFGABEN"


def test_tr_english():
    set_language("en")
    assert tr("btn_add") == "＋ Add"
    assert tr("btn_delete") == "✕ Delete"
    assert tr("section_jobs") == "SCHEDULED JOBS"


def test_tr_format_substitution():
    set_language("en")
    result = tr("dlg_delete_text", name="My Job")
    assert "My Job" in result


def test_tr_missing_key():
    result = tr("__nonexistent_key__")
    assert result == "[__nonexistent_key__]"


def test_set_get_language():
    set_language("de")
    assert get_language() == "de"
    set_language("en")
    assert get_language() == "en"


@pytest.mark.parametrize("env_val,expected", [
    ("de_DE.UTF-8", "de"),
    ("de_AT.UTF-8", "de"),
    ("de",          "de"),
    ("en_US.UTF-8", "en"),
    ("en_GB.UTF-8", "en"),
    ("fr_FR.UTF-8", "en"),   # fallback for unsupported languages
    ("C",           "en"),
    ("POSIX",       "en"),
])
def test_detect_system_language(env_val, expected, monkeypatch):
    monkeypatch.setenv("LANG", env_val)
    monkeypatch.delenv("LANGUAGE",    raising=False)
    monkeypatch.delenv("LC_ALL",      raising=False)
    monkeypatch.delenv("LC_MESSAGES", raising=False)
    assert detect_system_language() == expected


def test_detect_language_priority(monkeypatch):
    """LANGUAGE takes precedence over LANG."""
    monkeypatch.setenv("LANGUAGE", "de_DE.UTF-8")
    monkeypatch.setenv("LANG",     "en_US.UTF-8")
    monkeypatch.delenv("LC_ALL",      raising=False)
    monkeypatch.delenv("LC_MESSAGES", raising=False)
    assert detect_system_language() == "de"
