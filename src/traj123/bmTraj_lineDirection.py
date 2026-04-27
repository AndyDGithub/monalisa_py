import numpy as np


def bmTraj_lineDirection(t):
    # t: (imDim, N, nLine)
    N = t.shape[1]

    # Replicate first point along the N axis
    t1 = np.tile(t[:, 0:1, :], (1, N, 1))  # (imDim, N, nLine)

    e = t - t1  # differences from first point

    # Second half: MATLAB ceil(N/2):end (1-based) -> Python index ceil(N/2)-1: (0-based)
    start = int(np.ceil(N / 2)) - 1
    e = e[:, start:, :]  # (imDim, half_N, nLine)

    # Normalize per-point direction vectors
    e_norm = np.sqrt(np.sum(e ** 2, axis=0, keepdims=True))  # (1, half_N, nLine)
    e = e / e_norm  # (imDim, half_N, nLine)

    # Average over the N axis -> (imDim, nLine)
    e = np.mean(e, axis=1)
    return e
