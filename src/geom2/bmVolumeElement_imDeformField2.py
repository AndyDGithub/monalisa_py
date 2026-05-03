import numpy as np


def bmVolumeElement_imDeformField2(vf, N_u):
    """Compute the volume element imDeformField2 from a deformation field a
and grid size.

    The implementation follows the MATLAB reference logic:
    * vf must be a 2*M array where M is the number of grid points.
    * N_u is a 1*2 array containing the grid extents [Nx, Ny].
    * The function returns a 1-D array of length prod(N_u) containing the
      volume element values.
    """
    if vf.shape[0] != 2:
        raise ValueError("The trajectory must be 2Dim.")

    N_u = np.asarray(N_u).reshape(-1)
    if N_u.size != 2:
        raise ValueError("N_u must be a 1*2 array.")
    Nx, Ny = N_u[0], N_u[1]

    # Grid coordinates (1-based as in MATLAB)
    x_u = np.arange(1, Nx + 1)
    y_u = np.arange(1, Ny + 1)
    X, Y = np.meshgrid(x_u, y_u, indexing="ij")

    # Reshape deformation field
    vf = np.asarray(vf, dtype=float).reshape(2, -1)

    # Build t matrix
    t = np.vstack((X.ravel() + vf[0, :], Y.ravel() + vf[1, :]))
    t = t.reshape(2, Nx, Ny)

    # Compute cell averages
    s = (
        t[:, 0:-1, 0:-1]
        + t[:, 1:, 0:-1]
        + t[:, 0:-1, 1:]
        + t[:, 1:, 1:]
    ) / 4.0

    # Corner points
    a = s[:, 0:-1, 0:-1]
    b = s[:, 1:, 0:-1]
    c = s[:, 0:-1, 1:]
    d = s[:, 1:, 1:]

    # Flatten to 2*(Nx-2)(Ny-2)
    a = a.reshape(2, -1)
    b = b.reshape(2, -1)
    c = c.reshape(2, -1)
    d = d.reshape(2, -1)

    # Pad with zeros along the last row
    zero_row = np.zeros((1, a.shape[1]), dtype=float)
    a = np.vstack((a, zero_row))
    b = np.vstack((b, zero_row))
    c = np.vstack((c, zero_row))
    d = np.vstack((d, zero_row))

    # Cross products and magnitude
    cross1 = np.cross(b - a, c - a)
    cross2 = np.cross(c - b, d - b)
    v = (np.abs(cross1) + np.abs(cross2)) / 2.0
    v = np.linalg.norm(v, axis=0)

    # Reshape to grid minus borders
    v = v.reshape(Nx - 2, Ny - 2)

    # Pad edges
    v = np.vstack((v[0:1, :], v, v[-1:, :]))
    v = np.hstack((v[:, 0:1], v, v[:, -1:]))

    return v.ravel()
