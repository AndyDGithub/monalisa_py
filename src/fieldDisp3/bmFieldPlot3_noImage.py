import numpy as np

def bmFieldPlot3_noImage(arg_x, arg_y, arg_z, arg_vx, arg_vy, arg_vz, argSize, autoScaleFlag, myNorm_max):
    # Convert argSize to a 1D array of shape (3,)
    argSize = np.asarray(argSize).reshape(-1, 3)[0]  # or .flatten()
    # reshape arrays
    arg_x = np.reshape(arg_x, argSize)
    arg_y = np.reshape(arg_y, argSize)
    arg_z = np.reshape(arg_z, argSize)
    arg_vx = np.reshape(arg_vx, argSize)
    arg_vy = np.reshape(arg_vy, argSize)
    arg_vz = np.reshape(arg_vz, argSize)

    # rest of the code
