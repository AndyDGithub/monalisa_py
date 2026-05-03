import os
from third_part.matlab_compat.matlab_native import addpath, fullfile
from src.geom123 import bmTraj  # ensure submodule is loaded

def setup_test_path():
    """
    Set up test path by adding CI directory to MATLAB path.
    """
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    ci_dir = os.path.join(tests_dir, "ci")
    addpath(fullfile(ci_dir))

# Auto-generated entrypoint alias for import compatibility
TestMathOpUnit = setup_test_path
