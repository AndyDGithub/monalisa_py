import numpy as np

# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023


def bmRotation2(phi):
    R = np.array(
        [
            [np.cos(phi), -np.sin(phi)],
            [np.sin(phi), np.cos(phi)],
        ]
    )
    return R
