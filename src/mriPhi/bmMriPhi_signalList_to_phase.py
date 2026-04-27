from src.mriPhi.bmMriPhi_signalList_to_phaseList import bmMriPhi_signalList_to_phaseList
import numpy as np

def bmMriPhi_signalList_to_phase(signal_extracted_list):
    phi = bmMriPhi_signalList_to_phaseList(signal_extracted_list)

    if phi.shape[0] < 2:
        phase_list = phi
        single_phase = phi

        import matplotlib.pyplot as plt
        fig, ax = plt.subplots()
        ax.plot(single_phase, '.')
        plt.show()
        return (single_phase, phase_list)

    phase_list = np.zeros(phi.shape)
    phi_0 = phi[0]
    c_0 = complex(np.cos(phi_0), np.sin(phi_0))
    phase_list[0, :] = phi_0

    for i in range(1, phi.shape[0]):
        c = complex(np.cos(phi[i]), np.sin(phi[i]))
        temp_phiDiff = np.angle(np.mean(c / c_0))
        cDiff = complex(np.cos(temp_phiDiff), np.sin(temp_phiDiff))
        phase_list[i, :] = np.angle(c / cDiff)

    myReal = np.median(np.cos(phase_list), axis=1)
    myImag = np.median(np.sin(phase_list), axis=1)
    single_phase = np.angle(complex(myReal, myImag))

    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.plot(phase_list.flatten(), '.')
    plt.show()

    fig, ax = plt.subplots()
    ax.plot(single_phase, '.')
    plt.show()

    return (single_phase, phase_list)
