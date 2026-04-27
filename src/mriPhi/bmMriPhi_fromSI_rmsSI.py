import numpy as np

def bmMriPhi_fromSI_rmsSI(argSI, nCh, N, nShot):
    SI = np.reshape(argSI, [nCh ,N, nShot])
    # rmsSI = squeeze(sqrt(  mean(abs(SI).^2, 1)  ));
    rmsSI = np.squeeze(np.sqrt(np.mean(np.abs(SI)**2, axis=1)))
    # rmsSI = rmsSI - min(rmsSI.ravel());
    rmsSI -= np.min(rmsSI.ravel())
    # rmsSI = rmsSI/max(rmsSI.ravel());
    rmsSI /= np.max(rmsSI.ravel())
    return rmsSI
