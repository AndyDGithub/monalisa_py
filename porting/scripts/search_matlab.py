"""MATLAB file discovery and hash tracking utilities."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Iterable


MATLAB_SYNTAX_RE = re.compile(
    r"^\s*(function\b|end\b|if\b|elseif\b|for\b|while\b|switch\b|case\b|otherwise\b)"
)


def _iter_files(root: Path) -> Iterable[Path]:
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if any(part.startswith(".") for part in p.parts):
            continue
        yield p


def search_matlab_syntax(file_path: str | Path, max_lines: int = 200) -> bool:
    """
    Return True when a non-.m file likely contains MATLAB syntax.
    """
    path = Path(file_path)
    if not path.exists() or not path.is_file():
        return False
    try:
        with path.open("r", encoding="ISO-8859-1", errors="ignore") as handle:
            for i, line in enumerate(handle):
                if i >= max_lines:
                    break
                stripped = line.strip()
                if not stripped or stripped.startswith("%"):
                    continue
                if MATLAB_SYNTAX_RE.match(stripped) or stripped.endswith(";"):
                    return True
    except OSError:
        return False
    return False


def search_matlab_files(directory: str | Path = "../src/", include_non_m_files: bool = False) -> list[str]:
    """
    Discover MATLAB files under a directory.

    By default this returns only `.m` files. Set `include_non_m_files=True`
    to also include files that look MATLAB-like from content.
    """
    root = Path(directory).resolve()
    if not root.exists():
        return []

    out: list[str] = []
    for file_path in _iter_files(root):
        if file_path.suffix.lower() == ".m":
            out.append(str(file_path))
        elif include_non_m_files and search_matlab_syntax(file_path):
            out.append(str(file_path))
    return sorted(out)


def sha256_file(path: str | Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_hash_manifest(file_paths: Iterable[str | Path], root: str | Path | None = None) -> dict[str, str]:
    """
    Build {relative_or_absolute_path: sha256} for a file list.
    """
    root_path = Path(root).resolve() if root is not None else None
    manifest: dict[str, str] = {}
    for file_path in sorted(Path(p).resolve() for p in file_paths):
        key = str(file_path.relative_to(root_path)) if root_path else str(file_path)
        manifest[key.replace("\\", "/")] = sha256_file(file_path)
    return manifest


def load_manifest(path: str | Path) -> dict[str, str]:
    manifest_path = Path(path)
    if not manifest_path.exists():
        return {}
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        return {}
    return {str(k): str(v) for k, v in data.items()}


def save_manifest(path: str | Path, manifest: dict[str, str]) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def diff_manifests(old: dict[str, str], new: dict[str, str]) -> dict[str, list[str]]:
    old_keys = set(old)
    new_keys = set(new)
    added = sorted(new_keys - old_keys)
    removed = sorted(old_keys - new_keys)
    changed = sorted(k for k in old_keys & new_keys if old[k] != new[k])
    unchanged = sorted(k for k in old_keys & new_keys if old[k] == new[k])
    return {
        "added": added,
        "removed": removed,
        "changed": changed,
        "unchanged": unchanged,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Search MATLAB files and optionally manage hash manifests.")
    parser.add_argument("--directory", default="../src/", help="Directory to scan.")
    parser.add_argument(
        "--include-non-m",
        action="store_true",
        help="Include non-.m files that appear to contain MATLAB syntax.",
    )
    parser.add_argument("--hash-manifest", default=None, help="Path to read previous hash manifest.")
    parser.add_argument("--write-hashes", default=None, help="Path to write new hash manifest.")
    parser.add_argument("--json", action="store_true", help="Print JSON output.")
    args = parser.parse_args()

    files = search_matlab_files(args.directory, include_non_m_files=args.include_non_m)
    output: dict[str, object] = {"files": files, "count": len(files)}

    if args.hash_manifest or args.write_hashes:
        new_manifest = build_hash_manifest(files, root=args.directory)
        old_manifest = load_manifest(args.hash_manifest) if args.hash_manifest else {}
        diff = diff_manifests(old_manifest, new_manifest)
        output["hash_diff"] = diff
        output["changed_count"] = len(diff["added"]) + len(diff["changed"]) + len(diff["removed"])
        if args.write_hashes:
            save_manifest(args.write_hashes, new_manifest)
            output["written_manifest"] = str(Path(args.write_hashes).resolve())

    if args.json:
        print(json.dumps(output, indent=2))
    else:
        print(f"MATLAB files found: {len(files)}")
        for item in files:
            print(item)
        if "hash_diff" in output:
            diff = output["hash_diff"]
            print(f"\nAdded   : {len(diff['added'])}")
            print(f"Changed : {len(diff['changed'])}")
            print(f"Removed : {len(diff['removed'])}")
            print(f"Unchanged: {len(diff['unchanged'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


    
