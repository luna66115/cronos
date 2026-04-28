#!/usr/bin/env bash
# install.sh – Install Cronos into a virtual environment and create a desktop entry.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$HOME/.local/share/cronos/venv"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_SRC="$SCRIPT_DIR/cronos/assets/cronos_icon.svg"
ICON_DST="$HOME/.local/share/icons/hicolor/scalable/apps/cronos.svg"

echo "╔══════════════════════════════════════╗"
echo "║      Cronos – Installer              ║"
echo "╚══════════════════════════════════════╝"
echo ""

# ── Python check ─────────────────────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 not found. Please install Python 3.11+."
    exit 1
fi

PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$(echo "$PY_VER" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)

if [[ "$PY_MAJOR" -lt 3 ]] || [[ "$PY_MAJOR" -eq 3 && "$PY_MINOR" -lt 11 ]]; then
    echo "ERROR: Python 3.11+ required (found $PY_VER)."
    exit 1
fi

echo "✓ Python $PY_VER"

# ── Virtual environment ───────────────────────────────────────────────────────
echo "→ Creating virtual environment in $VENV_DIR …"
mkdir -p "$VENV_DIR"
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

echo "→ Installing dependencies …"
pip install --upgrade pip --quiet
pip install PyQt6 croniter --quiet
pip install -e "$SCRIPT_DIR" --quiet

echo "✓ Dependencies installed"

# ── Launcher script ───────────────────────────────────────────────────────────
mkdir -p "$BIN_DIR"
LAUNCHER="$BIN_DIR/cronos"
cat > "$LAUNCHER" <<EOF
#!/usr/bin/env bash
source "$VENV_DIR/bin/activate"
exec python -m cronos.main "\$@"
EOF
chmod +x "$LAUNCHER"
echo "✓ Launcher written to $LAUNCHER"

# ── Icon ──────────────────────────────────────────────────────────────────────
if [[ -f "$ICON_SRC" ]]; then
    mkdir -p "$(dirname "$ICON_DST")"
    cp "$ICON_SRC" "$ICON_DST"
    echo "✓ Icon installed"
fi

# ── Desktop entry ─────────────────────────────────────────────────────────────
mkdir -p "$DESKTOP_DIR"
cat > "$DESKTOP_DIR/cronos.desktop" <<EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Cronos
GenericName=Crontab Manager
Comment=A modern GUI crontab manager for Linux
Exec=$LAUNCHER
Icon=cronos
Terminal=false
Categories=System;Utility;
Keywords=cron;crontab;scheduler;task;
StartupWMClass=cronos
EOF

if command -v update-desktop-database &>/dev/null; then
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
fi

echo "✓ Desktop entry created"
echo ""
echo "══════════════════════════════════════════"
echo "  Cronos installed successfully!"
echo "  Run:  cronos"
echo "  Or launch from your application menu."
echo "══════════════════════════════════════════"
