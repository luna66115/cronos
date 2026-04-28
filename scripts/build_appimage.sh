#!/usr/bin/env bash
# scripts/build_appimage.sh – Builds a self-contained Cronos-x86_64.AppImage
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
DIST_DIR="$ROOT_DIR/dist"
BUILD_DIR="$ROOT_DIR/build"
APPDIR="$BUILD_DIR/Cronos.AppDir"
APPIMAGETOOL_URL="https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage"
APPIMAGETOOL="$BUILD_DIR/appimagetool"

GREEN='\033[0;32m'; BLUE='\033[0;34m'; NC='\033[0m'
step() { echo -e "${BLUE}→ $*${NC}"; }
ok()   { echo -e "${GREEN}✓ $*${NC}"; }

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║   Cronos AppImage Builder                ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── PyInstaller ───────────────────────────────────────────────────────────────
step "Running PyInstaller …"
cd "$ROOT_DIR"
pyinstaller \
  --onefile \
  --name cronos \
  --noconsole \
  --paths "$ROOT_DIR" \
  --add-data "styles.py:." \
  --add-data "i18n.py:." \
  --add-data "cron_manager.py:." \
  --add-data "assets:assets" \
  --hidden-import croniter \
  --hidden-import PyQt6.QtSvgWidgets \
  --hidden-import PyQt6.QtSvg \
  --distpath "$DIST_DIR" \
  --workpath "$BUILD_DIR/pyinstaller_work" \
  --noconfirm \
  main.py
ok "PyInstaller done"

# ── Assemble AppDir ───────────────────────────────────────────────────────────
step "Assembling AppDir …"
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/share/icons/hicolor/scalable/apps"
mkdir -p "$APPDIR/usr/share/applications"

cp "$DIST_DIR/cronos" "$APPDIR/usr/bin/cronos"
chmod +x "$APPDIR/usr/bin/cronos"

ICON_SRC="$ROOT_DIR/assets/cronos_icon.svg"
if [[ -f "$ICON_SRC" ]]; then
    cp "$ICON_SRC" "$APPDIR/cronos.svg"
    cp "$ICON_SRC" "$APPDIR/usr/share/icons/hicolor/scalable/apps/cronos.svg"
    ok "Icon copied"
else
    echo '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><circle cx="32" cy="32" r="30" fill="#89b4fa"/></svg>' \
        > "$APPDIR/cronos.svg"
fi

cp "$SCRIPT_DIR/appimage/cronos.desktop" "$APPDIR/cronos.desktop"
cp "$SCRIPT_DIR/appimage/cronos.desktop" "$APPDIR/usr/share/applications/cronos.desktop"

cat > "$APPDIR/AppRun" <<'APPRUN'
#!/usr/bin/env bash
HERE="$(dirname "$(readlink -f "$0")")"
export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-xcb}"
exec "$HERE/usr/bin/cronos" "$@"
APPRUN
chmod +x "$APPDIR/AppRun"
ok "AppDir assembled"

# ── appimagetool ──────────────────────────────────────────────────────────────
if ! command -v appimagetool &>/dev/null; then
    if [[ ! -f "$APPIMAGETOOL" ]]; then
        step "Downloading appimagetool …"
        curl -fsSL "$APPIMAGETOOL_URL" -o "$APPIMAGETOOL"
        chmod +x "$APPIMAGETOOL"
    fi
    APPIMAGETOOL_CMD="$APPIMAGETOOL --appimage-extract-and-run"
else
    APPIMAGETOOL_CMD="appimagetool"
fi

step "Building AppImage …"
mkdir -p "$DIST_DIR"
OUTPUT="$DIST_DIR/Cronos-x86_64.AppImage"
ARCH=x86_64 $APPIMAGETOOL_CMD "$APPDIR" "$OUTPUT"
chmod +x "$OUTPUT"

ok "Done!"
echo ""
echo "  Output: $OUTPUT"
echo "  Test:   $OUTPUT"
