# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

"""Remove and recreate a directory, matching MATLAB's bmClearDir behavior."
behavior."""
import os
import shutil


def bmClearDir(argDir: str) -> None:
    """Delete the directory at *argDir* recursively and recreate it."""
    if os.path.exists(argDir):
        shutil.rmtree(argDir)
    os.makedirs(argDir, exist_ok=True)
