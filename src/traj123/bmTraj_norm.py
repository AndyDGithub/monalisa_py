from src.arrayUtility.bmPointReshape import bmPointReshape
import numpy as np

def bmTraj_norm(t):
    mySize = np.shape(t)
    t = bmPointReshape(t)

    myNorm = np.zeros((1, t.shape[1]))
    for i in range(mySize[0]):
        myNorm += t[i]**2

    myNorm = np.sqrt(myNorm)
    myNorm = np.reshape(myNorm, (mySize[0], -1))

    return myNorm
