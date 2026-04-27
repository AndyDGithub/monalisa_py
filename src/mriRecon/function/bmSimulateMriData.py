from src.arrayUtility.bmOne import bmOne
from src.arrayUtility.bmPointReshape import bmPointReshape
def bmSimulateMriData(h, C, t, N_u, n_u, dK_u):
    if isinstance(h, (list, tuple)):
        y = [bmSimulateMriData(h_i, C, t_i, N_u, n_u, dK_u) for h_i, t_i in zip(h, t)]
        return np.array(y)
    if C is None or C.size == 0:
        C = bmOne([np.prod(n_u), 1], dtype=np.complex64)
    # Reshape h
    h = bmBlockReshape(h, n_u)
    C = bmBlockReshape(C, n_u)
    t = bmPointReshape(t, h.shape[1] if h.ndim>1 else 1)
    # rest simplified...
