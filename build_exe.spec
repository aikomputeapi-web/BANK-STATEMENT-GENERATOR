# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Bank Statement Generator

import os
from pathlib import Path

block_cipher = None

# Get the project root
PROJECT_ROOT = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    ['desktop_app.py'],
    pathex=[PROJECT_ROOT],
    binaries=[],
    datas=[
        ('templates_web', 'templates_web'),
        ('static', 'static'),
        ('templates', 'templates'),
        ('src', 'src'),
    ],
    hiddenimports=[
        'flask',
        'jinja2',
        'werkzeug',
        'faker',
        'reportlab',
        'reportlab.graphics',
        'reportlab.lib',
        'reportlab.platypus',
        'reportlab.pdfgen',
        'PIL',
        'yaml',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='BankStatementGenerator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Set to False for no console window (use True for debugging)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add path to .ico file if you have one
)
