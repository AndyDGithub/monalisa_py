from __future__ import annotations
from third_part.matlab_compat.matlab_native import size
from porting.lib.utils import ndims, size


def bmNanColor(argImage):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: if ndims(argImage) > 3
    # MATLAB: error('Wrong list of arguments');
    # MATLAB: elseif ndims(argImage) == 3
    # MATLAB: myImage = argImage(:,:,1);
    # MATLAB: else
    # MATLAB: myImage = argImage;
    # MATLAB: end
    # MATLAB: myZero = zeros(size(myImage));
    # MATLAB: myNan = isnan(myImage);
    # MATLAB: myNanColor = cat(3, myZero, myZero, myNan/1.7);
    # MATLAB: myImage(isnan(myImage)) = 0;
    # MATLAB: myImage = myImage-min(myImage(:));
    # MATLAB: myImage = myImage/max(myImage(:));
    # MATLAB: myCImage = cat(3, myImage, myImage, myImage)+ myNanColor;
    # MATLAB: figure
    # MATLAB: image(myCImage);
    # MATLAB: axis image
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    return None
