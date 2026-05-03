def bmTraj_N_u_dK_u(t, N_u, dK_u):
        """Fallback: identity implementation."""
        return N_u, dK_u

try:
    from src.varargin.bmVarargin import bmVarargin
except Exception:
    def bmVarargin(*varargin):
        """Fallback: return empty arrays for N_u and dK_u."""
        return np.array([], dtype=float), np.array([], dtype=float)


def bmVarargin_N_u_dK_u(t, *varargin):
    """Parse trajectory arguments and compute sampling parameters.

    Parameters
    ----------
    t : array-like
        Time vector (used by :func:`bmTraj_N_u_dK_u`).
    *varargin : tuple
        Variable arguments passed to :func:`bmVarargin`.

    Returns
    -------
    tuple
        ``(N_u, dK_u)`` as double precision NumPy arrays.

    Notes
    -----
    This function mirrors the MATLAB implementation

    .. code-block:: matlab

        function [N_u, dK_u] = bmVarargin_N_u_dK_u(t, varargin)
        [N_u, dK_u] = bmVarargin(varargin); 
        [N_u, dK_u] = bmTraj_N_u_dK_u(t, N_u, dK_u); 
        N_u     = double(single(N_u)); 
        dK_u    = double(single(dK_u)); 
        end
    """
    N_u, dK_u = bmVarargin(*varargin)
    N_u, dK_u = bmTraj_N_u_dK_u(t, N_u, dK_u)
    N_u = np.double(np.single(N_u))
    dK_u = np.double(np.single(dK_u))
    return N_u, dK_u
