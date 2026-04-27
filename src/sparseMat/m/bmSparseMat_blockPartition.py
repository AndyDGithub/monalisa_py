import numpy as np

def bmSparseMat_blockPartition(r_nJump, *varargs, nJumpPerBlock_factor, blockLengthMax_factor):
    r = np.array(r_nJump, dtype=np.int32).ravel()
    N = r.size
    # Sum <=0
    if r.sum() <= 0:
        return np.array([], dtype=np.int32), np.array([], dtype=np.int32), True
    # 'one' vararg
    if varargs and varargs[0] == 'one':
        starts = np.array([0], dtype=np.int32)
        lengths = np.array([N], dtype=np.int32)
        zero_block_flag = False
        return starts, lengths, zero_block_flag
    l_nJump = N
    r_nJump_max = r.max()
    nJumpPerBlock = int(np.fix(nJumpPerBlock_factor * r_nJump_max) + 1)
    block_length_max = int(np.fix(blockLengthMax_factor * r_nJump_max))
    starts = []
    lengths = []
    current_l_block_start = 0
    while current_l_block_start < l_nJump:
        # Determine block length
        current_block_length = 1
        ind_next = current_l_block_start + 1
        if ind_next < l_nJump:
            current_nJump_2 = r[current_l_block_start]  # first element of block
            while ind_next < l_nJump:
                current_nJump_1 = current_nJump_2
                current_nJump_2 = current_nJump_1 + r[ind_next]
                if (current_nJump_2 < nJumpPerBlock) and (current_block_length < block_length_max):
                    current_block_length += 1
                    ind_next += 1
                else:
                    break
        starts.append(current_l_block_start)
        lengths.append(current_block_length)
        current_l_block_start = current_l_block_start + current_block_length
    # Convert to int32
    starts_arr = np.array(starts, dtype=np.int32)
    lengths_arr = np.array(lengths, dtype=np.int32)
    # Determine zero_block_flag
    zero_block_flag = False
    # Check last block sum
    if len(starts) > 0:
        last_start = starts[-1]
        last_sum = r[last_start: last_start + lengths[-1]].sum()
        if last_sum <= 0:
            zero_block_flag = True
    return starts_arr, lengths_arr, zero_block_flag
