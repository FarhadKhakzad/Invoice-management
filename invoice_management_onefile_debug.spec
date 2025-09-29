"""Debug one-file PyInstaller spec (console enabled) for diagnosing startup crash.

Build:
    py -m PyInstaller --clean --noconfirm invoice_management_onefile_debug.spec

Differences vs release spec:
 - console=True and debug=True (shows traceback if crash)
 - Adds collect_submodules('PySide6') to ensure all Qt plugins/modules bundled
 - Keeps version info; icon still optional
"""
from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.win32.versioninfo import (
    VSVersionInfo,
    FixedFileInfo,
    StringFileInfo,
    StringTable,
    StringStruct,
    VarFileInfo,
    VarStruct,
)
import pathlib, sys

BASE_DIR = pathlib.Path(sys.argv[0]).parent.resolve()
ICON_PATH = None

hidden = set()
hidden.update(collect_submodules('jdatetime'))
hidden.update(collect_submodules('PySide6'))  # broaden for debugging
hidden = list(hidden)

version_info = VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=(0, 1, 0, 0),
        prodvers=(0, 1, 0, 0),
        mask=0x3F,
        flags=0x0,
        OS=0x40004,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0),
    ),
    kids=[
        StringFileInfo([
            StringTable('040904B0', [
                StringStruct('CompanyName', 'YourCompany / Author'),
                StringStruct('FileDescription', 'Invoice Management Application (Debug)'),
                StringStruct('FileVersion', '0.1.0'),
                StringStruct('InternalName', 'invoice_management_onefile_debug'),
                StringStruct('OriginalFilename', 'invoice_management_onefile_debug.exe'),
                StringStruct('ProductName', 'Invoice Management'),
                StringStruct('ProductVersion', '0.1.0'),
            ])
        ]),
        VarFileInfo([VarStruct('Translation', [0x0409, 0x04B0])]),
    ],
)

a = Analysis(
    ['view.py'],
    pathex=[str(BASE_DIR)],
    binaries=[],
    datas=[],
    hiddenimports=hidden,
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
    name='invoice_management_onefile_debug',
    debug=True,
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
    icon=ICON_PATH,
    version=version_info,
)
