from third_part.matlab_compat.matlab_native import double
import numpy as np

def bmTraj_random3_k0(nPt, N_u, dK_u):
    """
    Translate the MATLAB function bmTraj_random3_k0 to Python.

    MATLAB reference:
    % Bastien Milani
    % CHUV and UNIL
    % Lausanne - Switzerland
    % May 2023

    function t = bmTraj_random3_k0(nPt, N_u, dK_u)

    myEps = 100*eps; % magic_number

    N_u     = double(N_u(:)');
    dK_u    = double(dK_u(:)');

    lx = (N_u(1, 1)-1)*dK_u(1, 1);
    ly = (N_u(1, 2)-1)*dK_u(1, 2);
    lz = (N_u(1, 3)-1)*dK_u(1, 3);

    sx = N_u(1, 1)/2*dK_u(1, 1);
    sy = N_u(1, 2)/2*dK_u(1, 2);
    sz = N_u(1, 3)/2*dK_u(1, 3);

    x = (rand(1, nPt)*lx) - sx;
    y = (rand(1, nPt)*ly) - sy;
    z = (rand(1, nPt)*lz) - sz;

    t = cat(1, x(:)', y(:)', z(:)');

    n = sqrt( t(1, :).^2 + t(2, :).^2 + t(3, :).^2 );
    m = (n < myEps);
    if sum(m(:)) == 0
        t = cat(2, [0, 0, 0]', t(:, 1:end-1));
    end

    if size(t, 2) ~= nPt
        error('The output traj has wrong size.');
    end
    end
    """
    # Magic number similar to MATLAB eps
    myEps = 100 * np.finfo(float).eps

    # Ensure inputs are 1-D float arrays
    N_u = double(N_u.ravel().T)
    dK_u = double(dK_u.ravel().T)

    # Lengths in k-space
    lx = (N_u[0, 0] - 1) * dK_u[0, 0]
    ly = (N_u[0, 1] - 1) * dK_u[0, 1]
    lz = (N_u[0, 2] - 1) * dK_u[0, 2]

    # Center offsets
    sx = N_u[0, 0] / 2 * dK_u[0, 0]
    sy = N_u[0, 1] / 2 * dK_u[0, 1]
    sz = N_u[0, 2] / 2 * dK_u[0, 2]

    # Random points within the cube
    x = np.random.rand(1, nPt) * lx - sx
    y = np.random.rand(1, nPt) * ly - sy
    z = np.random.rand(1, nPt) * lz - sz

    # Stack into a 3 x nPt matrix
    t = np.vstack((x, y, z))

    # Compute radial distances per column
    n = np.sqrt(t[0, :] ** 2 + t[1, :] ** 2 + t[2, :] ** 2)
    m = n < myEps

    # If no point is near the origin, prepend [0;0;0] and drop last column
    if not np.any(m):
        t = np.concatenate((np.zeros((3, 1)), t[:, :-1]), axis=1)

    # Validate size
    if t.shape[1] != nPt:
        raise ValueError("The output traj has wrong size.")

    return t
