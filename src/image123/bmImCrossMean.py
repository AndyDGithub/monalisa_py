import numpy as np

def bmImCrossMean(argIm):
    """
    Compute cross-sectional mean of an image
    :param argIm: input image
    :return: cross-sectional mean of the input image
    """

    # get size of the input image
    imSize = argIm.shape
    
    if len(imSize) == 1:
        raise ValueError("Case not implemented. ")
    
    elif len(imSize) == 2:
        sx, sy = imSize
        
        # compute cross-sectional mean for real images
        if np.isrealobj(argIm):
            out = bmImCrossMean2_mex(sx, sy, argIm)
        
        # compute cross-sectional mean for complex images
        else:
            out_real = bmImCrossMean2_mex(sx, sy, np.real(argIm))
            out_imag = bmImCrossMean2_mex(sx, sy, np.imag(argIm))
            out = out_real + 1j * out_imag
        
    elif len(imSize) == 3:
        sx, sy, sz = imSize
        
        # compute cross-sectional mean for real images
        if np.isrealobj(argIm):
            out = bmImCrossMean3_mex(sx, sy, sz, argIm)
        
        # compute cross-sectional mean for complex images
        else:
            out_real = bmImCrossMean3_mex(sx, sy, sz, np.real(argIm))
            out_imag = bmImCrossMean3_mex(sx, sy, sz, np.imag(argIm))
            out = out_real + 1j * out_imag
    
    # reshape output to match input image size
    out = out.reshape(imSize)
    
    return out
