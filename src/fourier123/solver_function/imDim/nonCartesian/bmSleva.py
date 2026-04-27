"""Auto-generated from MATLAB source. Review manually before production use."""

from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.arrayUtility.bmColReshape import bmColReshape
from src.arrayUtility.bmSingle import bmSingle
from src.fourier123.map_function.nonCartesian.bmShanna import bmShanna
from src.fourier123.prep_function.bmKF import bmKF
from src.fourier123.prep_function.bmKF_conj import bmKF_conj
from src.linSpace.bmY_ve_reshape import bmY_ve_reshape
from src.mathOp.bmAxpy import bmAxpy
from src.mathOp.bmMinus import bmMinus
from src.mathOp.bmMult import bmMult
from src.mathOp.bmPlus import bmPlus
from src.mathOp.bmSquaredNorm import bmSquaredNorm
from third_part.matlab_compat.matlab_native import disp, double, single

from src.sparseMat.m.bmSparseMat_vec import int32
# Bastien Milani
# HES-SO
# Sion - Switzerland
# Dec 2024

import numpy as np

def unknown_function():
    y, ve, C,
    Gu, Gut, frSize,
    delta, regul_mode,
    nCGD, ve_max,
    # TODO(matlab-line): nIter, witnessInfo  )
    # initial -----------------------------------------------------------------
    # function_label
    function_label = "sleva"
    disp([function_label, " initial"])
    # magic_numbers
    myEps                   = 10*eps("single");  # -------------------------------- magic number
    # input data and output image are single.
    x                       = bmSingle(bmColReshape(x, frSize))
    y                       = bmSingle(y)
    # every size is double (because indices must be double in Matlab)
    nCh         = np.shape(y, 2)
    N_u         = double(int32(Gu.N_u.ravel().T))
    frSize         = double(int32(frSize.ravel().T))
    # every phsysical quantity is single
    dK_u                    = single(   Gu.d_u.ravel().T   )
    # TODO(matlab-line): dX_u                    = single(  (1./single(dK_u))./single(N_u)  );
    HX                      = single(  prod(dX_u.ravel())  )
    HZ                      = single(HX)
    HY                      = private_ve_to_HY(ve, ve_max, y)
    # algorithm parameters are single
    delta_list              = single(private_init_regul_param(delta,   nIter))
    # coil_sense and deapodization kernels are single
    C                       = single(bmBlockReshape(C, frSize))
    KFC                     = single(bmKF(          C,  N_u, frSize, dK_u, nCh, Gu.kernel_type, Gu.nWin, Gu.kernelParam))
    KFC_conj                = single(bmKF_conj(conj(C), N_u, frSize, dK_u, nCh, Gu.kernel_type, Gu.nWin, Gu.kernelParam))
    # TODO(matlab-line): bmInitialWitnessInfo(   witnessInfo, ...
    function_label,
    N_u, frSize, dK_u, ve_max,
    nIter,
    nCGD,
    delta_list, [],
    # TODO(matlab-line): regul_mode);
    [dafi, regul]           = private_dafi_regul(x, y, Gu, HY, HZ, frSize, KFC)
    disp(" initial done. ")
    # END_initial -------------------------------------------------------------
    # Outer_CGD_loop ----------------------------------------------------------
    disp([function_label, " is running "])
    # TODO(matlab-control): for c = 1:nIter
    # seting_regul_weight -------------------------------------------------
    # TODO(matlab-control): if strcmp(regul_mode, 'normal')
    delta       = delta_list(1, c)
    # TODO(matlab-control): elseif strcmp(regul_mode, 'adapt')
    delta       = private_adapt_delta(dafi, regul, delta_list(1, c))
    # END_seting_regul_weight ---------------------------------------------
    # CGD -----------------------------------------------------------------
    # L_Aube
    res_y_next              = bmMinus(  y,  private_M(x, Gu, frSize, KFC   )      )
    res_z_next              = bmMinus(  0,  private_F(x)    )
    dagM_res_y_next         = private_dagM(res_y_next, Gut, HX, HY, frSize, KFC_conj)
    dagF_res_z_next         = bmMult(delta, private_dagF(res_z_next))
    dagA_res_next           = bmPlus(dagM_res_y_next, dagF_res_z_next)
    p_next                  = dagA_res_next
    sqn_dagA_res_next       = bmSquaredNorm(  dagA_res_next, HX  )
    # TODO(matlab-control): for j = 1:nCGD
    # Le_Matin
    res_y_curr          = res_y_next
    res_z_curr          = res_z_next
    sqn_dagA_res_curr   = sqn_dagA_res_next
    p_curr              = p_next
    # TODO(matlab-control): if(sqn_dagA_res_curr < myEps)
    # TODO(matlab-line): break;
    # Le_Midi
    Mp_curr             = private_M(p_curr, Gu, frSize, KFC)
    Fp_curr             = private_F(p_curr)
    sqn_Mp_curr         = bmSquaredNorm(Mp_curr, HY)
    sqn_Fp_curr         = bmSquaredNorm(Fp_curr, delta*HZ)
    sqn_Ap_curr         = sqn_Mp_curr + sqn_Fp_curr
    # Le_Soir
    a                   = sqn_dagA_res_curr/sqn_Ap_curr
    x                   = bmAxpy(a, p_curr, x)
    # TODO(matlab-control): if j == nCGD
    # TODO(matlab-line): break;
    # La_Nouvelle_Aube
    res_y_next          = bmAxpy(-a, Mp_curr, res_y_curr)
    res_z_next          = bmAxpy(-a, Fp_curr, res_z_curr)
    dagM_res_y_next     =               private_dagM(res_y_next, Gut, HX, HY, frSize, KFC_conj)
    dagF_res_z_next     = bmMult(delta, private_dagF(res_z_next))
    dagA_res_next       = bmPlus(dagM_res_y_next, dagF_res_z_next)
    sqn_dagA_res_next   = bmSquaredNorm(dagA_res_next, HX)
    b                   = sqn_dagA_res_next/sqn_dagA_res_curr
    p_next              = bmAxpy(b, p_curr, dagA_res_next)
    # END_CGD -------------------------------------------------------------
    # monitoring ----------------------------------------------------------
    [dafi, regul]                   = private_dafi_regul(x, y, Gu, HY, HZ, frSize, KFC)
    objective                       = 0.5*dafi + 0.5*delta*regul
    # TODO(matlab-line): witnessInfo.param{11}(1, c)     = objective;
    # TODO(matlab-line): witnessInfo.param{12}(1, c)     = dafi;
    # TODO(matlab-line): witnessInfo.param{13}(1, c)     = regul;
    witnessInfo.watch(c, x, frSize, "loop")
    # END_monitoring ------------------------------------------------------
    disp([" ", function_label, " completed. "])
    # END_Outer_CGD_loop ------------------------------------------------------
    # final -------------------------------------------------------------------
    witnessInfo.watch(c, x, frSize, "final")
    x = bmBlockReshape(x, frSize)
    # END_final ---------------------------------------------------------------
    # HELP_FUNCIONS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

def private_ve_to_HY(ve, ve_max, y):
    ve = single(bmY_ve_reshape(ve,  np.shape(y)  ))
    HY = min(ve, single(ve_max));  # Important, we limit the value of ve.
    return HY

def private_dafi_regul(x, y, Gu, HY, HZ, frSize, KFC):
    temp_res    = y - bmShanna(x, Gu, KFC, frSize, "MATLAB");  # residu
    dafi        = bmSquaredNorm(temp_res, HY)
    regul       = bmSquaredNorm(x, HZ)
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

def private_adapt_delta(dafi, regul, delta_factor):
    delta   = delta_factor*regul/dafi
    # END_HELP_FUNCIONS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # MODEL_AND_SPARSIFIER %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    # forward_model
    return delta

def private_M(x, Gu, frSize, KFC):
    M_x = bmShanna(x, Gu, KFC, frSize, "MATLAB")
    # forward_sparsifier
    return M_x

def private_F(x):
    F_x = x
    # adjoint_model
    return F_x

def private_dagM(y, Gut, HX, HY, frSize, KFC_conj):
    # TODO(matlab-line): dagM_y = (1/HX)*bmNakatsha(HY.*y, Gut, KFC_conj, true, frSize, 'MATLAB'); % negative_gradient
    # adjoint_sparsifier
    return dagM_y

def private_dagF(z):
    dagF_z = z
    # END_MODEL_AND_SPARSIFIER %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    return dagF_z

def bmSleva():
    return unknown_function()
