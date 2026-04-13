# TODO Translation Examples (MATLAB -> Python)

This file documents how the agent should resolve generated TODO markers.

## Marker types

1. `# TODO(matlab-line): ...`
- Meaning: one MATLAB statement could not be translated safely.
- Expected action: replace with executable Python equivalent.

2. `# TODO(matlab-control): ...`
- Meaning: control-flow (`if`, `for`, `while`, etc.) was not translated.
- Expected action: rebuild Python control flow with correct indexing semantics.

## Translation patterns

### A) MATLAB indexing and slicing

Original MATLAB:
```matlab
res(1:padsize(1),:,:,:) = [];
```

Python equivalent:
```python
xpad = int(padsize[0])
res = res[xpad:, ...]
```

### B) MATLAB cell indexing

Original MATLAB:
```matlab
M = interp_kerns{type};
```

Python equivalent:
```python
M = interp_kerns[type_idx]
```

Notes:
- Ensure `type_idx` is 0-based in Python.

### C) MATLAB shape and size

Original MATLAB:
```matlab
[Nx,Ny,Nz,~] = size(kspace);
```

Python equivalent:
```python
Nx, Ny, Nz, _ = kspace.shape
```

### D) MATLAB logical normalization branch

Original MATLAB:
```matlab
if norm(mask(:)) > 0
    mask = normalize(mask, "norm");
end
```

Python equivalent:
```python
norm_val = np.linalg.norm(mask.ravel())
if norm_val > 0:
    mask = mask / norm_val
```

### E) MATLAB range loops

Original MATLAB:
```matlab
for i = 1+ystride:Ny-ystride
```

Python equivalent:
```python
for i in range(1 + ystride, Ny - ystride + 1):
    i0 = i - 1  # convert to 0-based if used for array indexing
```

## Deterministic acceptance rules for TODO replacement

- Result must compile (`python -m py_compile`).
- No `TODO(matlab-*)` marker remains in edited function block.
- Function signature must remain stable.
- Added imports must be project-local or standard scientific stack (`numpy`, `scipy`).
- Prefer explicit shape/index conversions.
