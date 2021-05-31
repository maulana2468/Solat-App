import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'

setup(name = "SolatApp" ,
      version = "1.0.0" ,
      description = "SolatApp muslims prayer schedule" ,
      executables = [Executable("app.py")])