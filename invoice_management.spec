"""PyInstaller specification for the Invoice Management desktop application.

Professional build settings:
 - Embeds required hidden imports (jdatetime submodules)
 - Adds Windows version resource metadata
 - Disables traceback dialog for cleaner user experience
 - Keeps console hidden (GUI app)
 - Leaves UPX enabled (if available) to reduce size

To build (PowerShell, from project root):
    pyinstaller --clean --noconfirm invoice_management.spec

Result:
    dist/invoice_management/invoice_management.exe

For a single-file variant (slower startup):
    pyinstaller --onefile --clean --noconfirm --name invoice_management view.py

Add a real icon by placing an .ico file at assets/app.ico and uncommenting ICON_PATH below.
"""

from PyInstaller.utils.hooks import collect_submodules
from PyInstaller.utils.win32.versioninfo import (  # type: ignore
    VSVersionInfo,
    FixedFileInfo,
    StringFileInfo,
    StringTable,
    StringStruct,
    VarFileInfo,
    VarStruct,
)
import pathlib

# Hidden imports (jdatetime dynamically imports modules)
hidden = collect_submodules('jdatetime')

BASE_DIR = (
    pathlib.Path(__file__).parent.resolve()
    if "__file__" in globals()
    else pathlib.Path.cwd()
)
# Optional icon (uncomment and ensure file exists)
# ICON_PATH = str(BASE_DIR / 'assets' / 'app.ico')
ICON_PATH = None  # placeholder (no icon supplied yet)

version_info = VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=(0, 1, 0, 0),
        prodvers=(0, 1, 0, 0),
        mask=0x3F,
        flags=0x0,
        OS=0x40004,
        fileType=0x1,        # Application
        subtype=0x0,
        date=(0, 0),
    ),
    kids=[
        StringFileInfo([
            StringTable('040904B0', [
                StringStruct('CompanyName', 'YourCompany / Author'),
                StringStruct('FileDescription', 'Invoice Management Application'),
                StringStruct('FileVersion', '0.1.0'),
                StringStruct('InternalName', 'invoice_management'),
                StringStruct('LegalCopyright', '© 2025 YourCompany'),
                StringStruct('OriginalFilename', 'invoice_management.exe'),
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
    datas=[],  # Assets embedded via Qt resource (resources_rc.py) so no datas needed
    hiddenimports=hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=1,  # basic bytecode optimization
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='invoice_management',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=True,  # suppress internal error dialog
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON_PATH,
    version=version_info,
)
