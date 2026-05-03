import numpy as np

def bmLowRes(c, t, ve, N_u, dK_u):
    """This function ensures that the points of the trajectory are inside t
the new grid defined by N_u and dK_u. It removes the points, the correspond
corresponding data from the channels and the volume elements and returns th
them if asked for."""

    # Convert inputs to numpy arrays if they're not already
    c = np.array(c)
    t = np.array(t)
    ve = np.array(ve)
    N_u = np.array(N_u)
    dK_u = np.array(dK_u)

    # Reshape N_u and dK_u
    N_u = N_u.reshape(-1, order='F')
    dK_u = dK_u.reshape(-1, order='F')

    imDim = N_u.shape[0]
    nPt = t.shape[1]

    myEps = np.finfo(float).eps * 1e3

    # Create mask to exclude points outside the grid
    myMask = np.ones((1, nPt), dtype=bool)

    for dim in range(imDim):
        temp_t = t[dim, :]
        dK_temp = dK_u[0, dim]
        L = dK_temp * N_u[0, dim]

        temp_mask = (-L/2 - myEps <= temp_t)
        temp_mask &= (temp_t <= L/2 - dK_temp + myEps)
        myMask &= temp_mask

    # Return data if asked for
    varargout = []
    if len(varargout) > 0:
        varargout.append(c[:, myMask])
    if len(varargout) > 1:
        varargout.append(t[:, myMask])
    if len(varargout) > 2:
        varargout.append(ve[:, myMask])

    return varargout
