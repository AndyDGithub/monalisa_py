"""Auto-generated from MATLAB source. Review manually before production use."""

from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.arrayUtility.bmColReshape import bmColReshape
from src.arrayUtility.bmMax import bmMax
from src.arrayUtility.bmSingle_of_cell import bmSingle_of_cell
from src.arrayUtility.bmZero import bmZero
from src.fourier123.map_function.partialCartesian.bmShanna_partialCartesian import bmShanna_partialCartesian
from src.fourier123.prep_function.bmFC import bmFC
from src.fourier123.prep_function.bmFC_conj import bmFC_conj
from src.image123.bmImDeform import bmImDeform
from src.image123.bmImDeformT import bmImDeformT
from src.linSpace.bmProx_oneNorm import bmProx_oneNorm
from src.linSpace.bmY_ve_reshape import bmY_ve_reshape
from third_part.matlab_compat.matlab_native import disp, double, single

from src.sparseMat.m.bmSparseMat_vec import int32
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

import numpy as np

def unknown_function():
    ind_u,
    Tu, Tut,
    delta, rho, regul_mode,
    nCGD, ve_max,
    # TODO(matlab-line): nIter, witnessInfo)
    # initial -----------------------------------------------------------------
    disp("tevaMorphosia_partialCartesian initial")
    myEps           = 10*eps("single");  # ---------------------------------------------------- magic_number
    y               = bmSingle_of_cell(y)
    nCh             = np.shape(y[1], 2)
    N_u             = double(int32(N_u.ravel().T))
    # TODO(matlab-control): if isempty(frSize)
    frSize = N_u
    frSize             = double(int32(frSize.ravel().T))
    nPt_u           = prod(frSize.ravel())
    dK_u            = double(single(dK_u.ravel().T))
    # TODO(matlab-line): dX_u            = single(  (1./single(dK_u))./single(N_u)  );
    Du              = single(  prod(dX_u.ravel())  )
    delta           = single(  np.abs(delta.ravel())  )
    rho             = single(  np.abs(rho.ravel())  )
    delta_list      = []
    rho_list        = []
    # TODO(matlab-control): if size(delta, 1) == 1
    delta_list  = linspace(delta, delta, nIter)
    # TODO(matlab-control): elseif size(delta, 1) == 2
    delta_list  = linspace(delta(1, 1), delta(2, 1), nIter)
    delta_list = delta_list.ravel().T
    # TODO(matlab-control): if size(rho, 1) == 1
    rho_list    = linspace(rho,     rho, nIter)
    # TODO(matlab-control): elseif size(rho, 1) == 2
    rho_list    = linspace(rho(1, 1),     rho(2, 1), nIter)
    rho_list = rho_list.ravel().T
    nFr             = np.shape(y.ravel(), 1)
    # TODO(matlab-control): if isempty(ve_max)
    ve_max = single(bmMax(ve))
    # TODO(matlab-control): for i = 1:nFr
    ve[i]       = single(bmY_ve_reshape(ve[i], np.shape(y[i])  ))
    ve[i]       = min(ve[i], single(ve_max))
    C               = single(bmBlockReshape(C, frSize))
    FC              = single(bmFC(          C,  N_u, frSize, dK_u)  )
    FC_conj         = single(bmFC_conj(conj(C), N_u, frSize, dK_u)  )
    # TODO(matlab-control): for i = 1:nFr
    x[i] = single(bmColReshape(x[i], frSize))
    # TODO(matlab-control): if isempty(Tu)
    Tu = cell(nFr, 1)
    # TODO(matlab-control): if isempty(Tut)
    Tut = cell(nFr, 1)
    witnessInfo.param_name[1]    = "recon_name"
    witnessInfo.param[1]         = "tevaMorphosia_partialCartesian"
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
    witnessInfo.param_name[10]    = "regul_mode"
    witnessInfo.param[10]         = regul_mode
    wit_residu_ind = 11
    witnessInfo.param_name[11]    = "residu"
    witnessInfo.param[11]         = np.zeros(1, nIter)
    wit_TV_ind = 12
    witnessInfo.param_name[12]   = "total_variation"
    witnessInfo.param[12]        = np.zeros(1, nIter)
    Vx_plus_u       = cell(nFr, 1)
    q1_next         = cell(nFr, 1)
    q2_next         = cell(nFr, 1)
    temp_B_q_next   = cell(nFr, 1)
    A1_p            = cell(nFr, 1)
    A2_p            = cell(nFr, 1)
    # initial of z and u
    # TODO(matlab-control): if isempty(z)
    z = cell(nFr, 1)
    # TODO(matlab-control): for i = 1:nFr
    i_minus_1   = mod(i - 2, nFr) + 1
    z[i]        = bmImDeform(Tu[i], x[i], frSize, []) - x[i_minus_1];  # z{i} = Bx{i}
    # TODO(matlab-control): if isempty(u)
    u = cell(nFr, 1)
    # TODO(matlab-control): for i = 1:nFr
    u[i]        = bmZero([nPt_u, 1], "complex_single")
    disp(" initial done. ")
    # END_initial -------------------------------------------------------------
    # ADMM loop ---------------------------------------------------------------
    # TODO(matlab-control): for c = 1:nIter
    # TODO(matlab-control): if strcmp(regul_mode, 'normal')
    delta   = delta_list(1, c)
    rho     = rho_list(1, c)
    # TODO(matlab-control): elseif strcmp(regul_mode, 'adapt')
    [delta, rho] = private_adapt_delta_rho(R, TV, delta_list(1, c), rho_list(1, c))
    Du_rho  = Du*rho
    # initial of CGD
    # TODO(matlab-control): for i = 1:nFr
    i_minus_1 = mod(i - 2, nFr) + 1
    q1_next[i] = y[i] - bmShanna_partialCartesian(x[i], ind_u[i], FC, N_u, frSize, dK_u)
    q2_next[i] = z[i] - u[i] + x[i_minus_1] - bmImDeform(Tu[i], x[i], frSize, [])
    # TODO(matlab-control): for i = 1:nFr
    i_plus_1 = mod(i, nFr) + 1
    # TODO(matlab-line): temp_B1_q1_next = bmNakatsha_partialCartesian(ve{i}.*q1_next{i}, ind_u{i}, FC_conj, N_u, frSize, dK_u); % negative_gradient
    temp_B2_q2_next = Du_rho*(  bmImDeformT(Tut[i], q2_next[i], frSize, []) - q2_next[i_plus_1] );  # negative_gradient
    temp_B_q_next[i] = temp_B1_q1_next + temp_B2_q2_next
    Q_next = 0
    # TODO(matlab-control): for i = 1:nFr
    # TODO(matlab-line): Q_next = Q_next + real(temp_B_q_next{i}(:)'*temp_B_q_next{i}(:));
    p_next = temp_B_q_next
    # END initial of CGD
    # TODO(matlab-control): for j = 1:nCGD
    q1 = q1_next
    q2 = q2_next
    p = p_next
    Q = Q_next
    # TODO(matlab-control): if(Q < myEps)
    # TODO(matlab-line): break;
    # TODO(matlab-control): for i = 1:nFr
    i_minus_1   = mod(i - 2, nFr) + 1
    A1_p[i]     = bmShanna_partialCartesian(p[i], ind_u[i], FC, N_u, frSize, dK_u)
    A2_p[i]     = bmImDeform(Tu[i], p[i], frSize, []) - p[i_minus_1]
    P = 0
    # TODO(matlab-control): for i = 1:nFr
    # TODO(matlab-line): P = P + real(  A1_p{i}(:)'*bmCol(ve{i}.*A1_p{i})  ) + Du_rho*real(  A2_p{i}(:)'*A2_p{i}(:)  );
    a = Q/P
    # TODO(matlab-control): for i = 1:nFr
    x[i] = x[i] + a*p[i]
    # TODO(matlab-control): if j == nCGD
    # TODO(matlab-line): break;
    # TODO(matlab-control): for i = 1:nFr
    q1_next[i] = q1[i] - a*A1_p[i]
    q2_next[i] = q2[i] - a*A2_p[i]
    # TODO(matlab-control): for i = 1:nFr
    i_plus_1 = mod(i, nFr) + 1
    # TODO(matlab-line): temp_B1_q1_next = bmNakatsha_partialCartesian(ve{i}.*q1_next{i}, ind_u{i}, FC_conj, N_u, frSize, dK_u);
    temp_B2_q2_next = Du_rho*(  bmImDeformT(Tut[i], q2_next[i], frSize, []) - q2_next[i_plus_1] )
    temp_B_q_next[i] = temp_B1_q1_next + temp_B2_q2_next
    Q_next = 0
    # TODO(matlab-control): for i = 1:nFr
    # TODO(matlab-line): Q_next = Q_next + real(  temp_B_q_next{i}(:)'*temp_B_q_next{i}(:)  );
    # TODO(matlab-control): for i = 1:nFr
    p_next[i] =  temp_B_q_next[i] + (Q_next/Q)*p[i]
    end  # END CGD
    # update of z and u
    # TODO(matlab-control): for i = 1:nFr
    i_minus_1       = mod(i - 2, nFr) + 1
    Vx_plus_u[i]    = bmImDeform(Tu[i], x[i], frSize, []) - x[i_minus_1] + u[i]
    # TODO(matlab-control): for i = 1:nFr
    z[i]            = bmProx_oneNorm(Vx_plus_u[i], delta/rho)
    u[i]            = Vx_plus_u[i] - z[i]
    # evaluation of the two different terms of the objective function
    R   = 0
    TV  = 0
    # TODO(matlab-control): for i = 1:nFr
    i_minus_1 = mod(i - 2, nFr) + 1
    temp_r  = y[i] - bmShanna_partialCartesian(x[i], ind_u[i], FC, N_u, frSize, dK_u);  # residu
    # TODO(matlab-line): R       = R + real(  temp_r(:)'*(  ve{i}(:).*temp_r(:)  )  );
    temp_r  = x[i_minus_1] - bmImDeform(Tu[i], x[i], frSize, [])
    TV      = TV + Du*np.sum(np.abs(  temp_r.ravel()  ))
    # TODO(matlab-line): witnessInfo.param{wit_residu_ind}(1, c)     = R;
    # TODO(matlab-line): witnessInfo.param{wit_TV_ind}(1, c)         = TV;
    witnessInfo.watch(c, x, frSize, "loop")
    # END_ADMM loop -----------------------------------------------------------
    # final -------------------------------------------------------------------
    witnessInfo.watch(c, x, frSize, "final")
    # TODO(matlab-control): for i = 1:nFr
    x[i] = bmBlockReshape(x[i], frSize)
    # END_final ---------------------------------------------------------------

def private_adapt_delta_rho(R, TV, delta_factor, rho_factor):
    # delta   = delta_factor*R/TV;
    delta   = delta_factor*TV/R
    rho     = rho_factor*delta
    return (delta, rho)

def bmTevaMorphosia_partialCartesian():
    return unknown_function()
