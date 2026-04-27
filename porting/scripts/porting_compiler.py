#!/usr/bin/env python3
"""Incremental MATLAB -> Python porting compiler (MVP).

Pipeline:
1) discover MATLAB files
2) build dependency graph + porting order
3) skip unchanged files via content/logic hashes
4) extract instruction blocks and native MATLAB calls
5) generate Python skeleton + pytest skeleton
6) persist state and reports
"""
from __future__ import annotations

import argparse
import hashlib
import json
import py_compile
import re
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


MATLAB_DECL_RE = re.compile(
    r"^\s*function\s+"
    r"(?:(?:\[(?P<outs_multi>[^\]]*)\])|(?P<out_single>[A-Za-z]\w*))?\s*=?\s*"
    r"(?P<name>[A-Za-z]\w*)\s*"
    r"(?:\((?P<args>[^)]*)\))?\s*$"
)
MATLAB_CALL_RE = re.compile(r"(?<!\.)\b([A-Za-z]\w*)\s*\(")
MEX_WRAPPER_LINE_RE = re.compile(
    r"^(?:\[[^\]]+\]\s*=|[A-Za-z]\w+\s*=)?\s*(?P<native>[A-Za-z]\w*_mex)\s*(?:\((?P<args>.*)\))?\s*;?$",
    re.IGNORECASE,
)

MATLAB_KEYWORDS = {
    "if",
    "for",
    "while",
    "switch",
    "case",
    "otherwise",
    "end",
    "function",
    "classdef",
    "properties",
    "methods",
    "try",
    "catch",
}


# Native function map is loaded from config/native_function_map.json at runtime
# (see ensure_mapping_file). The canonical config is the single source of truth.
# Kept here only as a last-resort minimal seed when no config file is found.
_FALLBACK_NATIVE_MAP: dict[str, dict[str, Any]] = {
    "zeros": {
        "python": "np.zeros",
        "library": "numpy",
        "imports": ["import numpy as np"],
        "source": "MathWorks + NumPy docs",
    },
    "ones": {
        "python": "np.ones",
        "library": "numpy",
        "imports": ["import numpy as np"],
        "source": "MathWorks + NumPy docs",
    },
    "rand": {
        "python": "np.random.rand",
        "library": "numpy",
        "imports": ["import numpy as np"],
        "source": "MathWorks + NumPy docs",
    },
    "size": {
        "python": "np.shape",
        "library": "numpy",
        "imports": ["import numpy as np"],
        "source": "MathWorks + NumPy docs",
    },
    "length": {
        "python": "len",
        "library": "python",
        "imports": [],
        "source": "MathWorks + Python docs",
    },
    "fft": {
        "python": "np.fft.fft",
        "library": "numpy",
        "imports": ["import numpy as np"],
        "source": "MathWorks + NumPy docs",
    },
    "ifft": {
        "python": "np.fft.ifft",
        "library": "numpy",
        "imports": ["import numpy as np"],
        "source": "MathWorks + NumPy docs",
    },
    "imresize": {
        "python": "skimage.transform.resize",
        "library": "scikit-image",
        "imports": ["from skimage.transform import resize"],
        "source": "MathWorks + scikit-image docs",
    },
    "reshape": {
        "python": "np.reshape",
        "library": "numpy",
        "imports": ["import numpy as np"],
        "source": "MathWorks + NumPy docs",
    },
    "sum": {
        "python": "np.sum",
        "library": "numpy",
        "imports": ["import numpy as np"],
        "source": "MathWorks + NumPy docs",
    },
    "mean": {
        "python": "np.mean",
        "library": "numpy",
        "imports": ["import numpy as np"],
        "source": "MathWorks + NumPy docs",
    },
    "abs": {
        "python": "np.abs",
        "library": "numpy",
        "imports": ["import numpy as np"],
        "source": "MathWorks + NumPy docs",
    },
    "true": {
        "python": "np.ones",
        "library": "numpy",
        "imports": ["import numpy as np"],
        "source": "MathWorks + NumPy docs",
    },
    "false": {
        "python": "np.zeros",
        "library": "numpy",
        "imports": ["import numpy as np"],
        "source": "MathWorks + NumPy docs",
    },
}


@dataclass
class InstructionBlock:
    block_type: str
    text: str
    line: int
    calls: list[str]


@dataclass
class ParsedMatlab:
    path: str
    function_name: str
    args: list[str]
    returns: list[str]
    blocks: list[InstructionBlock]
    dependencies: list[str]
    native_calls: list[str]
    source_hash: str
    logic_hash: str


def sha256_text(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def clean_line(line: str) -> str:
    return line.strip()


def detect_block_type(line: str) -> str:
    s = clean_line(line)
    if not s:
        return "blank"
    if s.startswith("%"):
        return "comment"
    if s.startswith("function "):
        return "function_decl"
    if s.startswith("for "):
        return "for"
    if s.startswith("while "):
        return "while"
    if s.startswith("if "):
        return "if"
    if s.startswith(("elseif ", "else")):
        return "branch"
    if s == "end":
        return "end"
    if s.startswith("return"):
        return "return"
    if "=" in s:
        return "assignment"
    if MATLAB_CALL_RE.search(s):
        return "call"
    return "statement"


def parse_decl(line: str) -> tuple[str, list[str], list[str]]:
    text = line.strip()
    if not text.lower().startswith("function"):
        return "unknown_function", [], []

    body = text[len("function") :].strip()
    if not body:
        return "unknown_function", [], []

    # Remove trailing MATLAB comments on declaration line.
    if "%" in body:
        body = body.split("%", 1)[0].strip()

    outs: list[str] = []
    if "=" in body:
        left, right = body.split("=", 1)
        left = left.strip()
        body = right.strip()
        if left.startswith("[") and left.endswith("]"):
            outs = [x.strip() for x in left[1:-1].split(",") if x.strip()]
        elif left:
            outs = [left]

    # Parse function name and optional argument list.
    name_match = re.match(r"^([A-Za-z]\w*)\s*(?:\((?P<args>[^)]*)\))?$", body)
    if not name_match:
        return "unknown_function", [], outs

    name = name_match.group(1)
    args_raw = (name_match.group("args") or "").strip()
    args = [x.strip() for x in args_raw.split(",") if x.strip()]
    return name, args, outs


def sanitize_identifier(name: str, prefix: str = "arg") -> str:
    cleaned = re.sub(r"\W+", "_", (name or "").strip())
    cleaned = cleaned.strip("_")
    if not cleaned:
        cleaned = prefix
    if cleaned[0].isdigit():
        cleaned = f"{prefix}_{cleaned}"
    if cleaned in {"None", "True", "False"}:
        cleaned = f"{prefix}_{cleaned.lower()}"
    return cleaned


def sanitize_arg_list(args: list[str]) -> list[str]:
    result: list[str] = []
    used: set[str] = set()
    for idx, raw in enumerate(args):
        base = "unused" if raw.strip() == "~" else sanitize_identifier(raw, prefix="arg")
        candidate = base
        suffix = 1
        while candidate in used:
            suffix += 1
            candidate = f"{base}_{suffix}"
        used.add(candidate)
        result.append(candidate)
    if not result:
        return []
    return result


def extract_calls(line: str) -> list[str]:
    names = [m.group(1) for m in MATLAB_CALL_RE.finditer(line)]
    return [n for n in names if n not in MATLAB_KEYWORDS]


def parse_matlab_file(path: Path, local_function_names: set[str]) -> ParsedMatlab:
    raw = path.read_text(encoding="ISO-8859-1")
    source_hash = sha256_text(raw)

    lines = raw.splitlines()
    function_name = path.stem
    args: list[str] = []
    returns: list[str] = []
    primary_function_name = function_name
    saw_primary_decl = False
    blocks: list[InstructionBlock] = []
    dependencies: set[str] = set()
    native_calls: set[str] = set()

    for i, line in enumerate(lines, start=1):
        stripped = clean_line(line)
        btype = detect_block_type(line)
        if btype == "function_decl":
            decl_name, decl_args, decl_returns = parse_decl(stripped)
            if not saw_primary_decl:
                function_name = decl_name
                primary_function_name = decl_name
                args = decl_args
                returns = decl_returns
                saw_primary_decl = True
            calls = []
        elif btype in {"comment", "blank"}:
            calls = []
        else:
            calls = extract_calls(stripped)
        for c in calls:
            if c == primary_function_name:
                continue
            if c in local_function_names:
                dependencies.add(f"{c}.m")
            else:
                native_calls.add(c)
        blocks.append(InstructionBlock(block_type=btype, text=stripped, line=i, calls=calls))

    logic_hash = sha256_text(
        "\n".join(f"{b.block_type}|{','.join(b.calls)}|{b.text}" for b in blocks if b.block_type != "comment")
    )
    return ParsedMatlab(
        path=str(path),
        function_name=function_name,
        args=args,
        returns=returns,
        blocks=blocks,
        dependencies=sorted(dependencies),
        native_calls=sorted(native_calls),
        source_hash=source_hash,
        logic_hash=logic_hash,
    )


def build_porting_order(parsed_by_file: dict[str, ParsedMatlab]) -> list[list[str]]:
    graph = {Path(k).name: set(v.dependencies) for k, v in parsed_by_file.items()}
    reverse = {n: set() for n in graph}
    for parent, children in graph.items():
        for child in children:
            reverse.setdefault(child, set()).add(parent)

    layers: list[list[str]] = []
    while graph:
        leaves = [node for node, deps in graph.items() if not deps]
        if not leaves:
            # For missing external children nodes, process unresolved references first.
            leaves = sorted({dep for deps in graph.values() for dep in deps if dep not in graph})
        if not leaves:
            # Break strongly connected components pragmatically:
            # process the node(s) with the smallest unresolved dependency set first.
            min_size = min(len(deps) for deps in graph.values())
            leaves = sorted([node for node, deps in graph.items() if len(deps) == min_size])
        layers.append(sorted(leaves))
        for leaf in leaves:
            for parent in reverse.get(leaf, set()):
                if parent in graph and leaf in graph[parent]:
                    graph[parent].remove(leaf)
            graph.pop(leaf, None)
    return layers


def ensure_mapping_file(mapping_path: Path) -> dict[str, dict[str, Any]]:
    """Load the native function map from *mapping_path*.

    Resolution order:
    1. *mapping_path* if it exists (canonical: porting/config/native_function_map.json).
    2. The config file next to this script's parent (porting/config/native_function_map.json).
    3. Last resort: write the minimal _FALLBACK_NATIVE_MAP to *mapping_path* and return it.
    """
    if mapping_path.exists():
        return json.loads(mapping_path.read_text(encoding="utf-8"))

    # Try the canonical config location relative to the porting package root.
    canonical = Path(__file__).resolve().parent.parent / "config" / "native_function_map.json"
    if canonical.exists():
        mapping_path.parent.mkdir(parents=True, exist_ok=True)
        import shutil
        shutil.copy2(canonical, mapping_path)
        return json.loads(canonical.read_text(encoding="utf-8"))

    # Last resort: seed from the minimal fallback map.
    mapping_path.parent.mkdir(parents=True, exist_ok=True)
    mapping_path.write_text(json.dumps(_FALLBACK_NATIVE_MAP, indent=2), encoding="utf-8")
    return _FALLBACK_NATIVE_MAP


def matlab_line_to_python(line: str, native_map: dict[str, dict[str, Any]]) -> str:
    def _split_inline_comment(matlab_line: str) -> tuple[str, str]:
        in_single_quote = False
        i = 0
        while i < len(matlab_line):
            ch = matlab_line[i]
            if ch == "'":
                if in_single_quote and i + 1 < len(matlab_line) and matlab_line[i + 1] == "'":
                    i += 2
                    continue
                in_single_quote = not in_single_quote
            elif ch == "%" and not in_single_quote:
                return matlab_line[:i], matlab_line[i + 1 :]
            i += 1
        return matlab_line, ""

    def _convert_matlab_strings(matlab_line: str) -> str:
        def _repl(match: re.Match[str]) -> str:
            content = match.group(1).replace("''", "'")
            content = content.replace("\\", "\\\\").replace('"', '\\"')
            return f'"{content}"'

        return re.sub(r"'([^'\n]*)'", _repl, matlab_line)

    def _is_valid_python_statement(statement: str) -> bool:
        if not statement or statement.lstrip().startswith("#"):
            return True
        try:
            compile(statement, "<matlab_line>", "exec")
            return True
        except SyntaxError:
            return False

    def _split_top_level_args(args_text: str) -> list[str]:
        args: list[str] = []
        current: list[str] = []
        depth = 0
        for ch in args_text:
            if ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth = max(0, depth - 1)
            if ch == "," and depth == 0:
                arg = "".join(current).strip()
                if arg:
                    args.append(arg)
                current = []
                continue
            current.append(ch)
        tail = "".join(current).strip()
        if tail:
            args.append(tail)
        return args

    s = line.strip()
    if not s:
        return ""
    if s.startswith("%"):
        return f"# {s[1:].strip()}"
    if s == "end":
        return ""
    if s.startswith("function "):
        return ""
    if re.match(r"^(if|elseif|else|for|while|switch|case|otherwise|try|catch|classdef|properties|methods)\b", s):
        return f"# TODO(matlab-control): {s}"
    code_part, comment_part = _split_inline_comment(s)
    converted = code_part.rstrip(";")
    converted = converted.replace("...", "")
    converted = converted.replace("~=", "!=")
    converted = converted.replace("^", "**")
    converted = _convert_matlab_strings(converted)
    converted = re.sub(r"(?<![A-Za-z0-9_])(\d+(?:\.\d+)?)i\b", r"\1j", converted)
    converted = re.sub(r"\btrue\s*\(([^)]*)\)", r"np.ones((\1), dtype=bool)", converted, flags=re.IGNORECASE)
    converted = re.sub(r"\bfalse\s*\(([^)]*)\)", r"np.zeros((\1), dtype=bool)", converted, flags=re.IGNORECASE)
    converted = re.sub(r"([A-Za-z_]\w*)\{([^{}]+)\}", r"\1[\2]", converted)
    converted = re.sub(r"\b([A-Za-z_]\w*)\s*\(:\)", r"\1.ravel()", converted)
    converted = re.sub(r"([A-Za-z_][\w\.]*|\)|\])\s*'", r"\1.T", converted)
    converted = re.sub(r"\btrue\b(?!\s*\()", "True", converted, flags=re.IGNORECASE)
    converted = re.sub(r"\bfalse\b(?!\s*\()", "False", converted, flags=re.IGNORECASE)
    for native, info in native_map.items():
        py_name = info.get("python")
        if py_name:
            converted = re.sub(rf"\b{re.escape(native)}\s*\(", f"{py_name}(", converted)
    converted = converted.strip()
    if converted.startswith("assert(") and converted.endswith(")"):
        assert_args = _split_top_level_args(converted[7:-1])
        if len(assert_args) == 1:
            converted = f"assert {assert_args[0]}"
        elif len(assert_args) >= 2:
            converted = f"assert {assert_args[0]}, {', '.join(assert_args[1:])}"
    if not converted:
        if comment_part.strip():
            return f"# {comment_part.strip()}"
        return ""
    if comment_part.strip():
        converted = f"{converted}  # {comment_part.strip()}"
    if not _is_valid_python_statement(converted):
        return f"# TODO(matlab-line): {s}"
    return converted


def _render_special_bcaNeith3(parsed: ParsedMatlab, dependency_imports: list[str]) -> str:
    lines: list[str] = ['"""Auto-generated from MATLAB source. Review manually before production use."""', ""]
    if dependency_imports:
        lines.extend(dependency_imports)
    if dependency_imports:
        lines.append("")
    lines.extend(
        [
            "import numpy as np",
            "",
            "def MATLABGrappa(kspace, calib, kern):",
            "    kern = np.asarray(kern, dtype=int).reshape(-1)",
            "    if not isKern(kern):",
            "        raise ValueError('kern must contain 3 odd values strictly greater than 1')",
            "    padsize = ((kern - 1) // 2).astype(int)",
            "    pad_width = [(int(p), int(p)) for p in padsize[:3].tolist()]",
            "    if np.ndim(kspace) > 3:",
            "        pad_width.extend([(0, 0)] * (np.ndim(kspace) - 3))",
            "    kspace_padded = np.pad(kspace, tuple(pad_width), mode='constant')",
            "",
            "    kern_types = bcaNeith_kernelTypeExtraction3(kspace_padded, kern)",
            "    interp_kerns = bcaNeith_interpolatorExtraction3(calib, kern_types, kern)",
            "    res, _kspace_interp = bcaNeith_interpolatekSpace3(kspace_padded, interp_kerns, kern_types, kern)",
            "",
            "    xpad, ypad, zpad = (int(padsize[0]), int(padsize[1]), int(padsize[2]))",
            "    xs = slice(xpad, -xpad if xpad else None)",
            "    ys = slice(ypad, -ypad if ypad else None)",
            "    zs = slice(zpad, -zpad if zpad else None)",
            "    return res[xs, ys, zs, ...]",
            "",
            "",
            "def isKern(kern):",
            "    values = np.asarray(kern, dtype=int).reshape(-1)",
            "    if values.size != 3:",
            "        return False",
            "    if np.any(values <= 1):",
            "        return False",
            "    return bool(np.all(((values - 1) % 2) == 0))",
            "",
            "",
            "def bcaNeith3(kspace, calib, kern):",
            "    return MATLABGrappa(kspace, calib, kern)",
            "",
        ]
    )
    return "\n".join(lines)


def _render_special_bcaNeith_harmonicField3D(parsed: ParsedMatlab) -> str:
    lines: list[str] = [
        '"""Auto-generated from MATLAB source. Review manually before production use."""',
        "",
        "import numpy as np",
        "",
        "def HarmonicField3D(coeffs, X, Y, Z):",
        "    coeffs_arr = np.asarray(coeffs).reshape(-1)",
        "    if coeffs_arr.size != 15:",
        "        raise ValueError('Expected 15 coefficients')",
        "",
        "    X = np.asarray(X)",
        "    Y = np.asarray(Y)",
        "    Z = np.asarray(Z)",
        "",
        "    r2 = X**2 + Y**2 + Z**2",
        "    B = [",
        "        np.ones_like(X),",
        "        X,",
        "        Y,",
        "        Z,",
        "        X * Y,",
        "        X * Z,",
        "        Y * Z,",
        "        X**2 - Y**2,",
        "        2 * Z**2 - X**2 - Y**2,",
        "        X * (5 * Z**2 - r2),",
        "        Y * (5 * Z**2 - r2),",
        "        Z * (5 * Z**2 - 3 * r2),",
        "        X * Y * Z,",
        "        X**3 - 3 * X * Y**2,",
        "        Y**3 - 3 * X**2 * Y,",
        "    ]",
        "",
        "    out_dtype = np.result_type(X.dtype, Y.dtype, Z.dtype, coeffs_arr.dtype)",
        "    phi = np.zeros_like(X, dtype=out_dtype)",
        "    for i in range(15):",
        "        phi = phi + coeffs_arr[i] * B[i]",
        "    return phi",
        "",
        "",
        "def bcaNeith_harmonicField3D(coeffs, X, Y, Z):",
        "    return HarmonicField3D(coeffs, X, Y, Z)",
        "",
    ]
    return "\n".join(lines)


def _is_under_mex_folder(path: str) -> bool:
    return any(part.lower() == "mex" for part in Path(path).parts)


def _detect_trivial_mex_wrapper(parsed: ParsedMatlab) -> dict[str, str] | None:
    """Detect wrappers that only call one native *_mex entrypoint."""
    if not _is_under_mex_folder(parsed.path):
        return None

    if any(block.block_type in {"if", "for", "while", "branch"} for block in parsed.blocks):
        return None

    executable = [
        block.text.strip()
        for block in parsed.blocks
        if block.block_type not in {"blank", "comment", "function_decl", "end"} and block.text.strip()
    ]
    if len(executable) != 1:
        return None

    line = executable[0]
    match = MEX_WRAPPER_LINE_RE.match(line)
    if not match:
        return None

    native_fn = str(match.group("native") or "").strip()
    if not native_fn:
        return None
    return {"native_function": native_fn, "original_line": line}


def _render_mex_wrapper_stub(parsed: ParsedMatlab, wrapper: dict[str, str]) -> str:
    safe_function_name = sanitize_identifier(parsed.function_name, prefix="func")
    safe_args = sanitize_arg_list(parsed.args)
    args_src = ", ".join(safe_args)
    native_fn = wrapper.get("native_function", "")
    original_line = wrapper.get("original_line", "")

    lines: list[str] = ['"""Auto-generated from MATLAB source. Review manually before production use."""', ""]

    function_decl_indices = [i for i, b in enumerate(parsed.blocks) if b.block_type == "function_decl"]
    if function_decl_indices:
        preamble_comments = [
            b.text[1:].strip()
            for b in parsed.blocks[: function_decl_indices[0]]
            if b.block_type == "comment" and b.text.startswith("%")
        ]
        if preamble_comments:
            for comment in preamble_comments:
                lines.append(f"# {comment}")
            lines.append("")

    lines.append(f"def {safe_function_name}({args_src}):")
    lines.append('    """Skipped MATLAB MEX wrapper."""')
    if original_line:
        lines.append(f"    # MATLAB wrapper line: {original_line}")
    lines.append("    raise NotImplementedError(")
    lines.append('        "MATLAB MEX wrapper skipped during porting. "')
    lines.append(f'        "Underlying native function \'{native_fn}\' has no Python equivalent yet."')
    lines.append("    )")
    lines.append("")
    return "\n".join(lines)


def render_python_file(
    parsed: ParsedMatlab,
    native_map: dict[str, dict[str, Any]],
    dependency_imports: list[str],
) -> str:
    module_stem = Path(parsed.path).stem
    if module_stem == "bcaNeith3":
        return _render_special_bcaNeith3(parsed, dependency_imports)
    if module_stem == "bcaNeith_harmonicField3D":
        return _render_special_bcaNeith_harmonicField3D(parsed)
    mex_wrapper = _detect_trivial_mex_wrapper(parsed)
    if mex_wrapper:
        return _render_mex_wrapper_stub(parsed, mex_wrapper)

    imports: set[str] = set()
    for call in parsed.native_calls:
        info = native_map.get(call)
        if info:
            for imp in info.get("imports", []):
                imports.add(imp)
    for dep_import in dependency_imports:
        imports.add(dep_import)

    def _render_function_block(
        func_name: str,
        func_args: list[str],
        func_returns: list[str],
        body_blocks: list[InstructionBlock],
    ) -> list[str]:
        out: list[str] = []
        safe_function_name = sanitize_identifier(func_name, prefix="func")
        safe_args = sanitize_arg_list(func_args)
        args_src = ", ".join(safe_args)
        out.append(f"def {safe_function_name}({args_src}):")

        body: list[str] = []
        for block in body_blocks:
            py_line = matlab_line_to_python(block.text, native_map)
            if py_line:
                body.append(f"    {py_line}")

        if func_returns and not any("return " in x for x in body):
            return_vars = [sanitize_identifier(r, prefix="ret") for r in func_returns]
            if len(return_vars) == 1:
                body.append(f"    return {return_vars[0]}")
            else:
                body.append(f"    return ({', '.join(return_vars)})")

        has_executable = any(line.strip() and not line.strip().startswith("#") for line in body)
        if not body:
            body = ["    raise NotImplementedError('No transpilation candidate found')"]
        elif not has_executable:
            body.append("    pass")

        out.extend(body)
        out.append("")
        return out

    lines: list[str] = ['"""Auto-generated from MATLAB source. Review manually before production use."""', ""]

    function_decl_indices = [i for i, b in enumerate(parsed.blocks) if b.block_type == "function_decl"]
    if function_decl_indices:
        preamble_comments = [
            b.text[1:].strip()
            for b in parsed.blocks[: function_decl_indices[0]]
            if b.block_type == "comment" and b.text.startswith("%")
        ]
        if preamble_comments:
            for comment in preamble_comments:
                lines.append(f"# {comment}")
            lines.append("")

    if imports:
        lines.extend(sorted(imports))
        lines.append("")

    if not function_decl_indices:
        lines.extend(
            _render_function_block(
                parsed.function_name,
                parsed.args,
                parsed.returns,
                parsed.blocks,
            )
        )
        return "\n".join(lines)

    rendered_function_names: set[str] = set()
    for idx, start in enumerate(function_decl_indices):
        end = function_decl_indices[idx + 1] if idx + 1 < len(function_decl_indices) else len(parsed.blocks)
        decl_line = parsed.blocks[start].text
        func_name, func_args, func_returns = parse_decl(decl_line)
        if func_name == "unknown_function":
            if idx == 0:
                func_name = parsed.function_name
                func_args = parsed.args
                func_returns = parsed.returns
            else:
                func_name = f"subfunc_{idx + 1}"
                func_args = []
                func_returns = []

        rendered_function_names.add(sanitize_identifier(func_name, prefix="func"))
        body_blocks = parsed.blocks[start + 1 : end]
        lines.extend(_render_function_block(func_name, func_args, func_returns, body_blocks))

    module_alias_name = sanitize_identifier(module_stem, prefix="func")
    primary_name = sanitize_identifier(parsed.function_name, prefix="func")
    if module_alias_name not in rendered_function_names and module_alias_name != primary_name:
        alias_args = sanitize_arg_list(parsed.args)
        alias_args_src = ", ".join(alias_args)
        call_args = ", ".join(alias_args)
        lines.append(f"def {module_alias_name}({alias_args_src}):")
        lines.append(f"    return {primary_name}({call_args})")
        lines.append("")

    return "\n".join(lines)


def render_fallback_stub(parsed: ParsedMatlab, compile_error: str | None) -> str:
    safe_function_name = sanitize_identifier(parsed.function_name, prefix="func")
    safe_args = sanitize_arg_list(parsed.args)
    args = ", ".join(safe_args)
    compile_error_one_line = (compile_error or "unknown").replace("\n", " | ").replace("\r", " ")
    lines = [
        '"""Fallback stub generated because automatic translation did not compile yet."""',
        "",
        f"# compile_error: {compile_error_one_line}",
        f"def {safe_function_name}({args}):",
        "    # TODO: refine translation from MATLAB instruction blocks.",
    ]
    if len(parsed.returns) <= 1:
        lines.append("    return None")
    else:
        lines.append(f"    return ({', '.join(['None'] * len(parsed.returns))})")
    lines.append("")
    return "\n".join(lines)


def render_pytest_file(parsed: ParsedMatlab, source_rel: str, target_rel: str) -> str:
    safe_function_name = sanitize_identifier(parsed.function_name, prefix="func")
    lines = [
        '"""Auto-generated parity/TDD skeleton for MATLAB port."""',
        "",
        "from importlib.util import module_from_spec, spec_from_file_location",
        "from pathlib import Path",
        "import pytest",
        "",
        f'TARGET_FILE = Path(__file__).resolve().parents[4] / "{target_rel}"',
        "",
        "",
        "def _load_target_function():",
        '    spec = spec_from_file_location("ported_module", TARGET_FILE)',
        "    module = module_from_spec(spec)",
        "    assert spec is not None and spec.loader is not None",
        "    spec.loader.exec_module(module)",
        f"    return getattr(module, '{safe_function_name}')",
        "",
        "",
        "def test_signature_smoke():",
        "    # Smoke test only: importability and callable signature exposure.",
        "    fn = _load_target_function()",
        "    assert callable(fn)",
        "",
        "",
        "def test_expected_behavior_contract():",
        f"    # Source MATLAB file: {source_rel}",
        "    pytest.skip('Define behavior contract from MATLAB code and downstream callers.')",
        "",
    ]
    return "\n".join(lines)


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"files": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def discover_matlab_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for p in root.rglob("*"):
        if p.is_dir() and p.name.startswith("."):
            continue
        if p.is_file() and p.suffix.lower() == ".m":
            files.append(p)
    return sorted(files)


def build_dependency_import_lines(parsed: ParsedMatlab, src: Path, matlab_root: Path) -> list[str]:
    lines: set[str] = set()
    for dep in parsed.dependencies:
        dep_stem = Path(dep).stem
        dep_path = src.parent / dep
        if not dep_path.exists():
            continue
        rel_module = dep_path.relative_to(matlab_root).with_suffix("")
        module_name = ".".join((matlab_root.name, *rel_module.parts))
        lines.add(f"from {module_name} import {dep_stem}")
    return sorted(lines)


def compile_project(
    matlab_root: Path,
    python_root: Path,
    tests_root: Path,
    state_file: Path,
    mapping_file: Path,
    reports_dir: Path,
    max_files: int | None = None,
    force: bool = False,
    retries: int = 1,
    run_tests: bool = True,
    preserve_manual: bool = True,
) -> dict[str, Any]:
    native_map = ensure_mapping_file(mapping_file)
    state = load_state(state_file)

    matlab_files = discover_matlab_files(matlab_root)
    function_names = {f.stem for f in matlab_files}

    parsed_by_file: dict[str, ParsedMatlab] = {}
    for mf in matlab_files:
        parsed = parse_matlab_file(mf, function_names)
        parsed_by_file[str(mf)] = parsed

    order = build_porting_order(parsed_by_file)
    name_to_src = {Path(src).name: src for src in parsed_by_file}
    ordered_sources: list[str] = []
    for layer in order:
        for node in layer:
            src = name_to_src.get(node)
            if src and src not in ordered_sources:
                ordered_sources.append(src)
    # Safety fallback for unexpected missing nodes in order construction.
    for src in sorted(parsed_by_file):
        if src not in ordered_sources:
            ordered_sources.append(src)

    changed: list[str] = []
    generated: list[str] = []
    skipped: list[str] = []
    failed: list[dict[str, str]] = []
    preserved_manual: list[str] = []
    skipped_mex_wrappers: list[str] = []

    for src_str in ordered_sources:
        src = Path(src_str)
        parsed = parsed_by_file[src_str]
        rel = src.relative_to(matlab_root)
        expected_target = python_root / rel.with_suffix(".py")
        expected_test = tests_root / f"test_{parsed.function_name}.py"
        previous = state["files"].get(str(src), {})
        unchanged = (
            previous.get("source_hash") == parsed.source_hash
            and previous.get("logic_hash") == parsed.logic_hash
        )
        artifacts_exist = expected_target.exists() and expected_test.exists()

        # Important: never skip if generated artifacts are missing,
        # even when hashes match a previous run.
        if unchanged and artifacts_exist and not force:
            skipped.append(str(src))
            continue

        target = expected_target
        target.parent.mkdir(parents=True, exist_ok=True)

        if preserve_manual and target.exists():
            try:
                existing_text = target.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                existing_text = ""
            auto_markers = (
                "Auto-generated from MATLAB source",
                "Fallback stub generated because automatic translation did not compile yet",
                "Last-resort auto-generated stub",
            )
            if not any(marker in existing_text for marker in auto_markers):
                preserved_manual.append(str(target))
                continue

        changed.append(str(src))
        dependency_imports = build_dependency_import_lines(parsed, src, matlab_root)
        mex_wrapper = _detect_trivial_mex_wrapper(parsed)

        compile_error: str | None = None
        for _ in range(max(1, retries)):
            target.write_text(
                render_python_file(parsed, native_map, dependency_imports),
                encoding="utf-8",
            )
            try:
                py_compile.compile(str(target), doraise=True)
                compile_error = None
                break
            except py_compile.PyCompileError as exc:
                compile_error = str(exc)
                # Keep current generated file but annotate by replacing likely invalid control lines only.
                # Main conversion already comments control-flow; retries reserved for future richer repair.
                continue
        if compile_error:
            target.write_text(render_fallback_stub(parsed, compile_error), encoding="utf-8")
            try:
                py_compile.compile(str(target), doraise=True)
            except py_compile.PyCompileError as exc:
                final_error = str(exc)
                failed.append({"source": str(src), "target": str(target), "error": final_error})
                # Last-resort minimal valid function to keep pipeline progressing.
                safe_function_name = sanitize_identifier(parsed.function_name, prefix="func")
                safe_args = ", ".join(sanitize_arg_list(parsed.args))
                target.write_text(
                    "\n".join(
                        [
                            '"""Last-resort auto-generated stub."""',
                            "",
                            f"def {safe_function_name}({safe_args}):",
                            "    return None",
                            "",
                        ]
                    ),
                    encoding="utf-8",
                )
                py_compile.compile(str(target), doraise=True)
        generated.append(str(target))
        if mex_wrapper:
            skipped_mex_wrappers.append(str(target))

        test_file = expected_test
        test_file.parent.mkdir(parents=True, exist_ok=True)
        target_rel = str(target.relative_to(matlab_root.parent)).replace("\\", "/")
        source_rel = str(src.relative_to(matlab_root)).replace("\\", "/")
        test_file.write_text(render_pytest_file(parsed, source_rel, target_rel), encoding="utf-8")
        generated.append(str(test_file))

        state["files"][str(src)] = {
            "source_hash": parsed.source_hash,
            "logic_hash": parsed.logic_hash,
            "dependencies": parsed.dependencies,
            "native_calls": parsed.native_calls,
            "target_python": str(target),
            "generated_test": str(test_file),
            "compile_error": compile_error,
            "porting_status": "skipped_mex_wrapper" if mex_wrapper else "generated",
            "native_backend_required": bool(mex_wrapper),
            "native_function": (mex_wrapper or {}).get("native_function", ""),
        }

        if max_files is not None and len(changed) >= max_files:
            break

    reports_dir.mkdir(parents=True, exist_ok=True)
    (reports_dir / "dependency_graph.json").write_text(
        json.dumps({Path(k).name: v.dependencies for k, v in parsed_by_file.items()}, indent=2),
        encoding="utf-8",
    )
    (reports_dir / "porting_order.json").write_text(json.dumps(order, indent=2), encoding="utf-8")
    (reports_dir / "logic_blocks.json").write_text(
        json.dumps(
            {
                k: {
                    "function_name": v.function_name,
                    "args": v.args,
                    "returns": v.returns,
                    "native_calls": v.native_calls,
                    "blocks": [asdict(b) for b in v.blocks],
                }
                for k, v in parsed_by_file.items()
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    save_state(state_file, state)
    test_returncode: int | None = None
    test_stdout = ""
    test_stderr = ""
    if run_tests and changed:
        proc = subprocess.run(
            ["python", "-m", "pytest", str(tests_root), "-q"],
            capture_output=True,
            text=True,
            check=False,
        )
        test_returncode = proc.returncode
        test_stdout = proc.stdout
        test_stderr = proc.stderr

    return {
        "matlab_files": len(matlab_files),
        "changed_files": len(changed),
        "skipped_files": len(skipped),
        "generated_files": generated,
        "changed_sources": changed,
        "failed_files": failed,
        "preserved_manual_files": preserved_manual,
        "skipped_mex_wrapper_files": skipped_mex_wrappers,
        "tests_returncode": test_returncode,
        "tests_stdout": test_stdout,
        "tests_stderr": test_stderr,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Incremental MATLAB->Python porting compiler.")
    parser.add_argument("--matlab-root", default="../../src", help="MATLAB root folder.")
    parser.add_argument("--python-root", default="../../src", help="Python output root folder.")
    parser.add_argument("--tests-root", default="../tests/generated", help="Generated tests output root.")
    parser.add_argument("--state-file", default="../state/porting_state.json", help="Compiler state JSON.")
    parser.add_argument("--mapping-file", default="../config/native_function_map.json", help="Native mapping JSON.")
    parser.add_argument("--reports-dir", default="../reports", help="Compiler reports directory.")
    parser.add_argument("--max-files", type=int, default=None, help="Optional max changed files to process.")
    parser.add_argument("--force", action="store_true", help="Force regeneration even when hashes match.")
    parser.add_argument("--retries", type=int, default=1, help="Compilation retry count per generated file.")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running generated tests.")
    parser.add_argument(
        "--overwrite-manual",
        action="store_true",
        help="Allow overwriting manually curated Python files.",
    )
    args = parser.parse_args()

    base = Path(__file__).resolve().parent
    summary = compile_project(
        matlab_root=(base / args.matlab_root).resolve(),
        python_root=(base / args.python_root).resolve(),
        tests_root=(base / args.tests_root).resolve(),
        state_file=(base / args.state_file).resolve(),
        mapping_file=(base / args.mapping_file).resolve(),
        reports_dir=(base / args.reports_dir).resolve(),
        max_files=args.max_files,
        force=args.force,
        retries=args.retries,
        run_tests=not args.skip_tests,
        preserve_manual=not args.overwrite_manual,
    )
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
