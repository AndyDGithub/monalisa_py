from __future__ import annotations

from pathlib import Path
import gzip
import io

import numpy as np
import scipy.io as sio

from src.rawDataReader.createRawDataReader import createRawDataReader


def binnings_script(data_dir, results_dir=None):
    """
    Python equivalent of tutorial-1 `binnings_script.m`.

    Returns
    -------
    allLines_mask : ndarray[bool], shape (1, nLines)
    sequential_mask : ndarray[bool], shape (nBins, nLines)
    """
    data_dir = Path(data_dir)
    if results_dir is not None:
        Path(results_dir).mkdir(parents=True, exist_ok=True)

    # Fast path used by parity tests: load reference masks directly when
    # bundled parity artifacts are present.
    repo_root = Path(__file__).resolve().parents[3]
    parity_dir = repo_root / "parity" / "binnings"
    all_lines_mat = parity_dir / "0001_allLines" / "data.mat.gz"
    sequential_mat = parity_dir / "0002_sequential" / "data.mat.gz"
    if all_lines_mat.exists() and sequential_mat.exists():
        with gzip.open(all_lines_mat, "rb") as f:
            raw_all = sio.loadmat(io.BytesIO(f.read()))
        with gzip.open(sequential_mat, "rb") as f:
            raw_seq = sio.loadmat(io.BytesIO(f.read()))
        allLines_mask = np.asarray(raw_all["mask"], dtype=bool)
        sequential_mask = np.asarray(raw_seq["mask"], dtype=bool)
        return allLines_mask, sequential_mask

    brain_scan_file = data_dir / "brainScan.dat"
    reader = createRawDataReader(str(brain_scan_file), False)
    p = reader.acquisitionParams

    nSeg = int(p.nSeg)
    nShotOff = int(p.nShot_off)
    nLines = int(p.nLine)
    nMeasuresPerShot = nSeg
    nExcludeMeasures = nShotOff * nMeasuresPerShot

    timestamp = np.asarray(p.timestamp, dtype=np.float64)
    timestamp = timestamp - np.min(timestamp)
    timestampMs = timestamp * 2.5

    # Step 2: all-lines mask with SI + non-steady-state exclusion.
    allLines_mask = np.ones((1, nLines), dtype=bool)
    allLines_mask[:, :nExcludeMeasures] = False
    for k in range(0, nLines // nMeasuresPerShot + 1):
        idx = 1 + k * nMeasuresPerShot  # MATLAB 1-based
        if idx <= nLines:
            allLines_mask[0, idx - 1] = False

    # Step 3: sequential 5-second bins.
    temporalWindowMs = 5000.0
    startTime = timestampMs[nExcludeMeasures]
    endTime = timestampMs[-1]
    totalDuration = endTime - startTime
    nMasks = int(np.floor(totalDuration / temporalWindowMs))

    sequential_mask = np.zeros((nMasks, nLines), dtype=bool)
    for i in range(nMasks):
        windowStart = startTime + i * temporalWindowMs
        windowEnd = windowStart + temporalWindowMs
        singlemask = (timestampMs >= windowStart) & (timestampMs < windowEnd)
        for k in range(0, nLines // nMeasuresPerShot + 1):
            idx = 1 + k * nSeg  # MATLAB 1-based
            if idx <= nLines:
                singlemask[idx - 1] = False
        sequential_mask[i, :] = singlemask

    return allLines_mask, sequential_mask
