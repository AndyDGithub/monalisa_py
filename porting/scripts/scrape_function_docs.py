#!/usr/bin/env python3
"""Build a lightweight doc-driven function catalog and mapping prototype.

Goal:
- fetch selected documentation pages
- extract likely function/API names from links and page snippets
- generate a catalog and candidate MATLAB -> Python mappings
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

try:
    from monalisa_py.porting.scripts.porting_compiler import discover_matlab_files, parse_matlab_file
except ImportError:
    from porting_compiler import discover_matlab_files, parse_matlab_file


TOKEN_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\b")
HREF_RE = re.compile(r'href=["\']([^"\']+)["\']', re.IGNORECASE)
TAG_RE = re.compile(r"<[^>]+>")
PY_MOD_RE = re.compile(
    r'<code[^>]*class="[^"]*\bxref py py-mod\b[^"]*"[^>]*>\s*<span[^>]*>([^<]+)</span>',
    re.IGNORECASE,
)
PY_FUNC_RE = re.compile(
    r'<code[^>]*class="[^"]*\bxref py py-func\b[^"]*"[^>]*>\s*<span[^>]*>([^<]+)</span>',
    re.IGNORECASE,
)

PY_DOC_SEEDS = [
    "https://docs.python.org/3/library/index.html",
    "https://docs.python.org/3.13/",
    "https://numpy.org/doc/stable/user/",
]
MATLAB_DOC_SEEDS = [
    "https://ch.mathworks.com/help/matlab/index.html?s_tid=hc_panel",
]

MATLAB_TO_PY_SEED = {
    "zeros": ("numpy", "np.zeros"),
    "ones": ("numpy", "np.ones"),
    "rand": ("numpy", "np.random.rand"),
    "reshape": ("numpy", "np.reshape"),
    "size": ("numpy", "np.shape"),
    "length": ("python", "len"),
    "sum": ("numpy", "np.sum"),
    "mean": ("numpy", "np.mean"),
    "abs": ("numpy", "np.abs"),
    "fft": ("numpy", "np.fft.fft"),
    "ifft": ("numpy", "np.fft.ifft"),
}


def fetch_text(url: str, timeout: int = 15) -> str:
    req = Request(url, headers={"User-Agent": "monalisa-porting-doc-scraper/0.1"})
    with urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", errors="ignore")


def normalize_name(token: str) -> str:
    return token.strip().lower()


def infer_library(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path.lower()
    if "numpy.org" in host:
        return "numpy"
    if "python.org" in host:
        if "/library/" in path:
            return "python-stdlib"
        return "python-docs"
    if "mathworks.com" in host:
        return "matlab"
    return "unknown"


def extract_tokens_from_html(html: str, base_url: str) -> tuple[set[str], list[str]]:
    tokens: set[str] = set()
    links: list[str] = []

    for href_match in HREF_RE.finditer(html):
        href = href_match.group(1).strip()
        abs_link = urljoin(base_url, href)
        links.append(abs_link)
        leaf = urlparse(abs_link).path.split("/")[-1]
        leaf = leaf.replace(".html", "")
        for tok in TOKEN_RE.findall(leaf):
            tokens.add(normalize_name(tok))

    # light text extraction for extra tokens
    text = TAG_RE.sub(" ", html)
    for tok in TOKEN_RE.findall(text):
        nt = normalize_name(tok)
        if 2 <= len(nt) <= 40:
            tokens.add(nt)

    return tokens, links


def extract_python_symbols_from_sphinx_html(html: str) -> dict[str, set[str]]:
    modules = {normalize_name(m) for m in PY_MOD_RE.findall(html)}
    functions = {normalize_name(f.replace("()", "")) for f in PY_FUNC_RE.findall(html)}
    # Also catch common module patterns from links such as os.path.html
    for href in HREF_RE.findall(html):
        leaf = urlparse(urljoin("https://docs.python.org/3/library/index.html", href)).path.split("/")[-1]
        if leaf.endswith(".html"):
            mod = leaf[:-5]
            if mod and mod not in {"index", "intro"}:
                modules.add(normalize_name(mod))
    return {"modules": modules, "functions": functions}


def crawl_catalog(seed_urls: list[str], max_pages: int) -> dict:
    visited: set[str] = set()
    queue = list(seed_urls)
    pages: list[dict] = []
    token_to_sources: dict[str, list[dict]] = {}
    python_modules: set[str] = set()
    python_functions: set[str] = set()

    while queue and len(visited) < max_pages:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)

        try:
            html = fetch_text(url)
        except Exception:
            continue

        tokens, links = extract_tokens_from_html(html, url)
        if "docs.python.org" in url and "/library/" in url:
            symbols = extract_python_symbols_from_sphinx_html(html)
            python_modules.update(symbols["modules"])
            python_functions.update(symbols["functions"])
        pages.append({"url": url, "token_count": len(tokens), "library": infer_library(url)})

        for token in tokens:
            if token not in token_to_sources:
                token_to_sources[token] = []
            token_to_sources[token].append({"url": url, "library": infer_library(url)})

        # keep crawl bounded and relevant
        for link in links[:150]:
            if "python.org" in link or "numpy.org" in link or "mathworks.com" in link:
                if link not in visited and len(queue) < max_pages * 3:
                    queue.append(link)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pages": pages,
        "tokens": token_to_sources,
        "python_symbols": {
            "modules": sorted(python_modules),
            "functions": sorted(python_functions),
        },
    }


def collect_project_matlab_native_calls(matlab_root: Path) -> set[str]:
    matlab_files = discover_matlab_files(matlab_root)
    local_functions = {p.stem for p in matlab_files}
    calls: set[str] = set()
    for path in matlab_files:
        parsed = parse_matlab_file(path, local_functions)
        calls.update(x.lower() for x in parsed.native_calls)
    return calls


def build_candidate_mapping(matlab_calls: set[str], catalog: dict) -> dict[str, dict]:
    tokens = catalog.get("tokens", {})
    py_symbols = catalog.get("python_symbols", {})
    py_modules = set(py_symbols.get("modules", []))
    py_functions = set(py_symbols.get("functions", []))
    mapping: dict[str, dict] = {}
    for call in sorted(matlab_calls):
        if call in MATLAB_TO_PY_SEED:
            lib, py_name = MATLAB_TO_PY_SEED[call]
            mapping[call] = {
                "python": py_name,
                "library": lib,
                "confidence": "seed-high",
                "sources": [{"url": "seed-rule", "library": lib}],
            }
            continue

        # prototype heuristic: same token exists in Python/Numpy docs
        srcs = tokens.get(call, [])
        py_srcs = [s for s in srcs if s["library"] in {"numpy", "python-stdlib", "python-docs"}]
        if call in py_functions:
            mapping[call] = {
                "python": call,
                "library": "python-stdlib",
                "confidence": "sphinx-high",
                "sources": py_srcs[:3],
            }
        elif call in py_modules:
            mapping[call] = {
                "python": call,
                "library": "python-stdlib-module",
                "confidence": "sphinx-high",
                "sources": py_srcs[:3],
            }
        elif py_srcs:
            top = py_srcs[:3]
            lib = top[0]["library"]
            py_name = f"np.{call}" if lib == "numpy" else call
            mapping[call] = {
                "python": py_name,
                "library": lib,
                "confidence": "heuristic-medium",
                "sources": top,
            }
        else:
            mapping[call] = {
                "python": None,
                "library": None,
                "confidence": "unknown",
                "sources": [],
            }
    return mapping


def main() -> int:
    parser = argparse.ArgumentParser(description="Scrape docs and build MATLAB->Python mapping prototype.")
    parser.add_argument("--matlab-root", default="../../src", help="MATLAB root in monalisa_py.")
    parser.add_argument("--max-pages", type=int, default=25, help="Maximum pages to crawl.")
    parser.add_argument("--catalog-output", default="../config/doc_function_catalog.json", help="Catalog output JSON.")
    parser.add_argument("--mapping-output", default="../config/doc_native_map_candidates.json", help="Mapping output JSON.")
    args = parser.parse_args()

    base = Path(__file__).resolve().parent
    matlab_root = (base / args.matlab_root).resolve()
    catalog_output = (base / args.catalog_output).resolve()
    mapping_output = (base / args.mapping_output).resolve()

    all_seeds = MATLAB_DOC_SEEDS + PY_DOC_SEEDS
    catalog = crawl_catalog(all_seeds, max_pages=args.max_pages)
    matlab_calls = collect_project_matlab_native_calls(matlab_root)
    mapping = build_candidate_mapping(matlab_calls, catalog)

    catalog_output.parent.mkdir(parents=True, exist_ok=True)
    catalog_output.write_text(json.dumps(catalog, indent=2), encoding="utf-8")
    mapping_output.parent.mkdir(parents=True, exist_ok=True)
    mapping_output.write_text(json.dumps(mapping, indent=2), encoding="utf-8")

    print(f"Catalog pages: {len(catalog.get('pages', []))}")
    print(f"Unique MATLAB native calls: {len(matlab_calls)}")
    print(f"Candidate mappings: {len(mapping)}")
    print(f"- catalog: {catalog_output}")
    print(f"- mapping: {mapping_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
