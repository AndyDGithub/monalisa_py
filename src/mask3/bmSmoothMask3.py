from __future__ import annotations
from third_part.matlab_compat.matlab_native import length, permute, roipoly, size


def bmSmoothMask3(argMask, nPixFilter):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: myMask = argMask;
    # MATLAB: for i = 1:size(myMask, 3)
    # MATLAB: temp_mask = myMask(:, :, i);
    # MATLAB: temp_bound = bwboundaries(temp_mask);
    # MATLAB: if size(temp_bound) > 0
    # MATLAB: sum_mask = false(size(temp_mask));
    # MATLAB: for j = 1:length(temp_bound)
    # MATLAB: temp_bound_j = temp_bound{j};
    # MATLAB: x = temp_bound_j(: ,2);
    # MATLAB: y = temp_bound_j(:, 1);
    # MATLAB: x = bmImBumpFiltering1(x, nPixFilter);
    # MATLAB: y = bmImBumpFiltering1(y, nPixFilter);
    # MATLAB: sum_mask = sum_mask | roipoly(temp_mask, x, y);
    # MATLAB: end
    # MATLAB: myMask(:, :, i) = sum_mask;
    # MATLAB: end
    # MATLAB: end
    # MATLAB: myMask = permute(myMask, [3, 1, 2]);
    # MATLAB: for i = 1:size(myMask, 3)
    # MATLAB: temp_mask = myMask(:, :, i);
    # MATLAB: temp_bound = bwboundaries(temp_mask);
    # MATLAB: if size(temp_bound) > 0
    # MATLAB: sum_mask = false(size(temp_mask));
    # MATLAB: for j = 1:length(temp_bound)
    # MATLAB: temp_bound_j = temp_bound{j};
    # MATLAB: x = temp_bound_j(: ,2);
    # MATLAB: y = temp_bound_j(:, 1);
    # MATLAB: x = bmImBumpFiltering1(x, nPixFilter);
    # MATLAB: y = bmImBumpFiltering1(y, nPixFilter);
    # MATLAB: sum_mask = sum_mask | roipoly(temp_mask, x, y);
    # MATLAB: end
    # MATLAB: myMask(:, :, i) = sum_mask;
    # MATLAB: end
    # MATLAB: end
    # MATLAB: myMask = permute(myMask, [2, 3, 1]);
    # MATLAB: myMask = permute(myMask, [2, 3, 1]);
    # MATLAB: for i = 1:size(myMask, 3)
    # MATLAB: temp_mask = myMask(:, :, i);
    # MATLAB: temp_bound = bwboundaries(temp_mask);
    # MATLAB: if size(temp_bound) > 0
    # MATLAB: sum_mask = false(size(temp_mask));
    # MATLAB: for j = 1:length(temp_bound)
    # MATLAB: temp_bound_j = temp_bound{j};
    # MATLAB: x = temp_bound_j(: ,2);
    # MATLAB: y = temp_bound_j(:, 1);
    # MATLAB: x = bmImBumpFiltering1(x, nPixFilter);
    # MATLAB: y = bmImBumpFiltering1(y, nPixFilter);
    # MATLAB: sum_mask = sum_mask | roipoly(temp_mask, x, y);
    # MATLAB: end
    # MATLAB: myMask(:, :, i) = sum_mask;
    # MATLAB: end
    # MATLAB: end
    # MATLAB: myMask = permute(myMask, [3, 1, 2]);
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    myMask = None
    return myMask
