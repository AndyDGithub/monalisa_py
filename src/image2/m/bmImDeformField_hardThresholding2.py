from src.arrayUtility.bmBlockReshape import bmBlockReshape
import numpy as np

def bmImDeformField_hardThresholding2(v, n_u, argTh):
    myEps = 1e-4

    if argTh <= myEps:
        raise ValueError('The input threshold is smaller than the chosen machine epsilon. It does not make sense.')
        return

    argSize = np.shape(v)
    v = bmBlockReshape(v, n_u)

    v_norm = np.sqrt(np.square(v[:, :, 0]) + np.square(v[:, :, 1]))
    m = (v_norm > argTh)
    m = np.repeat(m[..., None], 2, axis=2)

    eps_mask = (v_norm <= myEps)
    v_norm[eps_mask] = 1

    v_normalized = argTh * v / v_norm
    m_neg = ~m

    w = v * m_neg + v_normalized * m
    return np.reshape(w, argSize)
