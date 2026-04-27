from src.arrayUtility.bmBlockReshape import bmBlockReshape
import numpy as np

def bmImDeformField_hardThresholding3(v, n_u, argTh):
    myEps = 1e-4;  # ------------------------------------------------------------- magic_number

    if argTh <= myEps:
        raise ValueError('The input threshold is smaller than the chosen machine epsilon. It does not make sense.')
        return

    argSize = np.shape(v)
    v = bmBlockReshape(v, n_u)

    v_norm = np.sqrt(np.sum(v**2, axis=3))
    m = (v_norm > argTh)
    m = np.repeat(m[..., None], 3, axis=3)

    eps_mask = (v_norm <= myEps)
    v_norm[eps_mask] = 1

    v_norm = np.repeat(v_norm[..., None], 3, axis=3)
    v_normalized = argTh * v / v_norm

    m_neg = ~m
    w = v * m_neg + v_normalized * m

    return np.reshape(w, argSize)
