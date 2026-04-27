from third_part.matlab_compat.matlab_native import num2str, title
import numpy as np


def bmMriPhi_signalList_to_phaseList(s):
    s_x = s
    s_y = s_x - np.roll(s_x, 1, axis=1)
    s_y[:, 0] = s_y[:, 1]
    s_y = -s_y

    myNumList = []
    for i in range(len(s)):
        temp_s = s_x[i].ravel().T - np.mean(temp_s)
        temp_s = temp_s / np.std(temp_s)
        s_x[i] = temp_s

        temp_s = s_y[i].ravel().T - np.mean(temp_s)
        temp_s = temp_s / np.std(temp_s)
        s_y[i] = temp_s

        fig = plt.figure()
        plt.hold(True)
        plt.plot(s_x[i], s_y[i], '.-')
        title(num2str(i))
        plt.axis('image')
        plt.waitforbuttonpress()

        myAnswer = input("Press Enter to continue or 'n' to skip: ")
        if myAnswer == '':
            myNumList.append(i)

    s_x = s_x[myNumList]
    s_y = s_y[myNumList]

    myPhase = np.angle(complex(s_x, s_y))
    return myPhase
