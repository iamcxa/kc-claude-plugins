'use strict';

const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

const { parse } = require('./parser');
const { resolve, resolveMultiSite } = require('./resolver');
const { generate } = require('./codegen');

/**
 * hashSources(flowPath, mappingPaths) — compute SHA-256 of source files.
 *
 * Hash is computed from source file contents only (flow YAML + mapping YAMLs),
 * NOT from generated output. This makes it deterministic for staleness detection.
 *
 * @param {string} flowPath - Path to the flow YAML file
 * @param {string|string[]} mappingPaths - One or more mapping file paths
 * @returns {string} SHA-256 hex digest
 */
function hashSources(flowPath, mappingPaths) {
  var hash = crypto.createHash('sha256');
  hash.update(fs.readFileSync(flowPath, 'utf8'));
  var paths = Array.isArray(mappingPaths) ? mappingPaths : [mappingPaths];
  paths.forEach(function(p) { hash.update(fs.readFileSync(p, 'utf8')); });
  return hash.digest('hex');
}

/**
 * compile(flowPath, mappingDir, outputDir, options) — run the full compilation pipeline.
 *
 * Supports single-site (mapping: field) and cross-site (sites: block) flows.
 *
 * Pass 1: parse(flowPath, mappingDir) — load and validate YAML
 * Pass 2: resolve(flow, mapping) or resolveMultiSite(flow, sites) — build symbol tables
 * Pass 3: generate(resolved, flowName, meta) — emit bash script string with provenance
 * Output: write <flowName>.sh to outputDir, chmod 755
 *
 * options.dryRun {boolean} — validate + generate but skip writing output file
 * options.verbose {boolean} — print step details (id, type, operands, expects) to stderr
 *
 * Returns: Promise<{ success: boolean, outputPath?: string, stats?, errors? }>
 */
async function compile(flowPath, mappingDir, outputDir, options) {
  var dryRun = (options && options.dryRun) || false;
  var verbose = (options && options.verbose) || false;
  // Pass 1: Parse
  var parseResult = parse(flowPath, mappingDir);
  if (parseResult.errors.length > 0) {
    parseResult.errors.forEach(function(e) { console.error('ERROR: ' + e); });
    return { success: false, errors: parseResult.errors };
  }

  var resolveResult;
  var mappingPaths;

  if (parseResult.sites) {
    // --- Cross-site flow path ---
    resolveResult = resolveMultiSite(parseResult.flow, parseResult.sites);
    if (resolveResult.errors.length > 0) {
      resolveResult.errors.forEach(function(e) { console.error('ERROR: ' + e); });
      return { success: false, errors: resolveResult.errors };
    }

    // Auto-inject per-site base URL variables from each mapping's base_url
    // e.g., { OFFICE_BASE_URL: 'http://localhost:5173', APP_BASE_URL: 'http://localhost:8081' }
    if (!resolveResult.resolved.variables) {
      resolveResult.resolved.variables = {};
    }
    var siteNames = Object.keys(parseResult.sites);
    for (var i = 0; i < siteNames.length; i++) {
      var siteName = siteNames[i];
      var siteData = parseResult.sites[siteName];
      var siteVarName = siteName.toUpperCase() + '_BASE_URL';
      if (!resolveResult.resolved.variables.hasOwnProperty(siteVarName)) {
        resolveResult.resolved.variables[siteVarName] = (siteData.mapping && siteData.mapping.base_url) || '';
      }
    }

    // Build mapping paths for SHA-256 hashing (cross-site: all mapping files)
    mappingPaths = siteNames.map(function(sn) {
      return path.join(mappingDir, parseResult.sites[sn].mappingName + '.yaml');
    });

  } else {
    // --- Single-site flow path ---
    resolveResult = resolve(parseResult.flow, parseResult.mapping);
    if (resolveResult.errors.length > 0) {
      resolveResult.errors.forEach(function(e) { console.error('ERROR: ' + e); });
      return { success: false, errors: resolveResult.errors };
    }

    // Auto-inject base_url from mapping when flow has no variables block
    // Prevents unbound ${BASE_URL} in navigate commands under set -u
    if (!resolveResult.resolved.variables || !('base_url' in resolveResult.resolved.variables)) {
      if (!resolveResult.resolved.variables) {
        resolveResult.resolved.variables = {};
      }
      resolveResult.resolved.variables = Object.assign(
        { base_url: parseResult.mapping.base_url || '' },
        resolveResult.resolved.variables
      );
    }

    // Build mapping path for SHA-256 hashing (single-site: one mapping file)
    mappingPaths = [path.join(mappingDir, parseResult.flow.mapping + '.yaml')];
  }

  // Compute SHA-256 hash from source files (not generated output — deterministic)
  var sourceHash = hashSources(flowPath, mappingPaths);
  var flowName = parseResult.flow.name;

  // Build meta object for header provenance
  var meta = {
    flowName: flowName,
    flowPath: flowPath,
    hash: sourceHash,
    timestamp: new Date().toISOString(),
  };
  if (mappingPaths.length === 1) {
    meta.mappingPath = mappingPaths[0];
  } else {
    meta.mappingPaths = mappingPaths;
  }

  // verbose: print step details to stderr before codegen
  if (verbose) {
    var steps = resolveResult.resolved.steps;
    steps.forEach(function(step, i) {
      var n = i + 1;
      var t = steps.length;
      console.error('[' + n + '/' + t + '] ' + step.id + ': ' + step.type);
      if (step.operands) {
        console.error('  operands: ' + JSON.stringify(step.operands));
      }
      if (step.expects) {
        step.expects.forEach(function(e) {
          console.error('  expect: ' + e.type + ' — ' + e.raw);
        });
      }
    });
  }

  // Pass 3: Codegen — pass meta for header provenance
  var script = generate(resolveResult.resolved, flowName, meta);

  // Compute output path
  var outPath = path.join(outputDir, flowName + '.sh');

  // dryRun: skip file creation, just report what would happen
  var s = resolveResult.stats;
  if (dryRun) {
    console.error('DRY RUN: would write ' + outPath + ' (' + script.length + ' bytes, ' + s.total + ' steps)');
  } else {
    // Write output
    fs.mkdirSync(outputDir, { recursive: true });
    fs.writeFileSync(outPath, script, 'utf8');
    fs.chmodSync(outPath, '755');
  }

  // Print summary
  console.log(
    'Compiled: ' + s.total + ' steps, ' +
    s.activeExpects + ' expects active, ' +
    s.deferredExpects + ' expects deferred (Phase 2)'
  );

  return { success: true, outputPath: outPath, stats: s };
}

module.exports = { compile: compile };

// ---------------------------------------------------------------------------
// CLI entry point — only runs when executed directly
// ---------------------------------------------------------------------------

if (require.main === module) {
  var args = process.argv.slice(2);
  if (args.length === 0) {
    console.error('Usage: node compiler.js <flow.yaml> [--mapping-dir <dir>] [--output-dir <dir>]');
    process.exit(1);
  }

  var flowPath = args[0];
  var mappingDir = path.dirname(path.resolve(flowPath));
  var outputDir = process.cwd();

  // Simple --flag value parsing (commander is Phase 2)
  for (var i = 1; i < args.length; i++) {
    if (args[i] === '--mapping-dir' && args[i + 1]) { mappingDir = args[++i]; }
    if (args[i] === '--output-dir' && args[i + 1]) { outputDir = args[++i]; }
  }

  compile(flowPath, mappingDir, outputDir).then(function(result) {
    if (!result.success) process.exit(1);
  });
}
