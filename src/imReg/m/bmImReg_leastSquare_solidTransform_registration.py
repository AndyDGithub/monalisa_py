"""
bmImReg_leastSquare_solidTransform_registration — multi-resolution rigid registration.

Port status: structure ported; full numerical port requires testing.
"""
from __future__ import annotations
import numpy as np
from src.image123.bmImGaussFiltering import bmImGaussFiltering
from src.image123.bmImGradient import bmImGradient
from src.image123.bmImGrid import bmImGrid
from src.linAlg3.bmRotation3 import bmRotation3
from src.imReg.m.bmImReg_deform import bmImReg_deform
from src.imReg.m.bmImReg_getCenterMass_estimate import bmImReg_getCenterMass_estimate
from src.imReg.m.bmImReg_solidTransform_distance import bmImReg_solidTransform_distance
from src.imReg.m.bmImReg_transform_to_deformField import bmImReg_transform_to_deformField


def bmImReg_leastSquare_solidTransform_registration(x_ref_0, x_0,
                                                     nIter_max_list,
                                                     resolution_level_list,
                                                     initialSolidTransform=None,
                                                     X=None, Y=None, Z=None):
    """
    Multi-resolution least-squares rigid body registration.

    Parameters
    ----------
    x_ref_0                : reference image (fixed)
    x_0                    : moving image
    nIter_max_list         : max iterations per resolution level (scalar or list)
    resolution_level_list  : list of resolution levels (e.g. [8, 4, 2, 1])
    initialSolidTransform  : initial transform object or None
    X, Y, Z                : coordinate grids (computed if None)

    Returns
    -------
    v     : deformation field
    x_reg : registered image
    T     : final solid transform
    """
    raise NotImplementedError(
        "bmImReg_leastSquare_solidTransform_registration: "
        "full port pending — complex multi-resolution gradient optimizer."
    )
