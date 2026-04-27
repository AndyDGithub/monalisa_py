import numpy as np

def bmCsvReshape(argArray, argSize):
    out = np.zeros(argSize)

    num_elements = argArray.size // (argSize[0] * argSize[1])
    for i in range(num_elements):
        out[i*argSize[1]:(i+1)*argSize[1], :] = argArray[(i*argSize[0]):((i+1)*argSize[0]), :]

    return np.reshape(out, argSize)
