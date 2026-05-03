# Porting Framework: MATLAB to Python (monalisa_py)

This folder contains the deterministic-first + agent-assisted porting workflow for `monalisa_py`.

## Current status (important)

As of May 3, 2026, the repository is **not yet at full green on `python -m pytest tests/`** by setup alone.
Some failures are still real porting bugs (API mismatch, translation issues), not environment issues.

This README gives:
1. exact setup steps,
2. exact compile/build steps (including MEX),
3. exact commands to validate what is working today,
4. a quick map from common failures to likely root cause.

## 1) Environment setup (Windows PowerShell)

Run from repo root (`monalisa_py`):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install mat73 h5py
```

Notes:
- `mat73`/`h5py` are needed by parity loaders.
- If PowerShell blocks venv activation, run:
  `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

## 2) Build native MEX backends (required for gridder/image native paths)

The Python wrappers call compiled `*_mex` backends for several hot paths.

First check discovery only:

```powershell
python src\mex\m\compile_mex_for_monalisa.py --dry-run --summary-only
```

Then compile:

```powershell
python src\mex\m\compile_mex_for_monalisa.py --summary-only
```

If you want the pipeline to fail when any MEX command fails:

```powershell
python src\mex\m\compile_mex_for_monalisa.py --fail-on-error --summary-only
```

## 3) Run deterministic stabilization pipeline

This now includes:
- deterministic transpilation/update pipeline,
- MEX compile step,
- import auto-fix step (including `_mex` imports).

```powershell
python porting\scripts\run_porting_pipeline.py `
  --roots src,demo,tests,third_part `
  --skip-tests `
  --generate-contract-tests `
  --compare-parity-snapshots
```

Useful flags:
- `--mex-dry-run` (do not execute MEX commands)
- `--mex-fail-on-error`
- `--skip-mex-compile`
- `--skip-auto-fix-imports`

## 4) Validation ladder (recommended order)

### A. Fast smoke tests that should be stable

```powershell
python -m pytest `
  tests\unit\test_fourier.py `
  tests\unit\test_imresize.py `
  tests\unit\test_mitosis.py `
  tests\unit\test_mitosius.py `
  tests\unit\test_varargin.py `
  -v --tb=short
```

### B. Full test suite (expected to still have known failures today)

```powershell
python -m pytest tests\ -v --tb=short
```

## 5) Parity data prerequisites

Several parity tests expect raw data at:

`../monalisa/demo/data_demo/data_8_tutorial_1/brainScan.dat`

If missing, parity tests are skipped.
If present, parity execution tests run and may expose real implementation gaps.

Slow parity checks are gated by:

```powershell
$env:MONALISA_SLOW_TESTS="1"
```

## 6) Interpreting common failures

### Setup/build related

- `NotImplementedError: bmGridder_n2u_leight requires compiled MEX C extensions...`
  - Cause: native MEX backends not built or not loadable.
  - Action: run MEX compile step above and re-run tests.

### Real porting/translation issues (not fixed by setup)

- `TypeError: bmPointReshape() missing 1 required positional argument: 'varargin'`
  - Signature mismatch in translated API.

- `IndexError ... bmPhyllotaxisAngle3.py`
  - trajectory translation logic/indexing bug.

- `TypeError: bmVolumeElement() got an unexpected keyword argument 'data_dir'`
  - caller/callee API mismatch in parity path.

- `ImportError: cannot import name 'checkMetadataInterac' ...`
  - wrong import symbol/name mismatch.

- `test_bmFirstIndex_*`, `bmPermuteToCol_*`, `bmBlockReshape_nCh1` failures
  - behavioral mismatch vs MATLAB contract in array utility translations.

These need code fixes in `src/`, not environment changes.

## 7) Porting workflow entrypoints

Run full workflow (v2 default):

```powershell
python porting\scripts\run_agentic_porting_workflow.py --roots src,demo,tests,third_part
```

Legacy engine:

```powershell
python porting\scripts\run_agentic_porting_workflow.py --engine legacy --roots src,demo,tests,third_part
```

## 8) Reports to inspect after each run

- `porting/reports/pipeline_run_report.json`
- `porting/reports/mex_compile_report.json`
- `porting/reports/import_autofix_report.json`
- `porting/reports/generated_files_analysis.json`
- `porting/reports/agent_repair_cycle_report.json` (if repair cycle was run)

## 9) Practical definition of "fully functional" right now

Today, "fully functional" means:
1. environment created,
2. dependencies installed,
3. MEX commands compile successfully on your machine,
4. deterministic pipeline runs cleanly,
5. smoke/unit subset passes.

`tests/` full green is still a porting milestone in progress, not just a setup step.
