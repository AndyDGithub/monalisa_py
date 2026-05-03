import numpy as np
from src.function1.bmSinc import bmSinc

def bmFourierOfLittleDoor_function(k, L, a):
    """Compute the Fourier transform of a little door function.

    Parameters:
        k (np.ndarray): The input frequencies.
        L (float): The width parameter.
        a (float): The phase shift parameter.

    Returns:
        Ff (np.ndarray): The Fourier transform result.
    """
    Ff = bmSinc(L * np.pi * k) * np.exp(-1j * 2 * np.pi * a * k)
    return Ff
