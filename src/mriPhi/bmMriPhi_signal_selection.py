from src.fourierN.bmDFT import bmDFT
from third_part.matlab_compat.matlab_native import repmat
import numpy as np
from src.arrayUtility.bmBlockReshape import bmBlockReshape
from src.fourierN.bmIDF import bmIDF

def unknown_function():
    t_ref, nu_ref, lowPass_filter, bandPass_filter = local_variables  # Assuming these variables are passed to the function

    lowPass_filter = repmat(lowPass_filter, [np.shape(s, 1), 1])
    bandPass_filter = repmat(bandPass_filter, [np.shape(s, 1), 1])
    nSignal = np.shape(s, 1)
    nSignal_to_select = min([nSignal, local_variables[4]])

    Fs = bmDFT(s, t_ref, [], 2, 2)

    s_lowPass = np.real(bmIDF(lowPass_filter * Fs, nu_ref, [], 2, 2))
    s_bandPass = np.real(bmIDF(bandPass_filter * Fs, nu_ref, [], 2, 2))

    myDiff = np.abs(s_lowPass - s)
    myStd = np.zeros((nSignal, 1))
    for i in range(nSignal):
        myStd[i] = np.std(myDiff[i, :])

    myRms = np.sqrt(np.mean(np.abs(s_bandPass)**2, axis=1))
    myScore = myStd / myRms

    perm = np.argsort(myScore)
    s_lowPass = s_lowPass[perm, :]
    s_lowPass = s_lowPass[:nSignal_to_select, :]
    s_bandPass = s_bandPass[perm, :]
    s_bandPass = s_bandPass[:nSignal_to_select, :]

    return s_lowPass, s_bandPass

def bmMriPhi_signal_selection(s, t_ref, nu_ref, lowPass_filter, bandPass_filter, nSignal_to_select):
    local_variables = [t_ref, nu_ref, lowPass_filter, bandPass_filter, nSignal_to_select]  # Assuming these variables are passed to the function
    return unknown_function()
