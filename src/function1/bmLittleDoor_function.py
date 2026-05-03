import numpy as np

# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

def bmLittleDoor_function(x, L, a):
    """Return a step-like function with amplitude 1/L between -L/2 and L/2 

centered at a."""
    
    f = np.zeros_like(x)
    m1 = (x - a >= -L / 2) & (x - a < L / 2)
    f[m1] = 1 / L
    
    return f
