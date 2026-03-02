function setup_test_path()
% Ensure src is on MATLAB path for CI and local test runs.

thisFile = mfilename('fullpath');
testsDir = fileparts(fileparts(thisFile)); % .../tests
repoRoot = fileparts(testsDir);
srcDir = fullfile(repoRoot, 'src');

addpath(genpath(srcDir));
setenv('MONALISA_REPO_ROOT', repoRoot);

end
