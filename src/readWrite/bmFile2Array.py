import numpy as np
from src.arrayUtility.bmBlockReshape import bmBlockReshape

def bmFile2Array(argDir, argName, argChar, argType):
    myVarName = argName
    if argChar == 'd':
        myFileNameH = f"{argName}.hdat"
        myFileNameD = f"{argName}.dat"
        myFilePath = f"{argDir}/{myFileNameH}"
        
        myNdims = np.fromfile(myFilePath, dtype=np.uint8, count=1)[0]
        myNumbers = np.fromfile(myFilePath, dtype=np.uint8, sep='', count=-1)
        mySize = myNumbers[1: -1].reshape((-1, myNdims)).astype(int)
        
        myLength = 1
        for dim in mySize:
            myLength *= dim
            
        out = np.zeros(mySize.T, dtype=argType)
        myFilePath = f"{argDir}/{myFileNameD}"
        with open(myFilePath, 'rb') as myFile:
            out[:] = np.fromfile(myFile, dtype=argType, count=myLength)

    elif argChar == 't':
        myVarName = argName
        myFileName = f"{argName}.txt"
        myFilePath = f"{argDir}/{myFileName}"

        myNdims = np.fromfile(myFilePath, dtype=np.uint8, count=1)[0]
        myNumbers = np.fromfile(myFilePath, dtype=np.uint8, sep='', count=-1)
        mySize = myNumbers[1: -1].reshape((-1, myNdims)).astype(int)
        
        if myNdims == 1:
            out = np.zeros((mySize, 1), dtype=argType)
        else:
            out = np.zeros(mySize, dtype=argType)

        out[:] = np.genfromtxt(myFilePath, delimiter=' ', skip_header=1, filling_values=0)

    elif argChar == 'c':
        myVarName = argName
        myFileName = f"{argName}.csv"
        myFilePath = f"{argDir}/{myFileName}"

        myNdims = np.fromfile(myFilePath, dtype=np.uint8, count=1)[0]
        myNumbers = np.fromfile(myFilePath, dtype=np.uint8, sep='', count=-1)
        mySize = myNumbers[1: -1].reshape((-1, myNdims)).astype(int)

        if myNdims == 1:
            out = np.zeros((mySize, 1), dtype=argType)
        else:
            out = np.zeros(mySize, dtype=argType)

        temp = np.genfromtxt(myFilePath, delimiter=' ', skip_header=1, filling_values=0, max_rows=0)
        
        for i in range(temp.shape[0] // mySize[0] // mySize[1]):
            out[:, :, i] = temp[(i * mySize[1]):(i + 1) * mySize[1], :]

    return out
