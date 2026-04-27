from src.image123.bmImDFT import bmImDFT
from src.image123.bmImIDF import bmImIDF
import numpy as np


def bmImConv_fourier(a, b):
    a = a.ravel()
    b = b.ravel()

    Fa = bmImDFT(a)
    Fb = bmImDFT(b)

    out = bmImIDF(Fa * Fb)  # TODO(matlab-line): out = Fa.*Fb;

    return out
