# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

import numpy as np

def bmGetGyro(argString, *varargin):
    """
    Compute the gyromagnetic ratio for a given element.

    Parameters
    ----------
    argString : str
        Element symbol or isotope notation (e.g., 'Na', '23Na').
    varargin : tuple, optional
        First element can be 'Hz' or 'Rad' to specify output unit.
        If omitted, defaults to 'Rad'.

    Returns
    -------
    out : float
        Gyromagnetic ratio in the requested unit (Hz/T or Rad/T/s).
    varargout : list
        List containing unit string and element name.
    """
    # Determine unit flag: Hz or Rad
    HzFlag = False
    if varargin:
        unit = varargin[0]
        if unit == 'Hz':
            HzFlag = True
        elif unit == 'Rad':
            HzFlag = False

    gyros = {
        '1H': (267.513, '1H'),
        'H': (267.513, '1H'),
        '3He': (-203.789, '3He'),
        'He': (-203.789, '3He'),
        '7Li': (103.962, '7Li'),
        'Li': (103.962, '7Li'),
        '13C': (67.262, '13C'),
        'C': (67.262, '13C'),
        '19F': (251.662, '19F'),
        'F': (251.662, '19F'),
        '23Na': (70.761, '23Na'),
        'Na': (70.761, '23Na'),
        '27Al': (69.763, '27Al'),
        'Al': (69.763, '27Al'),
        '31P': (108.291, '31P'),
        'P': (108.291, '31P'),
        '63Cu': (71.118, '63Cu'),
        'Cu': (71.118, '63Cu')
    }

    if argString not in gyros:
        raise ValueError('Wrong list of arguments.')

    base_value, element_name = gyros[argString]
    out = base_value * 1e6
    if HzFlag:
        out = out / (2 * np.pi)

    unit_str = 'Hz / T' if HzFlag else 'Rad / T / s'
    varargout = [unit_str, element_name]
    return out, varargout
