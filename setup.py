import sys
from cx_Freeze import setup, Executable

build_exe_options = {"include_files": ["icons", "formulas", "constants.json", "functions.json"]}

shortcut_table = [
    ("DesktopShortcut",        # Shortcut
     "DesktopFolder",          # Directory_
     "Laser calculator",           # Name
     "TARGETDIR",              # Component_
     "[TARGETDIR]laser-calculator.exe",# Target
     None,                     # Arguments
     None,                     # Description
     None,                     # Hotkey
     None,                     # Icon
     None,                     # IconIndex
     None,                     # ShowCmd
     'TARGETDIR'               # WkDir
     )
    ]
msi_data = {"Shortcut": shortcut_table}
bdist_msi_options = {'data': msi_data}
# base="Win32GUI" should be used only for Windows GUI app
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(
    name = "Laser calculator",
    version = "1.0",
    description = "Calculator for laser and optics equations",
    options = {"build_exe": build_exe_options, "bdist_msi": bdist_msi_options,},
    executables = [Executable("laser-calculator.py", base=base)]
)

# run by running `python setup.py build` or  `python setup.py bdist_msi`