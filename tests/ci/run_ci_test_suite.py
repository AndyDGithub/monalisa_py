"""Auto-generated from MATLAB source. Review manually before production use."""

from tests.ci.setup_test_path import setup_test_path
import numpy as np

from third_part.matlab_compat.matlab_native import disp

from src.sparseMat.m.bmSparseMat_vec import error
from third_part.matlab_compat.matlab_native import fullfile

def run_ci_test_suite(dataDir, reportDir):
    # Run unit/integration/e2e MATLAB tests and write machine/human reports.
    # TODO(matlab-control): if nargin < 1 || isempty(dataDir)
    dataDir = fullfile("temp", "ci_data")
    # TODO(matlab-control): if nargin < 2 || isempty(reportDir)
    reportDir = fullfile("temp", "ci_reports")
    # TODO(matlab-control): if ~exist(reportDir, 'dir')
    mkdir(reportDir)
    setenv("MONALISA_CI_DATA_DIR", dataDir)
    setup_test_path()
    import matlab.unittest.TestSuite
    import matlab.unittest.TestRunner
    import matlab.unittest.plugins.DiagnosticsOutputPlugin
    import matlab.unittest.plugins.XMLPlugin
    runner = TestRunner.withTextOutput("OutputDetail", matlab.unittest.Verbosity.Detailed)
    runner.addPlugin(DiagnosticsOutputPlugin)
    runner.addPlugin(XMLPlugin.producingJUnitFormat(fullfile(reportDir, "junit.xml")))
    suiteUnit = TestSuite.fromFolder(fullfile("tests", "unit"), "IncludingSubfolders", True)
    suiteIntegration = TestSuite.fromFolder(fullfile("tests", "integration"), "IncludingSubfolders", True)
    suiteE2E = TestSuite.fromFolder(fullfile("tests", "e2e"), "IncludingSubfolders", True)
    resultsUnit = runner.run(suiteUnit)
    resultsIntegration = runner.run(suiteIntegration)
    resultsE2E = runner.run(suiteE2E)
    allResults = [resultsUnit, resultsIntegration, resultsE2E]
    summary.unit = summarizeResults(resultsUnit)
    summary.integration = summarizeResults(resultsIntegration)
    summary.e2e = summarizeResults(resultsE2E)
    # TODO(matlab-line): summary.global = summarizeResults(allResults);
    summary.generatedAtUtc = char(datetime("now", "TimeZone", "UTC", "Format", "yyyy-MM-dd""T""HH:mm:ss""Z"""))
    summary.dataDir = dataDir
    summary.reportDir = reportDir
    jsonText = jsonencode(summary, "PrettyPrint", True)
    fid = fopen(fullfile(reportDir, "matlab_test_summary.json"), "w")
    fwrite(fid, jsonText, "char")
    fclose(fid)
    md = buildMarkdownReport(summary)
    fid = fopen(fullfile(reportDir, "matlab_test_summary.md"), "w")
    fwrite(fid, md, "char")
    fclose(fid)
    disp("=== MATLAB CI TEST SUMMARY ===")
    disp(md)
    assertNoFailures(resultsUnit, "Unit tests failed")
    assertNoFailures(resultsIntegration, "Integration tests failed")
    assertNoFailures(resultsE2E, "End-to-end tests failed")

def summarizeResults(results):
    # TODO(matlab-control): if isempty(results)
    s.total = 0
    s.passed = 0
    s.failed = 0
    s.incomplete = 0
    s.durationSeconds = 0
    s.passRate = 0
    # TODO(matlab-line): return;
    s.total = numel(results)
    s.passed = np.sum([results.Passed])
    s.failed = np.sum([results.Failed])
    s.incomplete = np.sum([results.Incomplete])
    s.durationSeconds = np.sum([results.Duration])
    s.passRate = s.passed / max(1, s.total)
    return s

def buildMarkdownReport(summary):
    # TODO(matlab-line): txt = sprintf([ ...
    "# MATLAB CI Report\\n\\n"
    "- Generated (UTC): `%s`\\n"
    "- Data directory: `%s`\\n"
    "- Report directory: `%s`\\n\\n"
    "## Global\\n"
    "- Total: **%d**\\n"
    "- Passed: **%d**\\n"
    "- Failed: **%d**\\n"
    "- Incomplete: **%d**\\n"
    "- Duration (s): **%.3f**\\n"
    "- Pass rate: **%.2f%%**\\n\\n"
    "## Unit\\n"
    "- Total: %d, Passed: %d, Failed: %d, Incomplete: %d, Duration: %.3fs\\n"
    "## Integration\\n"
    "- Total: %d, Passed: %d, Failed: %d, Incomplete: %d, Duration: %.3fs\\n"
    "## End-to-end\\n"
    # TODO(matlab-line): '- Total: %d, Passed: %d, Failed: %d, Incomplete: %d, Duration: %.3fs\n'], ...
    summary.generatedAtUtc, summary.dataDir, summary.reportDir,
    # TODO(matlab-line): summary.global.total, summary.global.passed, summary.global.failed, ...
    # TODO(matlab-line): summary.global.incomplete, summary.global.durationSeconds, ...
    # TODO(matlab-line): 100 * summary.global.passRate, ...
    summary.unit.total, summary.unit.passed, summary.unit.failed,
    summary.unit.incomplete, summary.unit.durationSeconds,
    summary.integration.total, summary.integration.passed, summary.integration.failed,
    summary.integration.incomplete, summary.integration.durationSeconds,
    summary.e2e.total, summary.e2e.passed, summary.e2e.failed,
    # TODO(matlab-line): summary.e2e.incomplete, summary.e2e.durationSeconds);
    return txt

def assertNoFailures(results, message):
    # TODO(matlab-control): if isempty(results)
    # TODO(matlab-line): return;
    # TODO(matlab-control): if any([results.Failed]) || any([results.Incomplete])
    error(message)
