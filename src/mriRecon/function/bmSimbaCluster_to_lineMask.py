#
# nMask       = size(simbaCluster(:), 1); 
# lineMask    = false(nMask, nSeg, nShot);
#
# for i = 1:nMask
#     lineMask(i, :, simbaCluster{i}(:)') = true;
# end
#
# lineMask = reshape(lineMask, [nMask, nSeg*nShot]); 
#
# end

import numpy as np


def bmSimbaCluster_to_lineMask(simbaCluster, nSeg, nShot):
    """
    Convert a list of shot indices to a line mask.

    Parameters
    ----------
    simbaCluster : list of array_like
        List containing arrays of shot indices (1-based as in MATLAB).
    nSeg : int
        Number of segments.
    nShot : int
        Number of shots per segment.

    Returns
    -------
    lineMask : ndarray
        Line mask reshaped to (nMask, nSeg * nShot) as in MATLAB.
    """
    # MATLAB: nMask = size(simbaCluster(:), 1);
    nMask = len(simbaCluster)

    # MATLAB: lineMask = false(nMask, nSeg, nShot);
    lineMask = np.zeros((nMask, nSeg, nShot), dtype=bool)

    # MATLAB loop: for i = 1:nMask
    for i in range(nMask):
        # MATLAB: lineMask(i, :, simbaCluster{i}(:)') = true;
        # Convert 1-based MATLAB indices to 0-based Python indices.
        idx = np.asarray(simbaCluster[i]).astype(int) - 1
        lineMask[i, :, idx] = True

    # MATLAB: lineMask = reshape(lineMask, [nMask, nSeg*nShot]);
    lineMask = lineMask.reshape((nMask, nSeg * nShot))
    return lineMask
