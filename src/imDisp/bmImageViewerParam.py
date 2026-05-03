from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np


@dataclass
class bmImageViewerParam:
    """Parameters used to create and manage an interactive figure that
    visualizes data as an image.

    Authors:
        Bastien Milani
        CHUV and UNIL
        Lausanne - Switzerland
        May 2023

    Contributors:
        Dominik Helbing (Documentation)
        MattechLab 2024

    Parameters
    ----------
    argIn : bmImageViewerParam or int
        Either an existing instance to copy, or an integer (2-5) indicating
        the number of image dimensions.
    argIm : np.ndarray, optional
        The image data to be displayed.  Required when ``argIn`` is an int.
    """

    class_type: str = field(default="bmImageViewerParam", init=False)

    imDim: Optional[int] = None
    imSize: Optional[np.ndarray] = None

    numOfImages: Optional[int] = None
    curImNum: Optional[int] = None

    numOfImages_4: Optional[int] = None
    curImNum_4: Optional[int] = None

    numOfImages_5: Optional[int] = None
    curImNum_5: Optional[int] = None

    permutation: Optional[list] = None

    transpose_flag: bool = False
    reverse_flag: bool = False
    mirror_flag: bool = False

    point_A: Optional[np.ndarray] = None
    point_B: Optional[np.ndarray] = None
    point_C: Optional[np.ndarray] = None

    psi: Optional[float] = None
    theta: Optional[float] = None
    phi: Optional[float] = None

    rotation: Optional[np.ndarray] = None

    colorLimits: Optional[list] = None
    colorLimits_0: Optional[list] = None

    point_list: Optional[list] = None

    def __init__(self, argIn, argIm: Optional[np.ndarray] = None) -> None:
        self.class_type = "bmImageViewerParam"

        if isinstance(argIn, bmImageViewerParam):
            src = argIn
            self.imDim = src.imDim
            self.imSize = src.imSize
            self.permutation = src.permutation
            self.transpose_flag = src.transpose_flag
            self.psi = src.psi
            self.theta = src.theta
            self.phi = src.phi
            self.point_A = src.point_A
            self.point_B = src.point_B
            self.point_C = src.point_C
            self.rotation = src.rotation
            self.reverse_flag = src.reverse_flag
            self.mirror_flag = src.mirror_flag
            self.numOfImages = src.numOfImages
            self.curImNum = src.curImNum
            self.colorLimits = src.colorLimits
            self.colorLimits_0 = src.colorLimits_0
            self.numOfImages_4 = src.numOfImages_4
            self.curImNum_4 = src.curImNum_4
            self.numOfImages_5 = src.numOfImages_5
            self.curImNum_5 = src.curImNum_5
            self.point_list = src.point_list
        else:
            if argIm is None:
                raise ValueError("argIm is required when argIn is an integer.")
            argIm = np.asarray(argIm)
            self.imSize = np.array(argIm.shape, dtype=int)
            self.imDim = self.imSize.size
            self.permutation = None
            self.psi = None
            self.theta = None
            self.phi = None
            self.point_A = None
            self.point_B = None
            self.point_C = None
            self.rotation = None
            self.transpose_flag = False
            self.reverse_flag = False
            self.mirror_flag = False
            self.numOfImages = None
            self.curImNum = None
            flat = argIm.ravel()
            mn, mx = float(flat.min()), float(flat.max())
            if mn < mx:
                self.colorLimits = [mn, mx]
            else:
                self.colorLimits = [0.0, 1.0]
            self.colorLimits_0 = list(self.colorLimits)
            self.numOfImages_4 = None
            self.curImNum_4 = None
            self.numOfImages_5 = None
            self.curImNum_5 = None
            self.point_list = None

            if argIn == 2:
                self.psi = 0.0
                self.rotation = np.eye(2)

            elif argIn == 3:
                self.permutation = [1, 2, 3]
                self.psi = 0.0
                self.theta = 0.0
                self.phi = 0.0
                self.rotation = np.eye(3)
                self.numOfImages = int(self.imSize[2])
                self.curImNum = max(1, int(self.numOfImages // 2))

            elif argIn == 4:
                self.imSize = self.imSize[:3]
                self.permutation = [1, 2, 3]
                self.psi = 0.0
                self.theta = 0.0
                self.phi = 0.0
                self.rotation = np.eye(3)
                self.numOfImages = int(self.imSize[2])
                self.curImNum = max(1, int(self.numOfImages // 2))
                self.numOfImages_4 = int(argIm.shape[3])
                self.curImNum_4 = 1
                self.point_list = [[None] for _ in range(self.numOfImages_4)]

            elif argIn == 5:
                self.imSize = self.imSize[:3]
                self.permutation = [1, 2, 3]
                self.psi = 0.0
                self.theta = 0.0
                self.phi = 0.0
                self.rotation = np.eye(3)
                self.numOfImages = int(self.imSize[2])
                self.curImNum = max(1, int(self.numOfImages // 2))
                self.numOfImages_4 = int(argIm.shape[3])
                self.curImNum_4 = 1
                self.numOfImages_5 = int(argIm.shape[4])
                self.curImNum_5 = 1
                self.point_list = [
                    [None] * self.numOfImages_5
                    for _ in range(self.numOfImages_4)
                ]

            else:
                raise ValueError(
                    f"argIn must be a bmImageViewerParam instance or an integer "
                    f"in {{2, 3, 4, 5}}, got {argIn!r}."
                )
