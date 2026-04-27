import numpy as np

def bmBigDoor_function(x, L, a):
    f = np.zeros(np.shape(x))
    m1 = (x - a >= -L/2)
    f[m1] = 1
    m2 = (x - a >= L/2)
    f[m2] = 0
    return f
