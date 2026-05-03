from src.geom123 import bmTraj

def bcaNeith_interpolatorExtraction3(calib, kern_types, kernel):
    """
    Compatibility wrapper for MATLAB's ``InterpolatorExtraction``.
    """
    return InterpolatorExtraction(calib, kern_types, kernel)
