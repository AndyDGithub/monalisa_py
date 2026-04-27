from src.varargin.bmVarargin import bmVarargin
import numpy as np
from src.arrayUtility.arrayUtility import bmBlockReshape
import matplotlib.pyplot as plt


def unknown_function():
    nSeg, nShot, ind_shot_min, ind_shot_max = bmVarargin()
    s_filtered = np.array(nSeg)  # Placeholder for actual input s_filtered

    L           = int(np.shape(s_filtered)[1] / 2)
    s_mid       = s_filtered[:, :L]

    if ind_shot_min > 1:
        nLine_start = (ind_shot_min - 1)*nSeg
        s_start     = np.flip(s_mid[:, :nLine_start], axis=1)
    else:
        s_start     = []

    if ind_shot_max < nShot:
        nLine_end   = (nShot - ind_shot_max)*nSeg
        s_end       = np.flip(s_mid[:, -(nLine_end + 1):], axis=1)
    else:
        s_end       = []

    s_final = np.concatenate((s_start, s_mid, s_end), axis=1)

    argIm = bmVarargin()
    if argIm is not None:
        N           = int(np.shape(argIm)[0])

        fig = plt.figure()
        ax = fig.add_subplot(111)
        im = ax.imshow(argIm, cmap='gray')
        ax.set_ylim('auto', 'reverse')
        ax.yaxis.tick_right()
        ax.yaxis.set_label_position('right')

        x_plot = np.linspace(0, L-1, nSeg) + ind_shot_min - 1
        ax.plot(x_plot[::nSeg], N // 2 + (N // 8) * s_mid[:, ::nSeg], '.-', color='blue', markersize=15)

        x_plot = np.concatenate([np.linspace(-nLine_start, 0, nLine_start),
                                np.arange(L),
                                np.linspace(0, nLine_end, nLine_end)]) + ind_shot_min - 1
        ax.plot(x_plot[::nSeg], N // 2 + (N // 8) * s_final[:, ::nSeg], '.-', color='red')

        plt.show()


def bmMriPhi_fromSI_standartSignal_to_reformatedSignal():
    return unknown_function()
