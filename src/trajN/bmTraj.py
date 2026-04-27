from src.trajN.mlTrajFromPulseq import mlTrajFromPulseq
from src.traj3.bmTraj_fullRadial3_phyllotaxis_lineAssym2 import bmTraj_fullRadial3_phyllotaxis_lineAssym2
from src.traj3.mlTraj_fullRadial3_phyllotaxis_uniform_lineAssym2 import mlTraj_fullRadial3_phyllotaxis_uniform_lineAssym2
from src.traj3.mlTraj_fullRadial3_phyllotaxis_random_lineAssym2 import mlTraj_fullRadial3_phyllotaxis_random_lineAssym2


def bmTraj(mriAcquisition_node):
    """
    Compute the k-space sampling trajectory.

    Dispatches to the appropriate sub-function based on
    mriAcquisition_node.traj_type.

    Returns
    -------
    t : ndarray, shape (nDim, N, nLines)
        Normalised k-space trajectory.
    """
    assert hasattr(mriAcquisition_node, 'traj_type'), \
        "Missing required field: traj_type"
    traj_type = mriAcquisition_node.traj_type

    tl = traj_type.lower().strip()

    if tl == 'full_radial3_phylotaxis':
        return bmTraj_fullRadial3_phyllotaxis_lineAssym2(mriAcquisition_node)
    elif tl == 'uphy':
        print("Warning: Using the uniform phyllotaxis")
        return mlTraj_fullRadial3_phyllotaxis_uniform_lineAssym2(mriAcquisition_node)
    elif tl == 'flexyphy':
        print("Warning: Using polar randomization")
        return mlTraj_fullRadial3_phyllotaxis_random_lineAssym2(mriAcquisition_node)
    elif tl == 'pulseq':
        return mlTrajFromPulseq(mriAcquisition_node)
    else:
        raise ValueError(
            f'bmTraj: Unknown traj_type "{traj_type}". '
            'This probably means your trajectory is not implemented. '
            'You need to implement it yourself.'
        )
