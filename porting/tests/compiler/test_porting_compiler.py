from pathlib import Path

from monalisa_py.porting.scripts.porting_compiler import parse_decl, matlab_line_to_python, DEFAULT_NATIVE_MAP


def test_parse_decl_with_inputs_outputs():
    line = "function [img, meta] = reconstruct(kspace, cfg)"
    name, args, returns = parse_decl(line)
    assert name == "reconstruct"
    assert args == ["kspace", "cfg"]
    assert returns == ["img", "meta"]


def test_matlab_native_rewrite():
    line = "x = zeros(4, 4);"
    py = matlab_line_to_python(line, DEFAULT_NATIVE_MAP)
    assert py == "x = np.zeros(4, 4)"
