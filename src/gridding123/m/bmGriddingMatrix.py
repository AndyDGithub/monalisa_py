from __future__ import annotations
from third_part.matlab_compat.matlab_native import single
from porting.lib.utils import int32


def bmGriddingMatrix():
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # public_properties ---------------------------------------------------
    # All lists must be line vectors, not column. That means that their size
    # must be of the form [1, length(list)].
    # All sizes must be int32 excepted secrete_length which is int64.
    # All floating point values must be single precision.
    # information_param -----------------------------------------------
    # 
    # Just for keeping track of how the matrix was constructed.
    # These parameters have no funcitonal role and can be left empty.
    # END_information_param -------------------------------------------
    # END_public_properties -----------------------------------------------
    # private_properties
    # END_private_properties
    # public_method
    # END_public_method
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: classdef bmGriddingMatrix < handle
    # MATLAB: properties (Access = public)
    # MATLAB: u_ind   = int32([]);    % List of index-jumps in the pillar_values array. Vector.
    # MATLAB: w       = single([]);   % Gridding weights i.e. entries of the gridding matrix. Vector.
    # MATLAB: nPt     = int32([]);    % Number of points in the arbitrary gridd. Scalar.
    # MATLAB: Nx      = int32([]);    % Size x of the pillar gridd. Is non-zero for imDim > 0. Scalar.
    # MATLAB: Ny      = int32([]);    % Size y of the pillar gridd. Is non-zero for imDim > 1. Scalar.
    # MATLAB: Nz      = int32([]);    % Size z of the pillar gridd. Is non-zero for imDim > 2. Scalar.
    # MATLAB: secrete_length      = int64([]); % int64 !!!
    # MATLAB: N_u                 = int32([]);
    # MATLAB: d_u                 = single([]);
    # MATLAB: kernel_type         = 'void';
    # MATLAB: nWin                = int32([]);
    # MATLAB: kernelParam         = single([]);
    # MATLAB: gridding_type      = 'void';
    # MATLAB: end
    # MATLAB: properties (SetAccess = private, GetAccess = public)
    # MATLAB: end
    # MATLAB: methods
    # MATLAB: end
    # MATLAB: end % END class
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    return None
