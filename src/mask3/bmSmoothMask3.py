from __future__ import annotations
import numpy as np

from third_part.matlab_compat.matlab_native import roipoly

def bmSmoothMask3(argMask: np.ndarray, nPixFilter: int) -> np.ndarray:
    """Strict deterministic baseline port from MATLAB."""
    # Ensure argMask is a 3D numpy array
    if argMask.ndim != 3:
        raise ValueError("Input mask must be a 3D array")
    
    myMask = np.zeros_like(argMask, dtype=bool)
    
    for i in range(argMask.shape[2]):
        temp_mask = argMask[:, :, i]
        temp_bound = bwboundaries(temp_mask)
        
        if len(temp_bound) > 0:
            sum_mask = np.zeros_like(temp_mask, dtype=bool)
            for j, boundary in enumerate(temp_bound):
                x = boundary[:, 1]
                y = boundary[:, 0]
                
                # Apply filtering
                x = bmImBumpFiltering1(x, nPixFilter)
                y = bmImBumpFiltering1(y, nPixFilter)
                
                sum_mask |= roipoly(temp_mask, x, y)
            
            myMask[:, :, i] = sum_mask
    
    return myMask

# Example usage
if __name__ == "__main__":
    # Example input mask (3D numpy array of boolean values)
    argMask = np.array([
        [[False, False, True],
         [True,  True, False]],
        [[True,  True, True],
         [False, False, True]]
    ], dtype=bool)
    
    nPixFilter = 1
    result_mask = bmSmoothMask3(argMask, nPixFilter)
    print(result_mask)
