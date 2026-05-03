from __future__ import annotations
from third_part.matlab_compat.matlab_native import double

def bmTraj_UTE_r(N, t0, t_grad_start, t_grad_ramp, dt, dK_n):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # Bastien Milani
    # CHUV and UNIL
    # Lausanne - Switzerland
    # May 2023
    # We aknowledge
    # 
    # Jean Delacost
    # 
    # for his work on UTE MRI.
    # Originally, the first code for UTE trajectories
    # in this toolbox came from him.
    # N is the half number of points.
    # Typically 2*N = 384 and N = 192;
    
    t1 = t_grad_start
    t2 = t1 + t_grad_ramp
    
    t1 -= t0
    t2 -= t0
    t0 = 0

    t = np.arange(N) * dt
    p = 1 / dt

    m1 = (t < t1).astype(double)
    m2 = ((t >= t1) & (t <= t2)).astype(double)
    m3 = (t > t2).astype(double)

    r = m1 * 0 + m2 * p * (t - t1)**2 / (t2 - t1) / 2 + m3 * p * (t - (t2 +
+ t1) / 2)
    
    r = (2 * N * dK_n) * r / N / 2
    return r
