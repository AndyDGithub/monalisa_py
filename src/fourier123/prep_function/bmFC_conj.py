from src.arrayUtility.bmColReshape import bmColReshape
from numpy import prod, single, double

from src.sparseMat.m.bmSparseMat_vec import int32

def bmFC_conj(C_conj, N_u, n_u, dK_u):
    # argin_initial -----------------------------------------------------------
    if len(n_u) == 0:
        n_u = N_u
    C_conj      = single(   C_conj            )
    N_u         = double(   int32(N_u.ravel().T)    )
    n_u         = double(   int32(n_u.ravel().T)    )
    dK_u        = double(   single(dK_u.ravel().T)  )
    # END_argin_initial -------------------------------------------------------

    F_conj      = single(  1/prod(dK_u.ravel())  )
    C_conj      = single(  bmColReshape(C_conj, n_u)  )
    FC_conj     = single(  F_conj*C_conj  )

    return FC_conj
