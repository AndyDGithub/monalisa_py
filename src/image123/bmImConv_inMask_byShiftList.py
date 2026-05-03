from __future__ import annotations

import numpy as np


def isempty(a: np.ndarray | None) -> bool:
    """Return True if array is None or has zero size."""
    return a is None or a.size == 0


def logical(a: np.ndarray) -> np.ndarray:
    """Convert to boolean array."""
    return np.asarray(a).astype(bool)


def single(a: np.ndarray) -> np.ndarray:
    """Convert to single precision float."""
    return np.asarray(a).astype(np.float32)


def size(a: np.ndarray) -> tuple[int, ...]:
    """Return shape of array."""
    return np.shape(a)


def bmNdim(a: np.ndarray) -> int:
    """Return number of dimensions of array, treating 1-D vectors as 1."""
    return np.ndim(a)


def circshift(a: np.ndarray, shift: tuple[int, ...]) -> np.ndarray:
    """Circular shift array a by shift amounts along each axis."""
    if not isinstance(shift, (list, tuple)):
        raise TypeError("shift must be a sequence of integers")
    return np.roll(a, shift, axis=range(a.ndim))


def bmImConv_inMask_byShiftList(
    argIm: np.ndarray,
    argShiftList: np.ndarray,
    argMask: np.ndarray,
    nIter: int | None = None,
) -> np.ndarray:
    """Strict deterministic baseline port from MATLAB."""
    # Parse optional number of iterations
    if nIter is None:
        nIter = 1

    # Ensure types
    argIm = single(argIm)
    argMask = logical(argMask)

    argSize = size(argIm)
    myDim = bmNdim(argIm)
    if myDim == 1:
        argSize = np.array([argSize[0], 1], dtype=int)
        argIm = argIm.reshape(-1)
        argMask = argMask.reshape(-1)

    myMask_neg = ~argMask

    # Initialize output
    out_1 = argIm.copy()
    out_1[myMask_neg] = 0

    out_2 = np.zeros_like(argIm, dtype=np.float32)

    nShift = size(argShiftList)[0]

    # numOfNonZero
    myNumOfNonZero = np.zeros_like(argIm, dtype=np.float32)
    for i in range(nShift):
        shift_vec = tuple(int(v) for v in argShiftList[i, :])
        myNumOfNonZero += single(circshift(argMask, shift_vec))

    myNumOfNonZero[myMask_neg] = 1.0

    # convolution
    for _ in range(nIter):
        out_2.fill(0)
        for j in range(nShift):
            shift_vec = tuple(int(v) for v in argShiftList[j, :])
            out_2 += circshift(out_1, shift_vec)
        out_1 = out_2 / myNumOfNonZero
        out_1[myMask_neg] = 0

    out_1[myMask_neg] = argIm[myMask_neg]

    return out_1
