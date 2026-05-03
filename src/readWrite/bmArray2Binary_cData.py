from __future__ import annotations
from src.readWrite.bmArray2Binary import bmArray2Binary

def bmArray2Binary_cData(realData, imagData, argDir, realFileName, imagFileName):
    bmArray2Binary(realData, argDir, realFileName, 'single')
    bmArray2Binary(imagData, argDir, imagFileName, 'single')
