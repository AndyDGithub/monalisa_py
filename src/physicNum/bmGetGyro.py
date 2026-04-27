def bmGetGyro(argString, varargin):
    # Arg string is the name of an element. Ex : 'Na' or '23Na'.
    # Varargin accepts 'Hz' or 'Rad' or nothing.
    # out = gyromagnetic_ratio in Rad Hz / T or in Hz / T.
    # varargout = [unit, element_name].

    HzFlag = False
    if len(varargin) > 0:
        if varargin[0] == 'Hz':
            HzFlag = True
        elif varargin[0] == 'Rad':
            HzFlag = False

    gyros = {
        "1H": 267.513,
        "3He": -203.789,
        "7Li": 103.962,
        "13C": 67.262,
        "19F": 251.662,
        "23Na": 70.761,
        "27Al": 69.763,
        "31P": 108.291,
        "63Cu": 71.118
    }

    out = gyros[argString]
    varargout = [None, argString]

    if HzFlag:
        out *= 10**6
        out /= (2 * 3.14159)
    else:
        out *= 10**6

    if HzFlag:
        varargout[1] = "Hz / T"
    else:
        varargout[1] = "Rad / T / s"

    return (out, varargout)
