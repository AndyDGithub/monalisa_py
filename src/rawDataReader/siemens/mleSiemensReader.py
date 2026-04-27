import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', '..'))
from src.rawDataReader.mleRawDataReader import mleRawDataReader
from src.rawDataReader.siemens.dhSiemensReadMetaData import dhSiemensReadMetaData
from src.rawDataReader.siemens.bmSiemensReadRawData import bmSiemensReadRawData


class mleSiemensReader(mleRawDataReader):
    def __init__(self, filepath, autoFlag):
        super().__init__(filepath, autoFlag)

    def readMetaData(self):
        return dhSiemensReadMetaData(self.argFile, self.autoFlag)

    def readRawData(self, flagSS=False, flagExcludeSI=False):
        return bmSiemensReadRawData(self, flagSS, flagExcludeSI)
