classdef TestMathOpUnit < matlab.unittest.TestCase
    % BICEP-oriented unit tests for math operations.
    %
    % B: Boundary
    % I: Inverse relationships
    % C: Cross-check with native MATLAB expressions
    % E: Error conditions
    % P: Performance characteristics

    methods (TestClassSetup)
        function addProjectPath(~)
            if exist('setup_test_path', 'file') ~= 2
                thisFile = mfilename('fullpath');
                testsDir = fileparts(fileparts(thisFile)); % .../tests
                addpath(fullfile(testsDir, 'ci'));
            end
            setup_test_path();
        end
    end

    methods (Test)
        %% B - Boundary
        function testBmPlusBoundaryEmpty(testCase)
            a = [];
            b = [];
            out = bmPlus(a, b);
            testCase.verifyEqual(out, []);
        end

        function testBmPlusBoundaryZeros(testCase)
            a = zeros(4, 3);
            b = ones(4, 3);
            out = bmPlus(a, b);
            testCase.verifyEqual(out, b);
        end

        function testBmMinusBoundaryScalarToCell(testCase)
            x = 10;
            y = {1, 2; 3, 4};
            out = bmMinus(x, y);
            testCase.verifyEqual(out{1}, 9);
            testCase.verifyEqual(out{4}, 6);
        end

        function testBmMultBoundaryComplex(testCase)
            x = [1 + 2i, 3 - 4i];
            y = [-2 + 1i, 5 + 2i];
            out = bmMult(x, y);
            testCase.verifyEqual(out, x .* y, 'AbsTol', 1e-12);
        end

        %% I - Inverse relationships
        function testInversePlusMinusArray(testCase)
            a = randn(20, 15);
            b = randn(20, 15);
            back = bmMinus(bmPlus(a, b), b);
            testCase.verifyEqual(back, a, 'AbsTol', 1e-12);
        end

        function testInverseMinusPlusArray(testCase)
            a = randn(8, 9);
            b = randn(8, 9);
            back = bmPlus(bmMinus(a, b), b);
            testCase.verifyEqual(back, a, 'AbsTol', 1e-12);
        end

        function testInverseMultByOne(testCase)
            a = randn(16, 7);
            out = bmMult(a, 1);
            testCase.verifyEqual(out, a, 'AbsTol', 1e-12);
        end

        %% C - Cross-check
        function testBmPlusCrossCheckCell(testCase)
            x = {ones(2), 2 * ones(2)};
            y = {3 * ones(2), 4 * ones(2)};
            out = bmPlus(x, y);
            testCase.verifyEqual(out{1}, x{1} + y{1});
            testCase.verifyEqual(out{2}, x{2} + y{2});
        end

        function testBmMinusCrossCheckArray(testCase)
            a = randn(13, 11);
            b = randn(13, 11);
            out = bmMinus(a, b);
            testCase.verifyEqual(out, a - b, 'AbsTol', 1e-12);
        end

        function testBmMultCrossCheckCell(testCase)
            x = {ones(2), 2 * ones(2)};
            y = {3 * ones(2), 4 * ones(2)};
            out = bmMult(x, y);
            testCase.verifyEqual(out{1}, x{1} .* y{1});
            testCase.verifyEqual(out{2}, x{2} .* y{2});
        end

        function testBmEuclideProdCrossCheckScalarH(testCase)
            x = [1 + 1i; 2 - 1i; 3];
            H = 2.0;
            expected = real(x(:)' * (H * x(:)));
            got = bmEuclideProd(x, x, H);
            testCase.verifyEqual(got, expected, 'AbsTol', 1e-12);
            testCase.verifyEqual(bmSquaredNorm(x, H), expected, 'AbsTol', 1e-12);
        end

        function testBmEuclideProdCrossCheckVectorH(testCase)
            x = randn(10, 1) + 1i * randn(10, 1);
            h = rand(10, 1);
            expected = real(x(:)' * (h(:) .* x(:)));
            got = bmEuclideProd(x, x, h);
            testCase.verifyEqual(got, expected, 'AbsTol', 1e-12);
        end

        %% E - Error conditions
        function testBmPlusErrorMixedTypes(testCase)
            f = @() bmPlus(1, {1});
            testCase.assertThrowsAny(f);
        end

        function testBmMinusErrorUnsupportedCase(testCase)
            f = @() bmMinus({1}, 1);
            testCase.assertThrowsAny(f);
        end

        function testBmEuclideProdErrorUnsupportedCase(testCase)
            f = @() bmEuclideProd({1}, 1, 1);
            testCase.assertThrowsAny(f);
        end

        %% P - Performance characteristics
        function testBmMultPerformanceScaling(testCase)
            % Relative performance check: larger problem should not explode.
            smallA = rand(64, 64);
            smallB = rand(64, 64);
            largeA = rand(256, 256);
            largeB = rand(256, 256);

            tSmall = timeit(@() bmMult(smallA, smallB));
            tLarge = timeit(@() bmMult(largeA, largeB));

            % Very tolerant upper bound to avoid flaky CI while still catching
            % accidental catastrophic regressions.
            testCase.verifyLessThan(tLarge / max(tSmall, eps), 200);
        end
    end

    methods
        function assertThrowsAny(testCase, f)
            didThrow = false;
            try
                f();
            catch
                didThrow = true;
            end
            testCase.verifyTrue(didThrow, 'Expected an exception, but none was thrown.');
        end
    end
end
