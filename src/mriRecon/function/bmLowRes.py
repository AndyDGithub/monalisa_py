import numpy as np

def bmLowRes(c, t, ve, N_u, dK_u):
    varargout = []

    # Convert inputs to numpy arrays if they're not already
    c = np.array(c)
    t = np.array(t)
    ve = np.array(ve)
    N_u = np.array(N_u)
    dK_u = np.array(dK_u)

    # Reshape N_u and dK_u
    N_u = N_u.reshape(-1, order='F')
    dK_u = dK_u.reshape(-1, order='F')

    imDim = np.shape(N_u)[0]
    nPt = np.shape(t)[1]

    # Create mask to exclude points outside the grid
    myMask = np.ones((1, nPt), dtype=bool)

    if imDim > 0:
        temp_t = t[0, :]
        dK_temp = dK_u[0, 0]
        L = dK_temp * N_u[0, 0]

        temp_mask = (-L/2 - myEps <= temp_t)
        temp_mask &= (temp_t <= L/2 - dK_temp + myEps)
        myMask &= temp_mask

    if imDim > 1:
        temp_t = t[1, :]
        dK_temp = dK_u[0, 1]
        L = dK_temp * N_u[0, 1]

        temp_mask = (-L/2 - myEps <= temp_t)
        temp_mask &= (temp_t <= L/2 - dK_temp + myEps)
        myMask &= temp_mask

    if imDim > 2:
        temp_t = t[2, :]
        dK_temp = dK_u[0, 2]
        L = dK_temp * N_u[0, 2]

        temp_mask = (-L/2 - myEps <= temp_t)
        temp_mask &= (temp_t <= L/2 - dK_temp + myEps)
        myMask &= temp_mask

    # Return data if asked for
    if len(varargout) > 0:
        varargout.append(c[:, myMask])
    if len(varargout) > 1:
        varargout.append(t[:, myMask])
    if len(varargout) > 2:
        varargout.append(ve[:, myMask])

    return varargout
