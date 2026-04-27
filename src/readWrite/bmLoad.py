from numpy import loadtxt
import sys
sys.path.append('..')  # Add parent directory to the module search path

def bmLoad(arg_file):
    temp_load = loadtxt(f"{arg_file}.mat", dtype=object)
    temp_name = list(temp_load.dtype.names)

    if not temp_name:
        raise ValueError("No data fields found in the .mat file.")

    out = temp_load[temp_name[0]]  # Assuming only one field in the MATLAB struct

    return out
