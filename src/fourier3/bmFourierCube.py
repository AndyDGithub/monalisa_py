"""
bmFourierCube - Compute Fourier coefficients for a 3-D cube window.

The original MATLAB implementation computes the Fourier transform of a
box-car function in 3D (a,b,c). The function accepts a vector/matrix of
spatial frequencies argK that has 3 rows or 3 columns and a vector
argEdge specifying the cube size. An optional argument specifies the
center of the window. The implementation below follows the MATLAB
logic closely and uses NumPy for vectorised operations.

Author:   Bastien Milani (port by ChatGPT)
License:  BSD-3
"""

import numpy as np
from third_part.matlab_compat.matlab_native import permute


def bmFourierCube(argK: np.ndarray,
                  argEdge: np.ndarray,
                  *varargin: np.ndarray) -> np.ndarray:
    """
    Compute the Fourier coefficients of a 3-D cube window.

    Parameters
    ----------
    argK : ndarray
        3-D array of spatial frequencies. The first or second dimension
        must have length 3.
    argEdge : scalar or array-like of length 3
        Edge lengths (a,b,c) of the cube. If a scalar is supplied all
        edges are equal. Otherwise ``argEdge`` must be of length 3.
    varargin : optional
        The first optional argument is a 3-element center vector
        (myCenter). If omitted the center defaults to [0,0,0].

    Returns
    -------
    out : ndarray
        Fourier coefficients. The output shape mirrors the input
        shape with the 3-element dimension collapsed.

    Raises
    ------
    ValueError
        If the inputs do not meet the size/shape requirements.
    """

    # ------------------------------------------------------------------
    # 1. Parse and validate edge arguments
    # ------------------------------------------------------------------
    argEdge = np.atleast_1d(argEdge).reshape(-1)
    if argEdge.size == 1:
        a = b = c = float(argEdge[0])
    elif argEdge.size == 3:
        a, b, c = float(argEdge[0]), float(argEdge[1]), float(argEdge[2])
    else:
        raise ValueError("Wrong list of arguments: argEdge must be scalar or length 3.")

    if (a <= 0) or (b <= 0) or (c <= 0):
        raise ValueError("Edge lengths must be positive.")

    # ------------------------------------------------------------------
    # 2. Validate argK shape
    # ------------------------------------------------------------------
    argK = np.asarray(argK)
    if argK.ndim < 2:
        raise ValueError("argK must be at least 2-D.")

    # Accept either first or second dimension equal to 3
    if not (argK.shape[0] == 3 or argK.shape[1] == 3):
        raise ValueError("argK must have one dimension of length 3.")

    # ------------------------------------------------------------------
    # 3. Center handling
    # ------------------------------------------------------------------
    if len(varargin) >= 1 and varargin[0] is not None:
        myCenter = np.asarray(varargin[0]).reshape(3)
    else:
        myCenter = np.array([0.0, 0.0, 0.0])

    # ------------------------------------------------------------------
    # 4. Machine epsilon
    # ------------------------------------------------------------------
    myMachineEpsilon = 2 * np.finfo(np.float64).eps

    # ------------------------------------------------------------------
    # 5. Permute argK so that the cube dimension is the first axis
    # ------------------------------------------------------------------
    if argK.shape[0] == 3:
        k = argK
    else:
        # argK.shape[1] == 3
        k = np.swapaxes(argK, 0, 1)

    k_size = k.shape
    # Flatten all but the first dimension
    mySize = (3, int(np.prod(k_size[1:])))

    k0 = k.reshape(mySize)

    # ------------------------------------------------------------------
    # 6. Compute the Fourier coefficients
    # ------------------------------------------------------------------
    # Avoid division by zero: use np.where
    pi = np.pi

    # First dimension
    kx = k0[0, :]
    myX = np.where(np.abs(kx) < myMachineEpsilon,
                   a,
                   np.sin(pi * kx * a) / (pi * kx))

    # Second dimension
    ky = k0[1, :]
    myY = np.where(np.abs(ky) < myMachineEpsilon,
                   b,
                   np.sin(pi * ky * b) / (pi * ky))

    # Third dimension
    kz = k0[2, :]
    myZ = np.where(np.abs(kz) < myMachineEpsilon,
                   c,
                   np.sin(pi * kz * c) / (pi * kz))

    # ------------------------------------------------------------------
    # 7. Phase shift if center is non-zero
    # ------------------------------------------------------------------
    if not np.allclose(myCenter, np.array([0.0, 0.0, 0.0]), atol=1e-12):
        i_complex = 1j
        myX = myX * np.exp(-i_complex * 2 * pi * myCenter[0] * kx)
        myY = myY * np.exp(-i_complex * 2 * pi * myCenter[1] * ky)
        myZ = myZ * np.exp(-i_complex * 2 * pi * myCenter[2] * kz)

    out = myX * myY * myZ

    # ------------------------------------------------------------------
    # 8. Reshape output to match input shape
    # ------------------------------------------------------------------
    # For 2-D input
    if argK.ndim == 2:
        if argK.shape[0] == 3:
            out = out.reshape((1, -1))
        else:  # shape[1]==3
            out = out.reshape((-1, 1))
    elif argK.ndim > 2:
        if argK.shape[0] == 3:
            out = out.reshape((1, *k_size[1:]))
        else:  # shape[1]==3
            out = out.reshape((k_size[1], 1, *k_size[2:]))

    return out
