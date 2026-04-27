"""Auto-generated from MATLAB source. Review manually before production use."""

from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.arrayUtility.bmColReshape import bmColReshape
from src.arrayUtility.bmSingle import bmSingle
from src.arrayUtility.bmZero import bmZero
from src.fourier123.map_function.nonCartesian.bmShanna import bmShanna
from src.fourier123.prep_function.bmKF import bmKF
from src.fourier123.prep_function.bmKF_conj import bmKF_conj
from src.image123.bmImDeform import bmImDeform
from src.image123.bmImDeformT import bmImDeformT
from src.linSpace.bmProx_oneNorm import bmProx_oneNorm
from src.linSpace.bmY_ve_reshape import bmY_ve_reshape
from src.mathOp.bmAxpy import bmAxpy
from src.mathOp.bmMinus import bmMinus
from src.mathOp.bmMult import bmMult
from src.mathOp.bmPlus import bmPlus
from src.mathOp.bmSquaredNorm import bmSquaredNorm
from third_part.matlab_compat.matlab_native import disp, double, single

from src.sparseMat.m.bmSparseMat_vec import imag, int32, real
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

import numpy as np

def unknown_function():
    z1, z2, u1, u2,
    y, ve, C,
    Gu, Gut, frSize,
    Tu1, Tu1t, Tu2, Tu2t,
    delta, rho, regul_mode,
    nCGD, ve_max,
    # TODO(matlab-line): nIter, witnessInfo  )
    # initial -----------------------------------------------------------------
    # function_label
    function_label = "tevaDuoMorphosia"
    disp([function_label, " initial"])
    # magic_numbers
    myEps                   = 10*eps("single");  # -------------------------------- magic number
    # input data and output image are single.
    x                       = bmSingle(bmColReshape(x, frSize))
    y                       = bmSingle(y)
    # every size is double (because indices must be double in Matlab)
    nCh                     = double(np.shape(y[1], 2))
    nFr                     = double(np.shape(y.ravel(), 1))
    N_u                     = double(int32(Gu[1].N_u.ravel().T))
    frSize                     = double(int32(frSize.ravel().T))
    nPt_u                   = double(prod(frSize.ravel()))
    # every phsysical quantity is single
    dK_u                    = single(   Gu[1].d_u.ravel().T   )
    # TODO(matlab-line): dX_u                    = single(  (1./single(dK_u))./single(N_u)  );
    HX                      = single(  prod(dX_u.ravel())  )
    HZ1                     = single(HX)
    HZ2                     = single(HX)
    HY                      = private_ve_to_HY(ve, ve_max, y)
    # algorithm parameters are single
    delta_list              = single(private_init_regul_param(delta,   nIter))
    rho_list                = single(private_init_regul_param(rho,     nIter))
    # coil_sense and deapodization kernels are single
    C                       = single(bmBlockReshape(C, frSize))
    KFC                     = single(bmKF(          C,  N_u, frSize, dK_u, nCh, Gu[1].kernel_type, Gu[1].nWin, Gu[1].kernelParam))
    KFC_conj                = single(bmKF_conj(conj(C), N_u, frSize, dK_u, nCh, Gu[1].kernel_type, Gu[1].nWin, Gu[1].kernelParam))
    # initialize Tu's and Tut's
    # TODO(matlab-control): if isempty(Tu1)
    Tu1 = cell(nFr, 1)
    # TODO(matlab-control): if isempty(Tu1t)
    Tu1t = cell(nFr, 1)
    # TODO(matlab-control): if isempty(Tu2)
    Tu2 = cell(nFr, 1)
    # TODO(matlab-control): if isempty(Tu2t)
    Tu2t = cell(nFr, 1)
    # debluring kernel for deformations (we leave it empty ,so no effect).
    K_bump          = [];  # bmK_bump(N_u).^(0.5);
    # initialize z's
    # TODO(matlab-control): if isempty(z1)
    z1   = private_F1(x, Tu1, frSize, nFr, K_bump)
    # TODO(matlab-control): if isempty(z2)
    z2   = private_F2(x, Tu2, frSize, nFr, K_bump)
    # initialize u's
    # TODO(matlab-control): if isempty(u1)
    u1   = bmZero([nPt_u, 1], "complex_single", [nFr, 1])
    # TODO(matlab-control): if isempty(u2)
    u2   = bmZero([nPt_u, 1], "complex_single", [nFr, 1])
    # TODO(matlab-line): bmInitialWitnessInfo(   witnessInfo, ...
    function_label,
    N_u, frSize, dK_u, ve_max,
    nIter,
    nCGD,
    delta_list, rho_list,
    # TODO(matlab-line): regul_mode);
    [dafi, regul] = private_dafi_regul(x, y, Gu, Tu1, Tu2, HY, HZ1, HZ2, frSize, nFr, KFC, K_bump)
    disp(" initial done. ")
    # END_initial -------------------------------------------------------------
    # ADMM loop ---------------------------------------------------------------
    disp([function_label, " is running "])
    # TODO(matlab-control): for c = 1:nIter
    # seting_regul_weight -------------------------------------------------
    # TODO(matlab-control): if strcmp(regul_mode, 'normal')
    delta           = delta_list(1, c)
    rho             = rho_list(1, c)
    # TODO(matlab-control): elseif strcmp(regul_mode, 'adapt')
    [delta, rho]    = private_adapt_delta_rho(dafi, regul, delta_list(1, c), rho_list(1, c))
    # END_seting_regul_weight ---------------------------------------------
    # CGD -----------------------------------------------------------------
    # L_Aube
    res_y_next              = bmMinus(                y,  private_M(x, Gu, frSize, nFr, KFC   )      )
    res_z1_next             = bmMinus(  bmMinus(z1, u1),  private_F1(x, Tu1, frSize, nFr, K_bump)      )
    res_z2_next             = bmMinus(  bmMinus(z2, u2),  private_F2(x, Tu2, frSize, nFr, K_bump)      )
    dagM_res_y_next         = private_dagM(res_y_next, Gut, HX, HY, frSize, nFr, KFC_conj)
    dagF1_res_z1_next       = bmMult(rho, private_dagF1(res_z1_next, Tu1t, HX, HZ1, frSize, nFr, K_bump))
    dagF2_res_z2_next       = bmMult(rho, private_dagF2(res_z2_next, Tu2t, HX, HZ2, frSize, nFr, K_bump))
    dagA_res_next           = bmPlus(dagM_res_y_next, bmPlus(dagF1_res_z1_next, dagF2_res_z2_next))
    p_next                  = dagA_res_next
    sqn_dagA_res_next       = bmSquaredNorm(  dagA_res_next, HX  )
    # TODO(matlab-control): for j = 1:nCGD
    # Le_Matin
    res_y_curr          = res_y_next
    res_z1_curr         = res_z1_next
    res_z2_curr         = res_z2_next
    sqn_dagA_res_curr   = sqn_dagA_res_next
    p_curr              = p_next
    # TODO(matlab-control): if(sqn_dagA_res_curr < myEps)
    # TODO(matlab-line): break;
    # Le_Midi
    Mp_curr             = private_M(p_curr, Gu, frSize, nFr, KFC)
    F1p_curr            = private_F1(p_curr, Tu1, frSize, nFr, K_bump)
    F2p_curr            = private_F2(p_curr, Tu2, frSize, nFr, K_bump)
    sqn_Mp_curr         = bmSquaredNorm(Mp_curr, HY)
    sqn_F1p_curr        = bmSquaredNorm(F1p_curr, rho*HZ1)
    sqn_F2p_curr        = bmSquaredNorm(F2p_curr, rho*HZ2)
    sqn_Ap_curr         = sqn_Mp_curr + sqn_F1p_curr + sqn_F2p_curr
    # Le_Soir
    a                   = sqn_dagA_res_curr/sqn_Ap_curr
    x                   = bmAxpy(a, p_curr, x)
    # TODO(matlab-control): if j == nCGD
    # TODO(matlab-line): break;
    # La_Nouvelle_Aube
    res_y_next          = bmAxpy(-a, Mp_curr, res_y_curr)
    res_z1_next         = bmAxpy(-a, F1p_curr, res_z1_curr)
    res_z2_next         = bmAxpy(-a, F2p_curr, res_z2_curr)
    dagM_res_y_next     =             private_dagM(res_y_next, Gut, HX, HY, frSize, nFr, KFC_conj)
    dagF1_res_z1_next   = bmMult(rho, private_dagF1(res_z1_next, Tu1t, HX, HZ1, frSize, nFr, K_bump))
    dagF2_res_z2_next   = bmMult(rho, private_dagF2(res_z2_next, Tu2t, HX, HZ2, frSize, nFr, K_bump))
    dagA_res_next       = bmPlus(dagM_res_y_next, bmPlus(dagF1_res_z1_next, dagF2_res_z2_next))
    sqn_dagA_res_next   = bmSquaredNorm(dagA_res_next, HX)
    b                   = sqn_dagA_res_next/sqn_dagA_res_curr
    p_next              = bmAxpy(b, p_curr, dagA_res_next)
    # END_CGD -------------------------------------------------------------
    # updating_z_and_u ----------------------------------------------------
    F1x_plus_u1              = bmPlus(u1, private_F1(x, Tu1, frSize, nFr, K_bump))
    F2x_plus_u2              = bmPlus(u2, private_F2(x, Tu2, frSize, nFr, K_bump))
    z1                       = bmProx_oneNorm(F1x_plus_u1, delta/rho)
    z2                       = bmProx_oneNorm(F2x_plus_u2, delta/rho)
    u1                       = bmMinus(F1x_plus_u1, z1)
    u2                       = bmMinus(F2x_plus_u2, z2)
    # END_updating_z_and_u ------------------------------------------------
    # monitoring ----------------------------------------------------------
    [dafi, regul]                   = private_dafi_regul(x, y, Gu, Tu1, Tu2, HY, HZ1, HZ2, frSize, nFr, KFC, K_bump)
    objective                       = 0.5*dafi + 0.5*delta*regul
    # TODO(matlab-line): witnessInfo.param{11}(1, c)     = objective;
    # TODO(matlab-line): witnessInfo.param{12}(1, c)     = dafi;
    # TODO(matlab-line): witnessInfo.param{13}(1, c)     = regul;
    witnessInfo.watch(c, x, frSize, "loop")
    # END_monitoring ------------------------------------------------------
    disp([" ", function_label, " completed. "])
    # END_ADMM loop -----------------------------------------------------------
    # final -------------------------------------------------------------------
    witnessInfo.watch(c, x, frSize, "final")
    x = bmBlockReshape(x, frSize)
    # TODO(matlab-control): if nargout > 1
    varargout[1] = z1
    # TODO(matlab-control): if nargout > 2
    varargout[2] = z2
    # TODO(matlab-control): if nargout > 3
    varargout[3] = u1
    # TODO(matlab-control): if nargout > 4
    varargout[4] = u2
    # END_final ---------------------------------------------------------------
    # HELP_FUNCIONS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def private_ve_to_HY(ve, ve_max, y):
    nFr = np.shape(y.ravel(), 1)
    HY  = cell(nFr, 1)
    # TODO(matlab-control): for i = 1:nFr
    ve[i]               = single(bmY_ve_reshape(ve[i],  np.shape(y[i])  ))
    HY[i]               = min(ve[i], single(ve_max));  # Important, we limit the value of ve.
    return HY

def private_dafi_regul(x, y, Gu, Tu1, Tu2, HY, HZ1, HZ2, frSize, nFr, KFC, K_bump):
    dafi   = 0
    regul  = 0
    # TODO(matlab-control): for i = 1:nFr
    temp_res    = y[i] - bmShanna(x[i], Gu[i], KFC, frSize, "MATLAB");  # residu
    dafi        = dafi + bmSquaredNorm(temp_res, HY[i])
    i_minus_1   = mod( (i-1) - 1, nFr) + 1
    temp_res    = x[i_minus_1] - bmImDeform(Tu1[i], x[i], frSize, K_bump)
    regul       = regul + HZ1*np.sum(np.abs(  real(temp_res.ravel())  )) + HZ1*np.sum(np.abs(  imag(temp_res.ravel())  ))
    i_plus_1    = mod( (i+1) - 1, nFr) + 1
    temp_res    = x[i_plus_1] - bmImDeform(Tu2[i], x[i], frSize, K_bump)
    regul       = regul + HZ2*np.sum(np.abs(  real(temp_res.ravel())  )) + HZ2*np.sum(np.abs(  imag(temp_res.ravel())  ))
    return (dafi, regul)

def private_init_regul_param(in_param, nIter):
    out_param       = single(  np.abs(in_param.ravel())  )
    # TODO(matlab-control): if size(out_param, 1) == 1
    out_param   = linspace(out_param, out_param, nIter)
    # TODO(matlab-control): elseif size(out_param, 1) == 2
    out_param   = linspace(out_param(1, 1), out_param(2, 1), nIter)
    out_param = out_param.ravel().T
    out_param = single(out_param)
    return out_param

def private_adapt_delta_rho(dafi, regul, delta_factor, rho_factor):
    # delta   = delta_factor*R/TV;
    delta   = delta_factor*regul/dafi
    rho     = rho_factor*delta
    # END_HELP_FUNCIONS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # MODEL_AND_SPARSIFIER %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # forward_model
    return (delta, rho)

def private_M(x, Gu, frSize, nFr, KFC):
    M_x = cell(nFr, 1)
    # TODO(matlab-control): for i = 1:nFr
    M_x[i]     = bmShanna(x[i], Gu[i], KFC, frSize, "MATLAB")
    # forward_sparsifier_1
    return M_x

def private_F1(x, Tu1, frSize, nFr, K_bump):
    F1_x = cell(nFr, 1)
    # TODO(matlab-control): for i = 1:nFr
    i_minus_1   = mod( (i-1) - 1, nFr) + 1
    F1_x[i]     = 0.5*(bmImDeform(Tu1[i], x[i], frSize, K_bump) - x[i_minus_1])
    # forward_sparsifier_2
    return F1_x

def private_F2(x, Tu2, frSize, nFr, K_bump):
    F2_x = cell(nFr, 1)
    # TODO(matlab-control): for i = 1:nFr
    i_plus_1   = mod( (i+1) - 1, nFr) + 1
    F2_x[i]    = 0.5*(bmImDeform(Tu2[i], x[i], frSize, K_bump) - x[i_plus_1])
    # adjoint_model
    return F2_x

def private_dagM(y, Gut, HX, HY, frSize, nFr, KFC_conj):
    dagM_y = cell(nFr, 1)
    # TODO(matlab-control): for i = 1:nFr
    # TODO(matlab-line): dagM_y{i} = (1/HX)*bmNakatsha(HY{i}.*y{i}, Gut{i}, KFC_conj, true, frSize, 'MATLAB'); % negative_gradient
    # adjoint_sparsifier_1
    return dagM_y

def private_dagF1(z, Tu1t, HX, HZ1, frSize, nFr, K_bump):
    dagF1_z = cell(nFr, 1)
    # TODO(matlab-control): for i = 1:nFr
    i_plus_1   = mod( (i+1) - 1, nFr) + 1
    dagF1_z[i] = (0.5/HX)*(   bmImDeformT(Tu1t[i], HZ1*z[i], frSize, K_bump) - HZ1*z[i_plus_1]  );  # negative_gradient
    # adjoint_sparsifier_2
    return dagF1_z

def private_dagF2(z, Tu2t, HX, HZ2, frSize, nFr, K_bump):
    dagF2_z = cell(nFr, 1)
    # TODO(matlab-control): for i = 1:nFr
    i_minus_1   = mod( (i-1) - 1, nFr) + 1
    dagF2_z[i]  = (0.5/HX)*(   bmImDeformT(Tu2t[i], HZ2*z[i], frSize, K_bump) - HZ2*z[i_minus_1]  );  # negative_gradient
    # END_MODEL_AND_SPARSIFIER %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    return dagF2_z

def bmTevaDuoMorphosia_chain():
    return unknown_function()
