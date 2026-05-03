import numpy as np

"""
% Bastien Milani
% CHUV and UNIL
% Lausanne - Switzerland
% May 2023
"""

def bmTraj_randomPartialCartesian3_x(N_u, dK_u, myPerOne):
    """% Bastien Milani
    % CHUV and UNIL
    % Lausanne - Switzerland
    % May 2023
    """
    # Ensure input arrays are 1-D and convert to NumPy arrays
    N_u = np.asarray(N_u).flatten()
    dK_u = np.asarray(dK_u).flatten()

    # Extract dimensions and delta k values
    Nx, Ny, Nz = N_u[0], N_u[1], N_u[2]
    dKx, dKy, dKz = dK_u[0], dK_u[1], dK_u[2]

    # Generate k-space coordinates
    kx = np.arange(-Nx / 2, Nx / 2) * dKx
    ky = np.arange(-Ny / 2, Ny / 2) * dKy
    kz = np.arange(-Nz / 2, Nz / 2) * dKz

    # Create all combinations of ky and kz (ndgrid equivalent)
    ky_grid, kz_grid = np.meshgrid(ky, kz, indexing="ij")
    ky_flat = ky_grid.ravel()
    kz_flat = kz_grid.ravel()

    # Random selection of lines based on probability myPerOne
    m = np.random.rand(1, Ny * Nz) <= myPerOne
    m_flat = m.ravel()
    n_line = m_flat.sum()
    ky_selected = ky_flat[m_flat]
    kz_selected = kz_flat[m_flat]

    # Replicate kx and selected ky/kz for each line
    kx_rep = np.tile(kx, n_line)
    ky_rep = np.tile(ky_selected, Nx)
    kz_rep = np.tile(kz_selected, Nx)

    # Stack and return trajectory
    t = np.vstack((kx_rep, ky_rep, kz_rep))
    return t
