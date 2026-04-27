import numpy as np
from src.arrayUtility import bmBlockReshape

def bmConv2(f, h, dx, dy):
    n_u = np.shape(f)
    s = np.zeros(n_u)
    Nx = n_u[0]
    Ny = n_u[1]
    dR = dx * dy

    temp_sum = 0
    for nx in range(-Nx//2, Nx//2):
        for ny in range(-Ny//2, Ny//2):
            temp_sum = 0
            for px in range(-Nx//2, Nx//2):
                ind_2_x = px + Nx//2 + 1
                ind_3_x = bmBlockReshape.private_mod(nx - px, Nx) + Nx//2 + 1

                for py in range(-Ny//2, Ny//2):
                    ind_2_y = py + Ny//2 + 1
                    ind_3_y = bmBlockReshape.private_mod(ny - py, Ny) + Ny//2 + 1

                    temp_sum += dR * f[ind_2_x, ind_2_y] * h[ind_3_x, ind_3_y]

            s[nx + Nx//2 + 1, ny + Ny//2 + 1] = temp_sum

    return s
