from __future__ import annotations
from porting.lib.utils import errordlg


def bmCheckDir(argDir, dlgFlag):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: if nargin < 2
    # MATLAB: dlgFlag = true;
    # MATLAB: end
    # MATLAB: out = 1;
    # MATLAB: if isnumeric(argDir)
    # MATLAB: out = 0;
    # MATLAB: return;
    # MATLAB: end
    # MATLAB: if not(exist(argDir,'dir')==7)
    # MATLAB: out = 0;
    # MATLAB: if dlgFlag
    # MATLAB: errordlg('Directory does not exist');
    # MATLAB: end
    # MATLAB: end
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    out = None
    return out
