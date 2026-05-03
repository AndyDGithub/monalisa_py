from __future__ import annotations

def testStupidExample(testCase):
    """Strict deterministic baseline port from MATLAB."""
    actual = (1 + 1) * 3
    expected = 6
    testCase.verifyEqual(actual, expected)
    return None

# Auto-generated entrypoint alias for import compatibility
TestExample = testStupidExample
