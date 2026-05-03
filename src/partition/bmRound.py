import numpy as np

def bmRound(x, *args):
    """
    Round values to the closest integer or to a custom grid.
    
    Parameters
    ----------
    x : array_like
        Values to round.
    *args : tuple
        Optional grid of values to round to. Only the first element of args
args
        is used if provided.
    
    Returns
    -------
    ndarray
        Rounded values with the same shape as the input `x`.
    """
    arr = np.asarray(x)
    if not args:
        return np.round(arr)
    grid = np.asarray(args[0])
    if grid.size == 0:
        return np.round(arr)
    # Ensure grid is sorted
    grid_sorted = np.sort(grid.ravel())
    # Flatten input for vectorized operation
    flat = arr.ravel()
    # Compute absolute differences between each input value and grid
    diff = np.abs(grid_sorted[:, None] - flat[None, :])
    # Find index of minimum difference for each element
    idx = np.argmin(diff, axis=0)
    # Map to nearest grid value
    rounded = grid_sorted[idx]
    return rounded.reshape(arr.shape)
