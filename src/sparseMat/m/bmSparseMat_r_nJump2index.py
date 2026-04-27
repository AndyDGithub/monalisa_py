def bmSparseMat_r_nJump2index(r_nJump):
    r_nJump = np.array(r_nJump, dtype=np.int64)
    l_size = r_nJump.size
    out = np.repeat(np.arange(1, l_size+1), r_nJump)
    return out
