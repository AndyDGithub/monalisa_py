import tkinter as tk
from tkinter import messagebox

def bmGetString():
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    myAnswer = tk.simpledialog.askstring(title='bmGetString', prompt='Enter a string : ')

    if not myAnswer:
        return ""

    return myAnswer
