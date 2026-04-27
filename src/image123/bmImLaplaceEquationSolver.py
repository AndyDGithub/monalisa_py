from src.image123.bmImLaplaceIterator import bmImLaplaceIterator
from src.image123.bmImLaplacian import bmImLaplacian
import numpy as np
from src.varargin.bmVarargin import bmVarargin
from src.image123.bmImResize import bmBlockReshape  # Import bmBlockReshape


def bmImLaplaceEquationSolver(imStart, m, nIter, L_th, varargin):
    [omp_flag, nBlockPerThread] = bmVarargin(varargin)

    m_neg       = ~m
    out         = imStart
    myCondition = True

    while myCondition:
        out = bmImLaplaceIterator(out, m, nIter, omp_flag, nBlockPerThread)

        L   = bmImLaplacian(out)

        L_squared_norm  = np.sum(np.abs(    L[m_neg]  )**2)
        im_squared_norm = np.sum(np.abs(  out[m_neg]  )**2)

        r = np.sqrt(L_squared_norm / im_squared_norm)

        myCondition = (r > L_th)

    return out
