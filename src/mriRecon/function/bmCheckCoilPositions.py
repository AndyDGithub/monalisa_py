import numpy as np


def bmCheckCoilPositions(im_main, im_prescan, n_u):
    """
    Compute mean positions of coil sensitivities from main and prescan data
data.

    Parameters
    ----------
    im_main : np.ndarray
        Main imaging data. Expected shape:
        - 3D: (nx, ny, nCh) for 2-D coils
        - 4D: (nx, ny, nz, nCh) for 3-D coils
    im_prescan : np.ndarray
        Prescan data with same spatial shape as `im_main`.
    n_u : array_like
        Spatial dimensions. 1-D array of length 2 or 3: [nx, ny] or [nx, ny
ny
ny, nz].

    Returns
    -------
    tuple of np.ndarray
        (X1_mean, Y1_mean, Z1_mean, X2_mean, Y2_mean, Z2_mean)
        Each array has shape (nCh,).  For 2-D coils, the Z components are z
zero.
    """
    im_main = np.abs(im_main)
    im_prescan = np.abs(im_prescan)

    n_u = np.asarray(n_u).ravel()
    imDim = len(n_u)

    if imDim < 2:
        raise NotImplementedError("Case with imDim == 1 not implemented")

    # Number of channels
    if im_main.ndim <= imDim:
        nCh = 1
    else:
        nCh = im_main.shape[imDim]

    X1_mean = np.zeros(nCh, dtype=float)
    Y1_mean = np.zeros(nCh, dtype=float)
    Z1_mean = np.zeros(nCh, dtype=float)

    X2_mean = np.zeros(nCh, dtype=float)
    Y2_mean = np.zeros(nCh, dtype=float)
    Z2_mean = np.zeros(nCh, dtype=float)

    if imDim == 2:
        nx, ny = n_u[0], n_u[1]

        # 1-based grid
        X = (np.arange(nx) + 1).reshape(-1, 1).repeat(ny, axis=1)
        Y = (np.arange(ny) + 1).reshape(1, -1).repeat(nx, axis=0)

        for i in range(nCh):
            temp_im = im_main[:, :, i]
            temp_im /= temp_im.sum()
            X1_mean[i] = (X * temp_im).sum()
            Y1_mean[i] = (Y * temp_im).sum()
        # Z components remain zero
    elif imDim == 3:
        nx, ny, nz = n_u[0], n_u[1], n_u[2]

        X, Y, Z = np.meshgrid(
            np.arange(nx) + 1,
            np.arange(ny) + 1,
            np.arange(nz) + 1,
            indexing="ij",
        )

        X -= (nx / 2)
        Y -= (ny / 2)
        Z -= (nz / 2)

        for i in range(nCh):
            temp_im = im_main[:, :, :, i]
            temp_im /= temp_im.sum()
            X1_mean[i] = (X * temp_im).sum()
            Y1_mean[i] = (Y * temp_im).sum()
            Z1_mean[i] = (Z * temp_im).sum()

        for i in range(nCh):
            temp_im = im_prescan[:, :, :, i]
            temp_im /= temp_im.sum()
            X2_mean[i] = (X * temp_im).sum()
            Y2_mean[i] = (Y * temp_im).sum()
            Z2_mean[i] = (Z * temp_im).sum()

        a = 0.65
        X2_mean *= a
        Y2_mean *= a
        Z2_mean *= a

    return X1_mean, Y1_mean, Z1_mean, X2_mean, Y2_mean, Z2_mean
