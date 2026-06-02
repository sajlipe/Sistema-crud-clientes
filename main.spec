# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[
        (
            r'C:\Users\sajli\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\DLLs\_tkinter.pyd',
            '.',
        ),
        (
            r'C:\Users\sajli\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\DLLs\tcl86t.dll',
            '.',
        ),
        (
            r'C:\Users\sajli\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\DLLs\tk86t.dll',
            '.',
        ),
    ],
    datas=[
        ('assets/logo.ico', 'assets'),
        ('assets/logo.png', 'assets'),
        (
            r'C:\Users\sajli\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\tcl\tcl8.6',
            'tcl/tcl8.6',
        ),
        (
            r'C:\Users\sajli\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\tcl\tk8.6',
            'tcl/tk8.6',
        ),
    ],
    hiddenimports=['tkinter', 'tkinter.ttk', '_tkinter'],
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
    name='main',
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
    icon=['assets/logo.ico'],
)
