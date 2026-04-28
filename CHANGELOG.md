# Changelog

All notable changes to Cronos are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [1.0.0] – 2026-04-28

### Added
- Initial public release
- GUI crontab manager built with PyQt6
- Dark and Light themes (Catppuccin Mocha / Latte)
- Live upcoming-run preview via `croniter`
- German / English UI with automatic system-locale detection
- Language switch button in the header (no restart needed)
- Automatic crontab backup before every change
- Auto-refresh of the "Next Run" column every 60 seconds
- Enable / disable individual cron jobs without deleting them
- One-command `install.sh` with venv, launcher and `.desktop` entry
