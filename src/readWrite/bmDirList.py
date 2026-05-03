from __future__ import annotations
import os


def bmDirList(argDir, recursive_flag):
    """Strict deterministic baseline port from MATLAB."""
    # Check if argDir is a directory
    if not os.path.isdir(argDir):  
        return []
    
    # List all items in the directory
    myList = os.listdir(argDir)
    
    N = 0
    for item in myList:
        temp_dir = os.path.join(argDir, item)
        
        # Check if item is a directory
        if os.path.isdir(temp_dir):
            N += 1
    
    out = [None] * N
    myCount = 0
    for item in myList:
        temp_dir = os.path.join(argDir, item)
        
        # If item is a directory, add it to the output list
        if os.path.isdir(temp_dir):
            myCount += 1
            out[myCount - 1] = temp_dir
    
    # Recursive search if recursive_flag is True
    if recursive_flag:
        for i in range(len(out)):
            out.extend(bmDirList(out[i], True))
    
    return out
