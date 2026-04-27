import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
import pytest
from tests.parity import load_parity_data, check_fingerprint


def test_binnings_allLines_stored_vars():
    """Verify that parity data for binnings/allLines can be loaded and fingerprinted."""
    mat_vars, var_metas = load_parity_data("binnings", "allLines")
    stored = {v["name"]: v for v in var_metas}

    # Check each variable that is stored in the mat file
    for name, arr in mat_vars.items():
        if name not in stored:
            continue
        assert check_fingerprint(arr, stored[name]), (
            f"Fingerprint mismatch for {name}"
        )


def test_binnings_sequential_stored_vars():
    mat_vars, var_metas = load_parity_data("binnings", "sequential")
    stored = {v["name"]: v for v in var_metas}
    for name, arr in mat_vars.items():
        if name not in stored:
            continue
        assert check_fingerprint(arr, stored[name]), f"Fingerprint mismatch for {name}"


def test_mitosius_prepared_data_stored_vars():
    """Verify that the MATLAB-generated mitosius parity data is self-consistent."""
    mat_vars, var_metas = load_parity_data("mitosius", "prepared_data")
    stored = {v["name"]: v for v in var_metas}
    for name, arr in mat_vars.items():
        if name not in stored:
            continue
        assert check_fingerprint(arr, stored[name]), f"Fingerprint mismatch for {name}"


def test_coilSensitivity_stored_vars():
    mat_vars, var_metas = load_parity_data("coilSensitivityEstimation", "final_outputs")
    stored = {v["name"]: v for v in var_metas}
    for name, arr in mat_vars.items():
        if name not in stored:
            continue
        assert check_fingerprint(arr, stored[name]), f"Fingerprint mismatch for {name}"


def test_reconstructions_stored_vars():
    mat_vars, var_metas = load_parity_data("reconstructions", "final_reconstructions")
    stored = {v["name"]: v for v in var_metas}
    for name, arr in mat_vars.items():
        if name not in stored:
            continue
        assert check_fingerprint(arr, stored[name]), f"Fingerprint mismatch for {name}"
