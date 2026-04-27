from third_part.matlab_compat.matlab_native import addpath, fullfile

def setup_test_path():
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    ci_dir = os.path.join(tests_dir, "ci")
    addpath(fullfile(ci_dir))

# Auto-generated entrypoint alias for import compatibility
TestMathOpUnit = setup_test_path
