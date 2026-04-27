from __future__ import annotations


def bmTextFile2Cell(arg_file):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: fid = fopen(arg_file, 'r');
    # MATLAB: i = 1;
    # MATLAB: current_line = fgetl(fid);
    # MATLAB: c{i} = current_line;
    # MATLAB: while ischar(current_line)
    # MATLAB: i = i+1;
    # MATLAB: current_line = fgetl(fid);
    # MATLAB: c{i} = current_line;
    # MATLAB: end
    # MATLAB: fclose(fid);
    # MATLAB: c = c(:);
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    c = None
    return c
