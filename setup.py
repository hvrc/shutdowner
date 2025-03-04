import os
from cx_Freeze import setup, Executable

include_files = [("art/icon.ico", "art/icon.ico")]

setup(
    name="shutdowner",
    version="1.1",
    description="sets a timer and shuts down your computer",
    options={"build_exe": {"include_files": include_files}},
    executables=[Executable("shutdowner.py", base="Win32GUI", icon="art/icon.ico")]
)
