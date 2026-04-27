import numpy as np
from src.arrayUtility import bmBlockReshape

def bmMriPhi_manually_exclude_signal_of_list(s_in):
    myList = []

    for i in range(s_in.shape[0]):
        # Create figure (not actually necessary, just mimicking MATLAB behavior)
        import matplotlib.pyplot as plt
        fig = plt.figure()

        # Plot data (using MATLAB-like syntax, but with actual plotting)
        plt.plot(s_in[0], '.', label='First line')
        plt.plot(s_in[i], '.', label=f'Line {i+1}')

        # Display plot and wait for user input (using matplotlib's interactive mode)
        plt.legend()
        plt.show(block=True)

        if raw_input("Exclude this line? (y/n): ").lower() == 'y':
            myList.append(i)

    s_out = bmBlockReshape(s_in, myList, axis=0)
    return s_out
