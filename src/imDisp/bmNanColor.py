from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

def bmNanColor(argImage):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    if argImage.ndim > 3:
        raise ValueError('Wrong list of arguments')
    elif argImage.ndim == 3:
        myImage = argImage[:, :, 0]
    else:
        myImage = argImage

    myZero = np.zeros_like(myImage)
    myNan = np.isnan(myImage)
    myNanColor = np.stack((myZero, myZero, myNan / 1.7), axis=-1)
    myImage[myNan] = 0
    myImage -= myImage.min()
    myImage /= myImage.max()
    myCImage = np.stack((myImage, myImage, myImage), axis=-1) + myNanColor
    
    fig, ax = plt.subplots()
    ax.imshow(myCImage)
    ax.axis('image')
    return None
