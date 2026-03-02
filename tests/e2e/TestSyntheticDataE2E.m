classdef TestSyntheticDataE2E < matlab.unittest.TestCase
    % End-to-end test over diversified synthetic datasets.
    % This validates a complete mini-processing flow over multiple cases.

    properties
        Cases
    end

    methods (TestClassSetup)
        function addProjectPath(~)
            if exist('setup_test_path', 'file') ~= 2
                thisFile = mfilename('fullpath');
                testsDir = fileparts(fileparts(thisFile)); % .../tests
                addpath(fullfile(testsDir, 'ci'));
            end
            setup_test_path();
        end

        function loadCases(testCase)
            dataDir = getenv('MONALISA_CI_DATA_DIR');
            if isempty(dataDir)
                repoRoot = getenv('MONALISA_REPO_ROOT');
                if isempty(repoRoot)
                    thisFile = mfilename('fullpath');
                    testsDir = fileparts(fileparts(thisFile)); % .../tests
                    repoRoot = fileparts(testsDir);
                end
                dataDir = fullfile(repoRoot, 'temp', 'ci_data');
            end
            p = fullfile(dataDir, 'synthetic_cases.mat');
            testCase.assumeTrue(exist(p, 'file') == 2, ...
                sprintf('Missing synthetic dataset: %s', p));
            s = load(p, 'cases');
            testCase.Cases = s.cases;
        end
    end

    methods (Test)
        function testMiniPipelineOverAllCases(testCase)
            cases = testCase.Cases;
            testCase.verifyGreaterThan(numel(cases), 5);

            metrics = zeros(1, numel(cases));
            for i = 1:numel(cases)
                c = cases(i);
                x = bmPointReshape(c.raw, c.nCh);
                x2 = bmMult(x, conj(x));
                e = bmSquaredNorm(x2, c.scalarWeight);
                metrics(i) = e;
            end

            testCase.verifyTrue(all(isfinite(metrics)));
            testCase.verifyTrue(all(metrics >= 0));
            testCase.verifyGreaterThan(std(metrics), 0);
        end
    end
end
