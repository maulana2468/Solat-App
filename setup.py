import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == 'win32':
    base = 'Win32GUI'
    
build_exe_options = {"includes": ["sys", "os", "datetime", "ast", "requests", "collections", "time", "threading", 
                                  "bs4", "PyQt6.QtCore", "PyQt6.QtGui", "PyQt6.QtWidgets", "plyer", "playsound", "PyQt6"]
                    }

setup(name = "SolatApp" ,
      version = "1.0.0" ,
      description = "SolatApp muslims prayer schedule" ,
      options = {"build_exe": build_exe_options},
      executables = [Executable("app_new.py", base=base)])