"""MATLAB to Python port of ``DataFromISMRMRD.m`` (script form).

The original MATLAB file is a script with interactive plotting.
This Python port keeps the deterministic data-processing core and returns
structured outputs instead of opening GUI dialogs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET

import numpy as np


DEFAULT_FILE_PATH = "ismrmrd_testfile_body.mdr"


def _require_h5py():
    try:
        import h5py  # type: ignore[import-not-found]
    except Exception as exc:  # noqa: BLE001
        raise ImportError("DataFromISMRMRD requires optional dependency 'h5py'.") from exc
    return h5py


def _to_scalar(value: Any, *, name: str) -> int:
    arr = np.asarray(value).reshape(-1)
    unique = np.unique(arr)
    if unique.size != 1:
        raise ValueError(f"{name} must be constant over acquisitions.")
    return int(unique[0])


def _read_dataset_data(h5_file: Any) -> tuple[Any, Any, str]:
    data_group = h5_file["/dataset/data"]
    raw_data = data_group["data"]
    head = data_group["head"]
    xml_raw = h5_file["/dataset/xml"][()]
    if isinstance(xml_raw, bytes):
        xml_text = xml_raw.decode("utf-8", errors="ignore")
    else:
        xml_text = str(xml_raw)
    return raw_data, head, xml_text


def _extract_fov_from_xml(xml_text: str) -> tuple[np.ndarray, np.ndarray]:
    root = ET.fromstring(xml_text)
    x_vals = [float(node.text) for node in root.findall(".//x") if node.text is not None]
    y_vals = [float(node.text) for node in root.findall(".//y") if node.text is not None]
    z_vals = [float(node.text) for node in root.findall(".//z") if node.text is not None]
    if len(x_vals) < 4 or len(y_vals) < 4 or len(z_vals) < 4:
        raise ValueError("ISMRMRD XML does not contain expected FoV tags.")
    fov = np.array([x_vals[1], y_vals[1], z_vals[1]], dtype=np.float64) * 2.0
    fov_recon = np.array([x_vals[3], y_vals[3], z_vals[3]], dtype=np.float64) * 2.0
    return fov, fov_recon


def _matlab_like_shot_off(y_raw: np.ndarray) -> int:
    # y_raw expected shape: [nCh, N, nSeg, nShot]
    my_si = np.squeeze(y_raw[:, :, 0, :])
    if my_si.ndim != 2:
        return 0
    my_si = np.fft.ifft(my_si, axis=1)
    my_si = np.sqrt(np.sum(np.abs(my_si) ** 2, axis=0))
    my_si = my_si - np.min(my_si)
    max_val = np.max(my_si)
    if max_val > 0:
        my_si = my_si / max_val
    x_si = np.arange(1, my_si.shape[0] + 1, dtype=np.float64)[:, None]
    x_si = np.repeat(x_si, my_si.shape[1], axis=1)
    s_mean = np.mean(x_si * my_si, axis=0)
    threshold = float(np.std(s_mean) * 0.1)
    window_size = 10
    if s_mean.size == 0:
        return 0
    pad = window_size // 2
    padded = np.pad(s_mean, (pad, pad), mode="edge")
    running_std = np.array(
        [np.std(padded[i : i + window_size]) for i in range(s_mean.size)],
        dtype=np.float64,
    )
    below = np.where(running_std < threshold)[0]
    if below.size == 0:
        return 0
    return int(below[0] + 1)


def _default_trajectory(N: int, nLine: int) -> np.ndarray:
    # Placeholder deterministic trajectory with MATLAB-compatible shape [3, N*nLine].
    return np.zeros((3, int(N) * int(nLine)), dtype=np.float64)


def DataFromISMRMRD() -> dict[str, Any]:
    """Load ISMRMRD data and return deterministic processing outputs.

    Returns a dictionary so downstream scripts can consume values without
    relying on MATLAB workspace side-effects.
    """
    h5py = _require_h5py()
    file_path = Path(DEFAULT_FILE_PATH)
    with h5py.File(file_path, "r") as h5_file:
        raw_data, head, xml_text = _read_dataset_data(h5_file)

        N = _to_scalar(head["number_of_samples"][()], name="number_of_samples")
        nLine = int(raw_data.shape[0])
        nShot = int(np.unique(head["idx"]["segment"][()]).size)
        nSeg = int(nLine // nShot)
        nPar = int(np.unique(head["idx"]["kspace_encode_step_2"][()]).size)
        nCh = _to_scalar(head["active_channels"][()], name="active_channels")
        nEcho = int(np.unique(head["idx"]["contrast"][()]).size)
        fov, fov_recon = _extract_fov_from_xml(xml_text)

        y_raw = np.zeros((N, nCh, nLine), dtype=np.complex64)
        for i in range(nLine):
            acq = np.asarray(raw_data[i])
            acq = np.reshape(acq, (2, N, nCh))
            y_raw[:, :, i] = np.squeeze(acq[0, :, :] + 1j * acq[1, :, :])

    y_raw = np.transpose(y_raw, (1, 0, 2))  # [nCh, N, nLine]
    y_raw = np.reshape(y_raw, (nCh, N, nSeg, nShot))
    shot_off = _matlab_like_shot_off(y_raw)
    nShotOff = int(max(0, shot_off))
    self_nav_flag = True

    nS = int(nSeg)
    nSh = int(nShot)
    y_tmp = y_raw.copy()
    if self_nav_flag:
        y_tmp = y_tmp[:, :, 1:, :]
        nS -= 1
    if nShotOff > 0:
        y_tmp = y_tmp[:, :, :, nShotOff:]
        nSh -= nShotOff
    y = np.reshape(y_tmp, (nCh, N, nS * nSh))
    trajectory = _default_trajectory(N, nLine)

    summary = {
        "file_path": str(file_path),
        "N": N,
        "nLine": nLine,
        "nShot": nShot,
        "nSeg": nSeg,
        "nPar": nPar,
        "nCh": nCh,
        "nEcho": nEcho,
        "FoV": fov.tolist(),
        "FoV_recon": fov_recon.tolist(),
        "shotOff": shot_off,
        "nShotOff": nShotOff,
        "selfNav_flag": self_nav_flag,
        "y_shape": tuple(int(x) for x in y.shape),
        "trajectory_shape": tuple(int(x) for x in trajectory.shape),
    }
    return {
        "summary": summary,
        "y": y,
        "trajectory": trajectory,
    }
