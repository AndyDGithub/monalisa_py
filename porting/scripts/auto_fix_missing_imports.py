#!/usr/bin/env python3
"""Auto-fix missing project-local imports in translated src/*.py files.

Strategy:
- Build a symbol index from top-level function/class definitions in src.
- For each file, detect called names that are not builtins/locals/imported.
- If a missing name has a unique provider module in project, add:
    from src.<module_path> import <name>

Default mode is dry-run. Use --apply to write changes.
"""
from __future__ import annotations

import argparse
import ast
import builtins
import json
import keyword
import re
from collections import defaultdict
from pathlib import Path


IMPORT_FROM_RE = re.compile(
    r"^(?P<indent>\s*)from\s+(?P<module>[A-Za-z_][\w\.]*)\s+import\s+(?P<names>[A-Za-z_][\w]*(?:\s*,\s*[A-Za-z_][\w]*)*)\s*(?P<comment>#.*)?$"
)
RELATIVE_IMPORT_RE = re.compile(
    r"^(?P<indent>\s*)from\s+(?P<dots>\.+)(?P<module>[A-Za-z_][\w\.]*)?\s+import\s+(?P<names>[A-Za-z_][\w]*(?:\s*,\s*[A-Za-z_][\w]*)*)\s*(?P<comment>#.*)?$"
)
PROJECT_TOP_LEVELS = {"src", "demo", "tests", "third_part"}


def _iter_py_files(src_roots: list[Path]) -> list[Path]:
    files: list[Path] = []
    for root in src_roots:
        if root.exists():
            files.extend([p for p in root.rglob("*.py") if p.is_file()])
    dedup = {p.resolve(): p for p in files}
    return sorted(dedup.values(), key=lambda p: str(p))


def _iter_mex_cpp_files(src_roots: list[Path]) -> list[Path]:
    files: list[Path] = []
    for root in src_roots:
        if root.exists():
            files.extend([p for p in root.rglob("*_mex.cpp") if p.is_file()])
    dedup = {p.resolve(): p for p in files}
    return sorted(dedup.values(), key=lambda p: str(p))


def _module_path_from_file(repo_root: Path, py_file: Path) -> str:
    rel = py_file.resolve().relative_to(repo_root.resolve())
    parts = list(rel.with_suffix("").parts)
    return ".".join(parts)


def _module_path_from_cpp(repo_root: Path, cpp_file: Path) -> str:
    rel = cpp_file.resolve().relative_to(repo_root.resolve())
    parts = list(rel.with_suffix("").parts)
    return ".".join(parts)


def _parse_tree(path: Path) -> ast.AST | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except SyntaxError:
        return None


def _symbol_stem_index(py_files: list[Path]) -> dict[str, list[Path]]:
    index: dict[str, list[Path]] = defaultdict(list)
    for py_file in py_files:
        stem = py_file.stem
        if stem.startswith("__"):
            continue
        index[stem].append(py_file)
    return index


def _top_level_symbols(tree: ast.AST) -> set[str]:
    symbols: set[str] = set()
    for node in getattr(tree, "body", []):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            symbols.add(node.name)
    return symbols


def _imported_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "*":
                    continue
                names.add(alias.asname or alias.name)
    return names


def _defined_names(tree: ast.AST) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.add(node.name)
            for arg in node.args.args:
                names.add(arg.arg)
            for arg in node.args.kwonlyargs:
                names.add(arg.arg)
            if node.args.vararg:
                names.add(node.args.vararg.arg)
            if node.args.kwarg:
                names.add(node.args.kwarg.arg)
        elif isinstance(node, ast.ClassDef):
            names.add(node.name)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            names.add(node.id)
    return names


def _called_names(tree: ast.AST) -> set[str]:
    calls: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            calls.add(node.func.id)
    return calls


def _find_insertion_index(text: str) -> int:
    lines = text.splitlines(keepends=True)
    i = 0
    n = len(lines)

    # Skip module docstring.
    if i < n:
        stripped = lines[i].lstrip()
        if stripped.startswith('"""') or stripped.startswith("'''"):
            quote = stripped[:3]
            if stripped.count(quote) >= 2 and len(stripped.strip()) > 6:
                i += 1
            else:
                i += 1
                while i < n and quote not in lines[i]:
                    i += 1
                if i < n:
                    i += 1

    while i < n and not lines[i].strip():
        i += 1

    # Keep future imports grouped at top.
    while i < n and lines[i].lstrip().startswith("from __future__ import "):
        i += 1

    while i < n and lines[i].strip():
        if lines[i].lstrip().startswith("import ") or lines[i].lstrip().startswith("from "):
            i += 1
        else:
            break

    return i


def _rewrite_keyword_segment_imports(text: str) -> tuple[str, int]:
    lines = text.splitlines(keepends=True)
    changed_count = 0
    needs_importlib = False
    new_lines: list[str] = []

    for line in lines:
        m = IMPORT_FROM_RE.match(line.rstrip("\r\n"))
        if not m:
            new_lines.append(line)
            continue

        module = m.group("module")
        names = [n.strip() for n in m.group("names").split(",") if n.strip()]
        indent = m.group("indent") or ""
        comment = (m.group("comment") or "").strip()
        segments = module.split(".")
        if not any(keyword.iskeyword(seg) for seg in segments):
            new_lines.append(line)
            continue

        needs_importlib = True
        changed_count += 1
        for i, name in enumerate(names):
            suffix = f"  {comment}" if i == 0 and comment else ""
            new_lines.append(f'{indent}{name} = _importlib.import_module("{module}").{name}{suffix}\n')

    if changed_count == 0:
        return text, 0

    rewritten = "".join(new_lines)
    if "import importlib as _importlib" not in rewritten:
        idx = _find_insertion_index(rewritten)
        split_lines = rewritten.splitlines(keepends=True)
        insertion = ["import importlib as _importlib\n"]
        if idx > 0 and split_lines[idx - 1].strip():
            insertion.insert(0, "\n")
        split_lines = split_lines[:idx] + insertion + split_lines[idx:]
        rewritten = "".join(split_lines)

    return rewritten, changed_count


def _choose_unique_module_for_name(
    *,
    name: str,
    repo_root: Path,
    cur_file: Path,
    symbol_index: dict[str, list[Path]],
    stem_index: dict[str, list[Path]],
) -> str | None:
    providers = [p for p in symbol_index.get(name, []) if p.resolve() != cur_file.resolve()]
    if not providers:
        providers = [p for p in stem_index.get(name, []) if p.resolve() != cur_file.resolve()]
    if not providers:
        return None

    cur_dir = cur_file.parent.resolve()
    same_dir = [p for p in providers if p.parent.resolve() == cur_dir]
    chosen_candidates = same_dir or providers
    modules = sorted({_module_path_from_file(repo_root, p) for p in chosen_candidates})
    if len(modules) != 1:
        return None
    return modules[0]


def _load_defined_symbols_from_module(py_file: Path) -> set[str]:
    if not py_file.exists():
        return set()
    tree = _parse_tree(py_file)
    if tree is None:
        return set()
    return _top_level_symbols(tree)


def _load_external_symbol_maps(repo_root: Path) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    matlab_native_path = repo_root / "third_part" / "matlab_compat" / "matlab_native.py"
    runtime_metadata_path = repo_root / "third_part" / "matlab_compat" / "matlab_runtime_metadata.py"
    utils_path = repo_root / "porting" / "lib" / "utils.py"

    matlab_native_symbols = _load_defined_symbols_from_module(matlab_native_path)
    if matlab_native_symbols:
        out["third_part.matlab_compat.matlab_native"] = matlab_native_symbols

    runtime_metadata_symbols = _load_defined_symbols_from_module(runtime_metadata_path)
    if runtime_metadata_symbols:
        out["third_part.matlab_compat.matlab_runtime_metadata"] = runtime_metadata_symbols

    utils_symbols = _load_defined_symbols_from_module(utils_path)
    if utils_symbols:
        out["porting.lib.utils"] = utils_symbols

    return out


def _rewrite_bare_project_imports(
    *,
    text: str,
    repo_root: Path,
    py_file: Path,
    symbol_index: dict[str, list[Path]],
    stem_index: dict[str, list[Path]],
) -> tuple[str, int]:
    lines = text.splitlines(keepends=True)
    changed = 0
    out: list[str] = []

    for line in lines:
        stripped = line.rstrip("\r\n")
        m = IMPORT_FROM_RE.match(stripped)
        if not m:
            out.append(line)
            continue

        module = m.group("module")
        module_head = module.split(".", 1)[0]

        # Rewrite two cases:
        # 1) bare imports: from bmFoo import bmFoo
        # 2) qualified project imports that point to missing modules.
        should_rewrite = False
        if "." not in module:
            should_rewrite = True
        elif module_head in PROJECT_TOP_LEVELS:
            module_py = repo_root / Path(*module.split(".")).with_suffix(".py")
            module_pkg = repo_root / Path(*module.split(".")) / "__init__.py"
            should_rewrite = not (module_py.exists() or module_pkg.exists())

        if not should_rewrite:
            out.append(line)
            continue

        indent = m.group("indent") or ""
        comment = (m.group("comment") or "").strip()
        names = [n.strip() for n in m.group("names").split(",") if n.strip()]
        rewritten_lines: list[str] = []
        for idx, name in enumerate(names):
            chosen_module = _choose_unique_module_for_name(
                name=name,
                repo_root=repo_root,
                cur_file=py_file,
                symbol_index=symbol_index,
                stem_index=stem_index,
            )
            if not chosen_module:
                rewritten_lines = []
                break
            suffix = f"  {comment}" if idx == 0 and comment else ""
            rewritten_lines.append(f"{indent}from {chosen_module} import {name}{suffix}\n")

        if not rewritten_lines:
            out.append(line)
            continue

        # If all names map to same module, keep a compact import line.
        unique_modules = {IMPORT_FROM_RE.match(x.rstrip("\r\n")).group("module") for x in rewritten_lines}
        if len(unique_modules) == 1:
            target_module = next(iter(unique_modules))
            joined = ", ".join(names)
            suffix = f"  {comment}" if comment else ""
            out.append(f"{indent}from {target_module} import {joined}{suffix}\n")
        else:
            out.extend(rewritten_lines)
        changed += 1

    if changed == 0:
        return text, 0
    return "".join(out), changed


def _rewrite_relative_project_imports(
    *,
    text: str,
    repo_root: Path,
    py_file: Path,
) -> tuple[str, int]:
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    changed = 0

    cur_module = _module_path_from_file(repo_root, py_file)
    cur_parts = cur_module.split(".")

    for line in lines:
        stripped = line.rstrip("\r\n")
        m = RELATIVE_IMPORT_RE.match(stripped)
        if not m:
            out.append(line)
            continue

        indent = m.group("indent") or ""
        dots = m.group("dots") or "."
        rel_module = (m.group("module") or "").strip()
        names = m.group("names")
        comment = (m.group("comment") or "").strip()

        up = len(dots)
        # from .x import y => stay in current package => remove current module leaf.
        # from ..x import y => one level up package.
        base_parts = cur_parts[:-up]
        if not base_parts:
            out.append(line)
            continue
        if rel_module:
            abs_parts = base_parts + rel_module.split(".")
        else:
            abs_parts = base_parts
        abs_module = ".".join(abs_parts)
        suffix = f"  {comment}" if comment else ""
        out.append(f"{indent}from {abs_module} import {names}{suffix}\n")
        changed += 1

    if changed == 0:
        return text, 0
    return "".join(out), changed


def _plan_imports_for_file(
    *,
    repo_root: Path,
    src_root: Path,
    py_file: Path,
    symbol_index: dict[str, list[Path]],
    stem_index: dict[str, list[Path]],
    external_symbol_maps: dict[str, set[str]],
) -> dict[str, list[str]]:
    tree = _parse_tree(py_file)
    if tree is None:
        return {}

    imported = _imported_names(tree)
    defined = _defined_names(tree)
    called = _called_names(tree)
    builtins_set = set(dir(builtins))

    missing = sorted(
        name
        for name in called
        if name not in imported and name not in defined and name not in builtins_set
    )
    if not missing:
        return {}

    by_module: dict[str, list[str]] = defaultdict(list)
    cur_dir = py_file.parent.resolve()

    for name in missing:
        module = _choose_unique_module_for_name(
            name=name,
            repo_root=repo_root,
            cur_file=py_file,
            symbol_index=symbol_index,
            stem_index=stem_index,
        )
        if not module:
            providers = [mod for mod, symbols in external_symbol_maps.items() if name in symbols]
            if len(providers) == 1:
                module = providers[0]
        if not module:
            continue
        by_module[module].append(name)

    # Dedupe per module.
    out: dict[str, list[str]] = {}
    for module, names in by_module.items():
        out[module] = sorted(set(names))
    return out


def _build_mex_symbol_index(repo_root: Path, src_roots: list[Path]) -> dict[str, str]:
    index: dict[str, list[str]] = defaultdict(list)
    for cpp_file in _iter_mex_cpp_files(src_roots):
        symbol = cpp_file.stem
        module = _module_path_from_cpp(repo_root, cpp_file)
        index[symbol].append(module)
    out: dict[str, str] = {}
    for symbol, modules in index.items():
        uniq = sorted(set(modules))
        if len(uniq) == 1:
            out[symbol] = uniq[0]
    return out


def _plan_optional_mex_imports_for_file(
    *,
    py_file: Path,
    mex_symbol_index: dict[str, str],
) -> dict[str, list[str]]:
    tree = _parse_tree(py_file)
    if tree is None:
        return {}

    imported = _imported_names(tree)
    defined = _defined_names(tree)
    called = _called_names(tree)
    builtins_set = set(dir(builtins))
    by_module: dict[str, list[str]] = defaultdict(list)

    for name in sorted(called):
        if not name.endswith("_mex"):
            continue
        if name in imported or name in defined or name in builtins_set:
            continue
        module = mex_symbol_index.get(name)
        if not module:
            continue
        by_module[module].append(name)

    out: dict[str, list[str]] = {}
    for module, names in by_module.items():
        out[module] = sorted(set(names))
    return out


def _apply_optional_mex_imports(text: str, mex_plan: dict[str, list[str]]) -> tuple[str, int]:
    if not mex_plan:
        return text, 0

    lines = text.splitlines(keepends=True)
    idx = _find_insertion_index(text)
    insertion: list[str] = []
    changed = 0

    for module, names in sorted(mex_plan.items()):
        for name in names:
            direct_import_line = f"from {module} import {name}"
            if direct_import_line in text:
                continue
            if f"def {name}(" in text:
                continue

            insertion.extend(
                [
                    "try:\n",
                    f"    from {module} import {name}\n",
                    "except Exception:\n",
                    f"    def {name}(*_args, **_kwargs):\n",
                    "        raise NotImplementedError("
                    f"\"Native backend '{name}' is unavailable. Run compile_mex_for_monalisa() to build MEX binaries first.\""
                    ")\n",
                    "\n",
                ]
            )
            changed += 1

    if changed == 0:
        return text, 0

    if idx > 0 and lines[idx - 1].strip():
        insertion.insert(0, "\n")
    rewritten = "".join(lines[:idx] + insertion + lines[idx:])
    return rewritten, changed


def auto_fix_missing_imports(src_roots: list[Path], repo_root: Path, apply: bool) -> dict:
    py_files = _iter_py_files(src_roots)
    mex_symbol_index = _build_mex_symbol_index(repo_root, src_roots)
    keyword_rewrite_candidates: list[str] = []
    keyword_rewrite_changed: list[str] = []
    bare_import_rewrite_candidates: list[str] = []
    bare_import_rewrite_changed: list[str] = []
    relative_import_rewrite_candidates: list[str] = []
    relative_import_rewrite_changed: list[str] = []
    optional_mex_import_candidates: list[str] = []
    optional_mex_import_changed: list[str] = []

    symbol_index: dict[str, list[Path]] = defaultdict(list)
    for py_file in py_files:
        tree = _parse_tree(py_file)
        if tree is None:
            continue
        for symbol in _top_level_symbols(tree):
            symbol_index[symbol].append(py_file)
    stem_index = _symbol_stem_index(py_files)
    external_symbol_maps = _load_external_symbol_maps(repo_root)

    # First pass: rewrite invalid imports with python-keyword segments (e.g. ".class.").
    for py_file in py_files:
        original = py_file.read_text(encoding="utf-8", errors="ignore")
        rewritten, kw_changes = _rewrite_keyword_segment_imports(original)
        rewritten, rel_changes = _rewrite_relative_project_imports(
            text=rewritten,
            repo_root=repo_root,
            py_file=py_file,
        )
        rewritten, bare_changes = _rewrite_bare_project_imports(
            text=rewritten,
            repo_root=repo_root,
            py_file=py_file,
            symbol_index=symbol_index,
            stem_index=stem_index,
        )
        if kw_changes == 0 and bare_changes == 0 and rel_changes == 0:
            continue
        rel = str(py_file.relative_to(repo_root)).replace("\\", "/")
        if kw_changes > 0:
            keyword_rewrite_candidates.append(rel)
        if rel_changes > 0:
            relative_import_rewrite_candidates.append(rel)
        if bare_changes > 0:
            bare_import_rewrite_candidates.append(rel)
        if apply:
            py_file.write_text(rewritten, encoding="utf-8")
            if kw_changes > 0:
                keyword_rewrite_changed.append(rel)
            if rel_changes > 0:
                relative_import_rewrite_changed.append(rel)
            if bare_changes > 0:
                bare_import_rewrite_changed.append(rel)

    changed_files: list[str] = []
    plans: dict[str, dict[str, list[str]]] = {}
    mex_plans: dict[str, dict[str, list[str]]] = {}

    for py_file in py_files:
        plan = _plan_imports_for_file(
            repo_root=repo_root,
            src_root=src_roots[0],
            py_file=py_file,
            symbol_index=symbol_index,
            stem_index=stem_index,
            external_symbol_maps=external_symbol_maps,
        )
        mex_plan = _plan_optional_mex_imports_for_file(
            py_file=py_file,
            mex_symbol_index=mex_symbol_index,
        )

        if not plan and not mex_plan:
            continue

        text = py_file.read_text(encoding="utf-8", errors="ignore")
        insertion_lines: list[str] = []
        for module, names in sorted(plan.items()):
            import_line = f"from {module} import {', '.join(names)}"
            if import_line in text:
                continue
            insertion_lines.append(import_line + "\n")

        if not insertion_lines and not mex_plan:
            continue

        rel = str(py_file.relative_to(repo_root)).replace("\\", "/")
        if plan:
            plans[rel] = plan
        if mex_plan:
            mex_plans[rel] = mex_plan
            optional_mex_import_candidates.append(rel)

        if apply:
            working_text = text
            idx = _find_insertion_index(text)
            lines = working_text.splitlines(keepends=True)
            if insertion_lines and idx > 0 and lines[idx - 1].strip():
                insertion_lines.insert(0, "\n")
            if insertion_lines:
                working_text = "".join(lines[:idx] + insertion_lines + lines[idx:])
            working_text, mex_changes = _apply_optional_mex_imports(working_text, mex_plan)
            if working_text != text:
                py_file.write_text(working_text, encoding="utf-8")
                changed_files.append(rel)
            if mex_changes > 0:
                optional_mex_import_changed.append(rel)

    return {
        "src_roots": [str(p) for p in src_roots],
        "python_files_scanned": len(py_files),
        "files_with_import_plan": len(plans),
        "files_with_mex_import_plan": len(mex_plans),
        "files_changed": len(changed_files),
        "changed_files": changed_files,
        "plans": plans,
        "mex_plans": mex_plans,
        "keyword_import_rewrite_candidates": len(keyword_rewrite_candidates),
        "keyword_import_rewrite_changed": len(keyword_rewrite_changed),
        "keyword_import_rewrite_files": keyword_rewrite_changed,
        "relative_import_rewrite_candidates": len(relative_import_rewrite_candidates),
        "relative_import_rewrite_changed": len(relative_import_rewrite_changed),
        "relative_import_rewrite_files": relative_import_rewrite_changed,
        "bare_import_rewrite_candidates": len(bare_import_rewrite_candidates),
        "bare_import_rewrite_changed": len(bare_import_rewrite_changed),
        "bare_import_rewrite_files": bare_import_rewrite_changed,
        "optional_mex_import_candidates": len(optional_mex_import_candidates),
        "optional_mex_import_changed": len(optional_mex_import_changed),
        "optional_mex_import_files": optional_mex_import_changed,
        "mex_symbol_index_size": len(mex_symbol_index),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Auto-fix missing local imports in src python files.")
    parser.add_argument(
        "--roots",
        default="../../src",
        help="Comma-separated source roots to scan (e.g. ../../src,../../demo).",
    )
    parser.add_argument("--repo-root", default="../../", help="Repository root.")
    parser.add_argument("--apply", action="store_true", help="Apply changes (default is dry-run).")
    parser.add_argument("--output", default="../reports/import_autofix_report.json", help="Output report path.")
    parser.add_argument("--summary-only", action="store_true", help="Print only compact summary to stdout.")
    args = parser.parse_args()

    base = Path(__file__).resolve().parent
    src_roots = [(base / token.strip()).resolve() for token in args.roots.split(",") if token.strip()]
    repo_root = (base / args.repo_root).resolve()
    output = (base / args.output).resolve()

    report = auto_fix_missing_imports(src_roots=src_roots, repo_root=repo_root, apply=args.apply)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")

    if args.summary_only:
        compact = {
            "mode": "apply" if args.apply else "dry-run",
            "python_files_scanned": report["python_files_scanned"],
            "files_with_import_plan": report["files_with_import_plan"],
            "files_with_mex_import_plan": report.get("files_with_mex_import_plan", 0),
            "files_changed": report["files_changed"],
            "keyword_import_rewrite_changed": report.get("keyword_import_rewrite_changed", 0),
            "relative_import_rewrite_changed": report.get("relative_import_rewrite_changed", 0),
            "bare_import_rewrite_changed": report.get("bare_import_rewrite_changed", 0),
            "optional_mex_import_changed": report.get("optional_mex_import_changed", 0),
        }
        print(json.dumps(compact, indent=2))
    else:
        print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
