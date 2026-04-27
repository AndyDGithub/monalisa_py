import numpy as np
from scipy.special import iv  # Equivalent to MATLAB's besseli(0, y)

def bmKaiser(x, alpha, tau):
    I0alpha = iv(0, alpha)
    y = max(1 - (x / tau) ** 2, 0)
    y *= np.sqrt(y) * alpha
    y /= I0alpha
    return y
