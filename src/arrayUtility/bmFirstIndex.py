import numpy as np
from typing import Any


def bmFirstIndex(argString: str, argVal: Any, argVec: np.ndarray) -> int:
    """
    Return the first 1-based index of an element in *argVec* that satisfies
satisfies a
    comparison specified by *argString*.

    Parameters
    ----------
    argString : str
        One of ``'equalTo'``, ``'smallerThan'``, ``'biggerThan'``,
        ``'smallerEqualThan'`` or ``'biggerEqualThan'``.
    argVal : scalar
        The value to compare each element of *argVec* against.
    argVec : array-like
        The vector to search.

    Returns
    -------
    int
        The 0-based index of the first matching element. If no element
        matches, returns ``len(argVec)``.
    """
    argVec = np.asarray(argVec).ravel()

    if argString == "equalTo":
        mask = argVec == argVal
    elif argString == "smallerThan":
        mask = argVec < argVal
    elif argString == "biggerThan":
        mask = argVec > argVal
    elif argString == "smallerEqualThan":
        mask = argVec <= argVal
    elif argString == "biggerEqualThan":
        mask = argVec >= argVal
    else:
        raise ValueError("Unknown comparison: " + argString)

    indices = np.where(mask)[0]
    if indices.size == 0:
        return len(argVec)
    return int(indices[0])

# ------------------------------------------------------------------
# MATLAB reference implementation (for reference)
#
# function outIndex = bmFirstIndex(argString, argVal, argVec)
# argVec = argVec(:)';
# if strcmp(argString, 'equalTo')
#     myMask = (argVec == argVal);
# elseif strcmp(argString, 'smallerThan')
#     myMask = (argVec < argVal);
# elseif strcmp(argString, 'biggerThan')
#     myMask = (argVec > argVal);
# elseif strcmp(argString, 'smallerEqualThan')
#     myMask = (argVec <= argVal);
# elseif strcmp(argString, 'biggerEqualThan')
#     myMask = (argVec >= argVal);
# end
# myIndexList = 1:length(argVec);
# myIndexList = myIndexList(myMask);
# if isempty(myIndexList)
#     outIndex = length(argVec) + 1;
# else
#     outIndex = myIndexList(1);
# end
# ------------------------------------------------------------------
