from __future__ import annotations

import os
from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.varargin.bmVarargin import bmVarargin

def bmCheckDir(argDir, dlgFlag: bool = True) -> int:
    """
    Check whether a directory exists.

    Parameters
    ----------
    argDir : str | PathLike
        Path to the directory to check.
    dlgFlag : bool, optional
        If True and the directory does not exist, an error dialog is shown.
shown.
        In a headless environment this flag is ignored.

    Returns
    -------
    int
        1 if the directory exists and is a directory, 0 otherwise.
    """
    # Numeric arguments are invalid for directory checks.
    if isinstance(argDir, (int, float)):
        return 0

    # Resolve to string path if necessary.
    path = str(argDir)

    if not os.path.isdir(path):
        if dlgFlag:
            # In non-GUI environments we simply return 0 without raising.
            pass
        return 0

    return 1

# End of module.
