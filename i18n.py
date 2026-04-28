"""
i18n.py – Internationalization for Cronos.

Supported languages: German (de), English (en).
Auto-detection uses the LANG / LANGUAGE environment variable on Linux.
The language can be overridden at runtime via set_language().
"""

import locale
import os
from typing import Literal

Language = Literal["de", "en"]

_STRINGS: dict[str, dict[str, str]] = {
    # ── Window / Header ──────────────────────────────────────────────────────
    "app_title": {
        "de": "Cronos",
        "en": "Cronos",
    },
    "btn_refresh": {
        "de": "🔄 Aktualisieren",
        "en": "🔄 Refresh",
    },
    "tooltip_refresh": {
        "de": "Crontab neu einlesen",
        "en": "Reload crontab from disk",
    },
    "tooltip_theme_to_light": {
        "de": "Zu Light Mode wechseln",
        "en": "Switch to light mode",
    },
    "tooltip_theme_to_dark": {
        "de": "Zu Dark Mode wechseln",
        "en": "Switch to dark mode",
    },
    "warn_no_croniter": {
        "de": "⚠ croniter nicht installiert – Vorschau deaktiviert",
        "en": "⚠ croniter not installed – preview disabled",
    },
    # ── Table panel ──────────────────────────────────────────────────────────
    "section_jobs": {
        "de": "GEPLANTE AUFGABEN",
        "en": "SCHEDULED JOBS",
    },
    "col_enabled": {
        "de": "✓",
        "en": "✓",
    },
    "col_description": {
        "de": "Beschreibung",
        "en": "Description",
    },
    "col_minute": {
        "de": "Minute",
        "en": "Minute",
    },
    "col_hour": {
        "de": "Stunde",
        "en": "Hour",
    },
    "col_day_month_dow": {
        "de": "Tag/Monat/WT",
        "en": "Day/Month/DOW",
    },
    "col_command": {
        "de": "Befehl",
        "en": "Command",
    },
    "col_next_run": {
        "de": "Nächste Ausführung",
        "en": "Next Run",
    },
    "label_jobs_count_singular": {
        "de": "1 Job",
        "en": "1 job",
    },
    # ── Form panel ───────────────────────────────────────────────────────────
    "section_new_job": {
        "de": "NEUE AUFGABE",
        "en": "NEW JOB",
    },
    "section_edit_job": {
        "de": "AUFGABE BEARBEITEN",
        "en": "EDIT JOB",
    },
    "label_description": {
        "de": "Beschreibung:",
        "en": "Description:",
    },
    "placeholder_description": {
        "de": "Optionale Beschreibung (als Kommentar)",
        "en": "Optional description (stored as comment)",
    },
    "label_enabled": {
        "de": "Aktiv",
        "en": "Enabled",
    },
    "label_minute": {
        "de": "Minute:",
        "en": "Minute:",
    },
    "label_hour": {
        "de": "Stunde:",
        "en": "Hour:",
    },
    "label_day": {
        "de": "Tag:",
        "en": "Day:",
    },
    "label_month": {
        "de": "Monat:",
        "en": "Month:",
    },
    "label_weekday": {
        "de": "Wochentag:",
        "en": "Weekday:",
    },
    "label_command": {
        "de": "Befehl:",
        "en": "Command:",
    },
    "placeholder_command": {
        "de": "/pfad/zum/skript.sh  oder  /usr/bin/flatpak run ...",
        "en": "/path/to/script.sh  or  /usr/bin/flatpak run ...",
    },
    "btn_add": {
        "de": "＋ Hinzufügen",
        "en": "＋ Add",
    },
    "btn_save": {
        "de": "💾 Speichern",
        "en": "💾 Save",
    },
    "btn_delete": {
        "de": "✕ Löschen",
        "en": "✕ Delete",
    },
    "btn_clear": {
        "de": "✖ Leeren",
        "en": "✖ Clear",
    },
    # ── Preview ──────────────────────────────────────────────────────────────
    "section_preview": {
        "de": "NÄCHSTE AUSFÜHRUNGEN",
        "en": "UPCOMING RUNS",
    },
    "placeholder_preview": {
        "de": "Zeitangaben eingeben für Vorschau…",
        "en": "Enter schedule fields for preview…",
    },
    "preview_invalid": {
        "de": "⚠ Ungültige Syntax: {err}",
        "en": "⚠ Invalid syntax: {err}",
    },
    "preview_unavailable": {
        "de": "Keine Vorschau verfügbar",
        "en": "Preview not available",
    },
    "preview_no_future": {
        "de": "Keine zukünftigen Ausführungen gefunden",
        "en": "No upcoming runs found",
    },
    "preview_in_hours_mins": {
        "de": "in {h}h {m}min",
        "en": "in {h}h {m}min",
    },
    "preview_in_mins": {
        "de": "in {m}min",
        "en": "in {m}min",
    },
    # ── Status messages ──────────────────────────────────────────────────────
    "status_reloaded": {
        "de": "✓ Crontab neu eingelesen",
        "en": "✓ Crontab reloaded",
    },
    "status_added": {
        "de": "✓ Aufgabe hinzugefügt",
        "en": "✓ Job added",
    },
    "status_saved": {
        "de": "✓ Aufgabe gespeichert",
        "en": "✓ Job saved",
    },
    "status_deleted": {
        "de": "✓ Aufgabe gelöscht",
        "en": "✓ Job deleted",
    },
    # ── Dialogs ──────────────────────────────────────────────────────────────
    "dlg_delete_title": {
        "de": "Aufgabe löschen",
        "en": "Delete Job",
    },
    "dlg_delete_text": {
        "de": "Aufgabe '{name}' wirklich löschen?",
        "en": "Really delete job '{name}'?",
    },
    "dlg_error_write_title": {
        "de": "Fehler",
        "en": "Error",
    },
    "dlg_error_write_text": {
        "de": "Crontab konnte nicht geschrieben werden:\n{err}",
        "en": "Could not write crontab:\n{err}",
    },
    "dlg_error_command": {
        "de": "Bitte einen Befehl eingeben.",
        "en": "Please enter a command.",
    },
    "dlg_invalid_syntax_title": {
        "de": "Ungültige Syntax",
        "en": "Invalid Syntax",
    },
    "dlg_invalid_syntax_text": {
        "de": "Fehler in der Zeitangabe:\n{err}",
        "en": "Error in schedule expression:\n{err}",
    },
    "dlg_backup_fail_title": {
        "de": "Backup fehlgeschlagen",
        "en": "Backup Failed",
    },
    "dlg_backup_fail_text": {
        "de": "Das Backup konnte nicht erstellt werden:\n{err}\n\nTrotzdem fortfahren?",
        "en": "Could not create backup:\n{err}\n\nProceed anyway?",
    },
    # ── Cron presets ─────────────────────────────────────────────────────────
    "preset_every_minute": {
        "de": "Jede Minute",
        "en": "Every minute",
    },
    "preset_every_5min": {
        "de": "Alle 5 Min",
        "en": "Every 5 min",
    },
    "preset_every_10min": {
        "de": "Alle 10 Min",
        "en": "Every 10 min",
    },
    "preset_every_15min": {
        "de": "Alle 15 Min",
        "en": "Every 15 min",
    },
    "preset_every_30min": {
        "de": "Alle 30 Min",
        "en": "Every 30 min",
    },
    "preset_once_per_hour": {
        "de": "Einmal pro Stunde",
        "en": "Once per hour",
    },
    "preset_every_hour": {
        "de": "Jede Stunde",
        "en": "Every hour",
    },
    "preset_every_2h": {
        "de": "Alle 2 Std",
        "en": "Every 2 hrs",
    },
    "preset_every_6h": {
        "de": "Alle 6 Std",
        "en": "Every 6 hrs",
    },
    "preset_every_12h": {
        "de": "Alle 12 Std",
        "en": "Every 12 hrs",
    },
    "preset_midnight": {
        "de": "Mitternacht",
        "en": "Midnight",
    },
    "preset_morning": {
        "de": "Morgens (6)",
        "en": "Morning (6)",
    },
    "preset_noon": {
        "de": "Mittags (12)",
        "en": "Noon (12)",
    },
    "preset_evening": {
        "de": "Abends (18)",
        "en": "Evening (18)",
    },
    "preset_every_day": {
        "de": "Jeden Tag",
        "en": "Every day",
    },
    "preset_mon_fri": {
        "de": "Mo–Fr",
        "en": "Mon–Fri",
    },
    "preset_sat_sun": {
        "de": "Sa–So",
        "en": "Sat–Sun",
    },
    "preset_monday": {
        "de": "Montag",
        "en": "Monday",
    },
    "preset_tuesday": {
        "de": "Dienstag",
        "en": "Tuesday",
    },
    "preset_wednesday": {
        "de": "Mittwoch",
        "en": "Wednesday",
    },
    "preset_thursday": {
        "de": "Donnerstag",
        "en": "Thursday",
    },
    "preset_friday": {
        "de": "Freitag",
        "en": "Friday",
    },
    "preset_saturday": {
        "de": "Samstag",
        "en": "Saturday",
    },
    "preset_sunday": {
        "de": "Sonntag",
        "en": "Sunday",
    },
    "preset_custom": {
        "de": "Benutzerdefiniert",
        "en": "Custom",
    },
}


# ---------------------------------------------------------------------------
# Runtime state
# ---------------------------------------------------------------------------

_current_language: Language = "en"


def detect_system_language() -> Language:
    """
    Detect the system language from environment variables.

    Checks LANGUAGE, LC_ALL, LC_MESSAGES, LANG in order (standard Linux
    locale priority).  Falls back to English if the detected locale is not
    German.
    """
    for var in ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG"):
        value = os.environ.get(var, "")
        if value:
            # LANGUAGE may contain colon-separated list, take the first entry
            lang_code = value.split(":")[0].split("_")[0].lower()
            if lang_code == "de":
                return "de"
            if lang_code in ("en", "c", "posix"):
                return "en"

    # Final fallback: ask Python's locale module
    try:
        lang_code, _ = locale.getlocale()
        if lang_code and lang_code.lower().startswith("de"):
            return "de"
    except Exception:
        pass

    return "en"


def set_language(lang: Language) -> None:
    """Override the active language."""
    global _current_language
    _current_language = lang


def get_language() -> Language:
    """Return the currently active language."""
    return _current_language


def tr(key: str, **kwargs: str) -> str:
    """
    Look up *key* in the current language.

    Keyword arguments are substituted via str.format_map(), so::

        tr("dlg_delete_text", name="Backup Job")

    replaces ``{name}`` in the translated string.
    """
    entry = _STRINGS.get(key)
    if entry is None:
        return f"[{key}]"
    text = entry.get(_current_language, entry.get("en", f"[{key}]"))
    if kwargs:
        text = text.format_map(kwargs)
    return text
