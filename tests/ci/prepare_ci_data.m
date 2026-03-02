function prepare_ci_data(dataDir)
% Prepare diversified CI test data outside the repository-tracked files.
% Data source policy:
% 1) Optional download from URL list in MONALISA_TEST_DATA_URLS (semicolon separated)
% 2) Always generate deterministic synthetic datasets

if nargin < 1 || isempty(dataDir)
    dataDir = fullfile('temp', 'ci_data');
end

if ~exist(dataDir, 'dir')
    mkdir(dataDir);
end

% Try downloading external datasets if provided.
urlList = getenv('MONALISA_TEST_DATA_URLS');
if ~isempty(urlList)
    urls = split(string(urlList), ';');
    for i = 1:numel(urls)
        u = strtrim(urls(i));
        if strlength(u) == 0
            continue;
        end
        outFile = fullfile(dataDir, sprintf('external_%02d.mat', i));
        try
            websave(outFile, char(u));
            fprintf('Downloaded external test data: %s\n', outFile);
        catch ME
            warning('Could not download "%s": %s', u, ME.message);
        end
    end
end

% Deterministic synthetic datasets (diversified types/shapes).
rng(42);
cases = struct([]);

for k = 1:12
    nCh = randi([1, 4]);
    nPt = randi([4, 50]);
    raw = randn(nCh, nPt);
    if mod(k, 2) == 0
        raw = raw + 1i * randn(size(raw));
    end

    weight = rand(1, nCh * nPt);
    weight = reshape(weight, size(raw));
    scalarWeight = 0.5 + rand();

    cellX = {raw, raw * 2};
    cellY = {raw * 0.5, raw * 3};

    cases(k).id = k;
    cases(k).raw = raw; %#ok<*AGROW>
    cases(k).nCh = nCh;
    cases(k).weight = weight;
    cases(k).scalarWeight = scalarWeight;
    cases(k).cellX = cellX;
    cases(k).cellY = cellY;
end

save(fullfile(dataDir, 'synthetic_cases.mat'), 'cases', '-v7.3');
fprintf('Synthetic CI test data written to %s\n', fullfile(dataDir, 'synthetic_cases.mat'));

end
