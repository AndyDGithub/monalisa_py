import numpy as np

def bmBlockReshape(array, new_shape):
    # This is a placeholder for the actual implementation
    return array.reshape(new_shape)

def bmMriNoiseDecor(noise_meas, y, C, C_n_u):
    nCh = noise_meas.shape[1]
    nPt_noise = noise_meas.shape[0]
    
    C = bmBlockReshape(C, C_n_u)
    C_size = C.shape
    
    C_decor = np.zeros_like(C, dtype=np.complex64)
    
    if isinstance(y, list):  # Assuming y is a list of arrays
        y_decor = [np.zeros_like(x, dtype=np.complex64) for x in y]
        for i in range(len(y)):
            for k in range(nCh):
                for m in range(nCh):
                    y_decor[i][:, k] += np.linalg.cholesky(np.linalg.inv(
                        np.dot(noise_meas.T, noise_meas) / (nPt_noise - 1)
                    ))[k, m] * y[i][:, m]
            for k in range(nCh):
                for m in range(nCh):
                    C_decor[:, k] += np.linalg.cholesky(np.linalg.inv(
                        np.dot(noise_meas.T, noise_meas) / (nPt_noise - 1)
                    ))[k, m] * C[:, m]
    else:
        y_decor = np.zeros_like(y, dtype=np.complex64)
        for k in range(nCh):
            for m in range(nCh):
                y_decor[:, k] += np.linalg.cholesky(np.linalg.inv(
                    np.dot(noise_meas.T, noise_meas) / (nPt_noise - 1)
                ))[k, m] * y[:, m]
        for k in range(nCh):
            for m in range(nCh):
                C_decor[:, k] += np.linalg.cholesky(np.linalg.inv(
                    np.dot(noise_meas.T, noise_meas) / (nPt_noise - 1)
                ))[k, m] * C[:, m]
    
    C_decor = bmBlockReshape(C_decor, C_n_u)
    
    return y_decor, C_decor
