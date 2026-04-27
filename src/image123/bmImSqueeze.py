from src.image123.bmImReshape import bmImReshape

def bmImSqueeze(argIm):
    [outIm, imDim, imSize, s1, s2, s3] = bmImReshape(np.squeeze(argIm))

    if len(varargout) > 3:
        varargout[0] = s1
    if len(varargout) > 4:
        varargout[1] = s2
    if len(varargout) > 5:
        varargout[2] = s3

    return (outIm, imDim, imSize, varargout)
