"""Auto-generated from MATLAB source. Review manually before production use."""

from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.arrayUtility.bmColReshape import bmColReshape
from src.arrayUtility.bmZero import bmZero
from src.fourier123.map_function.nonCartesian.bmShanna import bmShanna
from src.fourier123.prep_function.bmKF import bmKF
from src.fourier123.prep_function.bmKF_conj import bmKF_conj
from src.linSpace.bmProx_oneNorm import bmProx_oneNorm
from src.linSpace.bmY_ve_reshape import bmY_ve_reshape
from src.optim.bmBackGradient import bmBackGradient
from src.optim.bmBackGradientT import bmBackGradientT
from third_part.matlab_compat.matlab_native import double, single

from src.sparseMat.m.bmSparseMat_vec import imag, int32, real

from src.fourier123.solver_function.imDim.nonCartesian.bmSensa import private_init_witnessInfo
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

import numpy as np

def unknown_function():
    delta, rho, nCGD, ve_max,
    # TODO(matlab-line): nIter, witnessInfo)
    # initial -----------------------------------------------------------------
    myEps   = 10*eps("single");  # -------------------------------------------------- magic number
    y               = single(y)
    nCh             = np.shape(y, 2)
    N_u             = double(int32(Gu.N_u.ravel().T))
    frSize             = double(frSize.ravel().T)
    # TODO(matlab-control): if isempty(frSize)
    frSize = N_u
    nPt_u           = prod(frSize.ravel())
    imDim           = np.shape(N_u.ravel(), 1)
    dK_u            = double(single(Gu.d_u.ravel().T))
    # TODO(matlab-line): dX_u            = single(  (1./single(dK_u))./single(N_u)  );
    # TODO(matlab-control): if isempty(ve_max)
    ve_max = max(ve.ravel())
    [delta, rho]    = private_init_delta_rho(delta, rho, nIter)
    HX              = single(  prod(dX_u.ravel())  )
    HZ              = single(  prod(dX_u.ravel())  )
    HY              = min(single(  bmY_ve_reshape(ve, np.shape(y))  ), single(ve_max))
    C               = single(bmColReshape(C, N_u))
    KFC             = single(bmKF(          C,  N_u, frSize, dK_u, nCh, Gu.kernel_type, Gu.nWin, Gu.kernelParam))
    KFC_conj        = single(bmKF_conj(conj(C), N_u, frSize, dK_u, nCh, Gu.kernel_type, Gu.nWin, Gu.kernelParam))
    x = single(bmColReshape(x, frSize))
    # TODO(matlab-control): if isempty(z)
    z = bmBackGradient(x, frSize, dX_u)
    # TODO(matlab-control): if isempty(u)
    u = bmZero([nPt_u, imDim], "complex_single")
    private_init_witnessInfo(witnessInfo, "steva", frSize, N_u, dK_u, delta, rho, nIter, nCGD, ve_max)
    # END_initial -------------------------------------------------------------
    # ADMM loop ---------------------------------------------------------------
    # TODO(matlab-control): for c = 1:nIter
    res_y_next   = y - bmShanna(x, Gu, KFC, frSize, "MATLAB")
    res_z_next   = (z - u) - bmBackGradient(x, frSize, dX_u)
    # TODO(matlab-line): dagM_res_y_next  = (1/HX)*bmNakatsha(HY.*res_y_next, Gut, KFC_conj, true, frSize, 'MATLAB');
    dagF_res_z_next  = rho(1, c)*(1/HX)*bmBackGradientT(HZ*res_z_next, frSize, dX_u)
    dagA_res_next   = dagM_res_y_next + dagF_res_z_next
    p_next          = dagA_res_next
    sqn_dagA_res_next = real(   dagA_res_next.ravel().T*(HX*dagA_res_next.ravel())   )
    # TODO(matlab-control): for i = 1:nCGD
    res_y_curr   = res_y_next
    res_z_curr   = res_z_next
    sqn_dagA_res_curr = sqn_dagA_res_next
    p_curr = p_next
    # TODO(matlab-control): if (sqn_dagA_res_curr < myEps)
    # TODO(matlab-line): break;
    Mp_curr     = bmShanna(p_curr, Gu, KFC, frSize, "MATLAB")
    Fp_curr     = bmBackGradient(p_curr, frSize, dX_u)
    # TODO(matlab-line): sqn_Mp_curr      = real(   Mp_curr(:)'*(HY(:).*Mp_curr(:))   );
    sqn_Fp_curr      = real(   Fp_curr.ravel().T*(rho(1, c)*HZ*Fp_curr.ravel())   )
    sqn_Ap_curr       = sqn_Mp_curr + sqn_Fp_curr
    a   = sqn_dagA_res_curr/sqn_Ap_curr
    x = x + a*p_curr
    # TODO(matlab-control): if i == nCGD
    # TODO(matlab-line): break;
    res_y_next          = res_y_curr - a*Mp_curr
    res_z_next          = res_z_curr - a*Fp_curr
    # TODO(matlab-line): dagM_res_y_next   = (1/HX)*bmNakatsha(HY.*res_y_next, Gut, KFC_conj, true, frSize, 'MATLAB');
    dagF_res_z_next   = rho(1, c)*(1/HX)*bmBackGradientT(HZ*res_z_next, frSize, dX_u)
    dagA_res_next     = dagM_res_y_next + dagF_res_z_next
    sqn_dagA_res_next = real(   dagA_res_next.ravel().T*(HX*dagA_res_next.ravel())   )
    b = sqn_dagA_res_next/sqn_dagA_res_curr
    p_next           = dagA_res_next + b*p_curr
    bGx_plus_u      = bmBackGradient(x, frSize, dX_u) + u
    z               = bmProx_oneNorm(bGx_plus_u, delta(1, c)/rho(1, c))
    u               = bGx_plus_u - z
    # monitoring ----------------------------------------------------------
    temp_r          = y - bmShanna(x, Gu, KFC, frSize, "MATLAB")
    # TODO(matlab-line): R               = real(  temp_r(:)'*(HY(:).*temp_r(:))  );
    temp_r  = bmBackGradient(x, frSize, dX_u)
    TV      = HZ*np.sum(np.abs(  real(temp_r.ravel())  )) + HZ*np.sum(np.abs(  imag(temp_r.ravel())  ))
    # TODO(matlab-line): witnessInfo.param{9}(1, c)  = R;
    # TODO(matlab-line): witnessInfo.param{10}(1, c) = TV;
    # END_monitoring ------------------------------------------------------
    witnessInfo.watch(c, x, frSize, "loop")
    # END_ADMM loop -----------------------------------------------------------
    # final -------------------------------------------------------------------
    witnessInfo.watch(c, x, frSize, "final")
    x = bmBlockReshape(x, frSize)
    # END_final ---------------------------------------------------------------

def private_init_delta_rho(delta, rho, nIter):
    rho             = single(  np.abs(rho.ravel())  )
    delta           = single(  np.abs(delta.ravel())  )
    # TODO(matlab-control): if size(delta, 1) == 1
    delta   = linspace(delta, delta, nIter)
    # TODO(matlab-control): elseif size(delta, 1) == 2
    delta   = linspace(delta(1, 1), delta(2, 1), nIter)
    delta = delta.ravel().T
    # TODO(matlab-control): if size(rho, 1) == 1
    rho     = linspace(rho,     rho, nIter)
    # TODO(matlab-control): elseif size(rho, 1) == 2
    rho     = linspace(rho(1, 1),     rho(2, 1), nIter)
    rho = rho.ravel().T
    return (delta, rho)

def o(witnessInfo, argName, frSize, N_u, dK_u, delta, rho, nIter, nCGD, ve_max):
    witnessInfo.param_name[1]    = "recon_name"
    witnessInfo.param[1]         = argName
    witnessInfo.param_name[2]    = "dK_u"
    witnessInfo.param[2]         = dK_u
    witnessInfo.param_name[3]    = "N_u"
    witnessInfo.param[3]         = N_u
    witnessInfo.param_name[4]    = "frSize"
    witnessInfo.param[4]         = frSize
    witnessInfo.param_name[5]    = "delta"
    witnessInfo.param[5]         = delta
    witnessInfo.param_name[6]    = "rho"
    witnessInfo.param[6]         = rho
    witnessInfo.param_name[7]    = "nIter"
    witnessInfo.param[7]         = nIter
    witnessInfo.param_name[8]    = "nCGD"
    witnessInfo.param[8]         = nCGD
    witnessInfo.param_name[9]    = "ve_max"
    witnessInfo.param[9]         = ve_max
    witnessInfo.param_name[10]    = "residu"
    witnessInfo.param[10]         = np.zeros(1, nIter)
    witnessInfo.param_name[11]   = "total_variation"
    witnessInfo.param[11]        = np.zeros(1, nIter)
    return private_init_witnessInf

def bmSteva():
    return unknown_function()
