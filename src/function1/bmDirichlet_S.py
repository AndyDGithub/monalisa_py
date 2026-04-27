"""Auto-generated from MATLAB source. Review manually before production use."""

# Bastien Milani
# CHUV and UNIL
# Lausanne - Switzerland
# May 2023

from src.function1.bmDirichletKernel import bmDirichletKernel

def bmDirichlet_S(N_over_2, dk, x):
    f = dk*bmDirichletKernel(2*pi*dk*x, N_over_2)
    return f
