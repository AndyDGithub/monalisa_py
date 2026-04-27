import numpy as np
from scipy import ndimage

def bmMidPlanMask(a, b, d_plan, d_mid):
    if (np.sum(np.abs(a)) == 0) or (np.sum(np.abs(b)) == 0):
        c = np.zeros((a.shape[0], a.shape[1], len(d_mid)), dtype=int)
        return c

    d_mid = d_mid.ravel()
    x_a, y_a = np.meshgrid(np.arange(1, a.shape[0] + 1), np.arange(1, a.shape[1] + 1))
    x_b, y_b = np.meshgrid(np.arange(1, b.shape[0] + 1), np.arange(1, b.shape[1] + 1))

    x_a = np.mean(x_a[a])
    y_a = np.mean(y_a[a])
    x_b = np.mean(x_b[b])
    y_b = np.mean(y_b[b])

    bound_a, _ = ndimage.measurements.label(a)
    bound_b, _ = ndimage.measurements.label(b)

    bound_a = np.concatenate((bound_a[:, -1:], bound_a[:, :-1]), axis=1)
    bound_b = np.concatenate((bound_b[:, -1:], bound_b[:, :-1]), axis=1)

    phase_a = np.angle(complex(bound_a[0, :] - x_a, bound_a[1, :] - y_a))
    phase_b = np.angle(complex(bound_b[0, :] - x_b, bound_b[1, :] - y_b))

    minInd_a = np.argmin(phase_a)
    minInd_b = np.argmin(phase_b)

    bound_a = np.concatenate((bound_a[:, minInd_a:], bound_a[:, :minInd_a]), axis=1)
    bound_b = np.concatenate((bound_b[:, minInd_b:], bound_b[:, :minInd_b]), axis=1)

    c = np.zeros((a.shape[0], a.shape[1], len(d_mid)), dtype=int)
    L_a = bound_a.shape[1]
    L_b = bound_b.shape[1]

    for k in range(len(d_mid)):
        r = np.zeros((2, L_a))

        for i in range(L_a):
            j = int(round(L_b * i / L_a))
            j = max(j, 1)
            j = min(j, L_b)

            p = bound_a[:, i]
            q = bound_b[:, j]

            r_temp = np.round(p + (q - p) * d_mid[k, 0] / d_plan)
            r[:, i] = r_temp[0:2, 1]

        c[:, :, k] = ndimage.measurements.roipoly(a, r[1, :], r[0, :])

    return c
