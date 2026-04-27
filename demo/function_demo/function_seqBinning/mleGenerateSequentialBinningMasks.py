import numpy as np
from src.arrayUtility.bmBlockReshape import bmBlockReshape  # Import block reshape function

def mleGenerateSequentialBinningMasks(temporalWindowSec, reader, debug=False):
    """Auto-generated from MATLAB source. Review manually before production use."""

    acquisitionParams = reader.acquisitionParams
    costTime = 2.5  # This is not magic, is siemens dependent do not change

    timeStamp = np.array(acquisitionParams.timestamp)
    timeStamp -= timeStamp.min()
    timestampMs = timeStamp * costTime

    temporalWindowMs = int(temporalWindowSec * 1000)
    nMeasures = acquisitionParams.nLine
    nseg = acquisitionParams.nSeg
    nShotOff = acquisitionParams.nShot_off
    nExcludeMeasures = nShotOff * nMeasuresPerShot
    startTime = timestampMs[nExcludeMeasures + 1]
    endTime = timestampMs[-1]
    totalDuration = endTime - startTime

    nMasks = int(np.floor(totalDuration / temporalWindowMs))
    cMask = np.zeros((nMasks, nMeasures), dtype=bool)

    for i in range(nMasks):
        windowStart = startTime + (i-1) * temporalWindowMs
        windowEnd = windowStart + temporalWindowMs

        mask = (timestampMs >= windowStart) & (timestampMs < windowEnd)
        idx = 1 + np.arange(0, nMeasures, nseg)
        cMask[i, :] = mask[idx]

    if any(cMask[:, :nExcludeMeasures]):
        raise ValueError("The first %d measurements (nseg * nShotOff) are not all False." % nExcludeMeasures)

    if debug:
        import matplotlib.pyplot as plt

        colors = plt.get_cmap('tab20')(np.linspace(0, 1, nMasks))
        timeInSeconds = timestampMs / 1000

        for i in range(nMasks):
            plt.plot(timeInSeconds, cMask[i, :] + i, 'Color', colors[i])

        plt.xlabel("Time (seconds)")
        plt.ylabel("Mask Index")
        plt.title("Binning Masks")

        plt.show()

    return cMask
