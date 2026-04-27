import os
from src.rawDataReader.siemens.mleSiemensReader import mleSiemensReader
from src.rawDataReader.ismrmrd.mleIsmrmrdReader import mleIsmrmrdReader


def createRawDataReader(filepath, autoFlag):
    _, ext = os.path.splitext(filepath)
    if ext.lower() == '.mrd':
        return mleIsmrmrdReader(filepath, autoFlag)
    elif ext.lower() == '.dat':
        return mleSiemensReader(filepath, autoFlag)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")
