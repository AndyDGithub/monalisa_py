import numpy as np
from src.function1.bmSinc import bmSinc


def bmFourierOfLittleDoor_function(k, L, a):
    Ff = bmSinc(L * np.pi * k) * np.exp(-1j * 2 * np.pi * a * k)
    return Ff
