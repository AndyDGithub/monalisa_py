# First End-to-End Porting Workflow

This workflow is the minimal production loop to port one MATLAB function with parity checks.

## Step 0 - Pick target
- Select a low-risk leaf function (example: `bmPointReshape`).
- Create a task file from template in `porting/tasks/`.

## Step 1 - Define behavior contract
- Identify MATLAB signature and edge cases.
- Define parity tolerance (`exact`, or `rtol`/`atol`).

## Step 2 - Build parity fixture
- Generate deterministic inputs.
- Save MATLAB outputs using `porting/matlab/harness/run_parity_case.m`.

## Step 3 - Implement Python
- Add function in `porting/python/monalisa_py/`.
- Mirror shape semantics (column-major vs row-major explicit handling).

## Step 4 - Add tests
- Unit test (behavioral).
- Parity test in `porting/python/tests/parity/` comparing against MATLAB artifacts.

## Step 5 - Auto-fix loop
- Run `pytest`.
- If parity fails: inspect mismatch, patch, rerun.
- Repeat until green.

## Step 6 - Review and docs
- Run reviewer checklist.
- Add docstring + migration note in task file.

## Step 7 - Mark done
- Update task `status: done`.
- Commit with task id.

## Definition of done
- Unit tests pass.
- Parity tests pass within declared tolerance.
- Task metadata complete.
- No unresolved reviewer blockers.
