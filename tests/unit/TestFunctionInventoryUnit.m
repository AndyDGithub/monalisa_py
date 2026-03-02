classdef TestFunctionInventoryUnit < matlab.unittest.TestCase
    % Baseline unit smoke test over all MATLAB functions under src/.
    % This does not validate full numerical behavior for each function,
    % but guarantees discoverability and basic accessibility project-wide.

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
        function testAllFunctionsResolvable(testCase)
            repoRoot = getenv('MONALISA_REPO_ROOT');
            if isempty(repoRoot)
                thisFile = mfilename('fullpath');
                testsDir = fileparts(fileparts(thisFile)); % .../tests
                repoRoot = fileparts(testsDir);
            end

            srcRoot = fullfile(repoRoot, 'src');
            files = dir(fullfile(srcRoot, '**', '*.m'));
            testCase.verifyGreaterThan(numel(files), 0, 'No MATLAB source files found.');

            missing = strings(0, 1);
            for k = 1:numel(files)
                [~, fn] = fileparts(files(k).name);
                if exist(fn, 'file') == 0
                    missing(end + 1) = string(fullfile(files(k).folder, files(k).name)); %#ok<AGROW>
                end
            end

            testCase.verifyEmpty(missing, ...
                sprintf('Some functions are not resolvable on MATLAB path:\n%s', strjoin(missing, newline)));
        end
    end
end
