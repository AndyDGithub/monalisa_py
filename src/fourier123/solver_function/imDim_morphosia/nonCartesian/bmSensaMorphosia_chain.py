from src.arrayUtility.bmCol import bmCol
from src.arrayUtility.bmMax import bmMax
from src.arrayUtility.bmSingle_of_cell import bmSingle_of_cell
from src.fourier123.map_function.nonCartesian.bmNakatsha import bmNakatsha
from src.fourier123.map_function.nonCartesian.bmShanna import bmShanna
from src.fourier123.prep_function.bmKF import bmKF
from src.fourier123.prep_function.bmKF_conj import bmKF_conj
from src.fourier123.solver_function.imDim_morphosia.nonCartesian.bmTevaMorphosia_chain_all_to_first import private_init_witnessInfo
from src.image123.bmImDeform import bmImDeform
from src.image123.bmImDeformT import bmImDeformT
from src.linSpace.bmY_ve_reshape import bmY_ve_reshape

from src.arrayUtility.bmColReshape import bmColReshape
def bmSensaMorphosia_chain(x, y, ve, C, Gu, Gut, frSize, Tu, Tut, nCGD, ve_max, nIter, witnessInfo):
    # initial
    myEps = 10 * np.finfo(np.float32).eps
    y = bmSingle_of_cell(y)
    nCh = y[0].shape[1]
    N_u = np.array(Gu[0].N_u).astype(np.float64)
    if frSize is None or len(frSize)==0:
        frSize = N_u
    dK_u = np.array(Gu[0].d_u, dtype=np.float32).astype(np.float64)
    nFr = len(y)
    dX_u = 1.0 / dK_u / N_u
    HX = np.prod(dX_u)
    if ve_max is None or len(ve_max)==0:
        ve_max = bmMax(ve)
    HY = []
    for i in range(nFr):
        ve_i = bmY_ve_reshape(ve[i], y[i].shape)
        ve_i = np.minimum(ve_i, ve_max.astype(np.float32))
        HY.append(ve_i.astype(np.float32))
    C = bmColReshape(C, N_u).astype(np.float32)
    KFC = bmKF(C, N_u, frSize, dK_u, nCh, Gu[0].kernel_type, Gu[0].nWin, Gu[0].kernelParam).astype(np.float32)
    KFC_conj = bmKF_conj(np.conj(C), N_u, frSize, dK_u, nCh, Gu[0].kernel_type, Gu[0].nWin, Gu[0].kernelParam).astype(np.float32)
    K_bump = []  # placeholder
    if isinstance(x, (list, tuple)):
        x = bmColReshape(x[0], frSize).astype(np.float32)
    else:
        x = bmColReshape(x, frSize).astype(np.float32)
    if Tu is None or len(Tu)==0:
        Tu = [None]*nFr
    if Tut is None or len(Tut)==0:
        Tut = [None]*nFr
    private_init_witnessInfo(witnessInfo, 'sensaMorphosia', frSize, N_u, dK_u, nIter, nCGD, ve_max)
    res_next = [None]*nFr
    Ap_curr = [None]*nFr
    for c in range(nIter):
        # initial CGD
        for i in range(nFr):
            intermed = bmImDeform(Tu[i], x, frSize, K_bump)
            res_next[i] = y[i] - bmShanna(intermed, Gu[i], KFC, frSize, 'MATLAB')
        # compute dagA_res_next
        dagA_res_next = np.zeros_like(x, dtype=np.float32)
        for i in range(nFr):
            intermed = bmNakatsha(HY[i] * res_next[i], Gut[i], KFC_conj, True, frSize, 'MATLAB')
            dagA_res_next += (1/HX) * bmImDeformT(Tut[i], intermed, frSize, K_bump)
        sqn_dagA_res_next = np.real(dagA_res_next.reshape(-1).T @ (HX * dagA_res_next.reshape(-1)))
        p_next = dagA_res_next
        sqn_dagA_res_curr = sqn_dagA_res_next
        for j in range(nCGD):
            if sqn_dagA_res_curr < myEps:
                break
            Ap_curr = [None]*nFr
            for i in range(nFr):
                intermed = bmImDeform(Tu[i], p_next, frSize, K_bump)
                Ap_curr[i] = bmShanna(intermed, Gu[i], KFC, frSize, 'MATLAB')
            sqn_Ap_curr = 0
            for i in range(nFr):
                sqn_Ap_curr += np.real(Ap_curr[i].reshape(-1).T @ bmCol(HY[i] * Ap_curr[i]))
            a = sqn_dagA_res_curr / sqn_Ap_curr
            x = x + a * p_next
            if j == nCGD-1:
                break
            for i in range(nFr):
                res_next[i] = res_next[i] - a * Ap_curr[i]
            dagA_res_next = np.zeros_like(x, dtype=np.float32)
            for i in range(nFr):
                intermed = bmNakatsha(HY[i] * res_next[i], Gut[i], KFC_conj, True, frSize, 'MATLAB')
                dagA_res_next += (1/HX) * bmImDeformT(Tut[i], intermed, frSize, K_bump)
            sqn_dagA_res_next = np.real(dagA_res_next.reshape(-1).T @ (HX * dagA_res_next.reshape(-1)))
            b = sqn_dagA_res_next / sqn_dagA_res_curr
            p_next = dagA_res_next + b * p_next
            sqn_dagA_res_curr = sqn_dagA_res_next
        # monitoring
        temp_res = [None]*nFr
        for i in range(nFr):
            intermed = bmImDeform(Tu[i], x, frSize, K_bump)
            temp_res[i] = y[i] - bmShanna(intermed, Gu[i], KFC, frSize, 'MATLAB')
        R = 0
        for i in range(nFr):
            R += np.real(temp_res[i].reshape(-1).T @ (HY[i].reshape(-1) * temp_res[i].reshape(-1)))
        witnessInfo.param[7][0, c] = R
        witnessInfo.watch(c, x, frSize, 'loop')
    witnessInfo.watch(nIter-1, x, frSize, 'final')
    x = bmBlockReshape(x, frSize)
    return x
