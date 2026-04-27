import importlib.util
import os
import numpy as np
import twixtools

# 'class' is a Python reserved keyword so we cannot use a normal dotted import.
# Use importlib to load the module directly from its file path.
_param_file = os.path.join(
    os.path.dirname(__file__), '..', '..', '..', 'src',
    'mriRecon', 'class', 'bmMriAcquisitionParam.py'
)
_spec = importlib.util.spec_from_file_location('bmMriAcquisitionParam', _param_file)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
bmMriAcquisitionParam = _mod.bmMriAcquisitionParam


def dhSiemensReadMetaData(argFile, autoFlag=True):
    """Read Siemens .dat metadata using twixtools. Returns bmMriAcquisitionParam."""

    # Read twix file (loads MDB metadata, NOT actual k-space data yet)
    twix_list = twixtools.read_twix(argFile)
    if isinstance(twix_list, list):
        myTwix = twix_list[-1]
    else:
        myTwix = twix_list

    mdb = myTwix['mdb']
    hdr = myTwix['hdr']
    proto = hdr.get('Protocol', {})
    cfg = hdr.get('Config', {})

    # --- Extract dimensions ---
    # Read N from the actual stored data (includes 2x oversampling),
    # which matches MATLAB mapVBVD_JH_for_monalisa behaviour (NCol = raw cols).
    N = 0
    for m in mdb:
        if m.is_image_scan():
            N = int(m.data.shape[1])
            break
    if N == 0:
        N = int(proto.get('NCol', cfg.get('NCol', 0)))

    nShot = int(proto.get('NShots', proto.get('NSeg', 0)))     # NSeg in Siemens = nShot in MATLAB
    nLine = int(proto.get('NLinMeas', 0))
    nSeg = int(proto.get('NSegments', 0))                       # NSegments in Siemens = nSeg in MATLAB
    nEcho = 1  # typically 1 for this acquisition

    # --- FoV: try multiple header locations (MATLAB order) ---
    FoV = -1.0
    fov_sections_keys = [
        ('Meas',     ['ReadFoV', 'FOV']),
        ('Protocol', ['ReadFoV', 'PeFOV', 'PhaseFoV']),
        ('Config',   ['ReadFoV', 'PhaseFoV', 'PeFOV', 'RoFOV']),
        ('Dicom',    ['dPhaseFOV', 'dReadoutFOV']),
    ]
    for section_name, keys in fov_sections_keys:
        section = hdr.get(section_name, {})
        for key in keys:
            val = section.get(key)
            if val is not None and isinstance(val, (int, float)) and float(val) > 0:
                FoV = float(val) * 2.0  # MATLAB multiplies by 2
                break
        if FoV > 0:
            break

    # --- Number of channels ---
    nCh = int(cfg.get('NCh', cfg.get('NImageChan', cfg.get('NChannels', cfg.get('NCha', 0)))))
    if nCh == 0:
        for m in mdb:
            if m.is_image_scan():
                nCh = len(m.channel_hdr)
                break

    # --- Timestamps (lightweight - just reads MDH header, not data) ---
    timestamps = np.array(
        [int(m.mdh.TimeStamp) for m in mdb if m.is_image_scan()],
        dtype=np.float64
    )

    # --- Estimate nShot_off from SI projection magnitude (MATLAB algorithm) ---
    nShot_off = _estimate_nshot_off(mdb, nSeg, nShot, N, nCh)

    # --- Build result object ---
    p = bmMriAcquisitionParam()
    p.N = int(N)
    p.nLine = int(nLine)
    p.nShot = int(nShot)
    p.nSeg = int(nSeg)
    p.nCh = int(nCh)
    p.nEcho = int(nEcho)
    p.FoV = float(FoV)
    p.timestamp = timestamps
    p.nShot_off = int(nShot_off)
    p.selfNav_flag = True
    p.roosk_flag = False
    p.traj_type = 'void'

    return p


def _estimate_nshot_off(mdb, nSeg, nShot, N, nCh):
    """
    Estimate nShot_off by analysing the SI projection magnitude.

    Mirrors MATLAB dhSiemensReadMetaData nShot_off estimation exactly:
      1. Extract SI lines [nCh, N, nShot]  (first segment of each shot)
      2. Crop 2x-oversampled readout from 2*N to N samples (OS removal)
      3. IDFT along N dimension:  fftshift(ifft(ifftshift(...)))  like MATLAB bmIDF
      4. RMS over channels
      5. Normalize
      6. Weighted mean (centre of mass per shot)  with x_SI = 1:N
      7. Sliding std with window=5  (MATLAB movstd … 'Endpoints','discard')
      8. nShot_off = first shot where std < prctile(std, 15)
    """
    image_mdbs = [m for m in mdb if m.is_image_scan()]
    si_mdbs = image_mdbs[::nSeg]          # first segment per shot
    actual_nShot = min(len(si_mdbs), nShot)

    si_data = []
    for m in si_mdbs[:actual_nShot]:
        si_data.append(m.data)            # (nCh, N_raw)

    if not si_data:
        return 0

    si_arr = np.stack(si_data, axis=-1).astype(np.complex64)   # (nCh, N_raw, nShot)
    N_raw = si_arr.shape[1]

    # N_raw should equal N (the oversampled column count read directly from data).
    # No k-space cropping needed; the IDFT below operates on the full N_raw points.
    if N_raw != N:
        raise ValueError(f"Unexpected readout length {N_raw} (expected {N}).")

    # --- IDFT matching MATLAB bmIDF(mySI, 1, [], 2) for even N (gridType=2) ---
    # bmIDF: fftshift( ifft( ifftshift(f, dim), [], dim ), dim ) * N * dK
    # Scaling by N cancels in the normalisation step below.
    si_ift = np.fft.fftshift(
        np.fft.ifft(np.fft.ifftshift(si_arr, axes=1), axis=1),
        axes=1,
    )   # (nCh, N, nShot)

    # --- RMS over channels (MATLAB: sqrt(sum(|.|^2, 1))) ---
    si_mag = np.sqrt(np.sum(np.abs(si_ift) ** 2, axis=0))   # (N, nShot)

    # --- Normalise globally ---
    mn, mx = si_mag.min(), si_mag.max()
    if mx > mn:
        si_mag = (si_mag - mn) / (mx - mn)

    # --- Weighted mean: x_SI = 1:N_raw (MATLAB row vector, column-broadcast) ---
    x_idx = np.arange(1, N_raw + 1, dtype=float)[:, np.newaxis]   # (N_raw, 1)
    s_mean = np.mean(x_idx * si_mag, axis=0)                   # (nShot,)

    # --- Sliding std, window=5, Endpoints='discard' (MATLAB movstd) ---
    window, half = 5, 2
    n = len(s_mean)
    running_std = np.array([
        np.std(s_mean[max(0, i - half):min(n, i + half + 1)], ddof=1)
        for i in range(n)
    ])
    # Keep only the fully-windowed positions (like Endpoints='discard')
    valid_std = running_std[half: n - half]

    if len(valid_std) == 0:
        return 0

    threshold = np.percentile(valid_std, 15)
    found = np.where(valid_std < threshold)[0]
    if len(found) == 0:
        return 0

    # MATLAB: nShot_off = find(running_std < threshold, 1)
    # find() returns a 1-based index directly, so the Python equivalent is
    # found[0] (0-based into valid_std) + 1.
    nShot_off = int(found[0]) + 1
    return nShot_off
