import numpy as np
from third_part.matlab_compat.matlab_native import permute


def bcaNeith_coilSensitivitySimulation2(Nx, Ny, Ncoils):
    sensemaps = np.zeros((Nx, Ny, Ncoils))
    ps = [np.ones((Nx, Ny)), lambda x: x,
          lambda x: (1/2)*(3*(x**2) - 1),
          lambda x: (1/2)*(5*(x**3)-3*x),
          lambda x: (1/8)*(35*(x**4)-30*(x**2)+3)]

    [X, Y] = np.meshgrid(np.linspace(-0.5, 0.5, Nx), np.linspace(-0.5, 0.5, Ny))
    b = np.zeros((9, Nx, Ny))
    k = 1

    for i in range(3):
        for j in range(3):
            fx = ps[i]
            fy = ps[j]
            b[k, :, :] = fx(X) * fy(Y)
            k += 1

    for nc in range(Ncoils):
        map = np.squeeze(private_tensorprod(np.random.randn(1, Nx), b, 2, 1)) + \
              1j * np.squeeze(private_tensorprod(np.random.randn(1, Nx), b, 2, 1))
        sensemaps[:, :, nc] = private_rescale_mag(np.abs(map)) * np.exp(1j * np.angle(map))

    return sensemaps


def private_tensorprod(A, B, dimA, dimB):
    szA = A.shape
    szDimA = szA[dimA]
    dimsA = list(range(len(szA)))
    dimsA.pop(dimA)
    permuteA = np.moveaxis(A, [dimA] + dimsA, [dimsA + [dimA]])

    permuted_reshapedA = np.reshape(permuteA, (np.prod(szA), szDimA))

    szB = B.shape
    szDimB = szB[dimB]
    dimsB = list(range(len(szB)))
    dimsB.pop(dimB)
    permuteB = np.moveaxis(B, [dimB] + dimsB, [dimsB + [dimB]])

    permuted_reshapedB = np.reshape(permuteB, (np.prod(szB), szDimB))

    tprod = np.matmul(permuted_reshapedA, np.moveaxis(permuted_reshapedB, -1, dimB))
    return np.moveaxis(tprod, [dimA, dimB], [dimsA + [dimA], dimsB + [dimB]])


def private_rescale_mag(x):
    a = np.min(x)
    b = np.max(x)
    res = x * (1 / (b - a))
    return res
