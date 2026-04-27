class mleRawDataReader:
    def __init__(self, filepath, autoFlag):
        self.argFile = filepath
        self.autoFlag = autoFlag
        self.acquisitionParams = self.readMetaData()

    def readMetaData(self):
        raise NotImplementedError("readMetaData must be implemented by subclass")

    def readRawData(self, flagSS=False, flagNoSI=False):
        raise NotImplementedError("readRawData must be implemented by subclass")
