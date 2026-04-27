import numpy as np
from src.arrayUtility import bmBlockReshape
from src.arrayUtility.bmPermuteToCol import bmPermuteToCol
from src.arrayUtility.bmPointReshape import bmPointReshape
from src.mriRecon.function.bmLowRes import bmLowRes
from src.geom123 import bmTraj
from reader import RawDataReader  # Assuming 'reader' is defined in the same module or imported correctly
from src.geom123.bmVolumeElement import bmVolumeElement


def bmCoilSense_nonCart_data(reader, N_u):
    myMriAcquisition_node = reader.acquisitionParams

    # Define grid spacing from acquisition FoV
    dK_u_raw = [1, 1, 1] / myMriAcquisition_node.FoV

    # Extract raw data
    y = reader.readRawData(True, True)

    # Compute trajectory and express it as points in 3 dimensions [3, #points]
    t = bmTraj(myMriAcquisition_node)
    t = bmPointReshape(t)

    # Compute volume elements if third output is required
    ve = np.ones((1,) + t.shape[1:])
    if len(reader.varargout) == 3:
        ve = bmVolumeElement(t, 'voronoi_full_radial3')

    # Only keep data in a box to keep the frequencies for lower resolution
    y, t, ve = bmLowRes(y, t, ve, N_u, dK_u_raw)

    y = bmPermuteToCol(y)

    # Return data if required
    reader.varargout[0] = y  # varargout{1}
    if len(reader.varargout) > 1:
        reader.varargout[1] = t  # varargout{2}
    if len(reader.varargout) > 2:
        reader.varargout[2] = ve  # varargout{3}

    return reader.varargout
