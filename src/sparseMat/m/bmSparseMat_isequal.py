import numpy as np
from src.arrayUtility import bmBlockReshape

def bmSparseMat_isequal(s, t):
    """
    Compare two sparse matrix structures for equality.

    Parameters
    ----------
    s : object or dict
        First sparse matrix structure.
    t : object or dict
        Second sparse matrix structure.

    Returns
    -------
    bool
        True if all relevant fields are equal, False otherwise.
    """
    fields = [
        "r_size",
        "r_ind",
        "r_jump",
        "r_nJump",
        "m_val",
        "l_size",
        "l_ind",
        "l_jump",
        "l_nJump",
        "nBlock",
        "block_length",
        "l_block_start",
        "m_block_start",
        "N_u",
        "d_u",
        "kernel_type",
        "nWin",
        "kernelParam",
        "block_type",
        "type",
        "l_squeeze_flag",
        "check_flag",
    ]

    for field in fields:
        # Retrieve value from s
        if hasattr(s, field):
            val_s = getattr(s, field)
        elif isinstance(s, dict):
            val_s = s.get(field)
        else:
            return False

        # Retrieve value from t
        if hasattr(t, field):
            val_t = getattr(t, field)
        elif isinstance(t, dict):
            val_t = t.get(field)
        else:
            return False

        # Compare values
        if isinstance(val_s, np.ndarray) and isinstance(val_t, np.ndarray):
            if not np.array_equal(val_s, val_t):
                return False
        else:
            if val_s != val_t:
                return False

    return True
