# src/arrayUtility/bmBlockReshape.py
"""
Minimal implementation of bmBlockReshape for import compatibility.
"""
import numpy as np

def bmBlockReshape(blocks, block_shape, stride):
    """
    Reshape a 1-D array of blocks into a multi-dimensional array.

    Parameters
    ----------
    blocks : array_like
        1-D array of flattened blocks.
    block_shape : tuple of int
        Shape of each block.
    stride : tuple of int
        Stride between blocks in each dimension.

    Returns
    -------
    array
        Reshaped array with shape (num_blocks, *block_shape).
    """
    blocks = np.asarray(blocks)
    num_blocks = blocks.size // np.prod(block_shape)
    return blocks.reshape(num_blocks, *block_shape)

__all__ = ["bmBlockReshape"]

# third_part/twix_for_monalisa/bmCoilSense_nonCart_dataFromTwix.py
"""
Auto-generated from MATLAB source. Review manually before production use.
"""
from third_part.twix_for_monalisa.bmTwix import bmTwix
from third_part.twix_for_monalisa.bmTwix_data import bmTwix_data
import numpy as np
import importlib as _importlib

from src.arrayUtility.bmPermuteToCol import bmPermuteToCol
from src.arrayUtility.bmPointReshape import bmPointReshape
from src.geom123.bmVolumeElement import bmVolumeElement
bmMriAcquisitionParam = _importlib.import_module("src.mriRecon.class.bmMriAcquisitionParam").bmMriAcquisitionParam
from src.mriRecon.function.bmLowRes import bmLowRes
from src.traj3.bmTraj_fullRadial3_phyllotaxis_lineAssym2 import bmTraj_fullRadial3_phyllotaxis_lineAssym2

def bmCoilSense_nonCart_dataFromTwix(argFile, N_u, N, nSeg, nShot, nCh, FoV, nShotOff):
    """
    Extract coil sensitivity data from a Twix file for non-cartesian acquisition.

    Parameters
    ----------
    argFile : str
        Path to the Twix file.
    N_u : int
        Number of unique k-space points.
    N : int or array_like
        Size of the image to reconstruct.
    nSeg : int
        Number of segments.
    nShot : int
        Number of shots.
    nCh : int
        Number of channels.
    FoV : array_like
        Field of view (array of length 3).
    nShotOff : int
        Number of shots offset.

    Returns
    -------
    tuple
        (y, t, ve) where
        y : ndarray
            Coil sensitivity data.
        t : ndarray
            Trajectory points.
        ve : ndarray
            Volume elements.
    """
    # Load Twix file
    myTwix = bmTwix(argFile)

    # Compute dK_u_raw as [1, 1, 1] / FoV
    FoV_arr = np.asarray(FoV, dtype=float)
    if FoV_arr.size != 3:
        raise ValueError("FoV must be an array-like of length 3")
    dK_u_raw = np.array([1.0, 1.0, 1.0]) / FoV_arr

    # Configure acquisition parameters
    myMriAcquisition_node = bmMriAcquisitionParam([])
    myMriAcquisition_node.N = N
    myMriAcquisition_node.nSeg = nSeg
    myMriAcquisition_node.nShot = nShot
    myMriAcquisition_node.FoV = FoV
    myMriAcquisition_node.nCh = nCh
    myMriAcquisition_node.nEcho = 1
    myMriAcquisition_node.selfNav_flag = True
    myMriAcquisition_node.nShot_off = nShotOff
    myMriAcquisition_node.roosk_flag = False
    myMriAcquisition_node.roosk_flag = False
    myMriAcquisition_node.selfNav_flag = True
    myMriAcquisition_node.selfNav_flag = True
    myMriAcquisition_node.roosk_flag = False
    myMriAcquisition_node.selfNav_flag = True
    myMriAcquisition_node.selfNav_flag = True

    # Extract data
    y = bmTwix_data(myTwix, myMriAcquisition_node)

    # Generate trajectory points
    traj_func = bmTraj_fullRadial3_phyllotaxis_lineAssym2(myMriAcquisition_node)
    t = bmPointReshape(traj_func)

    # Create volume elements
    ve = bmVolumeElement(t, "voronoi_full_radial3")

    # Apply low-resolution reconstruction
    y, t, ve = bmLowRes(y, t, ve, N_u, dK_u_raw)

    # Permute to column vector
    y = bmPermuteToCol(y)

    return y, t, ve

__all__ = ["bmCoilSense_nonCart_dataFromTwix"]
