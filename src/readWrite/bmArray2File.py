"""Write NumPy arrays to disk in a MATLAB-compatible spirit."""
from __future__ import annotations

from pathlib import Path
import numpy as np


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _write_header_txt(header_path: Path, arr: np.ndarray) -> None:
    lines = [
        str(arr.ndim),
        " ".join(str(x) for x in arr.shape),
        str(arr.size),
    ]
    header_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def bmArray2File(argDir, argName, argArray, argChar, argType):
    """Persist an array with simple text/csv/binary options.

    Parameters follow the MATLAB signature:
    - argChar='t' -> text with metadata header + flattened values
    - argChar='c' -> csv (2D) or flattened csv
    - argChar in {'d','m'} -> binary .dat + text .hdat header
    - argChar='s' -> standalone loader script with embedded flattened data
    """
    out_dir = Path(argDir)
    _ensure_dir(out_dir)
    arr = np.asarray(argArray)
    stem = str(argName)
    mode = str(argChar).lower()

    if mode == "t":
        out = out_dir / f"{stem}.txt"
        with out.open("w", encoding="utf-8") as f:
            f.write(f"{arr.ndim}\n")
            f.write(" ".join(str(x) for x in arr.shape) + "\n")
            f.write(f"{arr.size}\n")
            np.savetxt(f, arr.reshape(1, -1), fmt="%.17g")
        return

    if mode == "c":
        out = out_dir / f"{stem}.csv"
        if arr.ndim <= 2:
            np.savetxt(out, arr, delimiter=",", fmt="%.17g")
        else:
            np.savetxt(out, arr.reshape(arr.shape[0], -1), delimiter=",", fmt="%.17g")
        return

    if mode in {"d", "m"}:
        hdr = out_dir / f"{stem}.hdat"
        dat = out_dir / f"{stem}.dat"
        _write_header_txt(hdr, arr)
        np.asarray(arr).astype(np.dtype(argType)).tofile(dat)
        if mode == "m":
            loader = out_dir / f"{stem}_LOAD.py"
            loader.write_text(
                "\n".join(
                    [
                        "import numpy as np",
                        f"shape = {tuple(arr.shape)}",
                        f"dtype = np.dtype('{argType}')",
                        f"data = np.fromfile(r'{dat.as_posix()}', dtype=dtype).reshape(shape)",
                        "",
                    ]
                ),
                encoding="utf-8",
            )
        return

    if mode == "s":
        loader = out_dir / f"{stem}_LOAD.py"
        flat = arr.reshape(-1)
        loader.write_text(
            "\n".join(
                [
                    "import numpy as np",
                    f"shape = {tuple(arr.shape)}",
                    f"data = np.array({flat.tolist()}, dtype=np.float64).reshape(shape)",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        return

    raise ValueError(f"Unsupported argChar mode: {argChar}")
