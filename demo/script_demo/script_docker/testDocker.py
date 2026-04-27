# src/arrayUtility/bmBlockReshape.py
import numpy as np

def bmBlockReshape(block, block_size, num_blocks, reshape_type=None):
    """
    Reshape a 2-D block array into a collection of sub-blocks or back into the original array.
    
    Parameters
    ----------
    block : ndarray
        Input array.
    block_size : tuple of int
        Size of each block (rows, cols).
    num_blocks : tuple of int
        Number of blocks in each dimension (rows, cols).
    reshape_type : str, optional
        If 'reshape_to', reshape the block into a 4-D array of shape
        (num_blocks[0], num_blocks[1], block_size[0], block_size[1]).
        If 'reshape_from', perform the inverse operation.
    
    Returns
    -------
    ndarray
        Reshaped array.
    """
    # Default behavior: simply reshape into the block grid.
    if reshape_type is None or reshape_type == "reshape_to":
        return block.reshape(num_blocks[0], num_blocks[1], block_size[0], block_size[1])
    elif reshape_type == "reshape_from":
        return block.reshape(num_blocks[0] * block_size[0], num_blocks[1] * block_size[1])
    else:
        raise ValueError(f"Unknown reshape_type '{reshape_type}'")

# Auto-generated entrypoint alias for import compatibility
testDocker = bmBlockReshape
