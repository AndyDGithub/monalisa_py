import numpy as np

def bmTraj_randomPartialCartesian2_x(N_u, dK_u, myPerOne):
    """
    Generate a random partial Cartesian trajectory in the x-dimension.

    This function follows the MATLAB implementation:
        function t = bmTraj_randomPartialCartesian2_x(N_u, dK_u, myPerOne)

    Parameters
    ----------
    N_u : array_like
        Array containing the number of points in the u-direction.
    dK_u : array_like
        Array containing the k-space sampling spacing in the u-direction.
    myPerOne : float
        Probability for selecting each line in the y-direction.

    Returns
    -------
    t : ndarray
        Concatenated trajectory coordinates as a 1-D array.
    """
    N_u = np.asarray(N_u).reshape(-1)
    dK_u = np.asarray(dK_u).reshape(-1)

    Nx, Ny = N_u[0], N_u[1]
    dKx, dKy = dK_u[0], dK_u[1]

    # Create the full k-space grid in the x and y directions.
    kx = np.arange(-Nx // 2, Nx // 2) * dKx
    ky = np.arange(-Ny // 2, Ny // 2) * dKy

    # Randomly select lines in the y-direction based on the probability.
    mask = np.random.rand(1, Ny) <= myPerOne
    n_line = int(mask.sum())
    ky_sel = ky[mask[0]]

    # Replicate the selected kx and ky values to build the trajectory.
    kx_rep = np.tile(kx[:, None], (1, n_line))
    ky_rep = np.tile(ky_sel[None, :], (Nx, 1))

    # Concatenate and flatten to a 1-D trajectory vector.
    t = np.concatenate((kx_rep.flatten(), ky_rep.flatten()))
    return t
