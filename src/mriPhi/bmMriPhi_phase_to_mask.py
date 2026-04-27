from __future__ import annotations
from third_part.matlab_compat.matlab_native import plot, repmat, size


def bmMriPhi_phase_to_mask(phi, nPhase, argPercent):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: phi = phi(:).';
    # MATLAB: nPt = size(phi(:), 1);
    # MATLAB: c = (0:nPhase-1)/nPhase;
    # MATLAB: w = argPercent*2*pi/nPhase/2;
    # MATLAB: psi = complex(cos(phi),    sin(phi)   );
    # MATLAB: c   = complex(cos(c*2*pi), sin(c*2*pi));
    # MATLAB: c = repmat(c(:), [1, nPt]);
    # MATLAB: myMask  = false(nPhase, nPt);
    # MATLAB: for i   = 1:nPhase
    # MATLAB: myMask(i, :) = abs(angle(psi./c(i, :))) <= w;
    # MATLAB: end
    # MATLAB: figure
    # MATLAB: hold on
    # MATLAB: t = 1:size(phi, 2);
    # MATLAB: for i = 1:nPhase
    # MATLAB: temp_mask   = myMask(i, :);
    # MATLAB: temp_t      = t(1, temp_mask);
    # MATLAB: temp_phi    = phi(1, temp_mask);
    # MATLAB: plot(temp_t, temp_phi, '.');
    # MATLAB: end
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    myMask = None
    return myMask
