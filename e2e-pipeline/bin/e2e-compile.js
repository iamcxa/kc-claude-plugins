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
  .option('--flows-dir <dir>', 'flows directory', '.claude/e2e/flows')
  .option('--mappings-dir <dir>', 'mappings directory', '.claude/e2e/mappings')
  .option('--output-dir <dir>', 'output directory', '.claude/e2e/compiled')
  .action(async function(flowName, options) {
    var compileOptions = {
      dryRun: options.dryRun || false,
      verbose: options.verbose || false,
    };

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
        console.error('ERROR: cannot read flows directory: ' + flowsDir + '\n' + err.message);
        process.exit(1);
        return;
      }

      if (files.length === 0) {
        console.log('No YAML files found in ' + flowsDir);
        process.exit(0);
        return;
      }

      var passed = 0;
      var failed = 0;
      var failures = [];

      // Process each file — continue on error (CRITICAL: never stop on first failure)
      for (var i = 0; i < files.length; i++) {
        var flowFile = files[i];
        var flowPath = path.join(flowsDir, flowFile);
        var flowBaseName = path.basename(flowFile, '.yaml');
        try {
          var result = await compile(flowPath, mappingsDir, outputDir, compileOptions);
          if (result.success) {
            console.log('OK: ' + flowBaseName);
            passed++;
          } else {
            console.error('FAIL: ' + flowBaseName + (result.errors ? ' — ' + result.errors.join(', ') : ''));
            failures.push(flowBaseName);
            failed++;
          }
        } catch (err) {
          console.error('FAIL: ' + flowBaseName + ' — ' + err.message);
          failures.push(flowBaseName);
          failed++;
        }
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
        if (result.success) {
          console.log('OK: ' + path.basename(flowName, '.yaml'));
          process.exit(0);
        } else {
          if (result.errors) {
            result.errors.forEach(function(e) { console.error('ERROR: ' + e); });
          }
          process.exit(1);
        }
      } catch (err) {
        console.error('ERROR: ' + err.message);
        process.exit(1);
      }

    } else {
      // No flow-name and no --all: show help
      program.help();
    }
  });

// IMPORTANT: Use parseAsync (not parse) because compile() is async.
// Using parse() with async actions causes the process to exit before async work completes.
program.parseAsync(process.argv);
