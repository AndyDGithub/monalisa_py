import tkinter as tk
from os import path, getcwd

def bmGetDir():
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    myDir = tk.filedialog.askdirectory(title='Select Directory')

    if not myDir:
        varargout = [0, '', '']
    else:
        varargout = [1, path.join(myDir, ''), myDir]

    return varargout
