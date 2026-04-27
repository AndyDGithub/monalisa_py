from src.arrayUtility.bmColReshape import bmColReshape  # Ensure this line points to the correct module and function

from src.sparseMat.m.bmSparseMat_vec import error

from src.coilSense.map.bmCoilSense_pinv import bmCoilSense_pinv
from src.fourier1.bmIDF1 import bmIDF1
from src.fourier2.bmIDF2 import bmIDF2
from src.fourier3.bmIDF3 import bmIDF3
from src.gridding123.m.bmGut_partialCartesian import bmGut_partialCartesian
from src.image123.bmImCrope import bmImCrope
from third_part.matlab_compat.matlab_native import double, single

# ... (rest of your code)

def bmNasha_partialCartesian(y, ind_u, C, N_u, n_u, dK_u):
    # argin_initial -----------------------------------------------------------
    if not n_u:
        n_u = N_u

    y       = single(y)
    N_u     = double(np.array(N_u).ravel().T)
    n_u     = double(np.array(n_u).ravel().T)
    dK_u    = double(single(dK_u).ravel().T)
    imDim   = np.shape(N_u.ravel(), 1)
    nPt     = np.shape(y, 1)
    nCh     = np.shape(y, 2)

    C_flag = False
    if C is not None:
        C_flag = True
        C = single(bmColReshape(C, n_u))

    private_check(y, C, N_u, n_u, nPt, nCh)

    # END_argin_initial -------------------------------------------------------

    # gridding
    x = bmGut_partialCartesian(y, ind_u, N_u)

    # fft
    x = bmBlockReshape(x, N_u)

    if imDim == 1:
        x = bmIDF1(x, single(N_u), single(dK_u))
    elif imDim == 2:
        x = bmIDF2(x, single(N_u), single(dK_u))
    elif imDim == 3:
        x = bmIDF3(x, single(N_u), single(dK_u))

    # eventual croping
    if N_u != n_u:
        x = bmImCrope(x, N_u, n_u)

    # eventual coil_combine
    if C is not None:
        C = bmBlockReshape(C, n_u)
        x = bmCoilSense_pinv(C, x, n_u)

    return x

def k(y, C, N_u, unused, nPt, nCh):
    if not isinstance(y, single):
        error("The data""y"" must be of class single. ")

    # ... (rest of your function)
