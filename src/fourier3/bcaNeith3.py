def isKern(kern):
    """Return True if ``kern`` contains three strictly >1 odd integers."""
    values = np.asarray(kern, dtype=int).reshape(-1)
    if values.size != 3:
        return False
    if np.any(values <= 1):
        return False
    return bool(np.all(((values - 1) % 2) == 0))

def bcaNeith3(kspace, calib, kern):
    """Convenience wrapper that forwards to MATLABGrappa."""
    return MATLABGrappa(kspace, calib, kern)
