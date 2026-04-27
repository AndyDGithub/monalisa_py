import numpy as np
from src.coilSense.map.bmCoilSense_pinv import bmCoilSense_pinv
from src.coilSense.simu.bcaNeith_coilSensitivitySimulation2 import bcaNeith_coilSensitivitySimulation2
from src.fourier2.bcaNeith2 import bcaNeith2
from src.fourier2.bmIDF2 import bmIDF2
from src.arrayUtility.bmBlockReshape import bmBlockReshape  # Imported arrayUtility.arrayUtility

from third_part.matlab_compat.matlab_native import genpath

def grappa_2D_script():
    # Setting Path
    monalisa_dir = "/path/to/monalisa"  # Replace with actual path

    # Add the paths to all Monalisa subdirectories.
    src_dir = [monalisa_dir, '/', "src"]
    import sys
    sys.path.append(genpath(src_dir))

    # preparing data for simulation
    N_u         = (64, 64)
    dK_u        = (1./200, 1./200)  # arbitrary FoV
    nCh         = 16
    calib_size  = 32;  # Define the calibration size

    h           = phantom(N_u[0])  # Create the phantom image
    C           = bcaNeith_coilSensitivitySimulation2(N_u[0], N_u[1], nCh)

    umask               = np.ones(N_u)  # Create the undersampling mask (2x2 undersampling)
    umask[::2, :]    = 0
    umask[:, ::2]    = 0

    calib               = kspace[(N_u[0]/2-calib_size/2+1):(N_u[0]/2+calib_size/2), :, :]  # Extract the calibration data
    undersampled_kspace = np.multiply(umask, kspace)  # Undersampling the data

    # Call of GRAPPA implementation
    filled_kspace = bcaNeith2(undersampled_kspace, calib, [5,5])

    # recon and plots
    # recon
    x_grappa    = bmIDF2(filled_kspace,          N_u, dK_u)
    x_zero      = bmIDF2(undersampled_kspace,    N_u, dK_u)

    # coil_combine
    x_grappa    = bmCoilSense_pinv(C, x_grappa, N_u)
    x_zero      = bmCoilSense_pinv(C, x_zero,   N_u)

    # plots
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 3, figsize=(15, 7))

    ax[0, 0].imshow(np.abs(kspace[0]), cmap='gray')
    ax[0, 0].set_title('Original k-space')

    ax[0, 1].imshow(umask, cmap='gray')
    ax[0, 1].set_title('Undersampling mask')

    ax[0, 2].imshow(np.abs(undersampled_kspace[0]), cmap='gray')
    ax[0, 2].set_title('Undersampled k-space')

    ax[1, 0].imshow(np.abs(h), cmap='gray')
    ax[1, 0].set_title('Original image')

    ax[1, 1].imshow(np.abs(x_zero[0]), cmap='gray')
    ax[1, 1].set_title('Unsampled image')

    ax[1, 2].imshow(np.abs(x_grappa[0]), cmap='gray')
    ax[1, 2].set_title('GRAPPA reconstruction')

    plt.tight_layout()
    plt.show()
