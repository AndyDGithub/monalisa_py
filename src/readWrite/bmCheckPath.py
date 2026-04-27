from __future__ import annotations
from porting.lib.utils import errordlg


def bmCheckPath(argPath, dlgFlag):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: if nargin < 2
    # MATLAB: dlgFlag = 1;
    # MATLAB: end
    # MATLAB: out = 1;
    # MATLAB: if not(argPath(end) == '\')
    # MATLAB: out = 0;
    # MATLAB: if dlgFlag
    # MATLAB: errordlg('Path does not exist');
    # MATLAB: end
    # MATLAB: end
    # MATLAB: argPath = argPath(1:end-1);
    # MATLAB: if not(exist(argPath,'dir')==7)
    # MATLAB: out = 0;
    # MATLAB: if dlgFlag
    # MATLAB: errordlg('Path does not exist');
    # MATLAB: end
    # MATLAB: end
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    out = None
    return out
