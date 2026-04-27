from src.mriPhi.bmMriPhi_fromSI_rawPerShotSignal_to_standartSignal import bmMriPhi_fromSI_rawPerShotSignal_to_standartSignal
def bmMriPhi_fromSI_collect_signal_list(filter_type, t_ref, nu_ref, mySI, lowPass_filter, bandPass_filter, nCh, N, nSeg, nShot, nSignal_to_select, signal_exploration_level, ind_shot_min, ind_shot_max, ind_SI_min, ind_SI_max, s_reverse_flag):
    # reshape mySI
    mySI = np.reshape(mySI, (nCh, N, nShot))
    # crop SI columns
    mySI = mySI[:, ind_SI_min:ind_SI_max+1, :]  # inclusive
    N_croped = mySI.shape[1]
    s_list = []
    # heavy exploration
    if signal_exploration_level == 'heavy':
        temp_s = np.reshape(mySI, (nCh * N_croped, nShot))
        s_list.append(np.real(temp_s))
        s_list.append(np.imag(temp_s))
        s_list.append(np.abs(temp_s))
    # always collect signals
    # sum over N (axis=1)
    temp_s = np.sum(mySI, axis=1)  # shape [nCh, nShot]
    s_list.append(np.real(temp_s))
    s_list.append(np.imag(temp_s))
    s_list.append(np.abs(temp_s))
    # sum abs over N
    temp_s_abs = np.sum(np.abs(mySI), axis=1)  # shape [nCh, nShot]
    s_list.append(np.abs(temp_s_abs))
    # sum over channel (axis=0)
    temp_s = np.sum(mySI, axis=0)  # shape [N_croped, nShot]
    s_list.append(np.real(temp_s))
    s_list.append(np.imag(temp_s))
    s_list.append(np.abs(temp_s))
    # sum abs over channel
    temp_s_abs2 = np.sum(np.abs(mySI), axis=0)  # shape [N_croped, nShot]
    s_list.append(np.abs(temp_s_abs2))
    # sum over all channels N and N_croped flattened
    temp_s = np.reshape(mySI, (nCh * N_croped, nShot))
    temp_s = np.sum(temp_s, axis=0)  # shape [nShot]
    s_list.append(np.real(temp_s))
    s_list.append(np.imag(temp_s))
    s_list.append(np.abs(temp_s))
    # sum abs over all flattened
    temp_s_abs3 = np.reshape(mySI, (nCh * N_croped, nShot))
    temp_s_abs3 = np.sum(np.abs(temp_s_abs3), axis=0)
    s_list.append(np.abs(temp_s_abs3))
    # convert list to array
    s = np.vstack(s_list)
    # exploration level
    if signal_exploration_level == 'leight':
        s = s[:100]
    elif signal_exploration_level == 'medium':
        # nothing
        pass
    # reverse
    if s_reverse_flag:
        s = -s
    # convert to standard signal
    # need to use bmMriPhi_fromSI_rawPerShotSignal_to_standartSignal
    s = bmMriPhi_fromSI_rawPerShotSignal_to_standartSignal(s, nSeg, nShot, ind_shot_min, ind_shot_max)
    # select filter
    if filter_type == 'lowPass':
        s_filtered = bmMriPhi_fromSI_rawPerShotSignal_to_standartSignal(s, nSeg, nShot, ind_shot_min, ind_shot_max)
        # Wait, we already applied conversion above. Actually need to call conversion first, then signal selection.
