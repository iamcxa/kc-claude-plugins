'use strict';

const fs = require('node:fs');
const path = require('node:path');

const { parse } = require('./parser');
const { resolve } = require('./resolver');
const { generate } = require('./codegen');

/**
 * compile(flowPath, mappingDir, outputDir) — run the full compilation pipeline.
 *
 * Pass 1: parse(flowPath, mappingDir) — load and validate YAML
 * Pass 2: resolve(flow, mapping) — build symbol table, resolve operands
 * Pass 3: generate(resolved, flowName) — emit bash script string
 * Output: write <flowName>.sh to outputDir, chmod 755
 *
 * Returns: Promise<{ success: boolean, outputPath?: string, stats?, errors? }>
 */
async function compile(flowPath, mappingDir, outputDir) {
  // Pass 1: Parse
  var parseResult = parse(flowPath, mappingDir);
  if (parseResult.errors.length > 0) {
    parseResult.errors.forEach(function(e) { console.error('ERROR: ' + e); });
    return { success: false, errors: parseResult.errors };
  }

  // Pass 2: Resolve
  var resolveResult = resolve(parseResult.flow, parseResult.mapping);
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

  // Pass 3: Codegen
  var flowName = parseResult.flow.name;
  var script = generate(resolveResult.resolved, flowName);

  // Write output
  var outPath = path.join(outputDir, flowName + '.sh');
  fs.mkdirSync(outputDir, { recursive: true });
  fs.writeFileSync(outPath, script, 'utf8');
  fs.chmodSync(outPath, '755');

  // Print summary
  var s = resolveResult.stats;
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
