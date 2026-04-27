from __future__ import annotations
import numpy as np


def HarmonicField3D(coeffs, X, Y, Z):
    """Compute the 3D harmonic basis field from 15 coefficients."""
    #
    # Berk Can Acikgoz
    # University of Bern and Insel Spital
    # Bern - Switzerland
    # February 2025
    #
    # coeffs: 15x1 vector of basis coefficients
    # X, Y, Z: 3D grids from ndgrid
    # phi: result scalar field of same size as X/Y/Z

    coeffs_arr = np.asarray(coeffs).reshape(-1)
    if coeffs_arr.size != 15:
        raise ValueError("Expected 15 coefficients")

    X_arr = np.asarray(X)
    Y_arr = np.asarray(Y)
    Z_arr = np.asarray(Z)
    if X_arr.shape != Y_arr.shape or X_arr.shape != Z_arr.shape:
        raise ValueError("X, Y and Z must have the same shape")

    r2 = X_arr**2 + Y_arr**2 + Z_arr**2

    basis = [
        np.ones_like(X_arr),                    # 1
        X_arr,                                  # x
        Y_arr,                                  # y
        Z_arr,                                  # z
        X_arr * Y_arr,                          # xy
        X_arr * Z_arr,                          # xz
        Y_arr * Z_arr,                          # yz
        X_arr**2 - Y_arr**2,                    # x^2 - y^2
        2 * Z_arr**2 - X_arr**2 - Y_arr**2,    # 2z^2 - x^2 - y^2
        X_arr * (5 * Z_arr**2 - r2),            # x(5z^2 - r^2)
        Y_arr * (5 * Z_arr**2 - r2),            # y(5z^2 - r^2)
        Z_arr * (5 * Z_arr**2 - 3 * r2),        # z(5z^2 - 3r^2)
        X_arr * Y_arr * Z_arr,                  # xyz
        X_arr**3 - 3 * X_arr * Y_arr**2,        # x^3 - 3xy^2
        Y_arr**3 - 3 * X_arr**2 * Y_arr,        # y^3 - 3x^2y
    ]

    phi = np.zeros_like(X_arr, dtype=np.result_type(coeffs_arr, X_arr, Y_arr, Z_arr))
    for i in range(15):
        phi = phi + coeffs_arr[i] * basis[i]

    return phi

# Auto-generated entrypoint alias for import compatibility
bcaNeith_harmonicField3D = HarmonicField3D
