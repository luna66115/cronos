# cronos.spec – PyInstaller build specification for Cronos
#
# Usage:
#   pyinstaller cronos.spec
#
# The resulting binary lands in dist/cronos.

from pathlib import Path

ROOT = Path(SPECPATH)  # noqa: F821  (injected by PyInstaller)

a = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        (str(ROOT / "styles.py"),      "."),
        (str(ROOT / "i18n.py"),        "."),
        (str(ROOT / "cron_manager.py"),"."),
        (str(ROOT / "assets"),         "assets"),
    ],
    hiddenimports=[
        "croniter",
        "PyQt6.QtSvgWidgets",
        "PyQt6.QtSvg",
        "PyQt6.sip",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "matplotlib", "numpy", "scipy"],
    noarchive=False,
)

pyz = PYZ(a.pure)  # noqa: F821

exe = EXE(  # noqa: F821
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="cronos",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
