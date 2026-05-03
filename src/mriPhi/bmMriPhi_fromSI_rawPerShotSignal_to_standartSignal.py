import numpy as np
from src.interp1.bmInterp1 import bmInterp1
from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.geom123 import bmTraj

def bmMriPhi_fromSI_rawPerShotSignal_to_standartSignal(
    s: np.ndarray,
    nSeg: int,
    _,
    ind_shot_min: int,
    ind_shot_max: int,
) -> np.ndarray:
    """
    Convert a raw per-shot MRI signal into a standardized signal format.

    Parameters
    ----------
    s : np.ndarray
        Raw signal array of shape (nSignal, nSI), one point per sampling in
in interval.
    nSeg : int
        Number of segments per interleaved readout.
    _ : Any
        Unused placeholder to match MATLAB function signature.
    ind_shot_min : int
        Minimum shot index (inclusive, zero-based).
    ind_shot_max : int
        Maximum shot index (inclusive, zero-based).

    Returns
    -------
    np.ndarray
        Standardized signal of shape (nSignal, (nLine_to_interp - 1) * 2).
    """
    # Crop the signal to the requested shot range
    s = s[:, ind_shot_min : ind_shot_max + 1]

    # Reshape the signal into interleaved segments
    s = bmBlockReshape(s, nSeg)

    nSignal = s.shape[0]
    # Append the second-last column to the end (mimics MATLAB s(:, end-1))
    s_interpolant = np.concatenate((s, s[:, -2:]), axis=1)

    nLine_to_interp = nSeg * s.shape[1] + 1
    t_interp = np.arange(1, nLine_to_interp + 1)
    t_interpolant = np.arange(1, nLine_to_interp + 1, nSeg)

    s_out = np.zeros((nSignal, (nLine_to_interp - 1) * 2))

    for i in range(nSignal):
        # Interpolate the signal
        temp_s = bmInterp1(t_interpolant, s_interpolant[i], t_interp)
        # Remove the last element (MATLAB: temp_s(:, end) = [])
        temp_s = temp_s[:-1]
        # Mirror the signal
        temp_s = np.concatenate((temp_s, np.flip(temp_s)))
        # Center and normalize
        temp_s = temp_s - temp_s.mean()
        temp_s = temp_s / temp_s.std()
        s_out[i, :] = temp_s

    return s_out
