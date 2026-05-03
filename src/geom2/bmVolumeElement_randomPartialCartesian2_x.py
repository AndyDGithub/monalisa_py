from src.arrayUtility.bmPointReshape import bmPointReshape
from src.geom1.bmVolumeElement1 import bmVolumeElement1
import numpy as np

def bmVolumeElement_randomPartialCartesian2_x(t, N_u, dK_u):
    # Reshape input arguments to column vectors
    N_u = N_u.ravel().T
    dK_u = dK_u.ravel().T
    
    Nx = N_u[0]
    Ny = N_u[1]
    
    dKx = dK_u[0]
    dKy = dK_u[1]
    
    # Reshape input array t
    t = bmPointReshape(t)
    nPt = np.shape(t, 2)
    nLine = nPt / Nx
    
    t = np.reshape(t, [2, Nx, nLine])
    
    # Extract t1 from reshaped t
    t1 = bmPointReshape(t[1, :, 0])
    
    # Calculate volume element using helper function
    ve = bmVolumeElement1(t1)
    
    # Tile and scale the result
    ve = np.tile(ve.ravel(), [Nx, 1])
    ve = dKx * ve.ravel()
    
    return ve
