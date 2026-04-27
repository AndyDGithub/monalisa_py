from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.arrayUtility.bmColReshape import bmColReshape
from src.fourier123.map_function.partialCartesian.bmShanna_partialCartesian import bmShanna_partialCartesian
from src.fourier123.prep_function.bmFC import bmFC
from src.fourier123.prep_function.bmFC_conj import bmFC_conj
from src.linSpace.bmY_ve_reshape import bmY_ve_reshape
import numpy as np

from src.fourier123.map_function.partialCartesian.bmNakatsha_partialCartesian import bmNakatsha_partialCartesian
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023


def unknown_function(witnessInfo, argName, frSize, N_u, dK_u, nIter, nCGD, ve_max):
    myEps = 10 * np.finfo(np.float32).eps

    y = np.array(y, dtype=np.float32)
    nCh = y.shape[1]
    N_u = np.array(N_u, dtype=np.float64).ravel().T
    frSize = np.array(frSize, dtype=np.float64).ravel().T
    dK_u = np.array(dK_u, dtype=np.float64).ravel().T
    ve = bmY_ve_reshape(ve, y.shape)
    C = bmBlockReshape(C, frSize)
    FC = bmFC(C, N_u, frSize, dK_u)
    FC_conj = bmFC_conj(np.conj(C), N_u, frSize, dK_u)

    x = bmColReshape(x, N_u)

    if np.any(ve_max):
        ve_max = np.max(ve)
    else:
        ve_max = np.max(ve)

    dX_u = (1 / dK_u) / N_u
    HX = np.prod(dX_u)

    private_init_witnessInfo(witnessInfo, 'sensa_partialCartesian', frSize, N_u, dK_u, nIter, nCGD, ve_max)

    for c in range(nIter):
        res_next = y - bmShanna_partialCartesian(x, ind_u, FC, N_u, frSize, dK_u)
        dagM_res_next = (1 / HX) * bmNakatsha_partialCartesian(np.multiply(ve, res_next), ind_u, FC_conj, N_u, frSize, dK_u)
        sqn_dagM_res_next = np.real(np.dot(dagM_res_next.T, HX * dagM_res_next))

        p_next = dagM_res_next

        for j in range(nCGD):
            res_curr = res_next
            sqn_dagM_res_curr = sqn_dagM_res_next

            p_curr = p_next

            if sqn_dagM_res_curr < myEps:
                break

            Mp_curr = bmShanna_partialCartesian(p_curr, ind_u, FC, N_u, frSize, dK_u)
            sqn_Mp_curr = np.real(np.dot(Mp_curr.T, ve * Mp_curr))

            a = sqn_dagM_res_curr / sqn_Mp_curr
            x += a * p_curr

            if j == nCGD - 1:
                break

            res_next = res_curr - a * Mp_curr
            dagM_res_next = (1 / HX) * bmNakatsha_partialCartesian(np.multiply(ve, res_next), ind_u, FC_conj, N_u, frSize, dK_u)
            sqn_dagM_res_next = np.real(np.dot(dagM_res_next.T, HX * dagM_res_next))

            b = sqn_dagM_res_next / sqn_dagM_res_curr
            p_next = dagM_res_next + b * p_curr

    temp_r = y - bmShanna_partialCartesian(x, ind_u, FC, N_u, frSize, dK_u)
    R = np.real(np.dot(temp_r.T, ve * temp_r))
    witnessInfo.param[7][c] = R

    witnessInfo.watch('loop', x, frSize, c)


def private_init_witnessInfo(witnessInfo, argName, frSize, N_u, dK_u, nIter, nCGD, ve_max):
    witnessInfo['param_name'][0] = 'recon_name'
    witnessInfo['param'][0] = argName

    witnessInfo['param_name'][1] = 'dK_u'
    witnessInfo['param'][1] = dK_u

    witnessInfo['param_name'][2] = 'N_u'
    witnessInfo['param'][2] = N_u

    witnessInfo['param_name'][3] = 'frSize'
    witnessInfo['param'][3] = frSize

    witnessInfo['param_name'][4] = 'nIter'
    witnessInfo['param'][4] = nIter

    witnessInfo['param_name'][5] = 'nCGD'
    witnessInfo['param'][5] = nCGD

    witnessInfo['param_name'][6] = 've_max'
    witnessInfo['param'][6] = ve_max

    witnessInfo['param_name'][7] = 'residu'
    witnessInfo['param'][7] = np.zeros(nIter)


def bmSensa_partialCartesian():
    return unknown_function(witnessInfo, argName, frSize, N_u, dK_u, nIter, nCGD, ve_max)
