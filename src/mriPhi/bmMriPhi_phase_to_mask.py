import numpy as np
import matplotlib.pyplot as plt

def bmMriPhi_phase_to_mask(phi, nPhase, argPercent):
    """
    Convert phase data to a mask based on given parameters.
    
    Parameters:
    phi (np.ndarray): 1D array of phase values.
    nPhase (int): Number of phases.
    argPercent (float): Percentage of the angular range to consider for eac
each phase.
    
    Returns:
    myMask (np.ndarray): Boolean 2D mask indicating which points belong to 
each phase.
    """
    # Ensure phi is a column vector
    phi = phi[:, np.newaxis]
    
    # Number of points in phi
    nPt = phi.shape[0]
    
    # Create the phase angles c
    c = (np.arange(nPhase) / nPhase) * 2 * np.pi
    
    # Calculate the angular width for each phase
    w = argPercent * 2 * np.pi / nPhase / 2
    
    # Convert phi and c to complex numbers
    psi = np.exp(1j * phi)
    c = np.exp(1j * c[:, None])
    
    # Initialize the mask with False values
    myMask = np.zeros((nPhase, nPt), dtype=bool)
    
    # Create a time vector for plotting
    t = np.arange(1, phi.shape[1] + 1)
    
    # Determine which points belong to each phase
    for i in range(nPhase):
        temp_mask = np.abs(np.angle(psi / c[i, :])) <= w
        myMask[i, :] = temp_mask
        
        # Plotting the current phase
        temp_t = t[temp_mask]
        temp_phi = phi[temp_mask, :]
        plt.plot(temp_t, temp_phi, '.')
    
    # Show the plot
    plt.title('Phase Mask')
    plt.xlabel('Time')
    plt.ylabel('Phase')
    plt.show()
    
    return myMask

# Example usage:
phi = np.random.rand(100) * 2 * np.pi
nPhase = 5
argPercent = 0.1
mask = bmMriPhi_phase_to_mask(phi, nPhase, argPercent)
