from __future__ import annotations
from porting.lib.utils import errordlg


def bmCheckFile(argFile, dlgFlag):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: out = 1;
    # MATLAB: if not(exist(argFile,'file')==2)
    # MATLAB: out = 0;
    # MATLAB: if dlgFlag
    # MATLAB: errordlg('File does not exist');
    # MATLAB: end
    # MATLAB: end
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    out = None
    return out
