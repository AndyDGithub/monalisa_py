import os

def bmCheckPath(argPath, dlgFlag=1):
    """
    Strict deterministic baseline port from MATLAB.
    
    Parameters:
        argPath (str): The path to check.
        dlgFlag (int, optional): If 1, displays an error dialog if the path
path
path
path is invalid. Defaults to 1.
        
    Returns:
        int: 1 if the path exists and is a directory, 0 otherwise.
    """
    
    # Normalize the path
    argPath = os.path.normpath(argPath)
    
    # Check if the path ends with a directory separator
    if not argPath.endswith(os.sep):
        if dlgFlag:
            print("Error: Path does not exist")
        return 0
    
    # Check if the path exists and is a directory
    if os.path.exists(argPath) and os.path.isdir(argPath):
        return 1
    else:
        if dlgFlag:
            print("Error: Path does not exist")
        return 0

# Example usage:
path = "C:\\Users\\Username\\Documents"
result = bmCheckPath(path, dlgFlag=1)
print(result)  # Output will be 1 or 0 based on the path validity
