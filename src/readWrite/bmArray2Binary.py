import numpy as np

def bmArray2Binary(argArray, argDir, argFileName, argType):
    """
    Write array to binary format with header metadata.

    Parameters
    ----------
    argArray : array_like
        Input array to be written.
    argDir : str
        Directory where the files will be stored.
    argFileName : str
        Base name for the files (without extension).
    argType : str
        Target numeric type: 'double', 'int', 'int64', or 'single'.

    Returns
    -------
    None
    """
    # Convert the input array to the requested MATLAB-like type
    if argType == 'double':
        argArray = np.asarray(argArray, dtype=np.float64)
        myType = 'double'
    elif argType == 'int':
        argArray = np.asarray(argArray, dtype=np.int32)
        myType = 'int'
    elif argType == 'int64':
        argArray = np.asarray(argArray, dtype=np.int64)
        myType = 'int64'
    elif argType == 'single':
        argArray = np.asarray(argArray, dtype=np.float32)
        myType = 'float'
    else:
        raise ValueError("Type is unknown")

    # File names
    myFileNameH = f"{argFileName}.hdat"
    myFileNameD = f"{argFileName}.dat"
    header_path = f"{argDir}/{myFileNameH}"
    data_path = f"{argDir}/{myFileNameD}"

    # Header information
    myNdims = np.ndim(argArray)
    mySize = np.shape(argArray)
    myLength = argArray.size

    if myType == 'int':
        myOctetNum = 4
    elif myType == 'int64':
        myOctetNum = 8
    elif myType == 'double':
        myOctetNum = 8
    elif myType == 'float':
        myOctetNum = 4

    myNdims_string = str(myNdims)
    mySize_string = " ".join(str(dim) for dim in mySize)
    myLength_string = str(myLength)
    myOctetNum_string = str(myOctetNum)

    myType_string = "longlong" if myType == "int64" else myType

    # Write header file
    with open(header_path, "w", newline="") as f:
        f.write(f"{myNdims_string}\n")
        f.write(f"{mySize_string}\n")
        f.write(f"{myLength_string}\n")
        f.write(f"{myType_string}\n")
        f.write(f"{myOctetNum_string}\n")

    # Write binary data file
    with open(data_path, "wb") as f:
        f.write(argArray.tobytes())
