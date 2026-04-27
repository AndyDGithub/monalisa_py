import numpy as np
import matplotlib.pyplot as plt

def bmLineListPlot(a, argLinAssym=None):
    if a.ndim != 2:
        raise ValueError("Input array must be 2D")
    if argLinAssym == 1 or argLinAssym is None:
        # Plot each column
        for col in range(a.shape[1]):
            plt.plot(a[:,col], label=f"col {col}")
        plt.legend()
    elif argLinAssym == 2:
        # Plot derivative along columns
        diff = np.diff(a, axis=1)
        for col in range(diff.shape[1]):
            plt.plot(diff[:,col], label=f"deriv col {col}")
        plt.legend()
    else:
        raise ValueError(f"Unsupported argLinAssym value: {argLinAssym}")
    plt.show()
