import numpy as np

from src.readWrite.bmBinary2Array import bmBinary2Array


def bmBinary2Array_cData(argDir, argFileName_real, argFileName_imag):
    """Convert binary real and imaginary data files into a complex array.

    Parameters
    ----------
    argDir : str
        Directory containing the binary files.
    argFileName_real : str
        File name of the real part.
    argFileName_imag : str
        File name of the imaginary part.

    Returns
    -------
    numpy.ndarray
        Complex array composed of real and imaginary parts.
    """
    tempData_real = bmBinary2Array(argDir, argFileName_real)
    tempData_imag = bmBinary2Array(argDir, argFileName_imag)
    cData         = np.complex_(tempData_real, tempData_imag)
    return cData

# End of bmBinary2Array_cData.py
