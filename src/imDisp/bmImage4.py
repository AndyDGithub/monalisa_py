def bmImage4(argImagesTable, *varargin):
    argParam, uiwait_flag = bmVarargin(varargin)
    if argParam is None or argParam == {} or argParam == []:
        myParam = bmImageViewerParam(4, argImagesTable)
    else:
        myParam = bmImageViewerParam(argParam)
    # if argImagesTable is logical
    if isinstance(argImagesTable, np.ndarray) and argImagesTable.dtype == np.bool:
        argImagesTable = argImagesTable.astype(np.float32)
    return myParam
