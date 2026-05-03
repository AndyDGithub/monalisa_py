import os

def bmGetFile():
    """
    MATLAB: function varargout = bmGetFile()

    Opens a file selection dialog and returns the selected file information
information.
    The MATLAB implementation returns five outputs:
        1. Full file path
        2. Directory containing the file
        3. Path string (same as 1)
        4. File name
        5. Directory name

    The Python port mirrors this behavior and returns a list of five elemen
elements.
    If the dialog is cancelled or the selected path is invalid, all outputs
outputs are 0.
    """
    try:
        import tkinter.filedialog as tkfd
    except Exception:
        # If tkinter is unavailable (e.g., in a headless environment),
        # fall back to a non-interactive default that signals failure.
        return [0, 0, 0, 0, 0]

    # Open file dialog; returns full path or empty string if cancelled
    selected_path = tkfd.askopenfilename()

    if not selected_path:
        return [0, 0, 0, 0, 0]

    # Split path into directory and file name
    myDir = os.path.dirname(selected_path)
    myFileName = os.path.basename(selected_path)
    myPath = selected_path
    myFile = selected_path

    # Validate directory and file existence
    if not os.path.isdir(myDir) or not os.path.isfile(myFile):
        return [0, 0, 0, 0, 0]

    myDirName = os.path.basename(myDir)

    return [myFile, myDir, myPath, myFileName, myDirName]
