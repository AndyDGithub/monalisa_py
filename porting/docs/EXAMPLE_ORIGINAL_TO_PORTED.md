# Example: Original MATLAB -> Ported Python

This example shows the expected quality bar for a manually-corrected auto-generated file.

## MATLAB source

File: `src/fourier3/bcaNeith_harmonicField3D.m`

```matlab
function phi = HarmonicField3D(coeffs, X, Y, Z)
    if numel(coeffs) ~= 15
        error('Expected 15 coefficients');
    end
    r2 = X.^2 + Y.^2 + Z.^2;
    B = cell(15,1);
    B{1} = ones(size(X));
    B{2} = X;
    ...
    phi = zeros(size(X));
    for i = 1:15
        phi = phi + coeffs(i) * B{i};
    end
end
```

## Ported Python target

File: `src/fourier3/bcaNeith_harmonicField3D.py`

```python
import numpy as np

def HarmonicField3D(coeffs, X, Y, Z):
    coeffs_arr = np.asarray(coeffs).reshape(-1)
    if coeffs_arr.size != 15:
        raise ValueError("Expected 15 coefficients")

    X = np.asarray(X)
    Y = np.asarray(Y)
    Z = np.asarray(Z)

    r2 = X**2 + Y**2 + Z**2
    B = [
        np.ones_like(X),
        X,
        Y,
        Z,
        X * Y,
        X * Z,
        Y * Z,
        X**2 - Y**2,
        2 * Z**2 - X**2 - Y**2,
        X * (5 * Z**2 - r2),
        Y * (5 * Z**2 - r2),
        Z * (5 * Z**2 - 3 * r2),
        X * Y * Z,
        X**3 - 3 * X * Y**2,
        Y**3 - 3 * X**2 * Y,
    ]

    out_dtype = np.result_type(X.dtype, Y.dtype, Z.dtype, coeffs_arr.dtype)
    phi = np.zeros_like(X, dtype=out_dtype)
    for i in range(15):
        phi = phi + coeffs_arr[i] * B[i]
    return phi
```

## Why this is a good port

- same function contract and behavior,
- explicit shape/type handling,
- no MATLAB TODO markers,
- no ambiguous indexing,
- executable and testable in isolation.
