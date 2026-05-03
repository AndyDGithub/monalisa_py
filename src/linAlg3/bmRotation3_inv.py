# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

"""
MATLAB source reference:

function R_inv = bmRotation3_inv(psi, theta, phi)

psi   = -psi; 
theta = -theta; 
phi   = -phi; 

R1 =    [   
            cos(psi)    -sin(psi)   0
            sin(psi)     cos(psi)   0
            0            0          1
        ]; 

    
R2 =    [
             cos(theta) 0   sin(theta)
             0          1   0
            -sin(theta) 0   cos(theta)
        ];

    
R3 =    [   
            cos(phi)    -sin(phi)   0
            sin(phi)     cos(phi)   0
            0            0          1
        ]; 
    
    
R_inv = R1*R2*R3; 
    

end

"""

import numpy as np


def bmRotation3_inv(psi, theta, phi):
    """Inverse 3-D rotation matrix (MATLAB equivalent)."""
    psi = -psi
    theta = -theta
    phi = -phi

    R1 = np.array(
        [
            [np.cos(psi), -np.sin(psi), 0],
            [np.sin(psi), np.cos(psi), 0],
            [0, 0, 1],
        ]
    )

    R2 = np.array(
        [
            [np.cos(theta), 0, np.sin(theta)],
            [0, 1, 0],
            [-np.sin(theta), 0, np.cos(theta)],
        ]
    )

    R3 = np.array(
        [
            [np.cos(phi), -np.sin(phi), 0],
            [np.sin(phi), np.cos(phi), 0],
            [0, 0, 1],
        ]
    )

    return np.dot(R1, np.dot(R2, R3))
