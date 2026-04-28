"""
cron_manager.py – Low-level crontab read/write/parse helpers for Cronos.
"""

import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from croniter import croniter
    HAS_CRONITER = True
except ImportError:
    HAS_CRONITER = False


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class CronJob:
    minute: str = "*"
    hour: str = "*"
    day: str = "*"
    month: str = "*"
    weekday: str = "*"
    command: str = ""
    description: str = ""
    enabled: bool = True

    @property
    def cron_expression(self) -> str:
        return f"{self.minute} {self.hour} {self.day} {self.month} {self.weekday}"

    def to_crontab_line(self) -> str:
        lines = []
        if self.description:
            lines.append(f"# {self.description}")
        prefix = "" if self.enabled else "# "
        lines.append(f"{prefix}{self.cron_expression} {self.command}")
        return "\n".join(lines)

    def get_next_runs(self, count: int = 5) -> list[datetime]:
        if not HAS_CRONITER:
            return []
        try:
            cron = croniter(self.cron_expression, datetime.now())
            return [cron.get_next(datetime) for _ in range(count)]
        except Exception:
            return []


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------

def _is_cron_field(s: str) -> bool:
    """Return True if *s* looks like a valid cron time field."""
    return bool(s) and all(c in "0123456789*/-," for c in s)


def _parse_cron_line(line: str, enabled: bool = True) -> Optional[CronJob]:
    parts = line.split(None, 5)
    if len(parts) < 6:
        return None
    minute, hour, day, month, weekday = parts[:5]
    if not all(_is_cron_field(f) for f in (minute, hour, day, month, weekday)):
        return None
    return CronJob(
        minute=minute, hour=hour, day=day, month=month, weekday=weekday,
        command=parts[5], enabled=enabled,
    )


def parse_crontab(content: str) -> list[CronJob]:
    """Parse crontab text into a list of :class:`CronJob` objects."""
    jobs: list[CronJob] = []
    pending_description = ""

    for line in content.splitlines():
        stripped = line.strip()

        if not stripped:
            pending_description = ""
            continue

        if stripped.startswith("#"):
            comment = stripped[1:].strip()
            parts = comment.split()
            if len(parts) >= 6 and _is_cron_field(parts[0]):
                # Disabled job encoded as a comment
                job = _parse_cron_line(comment, enabled=False)
                if job:
                    job.description = pending_description
                    jobs.append(job)
                    pending_description = ""
            else:
                # Plain description comment – keep it for the next job
                pending_description = comment
            continue

        job = _parse_cron_line(stripped, enabled=True)
        if job:
            job.description = pending_description
            pending_description = ""
            jobs.append(job)
        else:
            pending_description = ""

    return jobs


# ---------------------------------------------------------------------------
# crontab I/O
# ---------------------------------------------------------------------------

def read_crontab() -> list[CronJob]:
    """Read and parse the current user's crontab. Returns [] on any error."""
    try:
        result = subprocess.run(
            ["crontab", "-l"],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            return []
        return parse_crontab(result.stdout)
    except Exception:
        return []


def write_crontab(jobs: list[CronJob]) -> tuple[bool, str]:
    """Serialise *jobs* and install them as the current user's crontab.

    Returns ``(True, "")`` on success or ``(False, error_message)`` on failure.
    """
    lines = [job.to_crontab_line() for job in jobs]
    content = "\n".join(lines)
    if content and not content.endswith("\n"):
        content += "\n"

    try:
        proc = subprocess.run(
            ["crontab", "-"],
            input=content, capture_output=True, text=True,
        )
        if proc.returncode != 0:
            return False, proc.stderr.strip()
        return True, ""
    except Exception as exc:
        return False, str(exc)


def backup_crontab() -> tuple[bool, str]:
    """Write a timestamped backup of the current crontab.

    Backups are stored in ``~/.local/share/cronos/backups/``.
    Returns ``(True, filepath)`` on success or ``(False, error_message)`` on
    failure.  Returns ``(True, "")`` when the crontab is empty (nothing to
    back up).
    """
    try:
        result = subprocess.run(
            ["crontab", "-l"],
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            return True, ""  # Empty crontab – nothing to back up

        backup_dir = Path.home() / ".local" / "share" / "cronos" / "backups"
        backup_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"crontab_backup_{timestamp}.txt"
        backup_path.write_text(result.stdout)
        return True, str(backup_path)
    except Exception as exc:
        return False, str(exc)


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------

def validate_cron_expression(
    minute: str, hour: str, day: str, month: str, weekday: str
) -> tuple[bool, str]:
    """Validate a cron expression.

    Returns ``(True, "")`` when valid or ``(False, error_message)`` otherwise.
    Uses *croniter* when available for full validation, falls back to a basic
    character check otherwise.  Empty strings are treated as ``*``.
    """
    # Normalise: replace empty strings with wildcard so croniter never
    # receives an incomplete expression.
    minute   = minute.strip()   or "*"
    hour     = hour.strip()     or "*"
    day      = day.strip()      or "*"
    month    = month.strip()    or "*"
    weekday  = weekday.strip()  or "*"

    if not HAS_CRONITER:
        for val in (minute, hour, day, month, weekday):
            if not _is_cron_field(val):
                return False, f"Invalid value: '{val}'"
        return True, ""

    try:
        croniter(f"{minute} {hour} {day} {month} {weekday}")
        return True, ""
    except Exception as exc:
        return False, str(exc)


# ---------------------------------------------------------------------------
# UI presets
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# UI presets  (labels are resolved lazily so language switches work)
# ---------------------------------------------------------------------------

def _build_minute_presets() -> list[tuple[str, Optional[str]]]:
    from i18n import tr
    return [
        (tr("preset_every_minute"), "*"),
        (tr("preset_every_5min"),   "*/5"),
        (tr("preset_every_10min"),  "*/10"),
        (tr("preset_every_15min"),  "*/15"),
        (tr("preset_every_30min"),  "*/30"),
        (tr("preset_once_per_hour"), "0"),
        (tr("preset_custom"),       None),
    ]


def _build_hour_presets() -> list[tuple[str, Optional[str]]]:
    from i18n import tr
    return [
        (tr("preset_every_hour"),  "*"),
        (tr("preset_every_2h"),    "*/2"),
        (tr("preset_every_6h"),    "*/6"),
        (tr("preset_every_12h"),   "*/12"),
        (tr("preset_midnight"),    "0"),
        (tr("preset_morning"),     "6"),
        (tr("preset_noon"),        "12"),
        (tr("preset_evening"),     "18"),
        (tr("preset_custom"),      None),
    ]


def _build_weekday_presets() -> list[tuple[str, Optional[str]]]:
    from i18n import tr
    return [
        (tr("preset_every_day"),   "*"),
        (tr("preset_mon_fri"),     "1-5"),
        (tr("preset_sat_sun"),     "6,0"),
        (tr("preset_monday"),      "1"),
        (tr("preset_tuesday"),     "2"),
        (tr("preset_wednesday"),   "3"),
        (tr("preset_thursday"),    "4"),
        (tr("preset_friday"),      "5"),
        (tr("preset_saturday"),    "6"),
        (tr("preset_sunday"),      "0"),
        (tr("preset_custom"),      None),
    ]


# Keep module-level names for backwards compatibility; rebuilt on each access
# via the functions above so that a language switch is reflected immediately.
MINUTE_PRESETS  = property(_build_minute_presets)   # type: ignore[assignment]
HOUR_PRESETS    = property(_build_hour_presets)      # type: ignore[assignment]
WEEKDAY_PRESETS = property(_build_weekday_presets)   # type: ignore[assignment]
