from src.mriPhi.bmMriPhi_fromSI_rmsSI import bmMriPhi_fromSI_rmsSI
from src.mriPhi.bmMriPhi_fromSI_get_standart_reference_signal import bmMriPhi_fromSI_get_standart_reference_signal
from src.mriPhi.bmMriPhi_fromSI_collect_signal_list import bmMriPhi_fromSI_collect_signal_list
from src.mriPhi.bmMriPhi_manually_exclude_signal_of_list import bmMriPhi_manually_exclude_signal_of_list
import numpy as np
from src.arrayUtility.bmBlockReshape import bmBlockReshape

from src.mriPhi.bmMriPhi_fromSI_standartSignal_to_reformatedSignal import bmMriPhi_fromSI_standartSignal_to_reformatedSignal
from src.mriPhi.bmMriPhi_graphical_frequency_selector import bmMriPhi_graphical_frequency_selector
from src.mriPhi.bmMriPhi_magnitude_to_mask import bmMriPhi_magnitude_to_mask


def lineMask_resp_fromSI_script():
    filter_type                 = "lowPass"  # 'lowPass' for resp. binning or   'bandPass' for card. binning
    nMask                       = 3
    maskWidth                   = 1
    nSignal_to_select           = 1;  # 1 manually, untrended, selected signal for resp. binning
    # 15 to 25 for card. binning.
    signal_exploration_level    = "leight"  # 'leight' or 'medium' or 'heavy'
    nCh                         = 30
    N                           = 384
    nSeg                        = 22
    nShot                       = 5749
    nLine                       = nSeg * nShot
    nPt                         = N * nLine

    # getting rmsSI from SI
    rmsSI = bmMriPhi_fromSI_rmsSI(SI, nCh, N, nShot)

    # getting standart_reference_signal from SI
    t_ref, Fs_ref, nu_ref, imNav, ind_shot_min, ind_shot_max, ind_SI_min, ind_SI_max = bmMriPhi_fromSI_get_standart_reference_signal(rmsSI, nCh, N, nSeg, nShot)

    # graphical frequency selector
    s_ref_lowPass, s_ref_bandPass, lowPass_filter, bandPass_filter = bmMriPhi_graphical_frequency_selector(t_ref, Fs_ref, nu_ref, imNav)

    # reformated_signal_ref
    check_image = rmsSI[ind_SI_min:ind_SI_max, :]
    reformated_signal_ref = bmMriPhi_fromSI_standartSignal_to_reformatedSignal(s_ref_lowPass, nSeg, nShot, ind_shot_min, ind_shot_max, check_image)

    # extracting reformated_signal_list from SI
    if nSignal_to_select > 1:
        reformated_signal_list = bmMriPhi_fromSI_collect_signal_list(filter_type, t_ref, nu_ref, SI, lowPass_filter, bandPass_filter, nCh, N, nSeg, nShot, nSignal_to_select - 1, signal_exploration_level, ind_shot_min, ind_shot_max, ind_SI_min, ind_SI_max)
    else:
        reformated_signal_list = [reformated_signal_ref]

    # exclude some of the signals manually
    final_signal_list = bmMriPhi_manually_exclude_signal_of_list(reformated_signal_list)

    # mask_construction
    rMask = bmMriPhi_magnitude_to_mask(final_signal_list, nMask, nSeg, nShot, ind_shot_min)
