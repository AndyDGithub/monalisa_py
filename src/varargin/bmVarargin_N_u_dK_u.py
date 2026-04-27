"""Auto-generated from MATLAB source. Review manually before production use."""

from src.traj123.bmTraj_N_u_dK_u import bmTraj_N_u_dK_u
from third_part.matlab_compat.matlab_native import double, single
# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

from src.varargin.bmVarargin import bmVarargin

def bmVarargin_N_u_dK_u(t, varargin):
    [N_u, dK_u] = bmVarargin(varargin)
    [N_u, dK_u] = bmTraj_N_u_dK_u(t, N_u, dK_u)
    N_u     = double(single(N_u))
    dK_u    = double(single(dK_u))
    return (N_u, dK_u)
