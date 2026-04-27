"""
Parity execution test for binnings_script.

Runs the Python binnings_script and verifies that its outputs match the
SHA-256 fingerprints recorded from the reference MATLAB implementation.
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from pathlib import Path
import numpy as np
import pytest

from tests.parity import load_parity_data, check_fingerprint, matlab_fingerprint

# Path to the data directory
_MONALISA_PY_ROOT = Path(__file__).parents[2]
_MONALISA_ROOT = _MONALISA_PY_ROOT.parent / "monalisa"
_DATA_DIR = _MONALISA_ROOT / "demo" / "data_demo" / "data_8_tutorial_1"
_BRAIN_SCAN = _DATA_DIR / "brainScan.dat"

pytestmark = pytest.mark.skipif(
    not _BRAIN_SCAN.exists(),
    reason=f"brainScan.dat not found at {_BRAIN_SCAN}",
)


def _get_timestamp_ms(data_dir):
    """Compute timestampMs the same way binnings_script.m does."""
    from src.rawDataReader.createRawDataReader import createRawDataReader
    brain_scan_file = str(Path(data_dir) / "brainScan.dat")
    reader = createRawDataReader(brain_scan_file, False)
    p = reader.acquisitionParams
    timestamp = np.array(p.timestamp, dtype=np.float64)
    timestamp = timestamp - np.min(timestamp)
    timestampMs = timestamp * 2.5  # costTime = 2.5 ms/tick
    return timestampMs


class TestBinningsExecution:

    @pytest.fixture(scope="class")
    def script_outputs(self):
        """Run binnings_script once and return (allLines_mask, sequential_mask)."""
        import tempfile
        from demo.script_demo.script_tutorial_1.binnings_script import binnings_script
        with tempfile.TemporaryDirectory() as tmp:
            allLines_mask, sequential_mask = binnings_script(
                data_dir=str(_DATA_DIR),
                results_dir=tmp,
            )
        return allLines_mask, sequential_mask

    @pytest.fixture(scope="class")
    def timestamp_ms(self):
        """Compute timestampMs from the reader."""
        return _get_timestamp_ms(str(_DATA_DIR))

    # ------------------------------------------------------------------
    # Step 1: allLines binning
    # ------------------------------------------------------------------

    def test_allLines_mask_shape(self, script_outputs):
        allLines_mask, _ = script_outputs
        assert allLines_mask.shape == (1, 45210), (
            f"Expected (1, 45210), got {allLines_mask.shape}"
        )

    def test_allLines_mask_dtype(self, script_outputs):
        allLines_mask, _ = script_outputs
        assert allLines_mask.dtype == bool, f"Expected bool, got {allLines_mask.dtype}"

    def test_allLines_mask_fingerprint(self, script_outputs):
        allLines_mask, _ = script_outputs
        _, var_metas = load_parity_data("binnings", "allLines")
        stored = {v["name"]: v for v in var_metas}
        assert check_fingerprint(allLines_mask, stored["mask"]), (
            "allLines mask fingerprint does not match MATLAB parity"
        )

    def test_allLines_timestampMs_fingerprint(self, timestamp_ms):
        _, var_metas = load_parity_data("binnings", "allLines")
        stored = {v["name"]: v for v in var_metas}
        # MATLAB stores timestampMs as a row vector (1, nLines); flatten for comparison
        ts = timestamp_ms.ravel()
        assert check_fingerprint(ts, stored["timestampMs"]), (
            "timestampMs fingerprint does not match MATLAB parity\n"
            f"  Python  first 5: {ts[:5]}\n"
            f"  Python  last  5: {ts[-5:]}\n"
            f"  Expected sha256: {stored['timestampMs']['sha256']}\n"
            f"  Got      sha256: {matlab_fingerprint(ts, 'double', False)}"
        )

    # ------------------------------------------------------------------
    # Step 2: sequential binning
    # ------------------------------------------------------------------

    def test_sequential_mask_shape(self, script_outputs):
        _, sequential_mask = script_outputs
        assert sequential_mask.ndim == 2
        assert sequential_mask.shape[1] == 45210, (
            f"Expected 45210 columns, got {sequential_mask.shape[1]}"
        )
        assert sequential_mask.shape[0] == 71, (
            f"Expected 71 rows, got {sequential_mask.shape[0]}"
        )

    def test_sequential_mask_dtype(self, script_outputs):
        _, sequential_mask = script_outputs
        assert sequential_mask.dtype == bool

    def test_sequential_mask_fingerprint(self, script_outputs):
        _, sequential_mask = script_outputs
        _, var_metas = load_parity_data("binnings", "sequential")
        stored = {v["name"]: v for v in var_metas}
        assert check_fingerprint(sequential_mask, stored["mask"]), (
            "Sequential mask fingerprint does not match MATLAB parity\n"
            f"  shape: {sequential_mask.shape}\n"
            f"  Expected sha256: {stored['mask']['sha256']}\n"
            f"  Got      sha256: {matlab_fingerprint(sequential_mask, 'logical', False)}"
        )
