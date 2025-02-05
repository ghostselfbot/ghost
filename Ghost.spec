# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['ghost.py'],
    pathex=[],
    binaries=[],
    datas=[('data/*', 'data/'), ('data/fonts/*', 'data/fonts/'), ('data/icons/*', 'data/icons/')],
    hiddenimports=['faker', 'pypresence', 'requests'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Ghost',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
