import numpy as np
from src.arrayUtility.bmPointReshape import bmPointReshape


def bmTraj_nLine(argTraj):
    argTraj = bmPointReshape(argTraj)
    th_n1 = 3.5
    th_n_de = 1 / 1000
    myEps = 10 * np.finfo(float).eps
    delta_separation = myEps / (th_n_de / 1000)

    imDim = argTraj.shape[0]
    nPt = argTraj.shape[1]

    # jump_mask: find where distance between consecutive points jumps
    d1 = np.concatenate(
        (np.zeros((imDim, 1), dtype=argTraj.dtype),
         argTraj[:, 1:] - argTraj[:, :-1]),
        axis=1,
    )
    n1 = np.sqrt(np.sum(d1 ** 2, axis=0))
    n1[0] = 0
    jump_mask = n1 > th_n1 * np.median(n1)

    # nonSeparated_mask: points that are too close together
    nonSeparated_mask = n1 <= delta_separation
    n1[nonSeparated_mask] = 1
    d1[:, nonSeparated_mask] = 0
    nonSeparated_mask = nonSeparated_mask | np.roll(nonSeparated_mask, -1)

    # dirChangeMask: detect direction changes
    e = d1 / n1[np.newaxis, :]
    de = e[:, 1:] - e[:, :-1]   # [imDim, nPt-1]
    de[:, 0] = 0                  # MATLAB: de(:,1) = zeros
    de = np.concatenate([de, np.zeros((imDim, 1))], axis=1)  # append trailing zero
    n_de = np.sqrt(np.sum(de ** 2, axis=0))
    dirChange_mask = n_de > th_n_de

    outOfLine_mask = jump_mask | dirChange_mask | nonSeparated_mask

    # Vectorised counting (replaces the Python for-loop for performance)
    # lastMaskVal starts True, so the "previous" value for index 1 is True.
    current = outOfLine_mask[1:]                               # [nPt-1]
    prev = np.concatenate([[True], outOfLine_mask[1:-1]])      # [nPt-1]
    in_line = ~current                                         # True when on a line
    line_starts = in_line & prev                               # transition into a line
    nLine = int(np.sum(line_starts))
    dK_list = n1[1:][in_line]

    N = nPt / nLine
    isN_integer = abs(N - round(N)) < 1e-12
    return nLine, N, isN_integer, dK_list
