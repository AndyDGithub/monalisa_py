import numpy as np
import os
from urllib.request import urlretrieve
from third_part.matlab_compat.matlab_native import disp

def a():
    # DOWNLOADDATA Download tutorial data using curl/wget via system()
    # Works on Windows / macOS / Linux
    print("Downloading tutorial data")
    scriptDir = os.path.dirname(os.path.realpath(__file__))
    os.chdir(scriptDir)

    files = [
        ("11p1lUw4pcj_xp1kPuKv3LO_cfcyYlnw_", "bodyCoil.dat"),
        ("12sYtd-KfkZYM8IBzg_DGXsxT3n_uHSLf", "brainScan.dat"),
        ("1dd8I74Hy4Hb97SF-fHBIkrZP_JzwpMa0", "surfaceCoil.dat")
    ]

    for fileId, outFile in files:
        url = f"https://drive.googleusercontent.com/download?id={fileId}&confirm=xxx"
        print(f"→ {outFile}")

        try:
            cmd = f"curl -L '{url}' -o '{outFile}'"
            os.system(cmd)
            print("  ✔ done")
        except Exception as e:
            print(f"  ❌ failed: {e}")
            disp(str(e))

    print("\nAll downloads completed.")
    return downloadData()

def buildDownloadCommand(fileId, outFile):
    # BUILD DOWNLOAD COMMAND FOR CURRENT OS
    url = f"https://drive.googleusercontent.com/download?id={fileId}&confirm=xxx"
    cmd = f"curl -L '{url}' -o '{outFile}'"
    return cmd

def downloadData():
    return a()
