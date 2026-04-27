from __future__ import annotations
from third_part.matlab_compat.matlab_native import length


def bmDirList(argDir, recursive_flag):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # This function return a list of dir (not names), only of directories.
    # recursive_flag must be true for reccursive.
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: if not(bmCheckDir(argDir, false))
    # MATLAB: out = [];
    # MATLAB: return;
    # MATLAB: end
    # MATLAB: myList = dir(argDir);
    # MATLAB: myList = myList(3:end);
    # MATLAB: N = 0;
    # MATLAB: for i = 1:length(myList)
    # MATLAB: temp_dir = [argDir, '/', myList(i).name];
    # MATLAB: if bmCheckDir(temp_dir, false)
    # MATLAB: N = N + 1;
    # MATLAB: end
    # MATLAB: end
    # MATLAB: out = cell(N, 1);
    # MATLAB: myCount = 0;
    # MATLAB: for i = 1:length(myList)
    # MATLAB: temp_dir = [argDir, '/', myList(i).name];
    # MATLAB: if bmCheckDir(temp_dir, false)
    # MATLAB: myCount = myCount + 1;
    # MATLAB: out{myCount} = temp_dir;
    # MATLAB: end
    # MATLAB: end
    # MATLAB: if recursive_flag
    # MATLAB: for i = 1:N
    # MATLAB: out = cat(1, out, bmDirList(out{i}, true));
    # MATLAB: end
    # MATLAB: end
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    out = None
    return out
