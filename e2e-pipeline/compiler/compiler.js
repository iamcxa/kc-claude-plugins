'use strict';

const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

const { parse } = require('./parser');
const { resolve, resolveMultiSite } = require('./resolver');
const { generate } = require('./codegen');
const { siteBaseUrlVariable } = require('./site-name');
const selectorPolicy = require('./lib/selector-policy.js');

var COMPILER_VERSION = require('../package.json').version;

var DEFAULT_SELECTOR_BASELINE = path.join('.claude', 'e2e', 'selector-baseline.tsv');

/**
 * loadSelectorBaseline(baselinePath) — read the grandfathered-findings baseline.
 *
 * An absent file is the normal case and yields an empty baseline. A present-but-malformed
 * file throws, because a baseline that silently fails to parse silently stops
 * grandfathering, and the compile then reds on something the author believes is listed.
 *
 * Read-only by construction: this is the only place the compile path touches the baseline
 * path, and it opens for reading. That absent write call is what makes "the gate cannot
 * regenerate its own baseline" true — the producer is a separate binary,
 * `bin/e2e-selector-baseline.js`, which prints to stdout.
 */
function loadSelectorBaseline(baselinePath) {
  var text;
  try {
    text = fs.readFileSync(baselinePath, 'utf8');
  } catch (e) {
    if (e && e.code === 'ENOENT') return selectorPolicy.parseBaseline('');
    throw e;
  }
  return selectorPolicy.parseBaseline(text);
}

/**
 * checkSelectorPolicy(...) — the two-severity selector gate (#88).
 *
 * Severity is a function of scope, per the captain's 2026-08-01 ruling:
 *
 *   warning   every `selector:` in each loaded mapping file — path:line:class on stderr
 *   blocking  the selectors this flow actually resolves
 *
 * Whole-file blocking was the alternative and was ruled out: it reds every flow that
 * loads a mapping carrying unrelated legacy debt, which the issue's own acceptance ideas
 * ask not to require.
 *
 * Returns { errors, errorDetails } — both empty when nothing blocks.
 */
function checkSelectorPolicy(mappingSources, referencedElements, baseline) {
  // Both channels traverse ELEMENTS, and the split between them is exact set subtraction
  // on element identity.
  //
  // An earlier revision warned from a line-oriented text scan and subtracted the blocking
  // set by (class, selector) string. Two elements can carry the identical banned selector
  // — the real corpus has one string on three elements — and the two traversals can also
  // disagree on the string itself whenever a YAML escape survives one and not the other.
  // Either way a finding was reported by both channels or by neither. Identity has no such
  // failure mode: an element is in exactly one channel.
  //
  // Line numbers are recovered per finding by `locateSelectorLine`, which returns null
  // rather than guessing. `scripts/lint-mapping.sh` keeps the text traversal, where a line
  // number is the natural unit.
  // Everything downstream — the finding identity, the baseline record, the diagnostic —
  // keys on the mapping file's BASENAME. A cross-site flow can legitimately load two
  // mappings from different directories that share one, and then a blocking finding in
  // one site suppresses the warning for the same element name in the other, and a single
  // baseline record grandfathers both. Rather than widen the key (which would make a
  // committed baseline depend on directory layout), refuse the ambiguity outright and say
  // so. This is the enforcement point for the docs' claim that a basename is a sufficient
  // key.
  var byBase = new Map();
  var collisions = [];
  mappingSources.forEach(function(src) {
    var base = path.basename(src.path);
    if (byBase.has(base) && byBase.get(base) !== src.path) collisions.push(base);
    byBase.set(base, src.path);
  });
  if (collisions.length > 0) {
    var collisionMessage =
      'two mapping files loaded by this flow share the basename ' +
      JSON.stringify(collisions[0]) +
      ', which the selector policy uses as a finding and baseline key. Rename one so the' +
      ' two are distinguishable.';
    return {
      errors: [collisionMessage],
      errorDetails: [{ message: collisionMessage, selector_class: null }],
    };
  }

  var allRecords = [];
  var textByFile = new Map();
  mappingSources.forEach(function(src) {
    var base = path.basename(src.path);
    textByFile.set(base, { text: src.text, path: src.path });
    allRecords = allRecords.concat(selectorPolicy.mappingElementRecords(src.mapping, base));
  });

  function identity(f) { return f.mappingFile + '\t' + f.page + '.' + f.element + '\t' + f.class; }

  function describe(f) {
    var src = textByFile.get(f.mappingFile);
    var line = src ? selectorPolicy.locateSelectorLine(src.text, f.element, f.selector) : null;
    var where = src ? src.path : f.mappingFile;
    return where + (line === null ? '' : ':' + line) + ': ' + f.page + '.' + f.element;
  }

  // Resolved elements, deduped: one element referenced by many steps is one finding.
  var seen = new Set();
  var resolvedFindings = [];
  selectorPolicy.scanElements(referencedElements || []).forEach(function(f) {
    var key = identity(f);
    if (seen.has(key)) return;
    seen.add(key);
    resolvedFindings.push(f);
  });

  var blocking = [];
  var grandfathered = [];
  resolvedFindings.forEach(function(f) {
    if (selectorPolicy.isGrandfathered(f, baseline)) grandfathered.push(f);
    else blocking.push(f);
  });

  selectorPolicy.scanElements(allRecords).forEach(function(f) {
    if (seen.has(identity(f))) return;   // already spoken for by the blocking channel
    console.error(
      'WARNING: ' + describe(f) + ': ' + f.class + ': banned selector ' +
      JSON.stringify(f.selector) + ' — ' + f.guidance +
      ' (no step in this flow resolves it, so it does not block)'
    );
  });

  grandfathered.forEach(function(f) {
    // Louder than the warning above on purpose: this flow actively depends on a selector
    // the baseline only tolerates. It does not block, but it must not read like dormant
    // debt either.
    console.error(
      'WARNING: ' + describe(f) + ': ' + f.class +
      ': this flow RESOLVES a grandfathered banned selector ' + JSON.stringify(f.selector) +
      ' — ' + f.guidance
    );
  });

  var errors = [];
  var errorDetails = [];
  blocking.forEach(function(f) {
    var message =
      describe(f) + ": banned selector class '" + f.class + "' in selector " +
      JSON.stringify(f.selector) + ' — ' + f.guidance +
      '. Fix the mapping, or record it in the selector baseline if it is pre-existing' +
      ' debt (see docs/ci-integration.md).';
    errors.push(message);
    errorDetails.push({
      message: message,
      selector_class: f.class,
      mapping_file: f.mappingFile,
      page: f.page,
      element: f.element,
      selector: f.selector,
    });
  });

  return { errors: errors, errorDetails: errorDetails };
}

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
  var coverage = (options && options.coverage) || false;
  var json = (options && options.json) || false;
  // Pass 1: Parse
  var parseResult = parse(flowPath, mappingDir);
  if (parseResult.errors.length > 0) {
    parseResult.errors.forEach(function(e) { console.error('ERROR: ' + e); });
    // JSON boundary: wrap parser.js's plain-string errors generically as
    // message-only errorDetails, without editing parser.js itself (parser
    // errors are structural/type errors — no candidate data applies).
    return {
      success: false,
      errors: parseResult.errors,
      errorDetails: parseResult.errors.map(function(m) { return { message: m }; }),
    };
  }

  var resolveResult;
  var mappingPaths;

  var coverageData = undefined;

  if (parseResult.sites) {
    // --- Cross-site flow path ---
    resolveResult = resolveMultiSite(parseResult.flow, parseResult.sites);
    if (resolveResult.errors.length > 0) {
      resolveResult.errors.forEach(function(e) { console.error('ERROR: ' + e); });
      return {
        success: false,
        errors: resolveResult.errors,
        errorDetails: resolveResult.errorDetails,
        stats: resolveResult.stats,
      };
    }

    // Auto-inject per-site base URL variables from each mapping's base_url
    // e.g., { OFFICE_BASE_URL: 'http://localhost:5173', APP_BASE_URL: 'http://localhost:8081' }
    if (!resolveResult.resolved.variables) {
      resolveResult.resolved.variables = {};
    }
    var siteNames = Object.keys(parseResult.sites);
    resolveResult.resolved.browserApps = {
      default: parseResult.sites[siteNames[0]].mapping.app,
    };
    for (var i = 0; i < siteNames.length; i++) {
      var siteName = siteNames[i];
      var siteData = parseResult.sites[siteName];
      resolveResult.resolved.browserApps[siteName] = siteData.mapping.app;
      var siteVarName = siteBaseUrlVariable(siteName);
      if (!Object.prototype.hasOwnProperty.call(resolveResult.resolved.variables, siteVarName)) {
        resolveResult.resolved.variables[siteVarName] = (siteData.mapping && siteData.mapping.base_url) || '';
      }
    }

    // Build mapping paths for SHA-256 hashing (cross-site: all mapping files)
    mappingPaths = siteNames.map(function(sn) {
      return path.join(mappingDir, parseResult.sites[sn].mappingName + '.yaml');
    });

    // Coverage analysis not yet supported for cross-site flows
    if (coverage) {
      console.error('Warning: Coverage analysis for cross-site flows is not yet supported');
      coverageData = null;
    }

  } else {
    // --- Single-site flow path ---
    resolveResult = resolve(parseResult.flow, parseResult.mapping, {
      runtimeValues: parseResult.flow.runtime_values || null,
    });
    if (resolveResult.errors.length > 0) {
      resolveResult.errors.forEach(function(e) { console.error('ERROR: ' + e); });
      return {
        success: false,
        errors: resolveResult.errors,
        errorDetails: resolveResult.errorDetails,
        stats: resolveResult.stats,
      };
    }
    resolveResult.resolved.browserApps = {
      default: parseResult.mapping.app,
    };

    // Auto-inject base_url from mapping when flow has no variables block
    // Prevents unbound ${BASE_URL} in navigate commands under set -u
    var singleSiteVariables = resolveResult.resolved.variables;
    var hasBaseUrl = singleSiteVariables && Object.keys(singleSiteVariables).some(function(variableName) {
      return variableName.toUpperCase() === 'BASE_URL';
    });
    if (!hasBaseUrl) {
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

    // Coverage analysis for single-site flows
    if (coverage) {
      var analyzeCoverage = require('./coverage').analyzeCoverage;
      coverageData = analyzeCoverage(parseResult.mapping, resolveResult.resolved.steps);
    }
  }

  // --- Selector policy gate (#88) -----------------------------------------
  //
  // Sits here, after resolve() and before generate()/write, because the blocking scope
  // is "what this flow resolves" and nothing earlier knows that: parse() returns before
  // resolve() runs, and validateMapping() sees only version/pages. A banned selector on
  // a resolved element therefore fails with no `.sh` produced — nothing a browser could
  // later run.
  var mappingObjects = parseResult.sites
    ? Object.keys(parseResult.sites).map(function(sn) { return parseResult.sites[sn].mapping; })
    : [parseResult.mapping];
  var mappingSources = mappingPaths.map(function(p, i) {
    return { path: p, text: fs.readFileSync(p, 'utf8'), mapping: mappingObjects[i] };
  });
  var referencedElements = (resolveResult.referencedElements || []).map(function(rec) {
    // Single-site resolution has one mapping and does not stamp the file; cross-site
    // stamps it per site because each site resolves against a different mapping.
    if (rec.mappingFile) return rec;
    return {
      mappingFile: path.basename(mappingPaths[0]),
      page: rec.page,
      element: rec.element,
      selector: rec.selector,
    };
  });
  var baselinePath = (options && options.selectorBaseline) || DEFAULT_SELECTOR_BASELINE;
  var selectorResult = checkSelectorPolicy(
    mappingSources,
    referencedElements,
    loadSelectorBaseline(baselinePath)
  );
  if (selectorResult.errors.length > 0) {
    selectorResult.errors.forEach(function(e) { console.error('ERROR: ' + e); });
    return {
      success: false,
      errors: selectorResult.errors,
      errorDetails: selectorResult.errorDetails,
      stats: resolveResult.stats,
    };
  }

  // Compute SHA-256 hash from source files (not generated output — deterministic)
  var sourceHash = hashSources(flowPath, mappingPaths);
  var flowName = parseResult.flow.name;

  // Build meta object for header provenance
  var meta = {
    flowName: flowName,
    flowPath: flowPath,
    hash: sourceHash,
    compilerVersion: COMPILER_VERSION,
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

  // Print summary — suppressed under --json, where stdout must carry exactly
  // one JSON document and nothing else (the CLI builds that document from the
  // returned errorDetails/stats below instead).
  if (!json) {
    console.log(
      'Compiled: ' + s.total + ' steps, ' +
      s.activeExpects + ' expects active, ' +
      (s.notAutomatedExpects || 0) + ' expects not automated'
    );
  }

  var returnVal = { success: true, outputPath: outPath, stats: s, errorDetails: resolveResult.errorDetails };
  if (coverage) {
    returnVal.coverage = coverageData;
  }
  return returnVal;
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
