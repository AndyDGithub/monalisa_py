import numpy as np

from src.rawDataReader.mleRawDataReader import mleRawDataReader
from src.rawDataReader.ismrmrd.dhIsmrmrdReadMetaData import dhIsmrmrdReadMetaData
from src.rawDataReader.ismrmrd.dhIsmrmrdReadRawData import dhIsmrmrdReadRawData


class mleIsmrmrdReader(mleRawDataReader):
    def __init__(self, filepath: str, autoFlag: bool):
        super().__init__(filepath, autoFlag)  # Call parent constructor

    def readMetaData(self) -> dict:
        myMriAcquisition_node = dhIsmrmrdReadMetaData(self)
        return myMriAcquisition_node

    def readRawData(self, flagSS: bool = False, flagExcludeSI: bool = False) -> np.ndarray:
        # Handle default values for optional arguments: if no argument
        # is passed there is no data filtering.
        rawdata = dhIsmrmrdReadRawData(self, flagSS, flagExcludeSI)

        # Assuming bmBlockReshape usage based on the failure context
        rawdata_reshaped = bmBlockReshape(rawdata)  # Adjust as necessary

        return rawdata_reshaped
