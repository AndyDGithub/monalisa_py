"""
Binning Generation Script
Port of binnings_script.m to Python.

Generates allLines and sequential binning masks from raw brain scan data.
"""

import os
import sys

_script_dir = os.path.dirname(os.path.abspath(__file__))
_monalisa_py_root = os.path.abspath(os.path.join(_script_dir, '..', '..', '..', '..'))
if _monalisa_py_root not in sys.path:
    sys.path.insert(0, _monalisa_py_root)

_monalisa_root = os.path.abspath(os.path.join(_monalisa_py_root, '..', 'monalisa'))
_data_dir = os.path.join(_monalisa_root, 'demo', 'data_demo', 'data_8_tutorial_1')
_results_dir = os.path.join(_data_dir, 'results')

import numpy as np
import scipy.io
from src.rawDataReader.createRawDataReader import createRawDataReader


def binnings_script(data_dir=None, results_dir=None):
    """
    Generate allLines and sequential binning masks from raw brain scan data.

    Parameters
    ----------
    data_dir : str, optional
        Path to the data directory containing brainScan.dat.
        Defaults to the sibling monalisa repository's data folder.
    results_dir : str, optional
        Path where result .mat files are written.
        Defaults to data_dir/results.

    Returns
    -------
    allLines_mask : ndarray, shape (1, nLines), dtype bool
        Mask including all steady-state lines.
    sequential_mask : ndarray, shape (nMasks, nLines), dtype bool
        Mask grouping data into 5-second temporal windows.
    """
    if data_dir is None:
        data_dir = _data_dir
    if results_dir is None:
        results_dir = os.path.join(data_dir, 'results')

    os.makedirs(results_dir, exist_ok=True)

    # ------------------------------------------------------------------
    # Step 1: Read the Raw Data
    # ------------------------------------------------------------------
    brain_scan_file = os.path.join(data_dir, 'brainScan.dat')

    brain_coil_reader = createRawDataReader(brain_scan_file, False)
    acquisition_params = brain_coil_reader.acquisitionParams

    nSeg = acquisition_params.nSeg               # Number of segments
    nShotOff = acquisition_params.nShot_off      # Number of off shots (non-steady state)
    nMeasuresPerShot = acquisition_params.nSeg   # Measurements per shot
    nExcludeMeasures = nShotOff * nMeasuresPerShot  # Total measurements to exclude
    nLines = acquisition_params.nLine            # Total number of radial lines

    # Cost time: Siemens-specific, do not change unless known
    costTime = 2.5

    # Extract timestamp in milliseconds
    timeStamp = np.array(acquisition_params.timestamp, dtype=float)
    timeStamp = timeStamp - np.min(timeStamp)  # Normalize to start from 0
    timestampMs = timeStamp * costTime          # Convert to milliseconds

    # ------------------------------------------------------------------
    # Step 2: AllLines Binning - Include All Steady-State Lines
    # Equivalent to MATLAB Step 2.
    # ------------------------------------------------------------------
    nbins = 1
    # MATLAB: mask = true(nbins, nLines)
    allLines_mask = np.ones((nbins, nLines), dtype=bool)

    # MATLAB: mask(nbins, 1:nExcludeMeasures) = false
    allLines_mask[nbins - 1, 0:nExcludeMeasures] = False

    # Exclude SI projections (one every nMeasuresPerShot lines)
    # MATLAB: for K = 0:floor(nLines / nMeasuresPerShot)
    #             idx = 1 + K * nMeasuresPerShot;
    #             if idx <= nLines
    #                 mask(idx) = false;   % linear index on (1, nLines) row vec
    #             end
    # Linear index on a (1, nLines) row vector: mask(idx) == mask(1, idx)
    # Python 0-based: mask[0, idx-1]  where idx = 1 + K*nMeasuresPerShot
    for K in range(0, int(np.floor(nLines / nMeasuresPerShot)) + 1):
        idx = 1 + K * nMeasuresPerShot  # MATLAB 1-based index
        if idx <= nLines:
            allLines_mask[0, idx - 1] = False  # Convert to 0-based

    # Save allLines binning
    save_name_all = os.path.join(results_dir, 'allLinesBinning.mat')
    scipy.io.savemat(save_name_all, {'mask': allLines_mask})
    print(f'All lines binning saved to: {save_name_all}')

    # ------------------------------------------------------------------
    # Step 3: Sequential Binning - Group Data into 5-Second Windows
    # Equivalent to MATLAB Step 3.
    # ------------------------------------------------------------------
    temporalWindowSec = 5
    temporalWindowMs = temporalWindowSec * 1000

    # MATLAB: startTime = timestampMs(nExcludeMeasures + 1)  [1-indexed]
    # Python:            timestampMs[nExcludeMeasures]        [0-indexed]
    startTime = timestampMs[nExcludeMeasures]
    endTime = timestampMs[-1]
    totalDuration = endTime - startTime

    nMasks = int(np.floor(totalDuration / temporalWindowMs))

    # MATLAB: mask = false(nMasks, nLines)
    sequential_mask = np.zeros((nMasks, nLines), dtype=bool)

    # MATLAB: for i = 1:nMasks
    for i in range(1, nMasks + 1):
        # MATLAB: windowStart = startTime + (i-1) * temporalWindowMs
        windowStart = startTime + (i - 1) * temporalWindowMs
        windowEnd = windowStart + temporalWindowMs

        singlemask = (timestampMs >= windowStart) & (timestampMs < windowEnd)

        # Exclude SI projections
        # MATLAB: for K = 0:floor(nLines / nMeasuresPerShot)
        #             idx = 1 + K * nSeg;
        #             if idx <= nLines
        #                 singlemask(idx) = false;
        for K in range(0, int(np.floor(nLines / nMeasuresPerShot)) + 1):
            idx = 1 + K * nSeg  # MATLAB 1-based index
            if idx <= nLines:
                singlemask[idx - 1] = False  # Convert to 0-based

        sequential_mask[i - 1, :] = singlemask

    # Save sequential binning
    save_name_seq = os.path.join(results_dir, 'sequentialBinning.mat')
    scipy.io.savemat(save_name_seq, {'mask': sequential_mask})
    print(f'Sequential bins saved to: {save_name_seq}')

    return allLines_mask, sequential_mask


if __name__ == '__main__':
    allLines_mask, sequential_mask = binnings_script()
    print(f'allLines mask shape:    {allLines_mask.shape}')
    print(f'sequential mask shape:  {sequential_mask.shape}')
