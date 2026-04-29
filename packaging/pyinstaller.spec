from pathlib import Path


project_root = Path(SPECPATH).resolve().parent
entry_script = project_root / 'main.py'

datas = []
bin_dir = project_root / 'bin'
if bin_dir.exists():
    for f in bin_dir.glob('*'):
        if f.is_file():
            # (origem, destino dentro do bundle)
            datas.append((str(f), 'bin'))

a = Analysis(
    [str(entry_script)],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=[],
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
    [],
    exclude_binaries=True,
    name='audio-to-video',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='audio-to-video',
)
