import matlab.unittest.TestSuite
import matlab.unittest.TestRunner
import matlab.unittest.plugins.DiagnosticsOutputPlugin

thisFile = mfilename('fullpath');
testsDir = fileparts(thisFile);
repoRoot = fileparts(testsDir);
addpath(fullfile(testsDir, 'ci'));
setup_test_path();
prepare_ci_data(fullfile(repoRoot, 'temp', 'ci_data'));

suite = [ ...
    TestSuite.fromFolder(fullfile(repoRoot, 'tests', 'unit'), 'IncludingSubfolders', true), ...
    TestSuite.fromFolder(fullfile(repoRoot, 'tests', 'integration'), 'IncludingSubfolders', true), ...
    TestSuite.fromFolder(fullfile(repoRoot, 'tests', 'e2e'), 'IncludingSubfolders', true) ...
    ];

runner = TestRunner.withTextOutput('OutputDetail', matlab.unittest.Verbosity.Detailed);
runner.addPlugin(DiagnosticsOutputPlugin);

results = runner.run(suite);
disp(table(results));

if any([results.Failed]) || any([results.Incomplete])
    error('One or more tests failed.');
end
