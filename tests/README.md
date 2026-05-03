# Unit Tests

This folder contains all **unit tests** for the Python port of Monalisa, using **pytest**.

---

## Good Practices for Writing Tests

- Group tests for the same function into the same test file.
- A test file should ideally not exceed **200–300 lines**.
- Write meaningful assertion messages.
- Comment tests to explain **what** is being tested and **why**.
- Use clear naming: test functions should describe the behavior being verified (e.g., `test_handles_empty_input`).
- Keep tests **fast**: avoid large data or heavy computation in unit tests.
- Before pushing new tests to `main`, verify them on the `ci-testing` branch.

---

## How to Write a New Test

Create a new file in this folder (e.g., `test_my_function.py`) using the following structure:

```python
import numpy as np
import pytest
from src.my_module.my_function import my_function


def test_basic_case():
    """my_function(3) should return 9 (3 squared)."""
    result = my_function(3)
    assert result == 9, f"Expected 9, got {result}"
```

File names must start with `test_` and function names must also start with `test_`.

Use pytest assertions:
```python
assert a == b
assert condition
with pytest.raises(ValueError):
    code_that_should_raise()
```

For more, see the [pytest documentation](https://docs.pytest.org/).

---

## How to Run the Tests Locally

From the `monalisa_py/` directory:

```bash
# Run all tests
python -m pytest tests/ -v --tb=short

# Run a specific test file
python -m pytest tests/test_my_function.py -v

# Run tests matching a keyword
python -m pytest tests/ -k "fourier" -v
```

---

## Summary

| File | Purpose |
|------|---------|
| `test_*.py` | Your test files go here |

If you are unsure where to start, find an existing `test_*.py` file, copy it, rename it, and modify it to test your own function.

---

## CI / GitHub Actions

When you push to `main` or `ci-testing`, tests are run automatically via GitHub Actions. See `.github/workflows/python-tests.yml`.
