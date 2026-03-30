# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path

block_cipher = None
ROOT = Path(os.path.abspath(SPECPATH)).parent.parent
SRC = ROOT / "src"
I18N_DIR = SRC / "aiready" / "i18n"
VERSION = os.environ.get("AIREADY_VERSION", "0.0.0")

a = Analysis(
    [str(ROOT / "build" / "entry_openclaw.py")],
    pathex=[str(SRC)],
    datas=[
        (str(I18N_DIR / "en.json"), "aiready/i18n"),
        (str(I18N_DIR / "ko.json"), "aiready/i18n"),
    ],
    hiddenimports=["customtkinter"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    cipher=block_cipher,
)
pyz = PYZ(a.pure, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    name="AIReady-OpenClaw-Mac",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    icon=None,
    exclude_binaries=True,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="AIReady-OpenClaw-Mac",
)
app = BUNDLE(
    coll,
    name="AIReady-OpenClaw-Mac.app",
    icon=None,
    bundle_identifier="com.aiready.openclaw",
    version=VERSION,
    info_plist={
        "NSHighResolutionCapable": True,
        "NSRequiresAquaSystemAppearance": False,
    },
)
