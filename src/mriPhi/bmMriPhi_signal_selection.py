from src.fourierN.bmDFT import bmDFT
from src.fourierN.bmIDF import bmIDF
import numpy as np


def bmMriPhi_signal_selection(s, t_ref, nu_ref, lowPass_filter, bandPass_filter, nSignal_to_select):
    nSignal = s.shape[1]
    nSignal_to_select = min(nSignal, nSignal_to_select)

    lowPass_filter = np.tile(lowPass_filter, (s.shape[1], 1))
    bandPass_filter = np.tile(bandPass_filter, (s.shape[1], 1))

    Fs = bmDFT(s, t_ref, [], 2, 2)

    s_lowPass = np.real(bmIDF(lowPass_filter * Fs, nu_ref, [], 2, 2))
    s_bandPass = np.real(bmIDF(bandPass_filter * Fs, nu_ref, [], 2, 2))

    myDiff = np.abs(s_lowPass - s)
    myStd = np.zeros((nSignal, 1))
    for i in range(nSignal):
        myStd[i] = np.std(myDiff[i, :])

    myRms = np.sqrt(np.mean(np.abs(s_bandPass) ** 2, axis=1))
    myScore = myStd.ravel() / myRms

    perm = np.argsort(myScore)
    s_lowPass = s_lowPass[perm, :]
    s_lowPass = s_lowPass[:nSignal_to_select, :]
    s_bandPass = s_bandPass[perm, :]
    s_bandPass = s_bandPass[:nSignal_to_select, :]

    return s_lowPass, s_bandPass
