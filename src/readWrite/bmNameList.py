from __future__ import annotations

from src.readWrite.bmCheckDir import bmCheckDir


def bmNameList(argDir, *, recursive=False):
    """Return a list of (short) names of all files and directories in the g
given directory."""
    if not bmCheckDir(argDir, False):
        return []

    myList = [f for f in os.listdir(argDir) if not f.startswith('.')]
    out = [f for f in myList if os.path.isdir(os.path.join(argDir, f))]
    if recursive:
        for item in out:
            sub_path = os.path.join(argDir, item)
            if os.path.isdir(sub_path):
                out.extend(bmNameList(sub_path, recursive=True))
    
    return out
