import numpy as np
import twixtools


def bmSiemensReadRawData(obj, flagSS, flagExcludeSI):
    """
    Extract raw k-space data from a Siemens .dat file using twixtools.

    Returns readouts in [nCh, N, nSeg*nShot] format (column-major equivalent
    matching MATLAB mapVBVD convention, nEcho == 1 only).

    Parameters
    ----------
    obj : mleSiemensReader
        Reader object with argFile and acquisitionParams.
    flagSS : bool
        If True, discard the first nShot_off shots (non-steady-state).
    flagExcludeSI : bool
        If True, discard segment 0 (SI projection) from every shot.
    """
    argFile = obj.argFile
    p = obj.acquisitionParams
    nCh = int(p.nCh)
    N = int(p.N)
    nSeg = int(p.nSeg)
    nShot = int(p.nShot)
    nShot_off = int(p.nShot_off)

    if p.nEcho != 1:
        raise ValueError(f"bmSiemensReadRawData: nEcho={p.nEcho} not implemented.")

    # --- Read twix file ---
    twix_list = twixtools.read_twix(argFile)
    myTwix = twix_list[-1] if isinstance(twix_list, list) else twix_list
    mdb = myTwix['mdb']

    # Collect all image scan MDbs in acquisition order
    image_mdbs = [m for m in mdb if m.is_image_scan()]

    expected_lines = nSeg * nShot
    if len(image_mdbs) != expected_lines:
        raise ValueError(
            f"Expected {expected_lines} image lines (nSeg={nSeg} * nShot={nShot}) "
            f"but got {len(image_mdbs)} image MDbs."
        )

    # Read data: each m.data is (nCh, N) where N = acquisitionParams.N
    # (the actual stored data size, including oversampling, set by dhSiemensReadMetaData)
    first = image_mdbs[0].data
    N_raw = first.shape[1]
    if N_raw != N:
        raise ValueError(
            f"Unexpected readout length {N_raw} (expected N={N} from acquisitionParams)."
        )

    readouts = np.empty((expected_lines, nCh, N), dtype=np.complex64)
    for idx, m in enumerate(image_mdbs):
        readouts[idx] = m.data

    # Transpose to MATLAB convention [nCh, N, nLines]
    # readouts: (nLines, nCh, N) → (nCh, N, nLines)
    readouts = readouts.transpose(1, 2, 0)  # (nCh, N, nLines)

    # Reshape nLines → (nSeg, nShot)
    readouts = readouts.reshape(nCh, N_raw, nSeg, nShot)

    # Filter non-steady-state shots (axis=3)
    if flagSS and nShot_off > 0:
        readouts = readouts[:, :, :, nShot_off:]
        nShot -= nShot_off

    # Filter SI projection segment (axis=2, index 0)
    if flagExcludeSI:
        readouts = readouts[:, :, 1:, :]   # drop index 0 along seg axis
        nSeg -= 1

    # Flatten back to [nCh, N, nSeg*nShot]
    readouts = readouts.reshape(nCh, N_raw, nSeg * nShot)

    return readouts
