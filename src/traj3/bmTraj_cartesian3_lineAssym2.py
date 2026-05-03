import numpy as np

def bmTraj_cartesian3_lineAssym2(*varargin):
    """Strict deterministic baseline port from MATLAB."""
    if len(varargin) == 0:
        raise ValueError("At least one argument required")

    # Extract N_u and dK_u
    if isinstance(varargin[0], dict):
        t_info = varargin[0]
        N_u = np.asarray(t_info["N_u"]).reshape(1, -1)
        dK_u = np.asarray(t_info["dK_u"]).reshape(1, -1)
    else:
        N_u = np.asarray(varargin[0]).reshape(1, -1)
        dK_u = np.asarray(varargin[1]).reshape(1, -1)

    if N_u.size != 3 or dK_u.size != 3:
        raise ValueError("N_u and dK_u must each contain 3 elements")

    # Build index ranges according to MATLAB logic
    seqs = []
    for N, d in zip(N_u[0], dK_u[0]):
        seq = np.arange(-N / 2.0, N / 2.0, 1.0) * d
        seqs.append(seq)

    # Generate full grid (equivalent to MATLAB ndgrid)
    X, Y, Z = np.meshgrid(*seqs, indexing="ij")

    # Concatenate into a 3xN_total matrix
    myTraj = np.vstack((X.ravel(), Y.ravel(), Z.ravel()))

    return myTraj

from src.geom123 import bmTraj
