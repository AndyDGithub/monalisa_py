#!/usr/bin/env python3
"""Generate deterministic Python requirements from project imports."""
from __future__ import annotations

import argparse
import ast
import json
import sys
from pathlib import Path


PROJECT_TOP_LEVELS = {
    "agentic",
    "demo",
    "parity",
    "porting",
    "script_outputs",
    "src",
    "tests",
    "third_part",
}

NON_PIP_IMPORTS = {
    "monalisa_py",
    "reader",
}

IMPORT_TO_PACKAGE = {
    "cv2": "opencv-python",
    "PIL": "Pillow",
    "matlab": "matlabengine",
    "skimage": "scikit-image",
    "sklearn": "scikit-learn",
    "yaml": "PyYAML",
    "pywt": "PyWavelets",
}


def _stdlib_names() -> set[str]:
    stdlib = set(getattr(sys, "stdlib_module_names", set()))
    stdlib.update(sys.builtin_module_names)
    return stdlib


def _iter_py_files(roots: list[Path]) -> list[Path]:
    files: list[Path] = []
    for root in roots:
        if root.exists():
            files.extend(path for path in root.rglob("*.py") if path.is_file())
    unique = {path.resolve(): path for path in files}
    return sorted(unique.values(), key=lambda p: str(p))


def _import_roots_from_tree(tree: ast.AST) -> set[str]:
    roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".", 1)[0].strip()
                if root:
                    roots.add(root)
        elif isinstance(node, ast.ImportFrom):
            if int(getattr(node, "level", 0) or 0) > 0:
                continue
            if not node.module:
                continue
            root = node.module.split(".", 1)[0].strip()
            if root:
                roots.add(root)
    return roots


def generate_requirements(repo_root: Path, roots: list[Path], output: Path) -> dict[str, object]:
    py_files = _iter_py_files(roots)
    stdlib = _stdlib_names()
    local_module_stems = {path.stem for path in py_files}
    local_import_roots: set[str] = set(local_module_stems)
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            if not path.is_file():
                continue
            try:
                rel = path.relative_to(root)
            except ValueError:
                continue
            if not rel.parts:
                continue
            first = rel.parts[0]
            if first.endswith(".py"):
                local_import_roots.add(Path(first).stem)
            else:
                local_import_roots.add(first)

    import_roots: set[str] = set()
    syntax_error_files: list[str] = []
    parsed_files = 0

    for py_file in py_files:
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8", errors="ignore"))
        except SyntaxError:
            syntax_error_files.append(str(py_file.relative_to(repo_root)).replace("\\", "/"))
            continue
        parsed_files += 1
        import_roots.update(_import_roots_from_tree(tree))

    external_modules = sorted(
        module
        for module in import_roots
        if module not in PROJECT_TOP_LEVELS
        and module not in NON_PIP_IMPORTS
        and module not in stdlib
        and module != "__future__"
        and module not in local_import_roots
    )
    requirements = sorted({IMPORT_TO_PACKAGE.get(module, module) for module in external_modules})

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(requirements) + ("\n" if requirements else ""), encoding="utf-8")

    return {
        "repo_root": str(repo_root),
        "roots": [str(path) for path in roots],
        "python_files_scanned": len(py_files),
        "python_files_parsed": parsed_files,
        "syntax_error_files": syntax_error_files,
        "local_module_stems_count": len(local_module_stems),
        "local_import_roots_count": len(local_import_roots),
        "import_roots_found": sorted(import_roots),
        "external_modules": external_modules,
        "requirements": requirements,
        "output": str(output),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic requirements from imports.")
    parser.add_argument(
        "--roots",
        default="../../src,../../demo,../../tests,../../third_part,../../agentic,../../porting",
        help="Comma-separated roots to scan.",
    )
    parser.add_argument("--repo-root", default="../../", help="Repository root.")
    parser.add_argument(
        "--output",
        default="../reports/requirements.generated.txt",
        help="Output requirements file.",
    )
    parser.add_argument("--summary-only", action="store_true", help="Print compact summary.")
    args = parser.parse_args()

    base = Path(__file__).resolve().parent
    repo_root = (base / args.repo_root).resolve()
    roots = [(base / token.strip()).resolve() for token in args.roots.split(",") if token.strip()]
    output = Path(args.output)
    if not output.is_absolute():
        output = (base / output).resolve()

    report = generate_requirements(repo_root=repo_root, roots=roots, output=output)
    if args.summary_only:
        compact = {
            "python_files_scanned": report["python_files_scanned"],
            "python_files_parsed": report["python_files_parsed"],
            "requirements_count": len(report["requirements"]),
            "output": report["output"],
        }
        print(json.dumps(compact, indent=2))
    else:
        print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
