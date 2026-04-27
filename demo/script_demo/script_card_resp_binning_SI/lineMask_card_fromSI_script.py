from src.mriPhi.bmMriPhi_fromSI_rmsSI import bmMriPhi_fromSI_rmsSI
from src.mriPhi.bmMriPhi_phase_to_mask import bmMriPhi_phase_to_mask
from src.mriPhi.bmMriPhi_signalList_to_phase import bmMriPhi_signalList_to_phase
import numpy as np
from third_part.twix_for_monalisa.bmTwix_getFirstProjOfShot import bmTwix_getFirstProjOfShot

from src.mriPhi.bmMriPhi_fromSI_collect_signal_list import bmMriPhi_fromSI_collect_signal_list
from src.mriPhi.bmMriPhi_fromSI_get_standart_reference_signal import bmMriPhi_fromSI_get_standart_reference_signal
from src.mriPhi.bmMriPhi_fromSI_standartSignal_to_reformatedSignal import bmMriPhi_fromSI_standartSignal_to_reformatedSignal
from src.mriPhi.bmMriPhi_graphical_frequency_selector import bmMriPhi_graphical_frequency_selector


class bmMriAcquisitionParam:
    def __init__(self):
        self.nCh = 0
        self.N = 0
        self.nSeg = 0
        self.nShot = 0
        self.nLine = 0
        self.nPt = 0


def lineMask_card_fromSI_script():
    filter_type = "bandPass"  # 'lowPass' for resp. binning or 'bandPass' for card. binning
    nMask = 20  # Should be adapted to heart_rate.
    maskWidth = 1
    nSignal_to_select = 20  # 1 manually, untrended, selected signal for resp. binning
    # 15 to 25 for card. binning.
    signal_exploration_level = "medium"  # 'light', 'medium' or 'heavy'

    p = bmMriAcquisitionParam()
    p.nCh = 42
    p.N = 480
    p.nSeg = 22
    p.nShot = 652
    p.nLine = p.nSeg * p.nShot
    p.nPt = p.N * p.nLine

    reconDir = "/Users/cag/Documents/Dataset/datasets/251114/exploreGradSp/"
    f = [reconDir, "meas_MID00367_FID11419_yiwei_grad0.dat"]
    SI = bmTwix_getFirstProjOfShot(f, p)

    # extract the SI projection from the raw data in Twix
    # bmIDF: from k-space to image space --> SI
    # % getting rmsSI from SI
    rmsSI = bmMriPhi_fromSI_rmsSI(SI, p.nCh, p.N, p.nShot)

    # normalized RMS of SI across nCh
    # % getting standart_reference_signal from SI
    t_ref, Fs_ref, nu_ref, imNav, ind_shot_min, ind_shot_max, ind_SI_min, ind_SI_max = bmMriPhi_fromSI_get_standart_reference_signal(rmsSI, p.nCh, p.N, p.nSeg, p.nShot)

    # graphical frequency selector
    s_ref_lowPass, s_ref_bandPass, lowPass_filter, bandPass_filter = bmMriPhi_graphical_frequency_selector(t_ref, Fs_ref, nu_ref, imNav)

    # reformated_signal_ref
    check_image = rmsSI[ind_SI_min:ind_SI_max, :]
    reformated_signal_ref = bmMriPhi_fromSI_standartSignal_to_reformatedSignal(s_ref_bandPass, p.nSeg, p.nShot, ind_shot_min, ind_shot_max, check_image)

    # extracting reformated_signal_list from SI
    if nSignal_to_select > 1:
        reformated_signal_list = bmMriPhi_fromSI_collect_signal_list(filter_type, t_ref, nu_ref, SI, lowPass_filter, bandPass_filter, p.nCh, p.N, p.nSeg, p.nShot, nSignal_to_select - 1, signal_exploration_level, ind_shot_min, ind_shot_max, ind_SI_min, ind_SI_max)
    else:
        reformated_signal_list = []
        reformated_signal_list.append(reformated_signal_ref)

    # % computing card phase
    cardPhase, cardPhase_list = bmMriPhi_signalList_to_phase(np.array(reformated_signal_list))

    # % mask_construction
    cMask = bmMriPhi_phase_to_mask(cardPhase, nMask, maskWidth)
