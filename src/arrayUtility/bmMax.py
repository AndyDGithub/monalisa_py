import numpy as np


def bmMax(x):
    if isinstance(x, list) or (isinstance(x, np.ndarray) and x.dtype == object):
        if isinstance(x, np.ndarray):
            x = x.ravel()
        m_list = np.array([np.max(np.asarray(item).ravel()) for item in x])
        return np.max(m_list)
    return np.max(np.asarray(x))
