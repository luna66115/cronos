#!/usr/bin/env bash
# uninstall.sh – Remove Cronos (venv, launcher, desktop entry, icon).
set -euo pipefail

VENV_DIR="$HOME/.local/share/cronos/venv"
LAUNCHER="$HOME/.local/bin/cronos"
DESKTOP="$HOME/.local/share/applications/cronos.desktop"
ICON="$HOME/.local/share/icons/hicolor/scalable/apps/cronos.svg"

echo "Removing Cronos …"
rm -rf  "$VENV_DIR"    && echo "✓ Removed venv"     || true
rm -f   "$LAUNCHER"    && echo "✓ Removed launcher"  || true
rm -f   "$DESKTOP"     && echo "✓ Removed desktop entry" || true
rm -f   "$ICON"        && echo "✓ Removed icon"      || true

if command -v update-desktop-database &>/dev/null; then
    update-desktop-database "$HOME/.local/share/applications" 2>/dev/null || true
fi

echo "Done. Crontab backups in ~/.local/share/cronos/backups/ were NOT removed."
