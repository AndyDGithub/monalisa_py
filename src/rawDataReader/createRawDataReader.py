import os


def createRawDataReader(filepath, autoFlag):
    _, ext = os.path.splitext(filepath)
    if ext.lower() == '.mrd':
        from src.rawDataReader.ismrmrd.mleIsmrmrdReader import mleIsmrmrdReader
        return mleIsmrmrdReader(filepath, autoFlag)
    elif ext.lower() == '.dat':
        from src.rawDataReader.siemens.mleSiemensReader import mleSiemensReader
        return mleSiemensReader(filepath, autoFlag)
    else:
        raise ValueError(f"Unsupported file extension: {ext}")
