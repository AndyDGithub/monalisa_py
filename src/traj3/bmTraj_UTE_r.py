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
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: t1 = t_grad_start;
    # MATLAB: t2 = t1 + t_grad_ramp;
    # MATLAB: t1 = t1 - t0;
    # MATLAB: t2 = t2 - t0;
    # MATLAB: t0 = 0;
    # MATLAB: t = (0:N-1)*dt;
    # MATLAB: p = 1/dt;
    # MATLAB: m1  = double(  (t <  t1)  );
    # MATLAB: m2  = double(  (t >= t1) & (t <= t2)  );
    # MATLAB: m3  = double(  (t > t2)  );
    # MATLAB: r   = m1.*0 + m2.*p.*(  (t - t1).^2  )/(t2 - t1)/2 + m3.*p.*(t - (t2 + t1)/2  );
    # MATLAB: r = (2*N*dK_n)*r/N/2;
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    r = None
    return r
