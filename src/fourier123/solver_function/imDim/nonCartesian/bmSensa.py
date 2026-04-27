from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.arrayUtility.bmColReshape import bmColReshape
from src.fourier123.map_function.nonCartesian.bmShanna import bmShanna
from src.fourier123.prep_function.bmKF import bmKF
from src.fourier123.prep_function.bmKF_conj import bmKF_conj
from src.linSpace.bmY_ve_reshape import bmY_ve_reshape
from third_part.matlab_compat.matlab_native import double, single
import numpy as np

from src.fourier123.map_function.nonCartesian.bmNakatsha import bmNakatsha


def unknown_function(witnessInfo, argName, frSize, N_u, dK_u, nIter, nCGD, ve_max):
    myEps = 10 * np.finfo(np.float32).eps

    y = single(y)
    nCh = np.shape(y)[1]
    N_u = double(single(N_u))
    frSize = double(single(frSize))
    dK_u = double(single(dK_u))
    C = single(bmColReshape(C, N_u))
    ve = single(bmY_ve_reshape(ve, np.shape(y)))
    KFC = single(bmColReshape(bmKF(C, N_u, frSize, dK_u, nCh, Gu.kernel_type, Gu.nWin, Gu.kernelParam), frSize))
    KFC_conj = single(bmColReshape(bmKF_conj(np.conj(C), N_u, frSize, dK_u, nCh, Gu.kernel_type, Gu.nWin, Gu.kernelParam), frSize))

    x = single(bmBlockReshape(x, frSize))
    dX_u = single((1 / dK_u) / N_u)
    HX = np.prod(dX_u)

    if not ve_max:
        ve_max = np.max(ve)

    HY = np.minimum(ve, ve_max)

    private_init_witnessInfo(witnessInfo, 'sensa', frSize, N_u, dK_u, nIter, nCGD, ve_max)

    for c in range(nIter):
        res_next = y - bmShanna(x, Gu, KFC, frSize, 'MATLAB')
        dagM_res_next = (1 / HX) * bmNakatsha(HY * res_next, Gut, KFC_conj, True, frSize, 'MATLAB')
        sqn_dagM_res_next = np.real(dagM_res_next @ dagM_res_next.T * HX)
        p_next = dagM_res_next

        for i in range(nCGD):
            res_curr = res_next
            sqn_dagM_res_curr = sqn_dagM_res_next
            p_curr = p_next

            if sqn_dagM_res_curr < myEps:
                break

            Mp_curr = bmShanna(p_curr, Gu, KFC, frSize, 'MATLAB')
            sqn_Mp_curr = np.real(Mp_curr @ HY.T * Mp_curr)

            a = sqn_dagM_res_curr / sqn_Mp_curr

            x += a * p_curr

            if i == nCGD - 1:
                break

            res_next = res_curr - a * Mp_curr
            dagM_res_next = (1 / HX) * bmNakatsha(HY * res_next, Gut, KFC_conj, True, frSize, 'MATLAB')
            sqn_dagM_res_next = np.real(dagM_res_next @ dagM_res_next.T * HX)
            b = sqn_dagM_res_next / sqn_dagM_res_curr

            p_next = dagM_res_next + b * p_curr

        witnessInfo.param[8][c] = np.real(np.dot(res_next.T, HY * res_next))
        witnessInfo.watch(c, x, frSize, 'loop')

    witnessInfo.watch(nIter - 1, x, frSize, 'final')
    x = bmBlockReshape(x, frSize)

    return x


def private_init_witnessInfo(witnessInfo, argName, frSize, N_u, dK_u, nIter, nCGD, ve_max):
    witnessInfo.param_name[0] = 'recon_name'
    witnessInfo.param[0] = argName

    witnessInfo.param_name[1] = 'dK_u'
    witnessInfo.param[1] = dK_u

    witnessInfo.param_name[2] = 'N_u'
    witnessInfo.param[2] = N_u

    witnessInfo.param_name[3] = 'frSize'
    witnessInfo.param[3] = frSize

    witnessInfo.param_name[4] = 'nIter'
    witnessInfo.param[4] = nIter

    witnessInfo.param_name[5] = 'nCGD'
    witnessInfo.param[5] = nCGD

    witnessInfo.param_name[6] = 've_max'
    witnessInfo.param[6] = ve_max

    witnessInfo.param_name[7] = 'residu'
    witnessInfo.param[7] = np.zeros((1, nIter))

# Auto-generated entrypoint alias for import compatibility
bmSensa = unknown_function
