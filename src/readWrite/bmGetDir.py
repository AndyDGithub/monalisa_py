import tkinter as tk
import os

def bmGetDir():
    """
    Open a dialog to select a directory and return three values:

    1. Directory path (full path) or 0 if no selection.
    2. Directory path with trailing separator.
    3. Directory name (last component of the path).

    This mirrors MATLAB's bmGetDir, which returns 0s when the user cancels 
or the path is invalid.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Open the directory selection dialog
    myDir = tk.filedialog.askdirectory(title='Select Directory')

    # If the user cancels, return zeros
    if not myDir:
        return [0, '', '']

    # Ensure the directory exists and is valid
    if not os.path.isdir(myDir):
        return [0, '', '']

    # Construct the outputs
    myPath = os.path.join(myDir, '')
    myDirName = os.path.basename(myDir)
    return [myDir, myPath, myDirName]
