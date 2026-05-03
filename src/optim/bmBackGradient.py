from __future__ import annotations

def bmBackGradient(x, n_u, dX_u):
    """Compute the back gradient of a given input."""
    from src.arrayUtility.bmZero import bmZero
    from src.optim.bmBackGradient_n import bmBackGradient_n
    
    imDim = len(n_u)
    nPt_u = np.prod(n_u)
    
    g = bmZero((nPt_u, imDim), dtype='complex_single')
    
    for n in range(imDim):
        g[:, n] = bmBackGradient_n(x, n_u, dX_u, n + 1)
    
    return g
