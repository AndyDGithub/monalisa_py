import numpy as np
import scipy.optimize as opt

def bmMonoExpFit1(x_data, y_data, start_idx, end_idx, fit_type, start_guess):
    # Ensure indices are within bounds
    if start_idx < 0 or end_idx > len(x_data) or start_idx >= end_idx:
        raise ValueError("Invalid start or end indices")
    # Trim data
    x_slice = x_data[start_idx:end_idx]
    y_slice = y_data[start_idx:end_idx]
    # initial guess for parameters
    initial = start_guess
    # define objective
    def residuals(params):
        A, k = params
        return y_slice - A * np.exp(-k * x_slice)
    # Fit
    try:
        result = opt.least_squares(residuals, initial)
        A_opt, k_opt = result.x
    except Exception as e:
        A_opt, k_opt = np.nan, np.nan
    # Compute r_squared
    y_pred = A_opt * np.exp(-k_opt * x_slice)
    ss_res = np.sum((y_slice - y_pred)**2)
    ss_tot = np.sum((y_slice - np.mean(y_slice))**2)
    r_squared = 1 - ss_res/ss_tot if ss_tot != 0 else np.nan
    # Return as tuple
    return A_opt, k_opt, r_squared, result
