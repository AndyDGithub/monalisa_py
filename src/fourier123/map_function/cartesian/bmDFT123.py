import numpy as np
from src.fourier1.bmDFT1 import bmDFT1
from src.fourier2.bmDFT2 import bmDFT2
from src.fourier3.bmDFT3 import bmDFT3


def bmDFT123(x, N_u, dK_u):
    n = np.size(N_u)
    if n == 1:
        return bmDFT1(x, N_u, dK_u)
    elif n == 2:
        return bmDFT2(x, N_u, dK_u)
    elif n == 3:
        return bmDFT3(x, N_u, dK_u)
    else:
        raise ValueError(f"Unsupported N_u size: {n}. Expected 1, 2, or 3.")
