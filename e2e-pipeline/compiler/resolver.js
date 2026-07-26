'use strict';

const { isValidSiteName, validateSiteNames } = require('./site-name');

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
    pattern: /^Fill\s+(\w+)(?:\s+with\s+'([^']*)')?(?:\s+on\s+([\w-]+))?$/i,
    extract: function(m) {
      return { element: m[1], value: m[2] || null, page: m[3] || null };
    },
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
  // SC-1032: capture-url-query — extracts a named query param from the current URL
  'capture-url-query': {
    pattern: /Capture\s+(\w+)\s+from\s+url\s+query/i,
    extract: function(m) { return { param: m[1] }; },
  },
};

function buildSymbolTable(mapping) {
  var table = new Map();
  var collisions = new Map();
  var byPage = new Map();
  var sharedPages = [];

  var pages = mapping.pages || {};
  for (var pageName in pages) {
    var pageData = pages[pageName];
    var pageTable = new Map();
    byPage.set(pageName, pageTable);
    if (isSharedPage(pageName, pageData)) {
      sharedPages.push(pageName);
    }
    var elements = pageData.elements || {};
    for (var elemName in elements) {
      var elemData = elements[elemName];
      var entry = { selector: elemData.selector, page: pageName };
      if (elemData.css_selector) entry.cssSelector = elemData.css_selector;
      pageTable.set(elemName, entry);
      if (table.has(elemName)) {
        // Track collision but do NOT fail here — only fail if this element is referenced
        if (!collisions.has(elemName)) {
          collisions.set(elemName, [table.get(elemName).page]);
        }
        collisions.get(elemName).push(pageName);
      } else {
        table.set(elemName, entry);
      }
    }
  }

  // Return collisions map so resolve() can check only referenced elements
  return { table: table, collisions: collisions, byPage: byPage, sharedPages: sharedPages };
}

function isSharedPage(pageName, pageData) {
  if (!pageData) return false;
  if (pageData.shared === true) return true;
  return pageName === '_global' && pageData.shared !== false;
}

// ---------------------------------------------------------------------------
// errorDetails — additive structured channel alongside the plain-string `errors`
// array. Every `errors.push(string)` call site gains a parallel `errorDetails.push(...)`
// with the SAME message, so the two arrays stay the same length and order. Tier-1
// (a named symbol with a real "did you mean" answer already sitting in the symbol
// table) carries the full shape; Tier-2 (structural/type errors) carries `{message}`
// only. See docs/dev/.spacedock-state/e2e-json-diagnostics.md "Design" for the split.
// ---------------------------------------------------------------------------

function tier1Detail(stepId, field, got, candidates, message) {
  return { step_id: stepId, field: field, got: got, candidates: candidates, message: message };
}

function tier2Detail(message) {
  return { message: message };
}

function parseActionString(type, action, stepId) {
  var parser = ACTION_PARSERS[type];
  if (!parser) {
    var unknownTypeMsg = "Step '" + stepId + "': unknown type '" + type + "'";
    return { error: unknownTypeMsg, detail: tier2Detail(unknownTypeMsg) };
  }
  var match = parser.pattern.exec(action);
  if (!match) {
    var formatMsg = "Step '" + stepId + "': action string does not match expected format for type '" + type + "'. Got: " + action;
    return { error: formatMsg, detail: tier2Detail(formatMsg) };
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
    var notFoundMsg = "Step '" + stepId + "': page '" + target + "' not found in mapping";
    return { error: notFoundMsg, detail: tier1Detail(stepId, 'page', target, [], notFoundMsg) };
  }
  if (!page.url_pattern) {
    var noUrlPatternMsg = "Step '" + stepId + "': cannot navigate to '" + target + "' (no url_pattern)";
    return { error: noUrlPatternMsg, detail: tier2Detail(noUrlPatternMsg) };
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

  // Phase 2 — element visibility with "is" and page qualifier
  { re: /^(\w+) is visible on ([\w-]+)$/, type: 'element-visible' },

  // Phase 2 — element visibility with page qualifier (more specific, before plain visible)
  { re: /^(\w+) visible on ([\w-]+)$/, type: 'element-visible' },

  // Phase 2 — element visibility without page qualifier
  { re: /^(\w+) visible$/, type: 'element-visible' },

  // Phase 2 — element not visible WITH page qualifier (more specific, before bare form)
  { re: /^(\w+) is not visible on ([\w-]+)$/, type: 'element-not-visible' },
  { re: /^(\w+) not visible on ([\w-]+)$/, type: 'element-not-visible' },

  // Phase 2 — element not visible (bare form)
  { re: /^(\w+) is not visible$/, type: 'element-not-visible' },
  { re: /^(\w+) not visible$/, type: 'element-not-visible' },

  // Phase 2 — URL checks (url-does-not-contain must come before url-contains)
  { re: /^url does not contain (.+)$/, type: 'url-not-contains' },
  { re: /^url contains (.+)$/, type: 'url-contains' },

  // Phase 2 — text NOT visible (negated; must come before positive text-visible)
  { re: /^text '(.+)' not on page$/, type: 'text-not-visible' },
  { re: /^text "(.+)" not visible$/, type: 'text-not-visible' },
  { re: /^text '(.+)' is not visible$/, type: 'text-not-visible' },

  // Phase 2 — text visibility (single-quote and double-quote variants)
  { re: /^text '(.+)' on page$/, type: 'text-visible' },
  { re: /^text '(.+)' is visible$/, type: 'text-visible' },
  { re: /^text "(.+)" visible$/, type: 'text-visible' },

  // Phase 2 — or-syntax (two elements, any-true logic)
  { re: /^(\w+) visible or (\w+) visible$/, type: 'or-visible' },
];

/**
 * Resolve a single element name using the symbol table, with built-in keyword fallback.
 * Returns { selector } on success, or pushes an error and returns null.
 */
function resolveElement(elemName, symbolTable, collisionsTable, stepId, errors, errorDetails) {
  if (collisionsTable.has(elemName)) {
    var colPages = collisionsTable.get(elemName);
    var ambigMsg = "Step '" + stepId + "': expect element '" + elemName + "' is ambiguous -- found on: " + colPages.join(', ');
    errors.push(ambigMsg);
    errorDetails.push(tier1Detail(stepId, 'element', elemName, colPages.slice(), ambigMsg));
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
  var notFoundMsg = "Step '" + stepId + "': expect element '" + elemName + "' not found in mapping";
  errors.push(notFoundMsg);
  errorDetails.push(tier1Detail(stepId, 'element', elemName, [], notFoundMsg));
  return null;
}

function elementResultFromEntry(entry) {
  var merged = { selector: entry.selector };
  if (entry.cssSelector) merged.cssSelector = entry.cssSelector;
  return merged;
}

function pageNames(mapping) {
  return Object.keys(mapping.pages || {});
}

function allElementPages(elemName, symbolResult) {
  var pages = [];
  if (symbolResult.collisions.has(elemName)) {
    pages = symbolResult.collisions.get(elemName).slice();
  } else {
    var entry = symbolResult.table.get(elemName);
    if (entry) pages = [entry.page];
  }
  return pages;
}

function resolveElementOnPage(elemName, pageName, symbolResult, stepId, mapping, errors, errorDetails, label) {
  if (!pageName) {
    return resolveElement(elemName, symbolResult.table, symbolResult.collisions, stepId, errors, errorDetails);
  }

  var pages = mapping.pages || {};
  if (!pages[pageName]) {
    var pageMsg = "Step '" + stepId + "': page '" + pageName + "' not found in mapping";
    errors.push(pageMsg);
    errorDetails.push(tier1Detail(stepId, 'page', pageName, pageNames(mapping), pageMsg));
    return null;
  }

  var ownPage = symbolResult.byPage.get(pageName);
  var ownEntry = ownPage && ownPage.get(elemName);
  if (ownEntry) return elementResultFromEntry(ownEntry);

  for (var i = 0; i < symbolResult.sharedPages.length; i++) {
    var sharedPageName = symbolResult.sharedPages[i];
    var sharedPage = symbolResult.byPage.get(sharedPageName);
    var sharedEntry = sharedPage && sharedPage.get(elemName);
    if (sharedEntry) return elementResultFromEntry(sharedEntry);
  }

  if (BUILT_IN_KEYWORDS[elemName]) {
    return { selector: BUILT_IN_KEYWORDS[elemName] };
  }

  var foundPages = allElementPages(elemName, symbolResult);
  if (foundPages.length > 0) {
    var foundOn = foundPages.join(', ');
    var wrongPageMsg = "Step '" + stepId + "': " + label + " '" + elemName + "' not found on page '" + pageName + "' (found on: " + foundOn + ") -- if it should be visible from any page, mark page '" + foundPages[0] + "' with shared: true in the mapping";
    errors.push(wrongPageMsg);
    errorDetails.push(tier1Detail(stepId, 'element', elemName, foundPages, wrongPageMsg));
    return null;
  }

  var notFoundMsg = "Step '" + stepId + "': " + label + " '" + elemName + "' not found in mapping";
  errors.push(notFoundMsg);
  errorDetails.push(tier1Detail(stepId, 'element', elemName, [], notFoundMsg));
  return null;
}

function resolveExpects(expects, symbolResult, stepId, mapping) {
  var resolvedExpects = [];
  var activeCount = 0;
  var deferredCount = 0;
  var errors = [];
  var errorDetails = [];

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
        var resolved = resolveElement(elemName, symbolResult.table, symbolResult.collisions, stepId, errors, errorDetails);
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
        var pageName = match[2] || null;
        var resolved = resolveElementOnPage(elemName, pageName, symbolResult, stepId, mapping, errors, errorDetails, 'element');
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
        var pageName = match[2] || null;
        var resolved = resolveElementOnPage(elemName, pageName, symbolResult, stepId, mapping, errors, errorDetails, 'element');
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
        var resolvedA = resolveElement(elemA, symbolResult.table, symbolResult.collisions, stepId, errors, errorDetails);
        var resolvedB = resolveElement(elemB, symbolResult.table, symbolResult.collisions, stepId, errors, errorDetails);
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

  return { resolvedExpects: resolvedExpects, activeCount: activeCount, deferredCount: deferredCount, errors: errors, errorDetails: errorDetails };
}

function resolve(flow, mapping, options) {
  var errors = [];
  var errorDetails = [];
  var runtimeValues = (options && options.runtimeValues) || null;

  var symbolResult = buildSymbolTable(mapping);

  var resolvedSteps = [];
  var activeExpects = 0;
  var deferredExpects = 0;
  var skipped = 0;

  var steps = flow.steps || [];
  for (var si = 0; si < steps.length; si++) {
    var step = steps[si];
    var stepId = step.id || '(unnamed)';

    if (!step.type) {
      var noTypeMsg = "Step '" + stepId + "' has no type field — run migration tool first";
      errors.push(noTypeMsg);
      errorDetails.push(tier2Detail(noTypeMsg));
      continue;
    }

    // SC-1032: capture-url-query — pass capture block through operands directly
    if (step.type === 'capture-url-query') {
      var capOp = {
        param: step.query,
        as: step.save_as.toUpperCase(),
        state_key: step.save_as,
        validate: step.validate || null,
      };
      var capStep = {
        id: stepId,
        action: step.action,
        type: 'capture-url-query',
        operands: capOp,
      };
      if (step.wait != null) capStep.timeout = Number(step.wait);
      resolvedSteps.push(capStep);
      continue;
    }

    var parseResult = parseActionString(step.type, step.action || '', stepId);
    if (parseResult.error) {
      errors.push(parseResult.error);
      errorDetails.push(parseResult.detail);
      continue;
    }

    var rawOperands = parseResult.operands;
    var resolvedOperands = Object.assign({}, rawOperands);
    var skipStep = false;

    if (step.type === 'navigate') {
      var navResult = resolveNavigate(rawOperands, stepId, mapping);
      if (navResult.error) {
        errors.push(navResult.error);
        errorDetails.push(navResult.detail);
        skipStep = true;
      } else {
        resolvedOperands = navResult.operands;
      }

    } else if (step.type === 'click' || step.type === 'fill') {
      var elemName = rawOperands.element;
      if (elemName) {
        var resolvedElement = resolveElementOnPage(elemName, rawOperands.page, symbolResult, stepId, mapping, errors, errorDetails, 'element');
        if (!resolvedElement) {
          skipStep = true;
        } else {
          resolvedOperands = Object.assign({}, rawOperands, resolvedElement);
        }
      }
      // SC-1032: thread runtime_ref from step YAML into operands for sensitive fill
      if (step.type === 'fill' && step.value && step.value.runtime_ref) {
        var runtimeKey = step.value.runtime_ref;
        var runtimeDecl = runtimeValues && runtimeValues[runtimeKey];
        if (!runtimeDecl) {
          var runtimeRefMsg = "Step '" + stepId + "': unknown runtime_ref '" + runtimeKey + "'";
          errors.push(runtimeRefMsg);
          errorDetails.push(tier2Detail(runtimeRefMsg));
          skipStep = true;
        } else {
          resolvedOperands.runtime_ref = runtimeKey;
          resolvedOperands.runtime_env = runtimeDecl.from_env;
        }
        // Clear plain value when using runtime_ref to avoid literal embedding
        resolvedOperands.value = null;
        resolvedOperands.sensitive = runtimeDecl && runtimeDecl.sensitive;
      }

    } else if (step.type === 'verify-external' || step.type === 'execute-external') {
      skipped++;
    }

    if (skipStep) continue;

    var stepExpects = [];
    if (Array.isArray(step.expect) && step.expect.length > 0) {
      var expectResult = resolveExpects(step.expect, symbolResult, stepId, mapping);
      stepExpects = expectResult.resolvedExpects;
      activeExpects += expectResult.activeCount;
      deferredExpects += expectResult.deferredCount;
      for (var ei = 0; ei < expectResult.errors.length; ei++) {
        errors.push(expectResult.errors[ei]);
        errorDetails.push(expectResult.errorDetails[ei]);
      }
    }

    var resolvedStep = {
      id: stepId,
      action: resolvedOperands.runtime_ref
        ? 'Fill ' + resolvedOperands.element + ' with sensitive runtime value'
        : step.action,
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

  // SC-1032: resolve finally steps
  var resolvedFinally = null;
  if (Array.isArray(flow.finally) && flow.finally.length > 0) {
    resolvedFinally = [];
    for (var fi = 0; fi < flow.finally.length; fi++) {
      var fStep = flow.finally[fi];
      var fStepId = fStep.id || '(unnamed-finally-' + fi + ')';
      if (fStep.type === 'http') {
        var request = fStep.request;
        function resolveRuntimeRef(ref) {
          if (runtimeValues && runtimeValues[ref]) {
            return { state_key: ref, env: runtimeValues[ref].from_env, sensitive: runtimeValues[ref].sensitive };
          }
          return { state_key: ref, env: ref.toUpperCase(), sensitive: false };
        }
        var pathSegments = request.url.path_segments.map(function(segment) {
          return typeof segment === 'object'
            ? { runtime_ref: resolveRuntimeRef(segment.runtime_ref) }
            : { literal: String(segment) };
        });
        var headers = {};
        Object.keys(request.headers || {}).forEach(function(headerName) {
          var header = request.headers[headerName];
          headers[headerName] = {
            scheme: header.scheme,
            runtime_ref: resolveRuntimeRef(header.runtime_ref),
          };
        });
        var httpOp = {
          method: request.method,
          baseEnv: request.url.base_from_env,
          pathSegments: pathSegments,
          headers: headers,
          body: request.json || null,
          expectedStatus: fStep.expect && fStep.expect.status,
          expectedBody: fStep.expect && fStep.expect.body,
          expectedBodyField: fStep.expect && fStep.expect.body_field,
        };
        resolvedFinally.push({
          id: fStepId,
          action: fStep.action,
          type: 'http',
          on_fail: 'fail',
          operands: httpOp,
        });
      }
    }
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
    runtimeValues: runtimeValues,
    steps: resolvedSteps,
    finally: resolvedFinally,
  };

  return { resolved: resolved, stats: stats, errors: errors, errorDetails: errorDetails };
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
  var errorDetails = [];

  // Build per-site symbol tables
  var siteTables = new Map();
  var siteNames = Object.keys(siteMappings);
  var siteNameErrors = validateSiteNames(siteNames);
  errors.push.apply(errors, siteNameErrors);
  siteNameErrors.forEach(function(m) { errorDetails.push(tier2Detail(m)); });
  for (var siteIndex = 0; siteIndex < siteNames.length; siteIndex++) {
    var siteName = siteNames[siteIndex];
    if (!isValidSiteName(siteName)) {
      continue;
    }
    var siteData = siteMappings[siteName];
    if (siteData && siteData.mapping) {
      siteTables.set(siteName, buildSymbolTable(siteData.mapping));
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
      var noSiteMsg = "Step '" + stepId + "': cross-site flow step must have a 'site:' qualifier";
      errors.push(noSiteMsg);
      errorDetails.push(tier2Detail(noSiteMsg));
      continue;
    }

    var siteName = step.site;
    var siteTableResult = siteTables.get(siteName);
    if (!siteTableResult) {
      var unknownSiteMsg = "Step '" + stepId + "': unknown site '" + siteName + "' (not in sites: block)";
      errors.push(unknownSiteMsg);
      errorDetails.push(tier2Detail(unknownSiteMsg));
      continue;
    }

    // Get site mapping for navigate resolution
    var siteMapping = siteMappings[siteName] && siteMappings[siteName].mapping;

    if (!step.type) {
      var noTypeMsg = "Step '" + stepId + "' has no type field — run migration tool first";
      errors.push(noTypeMsg);
      errorDetails.push(tier2Detail(noTypeMsg));
      continue;
    }

    var parseResult = parseActionString(step.type, step.action || '', stepId);
    if (parseResult.error) {
      errors.push(parseResult.error);
      errorDetails.push(parseResult.detail);
      continue;
    }

    var rawOperands = parseResult.operands;
    var resolvedOperands = Object.assign({}, rawOperands);
    var skipStep = false;

    if (step.type === 'navigate') {
      var navResult = resolveNavigate(rawOperands, stepId, siteMapping);
      if (navResult.error) {
        errors.push(navResult.error);
        errorDetails.push(navResult.detail);
        skipStep = true;
      } else {
        resolvedOperands = navResult.operands;
      }

    } else if (step.type === 'click' || step.type === 'fill') {
      var elemName = rawOperands.element;
      if (elemName) {
        var resolvedElement = resolveElementOnPage(elemName, rawOperands.page, siteTableResult, stepId, siteMapping, errors, errorDetails, 'element');
        if (!resolvedElement) {
          skipStep = true;
        } else {
          resolvedOperands = Object.assign({}, rawOperands, resolvedElement);
        }
      }

    } else if (step.type === 'verify-external' || step.type === 'execute-external') {
      skipped++;
    }

    if (skipStep) continue;

    var stepExpects = [];
    if (Array.isArray(step.expect) && step.expect.length > 0) {
      var expectResult = resolveExpects(step.expect, siteTableResult, stepId, siteMapping);
      stepExpects = expectResult.resolvedExpects;
      activeExpects += expectResult.activeCount;
      deferredExpects += expectResult.deferredCount;
      for (var ei = 0; ei < expectResult.errors.length; ei++) {
        errors.push(expectResult.errors[ei]);
        errorDetails.push(expectResult.errorDetails[ei]);
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

  return { resolved: resolved, stats: stats, errors: errors, errorDetails: errorDetails };
}

module.exports = { resolve: resolve, resolveMultiSite: resolveMultiSite, buildSymbolTable: buildSymbolTable };
