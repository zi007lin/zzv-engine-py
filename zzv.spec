# zzv.spec
block_cipher = None

a = Analysis(
    ['zzv/examples/basic_usage.py'],
    pathex=['.'],  # Include the current directory
    binaries=[],
    datas=[('zzv/**', 'zzv')],  # Include all zzv files
    hiddenimports=['zzv'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='zzv',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='zzv'
)
