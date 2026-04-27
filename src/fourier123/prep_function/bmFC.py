from src.arrayUtility.bmColReshape import bmColReshape
from third_part.matlab_compat.matlab_native import double, single

from src.sparseMat.m.bmSparseMat_vec import int32

def bmFC(C, N_u, n_u, dK_u):
    # argin_initial -----------------------------------------------------------
    if not n_u:
        n_u = N_u
    C       = single(   C                 )
    N_u     = double(   int32(N_u.ravel())    )
    n_u     = double(   int32(n_u.ravel())    )
    dK_u    = double(   single(dK_u.ravel())  )
    # END_argin_initial -------------------------------------------------------
    F       = single(  1/np.prod(N_u)/np.prod(dK_u)  )
    C       = single(bmColReshape(C, n_u))
    FC      = single(F*C)
    return FC
