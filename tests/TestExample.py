from __future__ import annotations


def testStupidExample(testCase):
    """Strict deterministic baseline port from MATLAB."""
    # MATLAB comments
    # TestExample - A simple example test class to demonstrate how to write unit tests in MATLAB.
    # This test checks if (1 + 1) * 3 equals 6.
    # MATLAB body snapshot (untranslated, kept for parity context)
    # MATLAB: classdef TestExample < matlab.unittest.TestCase
    # MATLAB: methods (Test)
    # MATLAB: actual = (1 + 1) * 3;
    # MATLAB: expected = 6;
    # MATLAB: testCase.verifyEqual(actual, expected);
    # MATLAB: end
    # MATLAB: end
    # MATLAB: end
    # TODO(matlab-logic): translate MATLAB logic faithfully.
    return None

# Auto-generated entrypoint alias for import compatibility
TestExample = testStupidExample
