import gzip
import hashlib
import io
import json
from pathlib import Path

import numpy as np
import scipy.io as sio


PARITY_ROOT = Path(__file__).parents[2] / "parity"


def _matlab_dtype(class_name, is_complex):
    mapping = {
        "double": np.complex128 if is_complex else np.float64,
        "single": np.complex64 if is_complex else np.float32,
        "logical": np.bool_,
        "uint8": np.uint8,
        "int32": np.int32,
        "uint32": np.uint32,
    }
    return mapping.get(class_name)


def matlab_fingerprint(arr, class_name, is_complex=None):
    """Compute SHA-256 fingerprint matching MATLAB parityFingerprintVariable.m."""
    arr = np.asarray(arr)

    if class_name == "cell" or arr.dtype == object:
        # Recursively fingerprint each cell element, join sha256s with '|', then hash
        parts = []
        for elem in arr.ravel(order="F"):
            sub = np.asarray(elem)
            sub_class = _numpy_to_matlab_class(sub)
            sub_is_complex = np.iscomplexobj(sub)
            parts.append(matlab_fingerprint(sub, sub_class, sub_is_complex))
        joined = "|".join(parts) + "|"
        return hashlib.sha256(joined.encode("ascii")).hexdigest()

    if is_complex is None:
        is_complex = np.iscomplexobj(arr)
    arr_f = np.asfortranarray(arr)
    h = hashlib.sha256()
    if class_name == "logical" or np.issubdtype(arr.dtype, np.bool_):
        h.update(arr_f.ravel(order="F").astype(np.uint8).tobytes())
    elif is_complex:
        h.update(arr_f.ravel(order="F").real.tobytes())
        h.update(arr_f.ravel(order="F").imag.tobytes())
    else:
        h.update(arr_f.ravel(order="F").tobytes())
    return h.hexdigest()


def _numpy_to_matlab_class(arr):
    dtype = arr.dtype
    if np.issubdtype(dtype, np.bool_):
        return "logical"
    if dtype in (np.float64, np.complex128):
        return "double"
    if dtype in (np.float32, np.complex64):
        return "single"
    if dtype == np.uint8:
        return "uint8"
    if dtype == np.int32:
        return "int32"
    if dtype == np.uint32:
        return "uint32"
    return "double"


def load_parity_data(script_name, step_name):
    """Load parity data for a given script/step. Returns (mat_vars, fingerprints)."""
    folder = PARITY_ROOT / script_name
    # Find the step folder
    step_folder = None
    for d in sorted(folder.iterdir()):
        if d.is_dir() and step_name in d.name:
            step_folder = d
            break
    if step_folder is None:
        raise FileNotFoundError(f"Parity step {step_name!r} not found in {folder}")

    with open(step_folder / "fingerprints.json") as f:
        fps = json.load(f)

    mat_path = step_folder / "data.mat.gz"
    mat_vars = {}
    if mat_path.exists():
        with gzip.open(mat_path, "rb") as f:
            raw = sio.loadmat(io.BytesIO(f.read()))
        for k, v in raw.items():
            if not k.startswith("_"):
                mat_vars[k] = v

    return mat_vars, fps["variables"]


def check_fingerprint(arr, var_meta):
    """Return True if arr matches the stored SHA256 fingerprint."""
    class_name = var_meta["class"]
    is_complex = var_meta["is_complex"]
    expected = var_meta["sha256"]
    arr = np.asarray(arr)
    if class_name != "cell" and arr.dtype != object:
        dtype = _matlab_dtype(class_name, is_complex)
        if dtype is not None:
            arr = arr.astype(dtype)
    return matlab_fingerprint(arr, class_name, is_complex) == expected
