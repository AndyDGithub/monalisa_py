from src.arrayUtility.bmColReshape import bmColReshape
from src.arrayUtility.bmPointReshape import bmPointReshape
from numpy import exp, reshape

def bmFourierModulation(y, t, x_shift):
    t = bmPointReshape(t)
    nPt = np.shape(t)[1]
    y = bmColReshape(y, nPt)
    nCh = np.shape(y)[0]
    myExp       = exp(-1j*2*np.pi*x_shift*t)
    myExp       = reshape(myExp, [nCh, 1]) * np.ones((1, nCh))
    return reshape(y * myExp, np.shape(y))
