from third_part.matlab_compat.matlab_native import double, int32, int64, single, num2str
import numpy as np

def y(argArray, argDir, argFileName, argType):
    if argType == 'double':
        argArray = double(argArray)
        myType = "double"
    elif argType == 'int':
        argArray = int32(argArray)
        myType = "int"
    elif argType == 'int64':
        argArray = int64(argArray)
        myType = "int64"
    elif argType == 'single':
        argArray = single(argArray)
        myType = "float"
    else:
        raise ValueError("Type is unknown")

    myFileNameH = strcat(argFileName, ".hdat")
    myFileNameD = strcat(argFileName, ".dat")
    myFile = strcat(argDir, "/", myFileNameH)
    myNdims  = np.ndim(argArray)
    mySize   = np.shape(argArray)
    myLength = len(argArray.ravel().T)

    if myType == 'int':
        myOctetNum = 4
    elif myType == 'int64':
        myOctetNum = 8
    elif myType == 'double':
        myOctetNum = 8
    elif myType == 'float':
        myOctetNum = 4

    myNdims_string = num2str(myNdims)
    mySize_string = " ".join([num2str(size_) for size_ in mySize])
    myLength_string = num2str(myLength)
    myOctetNum_string = num2str(myOctetNum)

    if myType == 'int64':
        myType_string = "longlong"
    else:
        myType_string = myType

    dlmwrite(myFile, myNdims_string,                "delimiter", "", "newline","pc")
    dlmwrite(myFile, mySize_string,      "-append", "delimiter", "", "newline","pc")
    dlmwrite(myFile, myLength_string,    "-append", "delimiter", "", "newline","pc")
    dlmwrite(myFile, myType_string,      "-append", "delimiter", "", "newline","pc")
    dlmwrite(myFile, myOctetNum_string,  "-append", "delimiter", "", "newline","pc")

    myFile = strcat(argDir, "/", myFileNameD)
    myFileStream = fopen(myFile, "w")
    fwrite(myFileStream, argArray, myType)
    fclose(myFileStream)

def bmArray2Binary(argArray, argDir, argFileName, argType):
    return y(argArray, argDir, argFileName, argType)
