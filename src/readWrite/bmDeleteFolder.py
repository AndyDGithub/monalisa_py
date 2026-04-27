from src.readWrite.bmCheckDir import bmCheckDir
import os
import numpy as np


def r(argDir):
    temp_dir = os.getcwd()
    os.chdir(argDir)

    try:
        os.rmdir(argDir, ignore_errors=True)
    except OSError as e:
        print(f"Error deleting directory {argDir}: {e}")
        raise

    os.chdir(temp_dir)


def bmDeleteFolder(argDir):
    r(argDir)
