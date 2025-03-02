# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

# Setze das Root-Verzeichnis explizit
root_dir = os.path.abspath(os.path.join(os.getcwd()))


a = Analysis(
    [os.path.join(root_dir, 'video_stabilizer.py')],
    pathex=[root_dir],  # Setzt das Root-Verzeichnis als Pfad
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VideoStabilizer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(root_dir, 'app', 'icon', 'output_icons', 'icon.ico')  # Windows Icon
)


# macOS App Bundle (Falls benötigt)
app = BUNDLE(
    exe,  # Korrektur: Nutzt das EXE-Objekt
    name='VideoStabilizer.app',  # Explizit die .app Endung für macOS
    icon=os.path.join(root_dir, 'app', 'icon', 'output_icons', 'icon.icns'),  # macOS Icon
#    bundle_identifier='com.jmeischner.VideoStabilizer'
)
