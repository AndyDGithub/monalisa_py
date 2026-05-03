from __future__ import annotations

import os
import tkinter as tk
from tkinter import messagebox


def bmCheckFile(argFile: str, dlgFlag: bool) -> int:
    """
    % Bastien Milani
    % CHUV and UNIL
    % Lausanne - Switzerland
    % May 2023

    """  # End of MATLAB comment block

    """Strict deterministic baseline port from MATLAB.

    Parameters
    ----------
    argFile : str
        Path to the file to be checked.
    dlgFlag : bool
        If True, display a GUI error dialog when the file does not exist.

    Returns
    -------
    int
        1 if the file exists, 0 otherwise.
    """
    if not os.path.isfile(argFile):
        if dlgFlag:
            # Using tkinter for a simple GUI dialog
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            messagebox.showerror("Error", "File does not exist")
        return 0
    return 1
