"""
tests/test_cron_manager.py – Unit tests for cron parsing and validation.
"""

import pytest
from cron_manager import (
    CronJob, parse_crontab, validate_cron_expression, _is_cron_field,
)


# ---------------------------------------------------------------------------
# _is_cron_field
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("value", ["*", "0", "*/5", "1-5", "1,3,5", "0-23/2"])
def test_is_cron_field_valid(value):
    assert _is_cron_field(value)


@pytest.mark.parametrize("value", ["", "abc", "@reboot", "1 2"])
def test_is_cron_field_invalid(value):
    assert not _is_cron_field(value)


# ---------------------------------------------------------------------------
# CronJob
# ---------------------------------------------------------------------------

def test_cron_job_expression():
    job = CronJob(minute="0", hour="6", day="*", month="*", weekday="1-5")
    assert job.cron_expression == "0 6 * * 1-5"


def test_cron_job_to_crontab_line_enabled():
    job = CronJob(minute="*/5", hour="*", day="*", month="*", weekday="*",
                  command="/usr/bin/backup.sh", description="Daily backup")
    line = job.to_crontab_line()
    assert "# Daily backup" in line
    assert "*/5 * * * * /usr/bin/backup.sh" in line


def test_cron_job_to_crontab_line_disabled():
    job = CronJob(minute="0", hour="2", day="*", month="*", weekday="*",
                  command="/usr/bin/sync.sh", enabled=False)
    line = job.to_crontab_line()
    assert line.startswith("# 0 2")


# ---------------------------------------------------------------------------
# parse_crontab
# ---------------------------------------------------------------------------

SAMPLE_CRONTAB = """\
# Backup job
*/5 * * * * /usr/bin/backup.sh

# Disabled job
# 0 2 * * * /usr/bin/disabled.sh

0 6 * * 1-5 /usr/bin/weekday.sh
"""


def test_parse_crontab_count():
    jobs = parse_crontab(SAMPLE_CRONTAB)
    assert len(jobs) == 3


def test_parse_crontab_descriptions():
    jobs = parse_crontab(SAMPLE_CRONTAB)
    assert jobs[0].description == "Backup job"
    assert jobs[1].description == "Disabled job"
    assert jobs[2].description == ""


def test_parse_crontab_enabled_flags():
    jobs = parse_crontab(SAMPLE_CRONTAB)
    assert jobs[0].enabled is True
    assert jobs[1].enabled is False
    assert jobs[2].enabled is True


def test_parse_crontab_fields():
    jobs = parse_crontab(SAMPLE_CRONTAB)
    assert jobs[0].minute == "*/5"
    assert jobs[2].weekday == "1-5"
    assert jobs[2].command == "/usr/bin/weekday.sh"


def test_parse_crontab_empty():
    assert parse_crontab("") == []
    assert parse_crontab("# only a comment\n") == []


# ---------------------------------------------------------------------------
# validate_cron_expression
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("expr", [
    ("*", "*", "*", "*", "*"),
    ("0", "6", "*", "*", "1-5"),
    ("*/15", "*/2", "1", "1-6", "0"),
])
def test_validate_valid(expr):
    valid, err = validate_cron_expression(*expr)
    assert valid, f"Expected valid, got error: {err}"


@pytest.mark.parametrize("expr", [
    ("abc", "*", "*", "*", "*"),
    ("60", "*", "*", "*", "*"),
    ("*", "25", "*", "*", "*"),
])
def test_validate_invalid(expr):
    valid, _ = validate_cron_expression(*expr)
    assert not valid
