#!/usr/bin/env node
'use strict';

/**
 * e2e-compile — Commander CLI for the E2E flow compiler.
 *
 * Usage:
 *   e2e-compile <flow-name>           compile a single flow
 *   e2e-compile --all                 compile all flows in flows directory
 *   e2e-compile --dry-run <flow-name> validate without writing output
 *   e2e-compile --verbose <flow-name> show resolved step details during compilation
 *   e2e-compile --help                show help
 *   e2e-compile --version             show version
 *
 * @see compiler/compiler.js for the compile() function API
 */

const { Command } = require('commander');
const path = require('node:path');
const fs = require('node:fs');
const { compile } = require('../compiler/compiler.js');
const { appendCoverageHistory, checkCoverageRegression } = require('../compiler/coverage.js');

const program = new Command();

program
  .name('e2e-compile')
  .description('Compile E2E flow YAML to standalone bash test scripts')
  .version('1.0.0');

program
  .argument('[flow-name]', 'flow name or path to compile (omit when using --all)')
  .option('--all', 'compile all flows in flows directory')
  .option('--dry-run', 'validate flow + mapping coherence without writing output')
  .option('--verbose', 'show resolved operands and expects per step')
  .option('--coverage', 'produce static coverage report after compilation')
  .option('--coverage-output <dir>', 'directory for coverage JSON output', '.claude/e2e/coverage')
  .option('--json', 'emit a single machine-readable JSON document on stdout instead of prose (structured errors with repair candidates where available)')
  .option('--flows-dir <dir>', 'flows directory', '.claude/e2e/flows')
  .option('--mappings-dir <dir>', 'mappings directory', '.claude/e2e/mappings')
  .option('--output-dir <dir>', 'output directory', '.claude/e2e/compiled')
  .action(async function(flowName, options) {
    var compileOptions = {
      dryRun: options.dryRun || false,
      verbose: options.verbose || false,
      coverage: options.coverage || false,
      json: options.json || false,
    };

    // Default stats shape for a JSON document whose compile() result has no
    // `stats` (e.g. a parse failure, which never reaches the resolver).
    function defaultStats(errorDetails) {
      return { total: 0, activeExpects: 0, deferredExpects: 0, notAutomatedExpects: 0, resolveErrors: (errorDetails || []).length };
    }

    // Stats for the --json document: the resolver's stats (when present) plus
    // a resolveErrors count, so a JSON consumer never has to derive it from
    // errors.length itself.
    function jsonStats(result) {
      var errCount = (result.errorDetails || []).length;
      if (result.stats) {
        return Object.assign({}, result.stats, { resolveErrors: errCount });
      }
      return defaultStats(result.errorDetails);
    }

    if (options.all) {
      // -----------------------------------------------------------------------
      // Batch mode (CLI-02): compile all YAML files in flows directory
      // -----------------------------------------------------------------------
      var flowsDir = options.flowsDir;
      var mappingsDir = options.mappingsDir;
      var outputDir = options.outputDir;

      var files;
      try {
        files = fs.readdirSync(flowsDir).filter(function(f) { return f.endsWith('.yaml'); });
      } catch (err) {
        var readErrMessage = 'cannot read flows directory: ' + flowsDir + ' — ' + err.message;
        console.error('ERROR: ' + readErrMessage);
        // Deliberately NOT the empty-directory shape below: an unreadable
        // directory is a failure (ok:false, exit 1), an empty one is a no-op
        // (ok:true, exit 0). Collapsing them would make "nothing to compile"
        // indistinguishable from "could not look".
        if (options.json) {
          console.log(JSON.stringify({
            ok: false,
            flows: [],
            summary: { passed: 0, failed: 0 },
            errors: [{ message: readErrMessage }],
          }));
        }
        process.exit(1);
        return;
      }

      if (files.length === 0) {
        if (options.json) {
          console.log(JSON.stringify({ ok: true, flows: [], summary: { passed: 0, failed: 0 } }));
        } else {
          console.log('No YAML files found in ' + flowsDir);
        }
        process.exit(0);
        return;
      }

      var passed = 0;
      var failed = 0;
      var failures = [];
      var flowResults = []; // --json accumulator: {flow, ok, stats, errors} per file

      // Aggregate coverage across all flows (for --all --coverage)
      var allCoverageElements = {};  // keyed by element name, accumulate verified/reached
      var allCoverageTotal = 0;
      var allCoverageVerified = 0;
      var allCoverageReached = 0;
      var coverageFlowCount = 0;

      // Process each file — continue on error (CRITICAL: never stop on first failure)
      for (var i = 0; i < files.length; i++) {
        var flowFile = files[i];
        var flowPath = path.join(flowsDir, flowFile);
        var flowBaseName = path.basename(flowFile, '.yaml');
        try {
          var result = await compile(flowPath, mappingsDir, outputDir, compileOptions);
          if (result.success) {
            if (!options.json) console.log('OK: ' + flowBaseName);
            passed++;
            flowResults.push({ flow: flowBaseName, ok: true, stats: jsonStats(result), errors: result.errorDetails || [] });
            // Aggregate coverage if available
            if (options.coverage && result.coverage) {
              coverageFlowCount++;
              result.coverage.elements.forEach(function(el) {
                if (!allCoverageElements[el.name]) {
                  allCoverageElements[el.name] = { name: el.name, page: el.page, reached_count: 0, verified_count: 0 };
                }
                allCoverageElements[el.name].reached_count += el.reached_count;
                allCoverageElements[el.name].verified_count += el.verified_count;
              });
            }
          } else {
            console.error('FAIL: ' + flowBaseName + (result.errors ? ' — ' + result.errors.join(', ') : ''));
            failures.push(flowBaseName);
            failed++;
            flowResults.push({
              flow: flowBaseName,
              ok: false,
              stats: jsonStats(result),
              errors: result.errorDetails || [],
            });
          }
        } catch (err) {
          console.error('FAIL: ' + flowBaseName + ' — ' + err.message);
          failures.push(flowBaseName);
          failed++;
          flowResults.push({
            flow: flowBaseName,
            ok: false,
            stats: defaultStats(null),
            errors: [{ message: err.message }],
          });
        }
      }

      // --json: one aggregated document, nothing else on stdout. Skips the
      // prose coverage-aggregate print/write below entirely (untested,
      // unscoped combination with --coverage; the per-flow coverage data
      // above is already discarded in that case).
      if (options.json) {
        console.log(JSON.stringify({
          ok: failed === 0,
          flows: flowResults,
          summary: { passed: passed, failed: failed },
        }));
        process.exit(failed > 0 ? 1 : 0);
        return;
      }

      // Emit aggregated coverage summary for --all --coverage
      if (options.coverage && coverageFlowCount > 0) {
        var aggElements = Object.values(allCoverageElements);
        var aggTotal = aggElements.length;
        aggElements.forEach(function(el) {
          if (el.reached_count > 0) allCoverageReached++;
          if (el.verified_count > 0) allCoverageVerified++;
        });
        allCoverageTotal = aggTotal;
        var aggPercent = aggTotal === 0 ? 0 : Math.round((allCoverageVerified / aggTotal) * 100);
        console.log('Coverage: ' + allCoverageVerified + '/' + aggTotal + ' elements (' + aggPercent + '%) verified across ' + coverageFlowCount + ' flow' + (coverageFlowCount === 1 ? '' : 's'));

        // Write aggregated coverage.json
        var coverageOutputDir = options.coverageOutput;
        fs.mkdirSync(coverageOutputDir, { recursive: true });
        var aggCoverageData = {
          flow: '__all__',
          timestamp: new Date().toISOString(),
          elements: aggElements,
          summary: {
            total: aggTotal,
            reached: allCoverageReached,
            verified: allCoverageVerified,
            percent: aggPercent,
          },
        };
        fs.writeFileSync(path.join(coverageOutputDir, 'coverage.json'), JSON.stringify(aggCoverageData, null, 2) + '\n', 'utf8');

        // Append to coverage-history.json
        var historyPath = path.join(coverageOutputDir, 'coverage-history.json');
        appendCoverageHistory(historyPath, {
          flow: '__all__',
          timestamp: new Date().toISOString(),
          percent: aggPercent,
          verified: allCoverageVerified,
          total: aggTotal,
        });
      }

      // Summary report
      console.log('\nBatch complete: ' + passed + ' OK, ' + failed + ' failed');
      if (failures.length > 0) {
        console.error('Failed flows: ' + failures.join(', '));
        process.exit(1);
      }
      process.exit(0);

    } else if (flowName) {
      // -----------------------------------------------------------------------
      // Single flow mode (CLI-01): compile one flow
      // -----------------------------------------------------------------------
      var flowsDir = options.flowsDir;
      var mappingsDir = options.mappingsDir;
      var outputDir = options.outputDir;

      // Resolve flow path: if flowName ends with .yaml, use as-is; otherwise append directory + extension
      var flowPath;
      if (flowName.endsWith('.yaml')) {
        flowPath = path.isAbsolute(flowName) ? flowName : path.join(flowsDir, flowName);
      } else {
        flowPath = path.join(flowsDir, flowName + '.yaml');
      }

      try {
        var result = await compile(flowPath, mappingsDir, outputDir, compileOptions);

        // --json: one document, nothing else on stdout. Returns before any of
        // the existing prose/coverage presentation below runs (an untested,
        // unscoped --json + --coverage combination skips coverage.json write
        // as a result — the resolved flow + compiled output are unaffected).
        if (options.json) {
          var jsonDoc = {
            ok: result.success,
            flow: path.basename(flowName, '.yaml'),
            stats: jsonStats(result),
            errors: result.errorDetails || [],
            coverage: (options.coverage && result.coverage) ? result.coverage : null,
          };
          console.log(JSON.stringify(jsonDoc));
          process.exit(result.success ? 0 : 1);
          return;
        }

        if (result.success) {
          console.log('OK: ' + path.basename(flowName, '.yaml'));

          // Output coverage data when --coverage flag was used
          if (options.coverage && result.coverage) {
            var cov = result.coverage;
            var coverageOutputDir = options.coverageOutput;
            var flowBaseName = path.basename(flowName, '.yaml');

            // Print coverage summary line
            console.log('Coverage: ' + cov.summary.verified + '/' + cov.summary.total + ' elements (' + cov.summary.percent + '%) verified across 1 flow');

            // Print reached-but-not-verified elements
            var reachedNotVerified = cov.elements.filter(function(el) { return el.reached_count > 0 && el.verified_count === 0; });
            if (reachedNotVerified.length > 0) {
              console.log('Reached but not verified (' + reachedNotVerified.length + '):');
              reachedNotVerified.forEach(function(el) { console.log('  - ' + el.page + '/' + el.name); });
            }

            // Print untouched elements
            var untouched = cov.elements.filter(function(el) { return el.reached_count === 0 && el.verified_count === 0; });
            if (untouched.length > 0) {
              console.log('Untouched (' + untouched.length + '):');
              untouched.forEach(function(el) { console.log('  - ' + el.page + '/' + el.name); });
            }

            // Write coverage.json to coverage output directory
            fs.mkdirSync(coverageOutputDir, { recursive: true });
            var coverageJson = {
              flow: flowBaseName,
              timestamp: new Date().toISOString(),
              elements: cov.elements,
              summary: cov.summary,
            };
            fs.writeFileSync(path.join(coverageOutputDir, 'coverage.json'), JSON.stringify(coverageJson, null, 2) + '\n', 'utf8');

            // Append to coverage-history.json
            var historyPath = path.join(coverageOutputDir, 'coverage-history.json');
            appendCoverageHistory(historyPath, {
              flow: flowBaseName,
              mapping: flowBaseName,
              timestamp: new Date().toISOString(),
              percent: cov.summary.percent,
              verified: cov.summary.verified,
              total: cov.summary.total,
            });

            // Check for regression and emit warning if applicable
            var warning = checkCoverageRegression(historyPath, flowBaseName, cov.summary.percent);
            if (warning) {
              console.log(warning);
            }
          }

          process.exit(0);
        } else {
          if (result.errors) {
            result.errors.forEach(function(e) { console.error('ERROR: ' + e); });
          }
          process.exit(1);
        }
      } catch (err) {
        console.error('ERROR: ' + err.message);
        // A throw from compile() (unwritable output dir, unreadable source, …)
        // still owes the --json caller a document: same single-flow shape, the
        // thrown text as a tier-2 error. Mirrors how batch mode already wraps a
        // thrown compile error.
        if (options.json) {
          var thrownErrors = [{ message: err.message }];
          console.log(JSON.stringify({
            ok: false,
            flow: path.basename(flowName, '.yaml'),
            stats: defaultStats(thrownErrors),
            errors: thrownErrors,
            coverage: null,
          }));
        }
        process.exit(1);
      }

    } else {
      // No flow-name and no --all. This is a usage error rather than a compile
      // error, but --json still emits a document: SKILL.md's Phase 3 was
      // rewritten to parse stdout unconditionally and has no prose fallback
      // left, so making the guarantee conditional on argument validity would
      // reopen exactly the hole this branch is being fixed for. The human
      // usage text moves to stderr so an interactive caller still sees it, and
      // the exit code becomes 1 — nothing was compiled, and the previous exit 0
      // told a consumer the run had succeeded.
      if (options.json) {
        var usageErrors = [{ message: 'no flow name given and --all not set: pass a flow name or --all' }];
        console.error(program.helpInformation());
        console.log(JSON.stringify({
          ok: false,
          flow: null,
          stats: defaultStats(usageErrors),
          errors: usageErrors,
          coverage: null,
        }));
        process.exit(1);
        return;
      }
      program.help();
    }
  });

// IMPORTANT: Use parseAsync (not parse) because compile() is async.
// Using parse() with async actions causes the process to exit before async work completes.
program.parseAsync(process.argv);
