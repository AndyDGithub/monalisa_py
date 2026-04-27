import numpy as np

def bmConv1(f, h, dx):
    f = f.ravel()
    h = h.ravel()

    N = len(f)
    s = np.zeros(N)

    temp_sum = 0
    for n in range(-N // 2, N // 2):
        for k in range(-N // 2, N // 2):
            ind_2 = k + N // 2 + 1
            ind_3 = (n - k) % N + N // 2 + 1
            temp_sum += dx * f[ind_2] * h[ind_3]

        s[n + N // 2 + 1] = temp_sum

    return s

def private_mod(n, N):
    myMod = (n + N / 2) % N - N / 2
    return myMod
