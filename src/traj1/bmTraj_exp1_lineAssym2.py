import numpy as np

def bmTraj_exp1_lineAssym2(N_u, dK_u, arg_exponent):
    N_u     = N_u.ravel().T
    dK_u    = dK_u.ravel().T
    lx = N_u[0, 0] * dK_u[0, 0]

    # x = (-N_u(1, 1)/2:N_u(1, 1)/2 - 1)*dK_u(1, 1)
    x = np.arange(-int(N_u[0, 0]/2), int(N_u[0, 0]/2), dtype=np.float64) * dK_u[0, 0]

    # x = (abs(x).^arg_exponent).*sign(x)
    abs_x = np.abs(x)
    x = np.where(x >= 0, abs_x**arg_exponent, -abs_x**arg_exponent) * np.sign(x)

    # x = N_u(1, 1)*dK_u(1, 1)*x/np.abs(x(1, 1))/2
    x *= N_u[0, 0]*dK_u[0, 0]/(np.abs(x[0]) + 1e-16)/2

    t = x.ravel().T
    return t
