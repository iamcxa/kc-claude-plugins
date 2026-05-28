'use strict';

const ACTION_PARSERS = {
  navigate: {
    pattern: /Navigate to\s+(.+)/i,
    extract: function(m) { return { target: m[1].trim() }; },
  },
  click: {
    pattern: /Click\s+(\w+)(?:\s+on\s+([\w-]+))?/i,
    extract: function(m) { return { element: m[1], page: m[2] || null }; },
  },
  fill: {
    pattern: /Fill\s+(\w+)\s+with\s+'([^']+)'(?:\s+on\s+([\w-]+))?/i,
    extract: function(m) { return { element: m[1], value: m[2], page: m[3] || null }; },
  },
  snapshot: {
    // Matches "Take snapshot", "snapshot", and "Verify <element>" (element verification is observe-then-assert)
    pattern: /snapshot|^Verify\s+(?!external)\w+/i,
    extract: function() { return {}; },
  },
  wait: {
    pattern: /Wait\s+(\d+)/i,
    extract: function(m) { return { seconds: parseInt(m[1], 10) }; },
  },
  'verify-external': {
    pattern: /Verify external/i,
    extract: function() { return {}; },
  },
  'execute-external': {
    pattern: /Execute external/i,
    extract: function() { return {}; },
  },
};

function buildSymbolTable(mapping) {
  var table = new Map();
  var collisions = new Map();

  var pages = mapping.pages || {};
  for (var pageName in pages) {
    var pageData = pages[pageName];
    var elements = pageData.elements || {};
    for (var elemName in elements) {
      var elemData = elements[elemName];
      if (table.has(elemName)) {
        // Track collision but do NOT fail here — only fail if this element is referenced
        if (!collisions.has(elemName)) {
          collisions.set(elemName, [table.get(elemName).page]);
        }
        collisions.get(elemName).push(pageName);
      } else {
        var entry = { selector: elemData.selector, page: pageName };
        if (elemData.css_selector) entry.cssSelector = elemData.css_selector;
        table.set(elemName, entry);
      }
    }
  }

  // Return collisions map so resolve() can check only referenced elements
  return { table: table, collisions: collisions };
}

function parseActionString(type, action, stepId) {
  var parser = ACTION_PARSERS[type];
  if (!parser) {
    return { error: "Step '" + stepId + "': unknown type '" + type + "'" };
  }
  var match = parser.pattern.exec(action);
  if (!match) {
    return {
      error: "Step '" + stepId + "': action string does not match expected format for type '" + type + "'. Got: " + action,
    };
  }
  return { operands: parser.extract(match) };
}

function resolveNavigate(operands, stepId, mapping) {
  var target = operands.target;

  if (target.startsWith('/')) {
    return { operands: { target: target } };
  }

  var pages = mapping.pages || {};
  var page = pages[target];
  if (!page) {
    return {
      error: "Step '" + stepId + "': page '" + target + "' not found in mapping",
    };
  }
  if (!page.url_pattern) {
    return {
      error: "Step '" + stepId + "': cannot navigate to '" + target + "' (no url_pattern)",
    };
  }
  return { operands: { target: target, urlPath: page.url_pattern } };
}

// ---------------------------------------------------------------------------
// Phase 2: Expect pattern dispatch table
// ---------------------------------------------------------------------------

// Built-in keywords that resolve to ARIA selectors without requiring a mapping entry
var BUILT_IN_KEYWORDS = {
  dialog: 'role=dialog',
};

// Ordered dispatch table for expect pattern matching.
// Priority matters: more specific patterns must come before general ones.
var EXPECT_PATTERNS = [
  // Phase 1 — kept as 'active' type for full backwards compatibility
  { re: /^(\w+) is visible$/, type: 'active' },

  // Phase 2 — element visibility with page qualifier (more specific, before plain visible)
  { re: /^(\w+) visible on [\w-]+$/, type: 'element-visible' },

  // Phase 2 — element visibility without page qualifier
  { re: /^(\w+) visible$/, type: 'element-visible' },

  // Phase 2 — element not visible WITH page qualifier (more specific, before bare form)
  { re: /^(\w+) is not visible on [\w-]+$/, type: 'element-not-visible' },
  { re: /^(\w+) not visible on [\w-]+$/, type: 'element-not-visible' },

  // Phase 2 — element not visible (bare form)
  { re: /^(\w+) is not visible$/, type: 'element-not-visible' },
  { re: /^(\w+) not visible$/, type: 'element-not-visible' },

  // Phase 2 — URL checks (url-does-not-contain must come before url-contains)
  { re: /^url does not contain (.+)$/, type: 'url-not-contains' },
  { re: /^url contains (.+)$/, type: 'url-contains' },

  // Phase 2 — text NOT visible (negated; must come before positive text-visible)
  { re: /^text '(.+)' not on page$/, type: 'text-not-visible' },
  { re: /^text "(.+)" not visible$/, type: 'text-not-visible' },

  // Phase 2 — text visibility (single-quote and double-quote variants)
  { re: /^text '(.+)' on page$/, type: 'text-visible' },
  { re: /^text "(.+)" visible$/, type: 'text-visible' },

  // Phase 2 — or-syntax (two elements, any-true logic)
  { re: /^(\w+) visible or (\w+) visible$/, type: 'or-visible' },
];

/**
 * Resolve a single element name using the symbol table, with built-in keyword fallback.
 * Returns { selector } on success, or pushes an error and returns null.
 */
function resolveElement(elemName, symbolTable, collisionsTable, stepId, errors) {
  if (collisionsTable.has(elemName)) {
    var colPages = collisionsTable.get(elemName);
    errors.push("Step '" + stepId + "': expect element '" + elemName + "' is ambiguous -- found on: " + colPages.join(', '));
    return null;
  }
  var entry = symbolTable.get(elemName);
  if (entry) {
    return { selector: entry.selector };
  }
  // Check built-in keywords (e.g., dialog -> role=dialog)
  if (BUILT_IN_KEYWORDS[elemName]) {
    return { selector: BUILT_IN_KEYWORDS[elemName] };
  }
  errors.push("Step '" + stepId + "': expect element '" + elemName + "' not found in mapping");
  return null;
}

function resolveExpects(expects, symbolTable, collisionsTable, stepId) {
  var resolvedExpects = [];
  var activeCount = 0;
  var deferredCount = 0;
  var errors = [];

  for (var i = 0; i < expects.length; i++) {
    var expectStr = expects[i];
    var matched = false;

    for (var p = 0; p < EXPECT_PATTERNS.length; p++) {
      var pattern = EXPECT_PATTERNS[p];
      var match = pattern.re.exec(expectStr);
      if (!match) continue;

      matched = true;
      var type = pattern.type;

      if (type === 'active') {
        // Phase 1 pattern: "element is visible"
        var elemName = match[1];
        var resolved = resolveElement(elemName, symbolTable, collisionsTable, stepId, errors);
        if (resolved) {
          resolvedExpects.push({
            type: 'active',
            raw: expectStr,
            elementName: elemName,
            selector: resolved.selector,
          });
          activeCount++;
        }
      } else if (type === 'element-visible') {
        // "element visible" or "element visible on page"
        var elemName = match[1];
        var resolved = resolveElement(elemName, symbolTable, collisionsTable, stepId, errors);
        if (resolved) {
          resolvedExpects.push({
            type: 'element-visible',
            raw: expectStr,
            elementName: elemName,
            selector: resolved.selector,
          });
          activeCount++;
        }
      } else if (type === 'element-not-visible') {
        // "element not visible" or "element is not visible"
        var elemName = match[1];
        var resolved = resolveElement(elemName, symbolTable, collisionsTable, stepId, errors);
        if (resolved) {
          resolvedExpects.push({
            type: 'element-not-visible',
            raw: expectStr,
            elementName: elemName,
            selector: resolved.selector,
          });
          activeCount++;
        }
      } else if (type === 'url-contains') {
        resolvedExpects.push({ type: 'url-contains', raw: expectStr, value: match[1] });
        activeCount++;
      } else if (type === 'url-not-contains') {
        resolvedExpects.push({ type: 'url-not-contains', raw: expectStr, value: match[1] });
        activeCount++;
      } else if (type === 'text-visible') {
        resolvedExpects.push({ type: 'text-visible', raw: expectStr, text: match[1] });
        activeCount++;
      } else if (type === 'text-not-visible') {
        resolvedExpects.push({ type: 'text-not-visible', raw: expectStr, text: match[1] });
        activeCount++;
      } else if (type === 'or-visible') {
        var elemA = match[1];
        var elemB = match[2];
        var resolvedA = resolveElement(elemA, symbolTable, collisionsTable, stepId, errors);
        var resolvedB = resolveElement(elemB, symbolTable, collisionsTable, stepId, errors);
        if (resolvedA && resolvedB) {
          resolvedExpects.push({
            type: 'or-visible',
            raw: expectStr,
            elements: [
              { elementName: elemA, selector: resolvedA.selector },
              { elementName: elemB, selector: resolvedB.selector },
            ],
          });
          activeCount++;
        }
      }

      break; // First matching pattern wins
    }

    if (!matched) {
      resolvedExpects.push({ type: 'deferred', raw: expectStr });
      deferredCount++;
    }
  }

  return { resolvedExpects: resolvedExpects, activeCount: activeCount, deferredCount: deferredCount, errors: errors };
}

function resolve(flow, mapping) {
  var errors = [];

  var symbolResult = buildSymbolTable(mapping);
  var table = symbolResult.table;
  var collisions = symbolResult.collisions;

  var resolvedSteps = [];
  var activeExpects = 0;
  var deferredExpects = 0;
  var skipped = 0;

  var steps = flow.steps || [];
  for (var si = 0; si < steps.length; si++) {
    var step = steps[si];
    var stepId = step.id || '(unnamed)';

    if (!step.type) {
      errors.push("Step '" + stepId + "' has no type field — run migration tool first");
      continue;
    }

    var parseResult = parseActionString(step.type, step.action || '', stepId);
    if (parseResult.error) {
      errors.push(parseResult.error);
      continue;
    }

    var rawOperands = parseResult.operands;
    var resolvedOperands = Object.assign({}, rawOperands);
    var skipStep = false;

    if (step.type === 'navigate') {
      var navResult = resolveNavigate(rawOperands, stepId, mapping);
      if (navResult.error) {
        errors.push(navResult.error);
        skipStep = true;
      } else {
        resolvedOperands = navResult.operands;
      }

    } else if (step.type === 'click' || step.type === 'fill') {
      var elemName = rawOperands.element;
      if (elemName) {
        if (collisions.has(elemName)) {
          // Element exists but is ambiguous — fail only when referenced
          var colPages = collisions.get(elemName);
          errors.push("Step '" + stepId + "': element '" + elemName + "' is ambiguous -- found on: " + colPages.join(', '));
          skipStep = true;
        } else {
          var entry = table.get(elemName);
          if (!entry) {
            errors.push("Step '" + stepId + "': element '" + elemName + "' not found in mapping");
            skipStep = true;
          } else {
            var merged = { selector: entry.selector };
            if (entry.cssSelector) merged.cssSelector = entry.cssSelector;
            resolvedOperands = Object.assign({}, rawOperands, merged);
          }
        }
      }

    } else if (step.type === 'verify-external' || step.type === 'execute-external') {
      skipped++;
    }

    if (skipStep) continue;

    var stepExpects = [];
    if (Array.isArray(step.expect) && step.expect.length > 0) {
      var expectResult = resolveExpects(step.expect, table, collisions, stepId);
      stepExpects = expectResult.resolvedExpects;
      activeExpects += expectResult.activeCount;
      deferredExpects += expectResult.deferredCount;
      for (var ei = 0; ei < expectResult.errors.length; ei++) {
        errors.push(expectResult.errors[ei]);
      }
    }

    var resolvedStep = {
      id: stepId,
      action: step.action,
      type: step.type,
      operands: resolvedOperands,
    };
    if (stepExpects.length > 0) {
      resolvedStep.expects = stepExpects;
    }
    // Thread wait: field as per-step timeout for poll-until (CODEGEN-02)
    if (step.wait != null) {
      resolvedStep.timeout = Number(step.wait);
    }
    // Thread screenshot: field for post-step capture
    if (step.screenshot) {
      resolvedStep.screenshot = true;
    }
    resolvedSteps.push(resolvedStep);
  }

  var stats = {
    total: (flow.steps || []).length,
    activeExpects: activeExpects,
    deferredExpects: deferredExpects,
    skipped: skipped,
  };

  var resolved = {
    name: flow.name,
    description: flow.description,
    variables: flow.variables,
    steps: resolvedSteps,
  };

  return { resolved: resolved, stats: stats, errors: errors };
}

/**
 * resolveMultiSite(flow, siteMappings) — resolve a cross-site flow.
 *
 * siteMappings: { [siteName]: { mappingName, mapping } }
 *   - Each entry holds a loaded mapping object with its name
 *
 * Returns: { resolved, stats, errors }
 *   - resolved.steps each have a session field from step.site qualifier
 *   - Element lookups use the per-site symbol table
 */
function resolveMultiSite(flow, siteMappings) {
  var errors = [];

  // Build per-site symbol tables
  var siteTables = {};
  for (var siteName in siteMappings) {
    var siteData = siteMappings[siteName];
    if (siteData && siteData.mapping) {
      siteTables[siteName] = buildSymbolTable(siteData.mapping);
    }
  }

  var resolvedSteps = [];
  var activeExpects = 0;
  var deferredExpects = 0;
  var skipped = 0;

  var steps = flow.steps || [];
  for (var si = 0; si < steps.length; si++) {
    var step = steps[si];
    var stepId = step.id || '(unnamed)';

    // Require site: qualifier on every step in a cross-site flow
    if (!step.site) {
      errors.push("Step '" + stepId + "': cross-site flow step must have a 'site:' qualifier");
      continue;
    }

    var siteName = step.site;
    var siteTableResult = siteTables[siteName];
    if (!siteTableResult) {
      errors.push("Step '" + stepId + "': unknown site '" + siteName + "' (not in sites: block)");
      continue;
    }

    var table = siteTableResult.table;
    var collisions = siteTableResult.collisions;
    // Get site mapping for navigate resolution
    var siteMapping = siteMappings[siteName] && siteMappings[siteName].mapping;

    if (!step.type) {
      errors.push("Step '" + stepId + "' has no type field — run migration tool first");
      continue;
    }

    var parseResult = parseActionString(step.type, step.action || '', stepId);
    if (parseResult.error) {
      errors.push(parseResult.error);
      continue;
    }

    var rawOperands = parseResult.operands;
    var resolvedOperands = Object.assign({}, rawOperands);
    var skipStep = false;

    if (step.type === 'navigate') {
      var navResult = resolveNavigate(rawOperands, stepId, siteMapping);
      if (navResult.error) {
        errors.push(navResult.error);
        skipStep = true;
      } else {
        resolvedOperands = navResult.operands;
      }

    } else if (step.type === 'click' || step.type === 'fill') {
      var elemName = rawOperands.element;
      if (elemName) {
        if (collisions.has(elemName)) {
          var colPages = collisions.get(elemName);
          errors.push("Step '" + stepId + "': element '" + elemName + "' is ambiguous -- found on: " + colPages.join(', '));
          skipStep = true;
        } else {
          var entry = table.get(elemName);
          if (!entry) {
            errors.push("Step '" + stepId + "': element '" + elemName + "' not found in mapping");
            skipStep = true;
          } else {
            var merged = { selector: entry.selector };
            if (entry.cssSelector) merged.cssSelector = entry.cssSelector;
            resolvedOperands = Object.assign({}, rawOperands, merged);
          }
        }
      }

    } else if (step.type === 'verify-external' || step.type === 'execute-external') {
      skipped++;
    }

    if (skipStep) continue;

    var stepExpects = [];
    if (Array.isArray(step.expect) && step.expect.length > 0) {
      var expectResult = resolveExpects(step.expect, table, collisions, stepId);
      stepExpects = expectResult.resolvedExpects;
      activeExpects += expectResult.activeCount;
      deferredExpects += expectResult.deferredCount;
      for (var ei = 0; ei < expectResult.errors.length; ei++) {
        errors.push(expectResult.errors[ei]);
      }
    }

    var resolvedStep = {
      id: stepId,
      action: step.action,
      type: step.type,
      session: siteName,
      operands: resolvedOperands,
    };
    if (stepExpects.length > 0) {
      resolvedStep.expects = stepExpects;
    }
    // Thread wait: field as per-step timeout for poll-until (CODEGEN-02)
    if (step.wait != null) {
      resolvedStep.timeout = Number(step.wait);
    }
    // Thread screenshot: field for post-step capture
    if (step.screenshot) {
      resolvedStep.screenshot = true;
    }
    resolvedSteps.push(resolvedStep);
  }

  var stats = {
    total: (flow.steps || []).length,
    activeExpects: activeExpects,
    deferredExpects: deferredExpects,
    skipped: skipped,
  };

  var resolved = {
    name: flow.name,
    description: flow.description,
    variables: flow.variables,
    steps: resolvedSteps,
  };

  return { resolved: resolved, stats: stats, errors: errors };
}

module.exports = { resolve: resolve, resolveMultiSite: resolveMultiSite, buildSymbolTable: buildSymbolTable };
