from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.arrayUtility.bmColReshape import bmColReshape
from src.gridding123.m.bmGu_partialCartesian import bmGu_partialCartesian
from src.image123.bmImZeroFill import bmImZeroFill
from third_part.matlab_compat.matlab_native import double, repmat, single
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023


def private_check(x, FC, N_u, n_u, nCh, C_flag):
    if not isinstance(x, single):
        raise ValueError('The data x must be of class single')

    if not isinstance(FC, single):
        raise ValueError('"FC" must be of class single')

    if np.prod(N_u) != x.shape[0]:
        raise ValueError('The data matrix x is not in the correct size')

    if C_flag:
        if FC.shape != (np.prod(n_u), nCh):
            raise ValueError('The matrix C is probably not in the correct size')


def bmShanna_partialCartesian(x, ind_u, FC, N_u, n_u, dK_u):
    # argin_initial -----------------------------------------------------------
    C_flag = False

    if FC.size == 0:
        FC = single(1 / np.prod(N_u) / np.prod(dK_u))
        C_flag = False
    else:
        C_flag = True

    if n_u.size == 0:
        n_u = N_u

    N_u = double(np.array(N_u).T)
    n_u = double(np.array(n_u).T)
    imDim = np.shape(N_u, 1)
    x_size_2 = np.shape(x, 2)

    if x_size_2 == 1:
        nCh = FC.shape[1]
    else:
        nCh = x_size_2

    private_check(x, FC, N_u, n_u, nCh, C_flag)
    # END_argin_initial -------------------------------------------------------

    # eventual channel extension
    if x_size_2 < nCh:
        x = repmat(x, [1, nCh])

    # coil decombine
    x = x * FC

    # eventual zero_filling
    if not np.array_equal(N_u, n_u):
        x = bmBlockReshape(x, n_u)
        x = bmImZeroFill(x, N_u, n_u, "complex_single")
        x = bmColReshape(x, N_u)

    # fft
    x = bmBlockReshape(x, N_u)
    for n in range(1, 4):
        if imDim > (n - 1):
            x = np.fft.ifftshift(np.fft.fft(np.fft.fftshift(x, n), [], n), n)

    x = bmColReshape(x, N_u)

    # gridding
    y = bmGu_partialCartesian(x, ind_u, N_u)

    return y
