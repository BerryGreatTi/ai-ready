# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path

block_cipher = None
ROOT = Path(os.path.abspath(SPECPATH)).parent.parent
SRC = ROOT / "src"
I18N_DIR = SRC / "aiready" / "i18n"

a = Analysis(
    [str(ROOT / "build" / "entry_claude_code.py")],
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
    a.binaries,
    a.datas,
    [],
    name="AIReady-ClaudeCode-Win",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=None,
)
