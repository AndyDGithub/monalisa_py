from src.geom123 import bmTraj

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Minimal stub for the third_part.matlab_compat.matlab_native module.
# It supplies the names expected by `bmDicomLoad`.
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
third_part = types.ModuleType("third_part")
matlab_compat = types.ModuleType("third_part.matlab_compat")
matlab_native = types.ModuleType("third_part.matlab_compat.matlab_native")

def _isempty(x):
    """Placeholder for MATLAB's isempty."""
    return not bool(x)

def _length(x):
    """Placeholder for MATLAB's length."""
    return len(x)

def _size(x):
    """Placeholder for MATLAB's size."""
    return np.array(x).shape

def _s(x):
    """Placeholder for MATLAB's s."""
    return x

matlab_native.isempty = _isempty
matlab_native.length = _length
matlab_native.size = _size
matlab_native.s = _s

third_part.matlab_compat = matlab_compat
matlab_compat.matlab_native = matlab_native
sys.modules["third_part"] = third_part
sys.modules["third_part.matlab_compat"] = matlab_compat
sys.modules["third_part.matlab_compat.matlab_native"] = matlab_native

# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# bmSensitivaDuoMorphosia_chain
# ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def bmSensitivaDuoMorphosia_chain(
    x,
    y,
    ve,
    C,
    Gu,
    Gut,
    frSize,
    Tu1,
    Tu1t,
    Tu2,
    Tu2t,
    delta,
    regul_mode,
    nCGD,
    ve_max,
    nIter,
    witnessInfo,
):
    """
    Minimal placeholder for MATLAB function `bmSensitivaDuoMorphosia_chain`
`bmSensitivaDuoMorphosia_chain`
`bmSensitivaDuoMorphosia_chain`.

    The original implementation performs a complex ADMM reconstruction.
    For test purposes, this function simply reshapes the input image `x`
    to the desired frame size using the already ported `bmBlockReshape`
    helper.
    """
    return bmBlockReshape(x, frSize)
