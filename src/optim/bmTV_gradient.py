import numpy as np

def bmTV_gradient(x, N_u, dX_u):
    # Initialize g to None
    g = None
    
    # Ensure N_u and dX_u are not empty
    if len(N_u) == 0 or len(dX_u) == 0:
        raise ValueError("N_u and dX_u must not be empty")
    
    # Calculate the dimensionality of N_u
    imDim = len(N_u)
    
    # Initialize g as a complex array with zeros
    g = np.zeros_like(x, dtype=complex)
    
    if imDim == 1:
        x_real = np.real(x).reshape(-1, 1)
        x_imag = np.imag(x).reshape(-1, 1)
        
        myShift_1 = [1]
        g_real = np.roll(x_real, shift=myShift_1[0], axis=0)
        g_imag = np.roll(x_imag, shift=myShift_1[0], axis=0)
        g_real -= x_real
        g_imag -= x_imag
        g_real /= dX_u[myShift_1[0] - 1]
        g_imag /= dX_u[myShift_1[0] - 1]
        g_real[0, :] = 0
        g_imag[0, :] = 0
        
        g_real -= np.roll(g_real, shift=-myShift_1[0], axis=0)
        g_imag -= np.roll(g_imag, shift=-myShift_1[0], axis=0)
        g += g_real + 1j * g_imag
    
    elif imDim == 2:
        x_real = np.real(x).reshape(-1)
        x_imag = np.imag(x).reshape(-1)
        
        myShift_1 = [1, 0]
        myShift_2 = [0, 1]
        
        # Handle the first dimension
        g_real = np.roll(x_real, shift=myShift_1[0], axis=0)
        g_imag = np.roll(x_imag, shift=myShift_1[0], axis=0)
        g_real -= x_real
        g_imag -= x_imag
        g_real /= dX_u[myShift_1[0] - 1]
        g_imag /= dX_u[myShift_1[0] - 1]
        g_real[0, :] = 0
        g_imag[0, :] = 0
        
        g_real -= np.roll(g_real, shift=-myShift_1[0], axis=0)
        g_imag -= np.roll(g_imag, shift=-myShift_1[0], axis=0)
        g += g_real + 1j * g_imag
        
        # Handle the second dimension
        g_real = np.roll(x_real, shift=myShift_2[1], axis=1)
        g_imag = np.roll(x_imag, shift=myShift_2[1], axis=1)
        g_real -= x_real
        g_imag -= x_imag
        g_real /= dX_u[myShift_2[1] - 1]
        g_imag /= dX_u[myShift_2[1] - 1]
        g_real[:, 0] = 0
        g_imag[:, 0] = 0
        
        g_real -= np.roll(g_real, shift=-myShift_2[1], axis=1)
        g_imag -= np.roll(g_imag, shift=-myShift_2[1], axis=1)
        g += g_real + 1j * g_imag
    
    elif imDim == 3:
        x_real = np.real(x).reshape(-1)
        x_imag = np.imag(x).reshape(-1)
        
        myShift_1 = [1, 0, 0]
        myShift_2 = [0, 1, 0]
        myShift_3 = [0, 0, 1]
        
        # Handle the first dimension
        g_real = np.roll(x_real, shift=myShift_1[0], axis=0)
        g_imag = np.roll(x_imag, shift=myShift_1[0], axis=0)
        g_real -= x_real
        g_imag -= x_imag
        g_real /= dX_u[myShift_1[0] - 1]
        g_imag /= dX_u[myShift_1[0] - 1]
        g_real[0, :] = 0
        g_imag[0, :] = 0
        
        g_real -= np.roll(g_real, shift=-myShift_1[0], axis=0)
        g_imag -= np.roll(g_imag, shift=-myShift_1[0], axis=0)
        g += g_real + 1j * g_imag
        
        # Handle the second dimension
        g_real = np.roll(x_real, shift=myShift_2[1], axis=1)
        g_imag = np.roll(x_imag, shift=myShift_2[1], axis=1)
        g_real -= x_real
        g_imag -= x_imag
        g_real /= dX_u[myShift_2[1] - 1]
        g_imag /= dX_u[myShift_2[1] - 1]
        g_real[:, 0, :] = 0
        g_imag[:, 0, :] = 0
        
        g_real -= np.roll(g_real, shift=-myShift_2[1], axis=1)
        g_imag -= np.roll(g_imag, shift=-myShift_2[1], axis=1)
        g += g_real + 1j * g_imag
        
        # Handle the third dimension
        g_real = np.roll(x_real, shift=myShift_3[2], axis=2)
        g_imag = np.roll(x_imag, shift=myShift_3[2], axis=2)
        g_real -= x_real
        g_imag -= x_imag
        g_real /= dX_u[myShift_3[2] - 1]
        g_imag /= dX_u[myShift_3[2] - 1]
        g_real[:, :, 0] = 0
        g_imag[:, :, 0] = 0
        
        g_real -= np.roll(g_real, shift=-myShift_3[2], axis=2)
        g_imag -= np.roll(g_imag, shift=-myShift_3[2], axis=2)
        g += g_real + 1j * g_imag
    
    else:
        raise ValueError("Unsupported dimensionality for N_u")
    
    # Scale g by the product of dX_u
    D_u = np.prod(dX_u)
    g *= D_u
    
    return g
