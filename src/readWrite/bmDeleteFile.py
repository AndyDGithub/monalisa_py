# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

from __future__ import annotations

import os

def bmDeleteFile(arg_file: str) -> None:
    """Delete the specified file if it exists.

    Parameters:
        arg_file (str): The path to the file to be deleted.
    """
    try:
        os.unlink(arg_file)
    except FileNotFoundError:
        pass
