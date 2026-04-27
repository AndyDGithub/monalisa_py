from third_part.matlab_compat.matlab_native import double, single
import numpy as np

def bmBinary2Array(argDir: str, argFileName: str) -> np.ndarray:
    myFileNameH = f"{argFileName}.hdat"
    myFileNameD = f"{argFileName}.dat"
    myFile = f"{argDir}/{myFileNameH}"
    myCell = np.genfromtxt(myFile, dtype='str', delimiter='\n')
    myNdims = int(myCell[0])
    mySize = np.zeros(myNdims, dtype=int)
    for i in range(myNdims):
        mySize[i] = int(myCell[i + 1])
    myLength = int(myCell[myNdims + 2])
    myType = str(myCell[myNdims + 3])
    myOctetNum = int(myCell[myNdims + 4])

    if myType == 'longlong':
        myType = 'int64'

    out = np.zeros(1, dtype=np.int64)

    myFile = f"{argDir}/{myFileNameD}"
    with open(myFile, "rb") as myFileStream:
        out[:] = np.fromfile(myFileStream, dtype=myType, count=myLength)

    out = np.reshape(out, mySize)

    if myType == 'int':
        out = out.astype(np.int32)
    elif myType == 'int64':
        pass  # already int64
    elif myType == 'double':
        out = out.astype(np.float64)
    elif myType == 'float':
        out = out.astype(np.float32)

    return out
