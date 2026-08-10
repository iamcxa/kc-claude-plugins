'use strict';

const path = require('node:path');

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

function buildSymbolTable(mapping, mappingPath) {
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
      var entry = {
        selector: elemData.selector,
        page: pageName,
        mappingPath: mappingPath || null,
        visibilityPolicy: elemData.visibility_policy || 'strict',
      };
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

  // Return collisions map so resolve() can check only referenced elements.
  // `referenced` accumulates every element a step actually resolves, with the page
  // and element name the symbol table knows. Without it the resolved output carries
  // only bare selectors, and the compile gate cannot say WHICH element is banned nor
  // key a baseline record by anything stable (#88).
  return { table: table, collisions: collisions, byPage: byPage, sharedPages: sharedPages, referenced: [] };
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

function unmatchedExpectDetail(stepId, raw, message) {
  return {
    step_id: stepId,
    stepId: stepId,
    field: 'expect',
    raw: raw,
    got: raw,
    candidates: [],
    message: message,
  };
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

/**
 * fillValueInterpolationError(value, stepId) — reject `${...}` in a fill value.
 *
 * The two executors disagree, and that is the whole defect. The `/e2e-test` agent
 * runner substitutes `${key}` from `variables:` (`agents/e2e-test-runner.md`), and
 * `docs/multi-site-testing.md` shows a flow that relies on it. Compilation never
 * substituted: `variables:` become the script's own parameters (`email:` becomes
 * `EMAIL="${2:-…}"`), a different name in a different scope, and the written token
 * reached the input field as eight literal characters with nothing reporting it.
 *
 * Refusing is what the compile path can honestly do today. Implementing the
 * substitution means emitting the value double-quoted — a `$(...)` execution
 * surface — and, on the `css_selector` path, crossing bash-then-JS escaping. Those
 * are exactly the two emission sites #180 records as invisible to the current gate,
 * so that work is sequenced after the instrument exists, not before.
 *
 * Returns a message, or null when the value is fine. A bare `$` is fine; only the
 * `${…}` form is refused, because that is the one that looks like it should work.
 */
function fillValueInterpolationError(value, stepId) {
  if (typeof value !== 'string') return null;
  var found = /\$\{[^}]*\}/.exec(value);
  if (!found) return null;
  return "Step '" + stepId + "': fill value contains " + found[0] +
    ', which compiled scripts never interpolate — the field would receive those' +
    ' characters literally. Flow `variables:` bind as script parameters, not into' +
    ' step values. (The /e2e-test agent runner does substitute them, so a flow that' +
    ' works there can still fail to compile.) Use a literal value, or' +
    ' `value: {runtime_ref: ...}` for one that must come from the environment.';
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
  dialog: { selector: 'role=dialog', cssSelector: 'dialog,[role="dialog"]' },
};

var ELEMENT_REFERENCE = '([A-Za-z_][A-Za-z0-9_]*(?:\\([^)]*\\))?)';

// Ordered dispatch table for expect pattern matching.
// Priority matters: more specific patterns must come before general ones.
var EXPECT_PATTERNS = [
  // Phase 1 — kept as 'active' type for full backwards compatibility
  { re: new RegExp('^' + ELEMENT_REFERENCE + ' is visible$'), type: 'active' },

  // Phase 2 — element visibility with "is" and page qualifier
  { re: new RegExp('^' + ELEMENT_REFERENCE + ' is visible on ([\\w-]+)$'), type: 'element-visible' },

  // Phase 2 — element visibility with page qualifier (more specific, before plain visible)
  { re: new RegExp('^' + ELEMENT_REFERENCE + ' visible on ([\\w-]+)$'), type: 'element-visible' },

  // Phase 2 — element visibility without page qualifier
  { re: new RegExp('^' + ELEMENT_REFERENCE + ' visible$'), type: 'element-visible' },

  // Phase 2 — element not visible WITH page qualifier (more specific, before bare form)
  { re: new RegExp('^' + ELEMENT_REFERENCE + ' is not visible on ([\\w-]+)$'), type: 'element-not-visible' },
  { re: new RegExp('^' + ELEMENT_REFERENCE + ' not visible on ([\\w-]+)$'), type: 'element-not-visible' },

  // Phase 2 — element not visible (bare form)
  { re: new RegExp('^' + ELEMENT_REFERENCE + ' is not visible$'), type: 'element-not-visible' },
  { re: new RegExp('^' + ELEMENT_REFERENCE + ' not visible$'), type: 'element-not-visible' },

  // Enabled/disabled assertions first establish visibility with the shared DOM probe.
  { re: new RegExp('^' + ELEMENT_REFERENCE + ' (?:is )?enabled(?: on ([\\w-]+))?$'), type: 'element-enabled' },
  { re: new RegExp('^' + ELEMENT_REFERENCE + ' (?:is )?disabled(?: on ([\\w-]+))?$'), type: 'element-disabled' },

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
  { re: new RegExp('^' + ELEMENT_REFERENCE + ' visible or ' + ELEMENT_REFERENCE + ' visible$'), type: 'or-visible' },
];

/**
 * Resolve a single element name using the symbol table, with built-in keyword fallback.
 * Returns { selector } on success, or pushes an error and returns null.
 */
function recordReference(symbolResult, elemName, page, selector) {
  // Throw rather than no-op. This is the ONLY channel by which a resolved element reaches
  // the compile-time selector gate, so a symbol-table-shaped object without `.referenced`
  // — plausible from a future refactor that hand-builds one — would silently make the gate
  // blind to that element: banned selector, clean compile, no signal anywhere. Every
  // current caller goes through buildSymbolTable(), which always sets it, so this is a
  // wiring assertion and not a runtime branch anyone should hit.
  if (!symbolResult || !symbolResult.referenced) {
    throw new Error(
      'recordReference: symbolResult has no `referenced` accumulator, so the selector ' +
      'gate cannot see element ' + elemName + ' — build symbol tables via buildSymbolTable()'
    );
  }
  symbolResult.referenced.push({ page: page, element: elemName, selector: selector });
}

function resolveElement(elemName, symbolResult, stepId, errors, errorDetails) {
  var symbolTable = symbolResult.table;
  var collisionsTable = symbolResult.collisions;
  if (collisionsTable.has(elemName)) {
    var colPages = collisionsTable.get(elemName);
    var ambigMsg = "Step '" + stepId + "': expect element '" + elemName + "' is ambiguous -- found on: " + colPages.join(', ');
    errors.push(ambigMsg);
    errorDetails.push(tier1Detail(stepId, 'element', elemName, colPages.slice(), ambigMsg));
    return null;
  }
  var entry = symbolTable.get(elemName);
  if (entry) {
    return elementResultFromEntry(entry, elemName, symbolResult);
  }
  // Check built-in keywords (e.g., dialog -> role=dialog). These are compiler-owned
  // constants, not mapping content, so they are deliberately NOT recorded as referenced
  // elements: no mapping author can introduce a banned form through them, and a baseline
  // record naming one would point at a file that does not contain it.
  if (BUILT_IN_KEYWORDS[elemName]) {
    return {
      selector: BUILT_IN_KEYWORDS[elemName].selector,
      cssSelector: BUILT_IN_KEYWORDS[elemName].cssSelector,
      visibilityPolicy: 'strict',
      mappingPage: null,
      mappingPath: '<compiler built-in>',
    };
  }
  var notFoundMsg = "Step '" + stepId + "': expect element '" + elemName + "' not found in mapping";
  errors.push(notFoundMsg);
  errorDetails.push(tier1Detail(stepId, 'element', elemName, [], notFoundMsg));
  return null;
}

function elementResultFromEntry(entry, elemName, symbolResult, page) {
  recordReference(symbolResult, elemName, page !== undefined ? page : entry.page, entry.selector);
  var merged = {
    selector: entry.selector,
    visibilityPolicy: entry.visibilityPolicy || 'strict',
    mappingPage: page !== undefined ? page : entry.page,
    mappingPath: entry.mappingPath,
  };
  if (entry.cssSelector) merged.cssSelector = entry.cssSelector;
  return merged;
}

function parseElementReference(reference, stepId, errors, errorDetails) {
  var match = /^([A-Za-z_][A-Za-z0-9_]*)(?:\((.*)\))?$/.exec(reference);
  if (!match) return null;
  var parameters = null;
  if (match[2] !== undefined) {
    parameters = Object.create(null);
    var assignments = match[2] === '' ? [] : match[2].split(',');
    for (var i = 0; i < assignments.length; i++) {
      var assignment = assignments[i];
      var equals = assignment.indexOf('=');
      var key = equals === -1 ? '' : assignment.slice(0, equals).trim();
      var value = equals === -1 ? '' : assignment.slice(equals + 1).trim();
      if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(key) || value === '') {
        var parameterMsg = "Step '" + stepId + "': invalid element parameter '" + assignment + "' in " + reference;
        errors.push(parameterMsg);
        errorDetails.push(tier2Detail(parameterMsg));
        return null;
      }
      if ((value[0] === '"' && value[value.length - 1] === '"') ||
          (value[0] === "'" && value[value.length - 1] === "'")) {
        value = value.slice(1, -1);
      }
      parameters[key] = value;
    }
  }
  return { elementName: match[1], parameters: parameters };
}

function substituteSelectorTemplate(template, parameters) {
  if (!parameters) return template;
  return template.replace(/\$\{([A-Za-z_][A-Za-z0-9_]*)\}/g, function(token, name) {
    return Object.hasOwn(parameters, name) ? parameters[name] : token;
  });
}

function isLiteralCssSelector(selector) {
  if (typeof selector !== 'string' || selector.trim() === '') return false;
  var trimmed = selector.trim();
  if (/^(?:role|text|xpath|css|id|testid|label)=/i.test(trimmed)) return false;
  if (/^find\s+(?:role|text|testid|label)\b/i.test(trimmed)) return false;
  if (/^(?:\/\/|\.\/\/)/.test(trimmed)) return false;
  return true;
}

function resolveVisibilityElement(reference, pageName, symbolResult, stepId, mapping, errors, errorDetails) {
  var parsed = parseElementReference(reference, stepId, errors, errorDetails);
  if (!parsed) return null;
  var resolved = resolveElementOnPage(
    parsed.elementName,
    pageName,
    symbolResult,
    stepId,
    mapping,
    errors,
    errorDetails,
    'element'
  );
  if (!resolved) return null;

  var effectiveSelector = substituteSelectorTemplate(resolved.selector, parsed.parameters);
  var cssSelectorTemplate = resolved.cssSelector || null;
  var cssSelector = cssSelectorTemplate
    ? substituteSelectorTemplate(cssSelectorTemplate, parsed.parameters)
    : isLiteralCssSelector(effectiveSelector) ? effectiveSelector : null;
  var unresolved = /\$\{[A-Za-z_][A-Za-z0-9_]*\}/.test(effectiveSelector) ||
    (cssSelector && /\$\{[A-Za-z_][A-Za-z0-9_]*\}/.test(cssSelector));
  if (unresolved) {
    var unresolvedMsg = "Step '" + stepId + "': unresolved selector parameter for " + reference;
    errors.push(unresolvedMsg);
    errorDetails.push(tier2Detail(unresolvedMsg));
    return null;
  }
  if (!cssSelector) {
    var mappingIdentity = resolved.mappingPath || '<mapping>';
    var pageIdentity = resolved.mappingPage || pageName || '<unknown-page>';
    var cssMsg =
      "Step '" + stepId + "': mapped visibility in " + mappingIdentity + ' at ' +
      pageIdentity + '.' + parsed.elementName + ' uses non-CSS selector ' +
      JSON.stringify(resolved.selector) +
      '; add css_selector with a literal CSS selector for deterministic DOM visibility';
    errors.push(cssMsg);
    errorDetails.push(tier2Detail(cssMsg));
    return null;
  }

  var result = {
    elementName: parsed.elementName,
    selector: resolved.selector,
    cssSelector: cssSelector,
    visibilityPolicy: resolved.visibilityPolicy || 'strict',
  };
  if (parsed.parameters) {
    result.selectorTemplate = resolved.selector;
    if (cssSelectorTemplate) result.cssSelectorTemplate = cssSelectorTemplate;
    result.effectiveSelector = effectiveSelector;
  }
  return result;
}

function resolvedVisibilityExpect(type, raw, resolved) {
  var result = {
    elementName: resolved.elementName,
    selector: resolved.selector,
    cssSelector: resolved.cssSelector,
    visibilityPolicy: resolved.visibilityPolicy,
  };
  if (type !== undefined) result.type = type;
  if (raw !== undefined) result.raw = raw;
  if (resolved.selectorTemplate) result.selectorTemplate = resolved.selectorTemplate;
  if (resolved.cssSelectorTemplate) result.cssSelectorTemplate = resolved.cssSelectorTemplate;
  if (resolved.effectiveSelector) result.effectiveSelector = resolved.effectiveSelector;
  return result;
}

function resolvedActionElement(resolved) {
  var result = { selector: resolved.selector };
  if (resolved.cssSelector) result.cssSelector = resolved.cssSelector;
  return result;
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
    return resolveElement(elemName, symbolResult, stepId, errors, errorDetails);
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
  if (ownEntry) return elementResultFromEntry(ownEntry, elemName, symbolResult, pageName);

  for (var i = 0; i < symbolResult.sharedPages.length; i++) {
    var sharedPageName = symbolResult.sharedPages[i];
    var sharedPage = symbolResult.byPage.get(sharedPageName);
    var sharedEntry = sharedPage && sharedPage.get(elemName);
    if (sharedEntry) return elementResultFromEntry(sharedEntry, elemName, symbolResult, sharedPageName);
  }

  if (BUILT_IN_KEYWORDS[elemName]) {
    return {
      selector: BUILT_IN_KEYWORDS[elemName].selector,
      cssSelector: BUILT_IN_KEYWORDS[elemName].cssSelector,
      visibilityPolicy: 'strict',
      mappingPage: null,
      mappingPath: '<compiler built-in>',
    };
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
  var notAutomatedCount = 0;
  var errors = [];
  var errorDetails = [];

  for (var i = 0; i < expects.length; i++) {
    var expectStr = expects[i];
    var matched = false;

    if (expectStr && typeof expectStr === 'object') {
      var keys = Object.keys(expectStr);
      var reason = expectStr.not_automated;
      if (keys.length === 1 &&
          keys[0] === 'not_automated' &&
          typeof reason === 'string' &&
          reason.trim().length > 0) {
        var trimmedReason = reason.trim();
        resolvedExpects.push({
          type: 'not-automated',
          raw: trimmedReason,
          reason: trimmedReason,
        });
        notAutomatedCount++;
      } else {
        var objectMsg = "Step '" + stepId + "': invalid expect object " + JSON.stringify(expectStr) + " -- only {not_automated: <non-empty string>} is allowed";
        errors.push(objectMsg);
        errorDetails.push(unmatchedExpectDetail(stepId, expectStr, objectMsg));
      }
      continue;
    }

    if (typeof expectStr !== 'string') {
      var typeMsg = "Step '" + stepId + "': unsupported expect value " + JSON.stringify(expectStr) + " -- expect entries must be strings or {not_automated: <non-empty string>}";
      errors.push(typeMsg);
      errorDetails.push(unmatchedExpectDetail(stepId, expectStr, typeMsg));
      continue;
    }

    for (var p = 0; p < EXPECT_PATTERNS.length; p++) {
      var pattern = EXPECT_PATTERNS[p];
      var match = pattern.re.exec(expectStr);
      if (!match) continue;

      matched = true;
      var type = pattern.type;

      if (type === 'active') {
        // Phase 1 pattern: "element is visible"
        var elemRef = match[1];
        var resolved = resolveVisibilityElement(elemRef, null, symbolResult, stepId, mapping, errors, errorDetails);
        if (resolved) {
          resolvedExpects.push(resolvedVisibilityExpect('active', expectStr, resolved));
          activeCount++;
        }
      } else if (type === 'element-visible') {
        // "element visible" or "element visible on page"
        var elemRef = match[1];
        var pageName = match[2] || null;
        var resolved = resolveVisibilityElement(elemRef, pageName, symbolResult, stepId, mapping, errors, errorDetails);
        if (resolved) {
          resolvedExpects.push(resolvedVisibilityExpect('element-visible', expectStr, resolved));
          activeCount++;
        }
      } else if (type === 'element-not-visible') {
        // "element not visible" or "element is not visible"
        var elemRef = match[1];
        var pageName = match[2] || null;
        var resolved = resolveVisibilityElement(elemRef, pageName, symbolResult, stepId, mapping, errors, errorDetails);
        if (resolved) {
          resolvedExpects.push(resolvedVisibilityExpect('element-not-visible', expectStr, resolved));
          activeCount++;
        }
      } else if (type === 'element-enabled' || type === 'element-disabled') {
        var elemRef = match[1];
        var pageName = match[2] || null;
        var resolved = resolveVisibilityElement(elemRef, pageName, symbolResult, stepId, mapping, errors, errorDetails);
        if (resolved) {
          resolvedExpects.push(resolvedVisibilityExpect(type, expectStr, resolved));
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
        var resolvedA = resolveVisibilityElement(elemA, null, symbolResult, stepId, mapping, errors, errorDetails);
        var resolvedB = resolveVisibilityElement(elemB, null, symbolResult, stepId, mapping, errors, errorDetails);
        if (resolvedA && resolvedB) {
          resolvedExpects.push({
            type: 'or-visible',
            raw: expectStr,
            elements: [
              resolvedVisibilityExpect(undefined, undefined, resolvedA),
              resolvedVisibilityExpect(undefined, undefined, resolvedB),
            ],
          });
          activeCount++;
        }
      }

      break; // First matching pattern wins
    }

    if (!matched) {
      var unmatchedMsg = "Step '" + stepId + "': unsupported expect string '" + expectStr + "' -- rewrite it using docs/writing-tests.md#expect-grammar-reference or declare {not_automated: <reason>} when genuinely human-only";
      errors.push(unmatchedMsg);
      errorDetails.push(unmatchedExpectDetail(stepId, expectStr, unmatchedMsg));
      deferredCount++;
    }
  }

  return { resolvedExpects: resolvedExpects, activeCount: activeCount, deferredCount: deferredCount, notAutomatedCount: notAutomatedCount, errors: errors, errorDetails: errorDetails };
}

function resolve(flow, mapping, options) {
  var errors = [];
  var errorDetails = [];
  var runtimeValues = (options && options.runtimeValues) || null;

  var symbolResult = buildSymbolTable(mapping, options && options.mappingPath);

  var resolvedSteps = [];
  var activeExpects = 0;
  var deferredExpects = 0;
  var notAutomatedExpects = 0;
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
          resolvedOperands = Object.assign({}, rawOperands, resolvedActionElement(resolvedElement));
        }
      }
      var interpMsg = fillValueInterpolationError(rawOperands.value, stepId);
      if (interpMsg) {
        errors.push(interpMsg);
        errorDetails.push(tier2Detail(interpMsg));
        skipStep = true;
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
      notAutomatedExpects += expectResult.notAutomatedCount;
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
    notAutomatedExpects: notAutomatedExpects,
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

  // `referencedElements` sits beside `resolved`, not inside it, so codegen's input shape
  // is untouched. The compile gate (#88) reads it; nothing else does.
  return {
    resolved: resolved,
    stats: stats,
    errors: errors,
    errorDetails: errorDetails,
    referencedElements: symbolResult.referenced,
  };
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
function resolveMultiSite(flow, siteMappings, options) {
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
      var mappingPath = siteData.mappingPath || (options && options.mappingDir
        ? path.join(options.mappingDir, siteData.mappingName + '.yaml')
        : siteData.mappingName ? siteData.mappingName + '.yaml' : null);
      siteTables.set(siteName, buildSymbolTable(siteData.mapping, mappingPath));
    }
  }

  var resolvedSteps = [];
  var activeExpects = 0;
  var deferredExpects = 0;
  var notAutomatedExpects = 0;
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
          resolvedOperands = Object.assign({}, rawOperands, resolvedActionElement(resolvedElement));
        }
      }
      var siteInterpMsg = fillValueInterpolationError(rawOperands.value, stepId);
      if (siteInterpMsg) {
        errors.push(siteInterpMsg);
        errorDetails.push(tier2Detail(siteInterpMsg));
        skipStep = true;
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
      notAutomatedExpects += expectResult.notAutomatedCount;
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
    notAutomatedExpects: notAutomatedExpects,
    skipped: skipped,
  };

  var resolved = {
    name: flow.name,
    description: flow.description,
    variables: flow.variables,
    steps: resolvedSteps,
  };

  // Cross-site: each site resolves against its own mapping, so the mapping file is
  // stamped per site here rather than by the caller. The basename is already unique per
  // site, which is why a baseline record needs no site column.
  var referencedElements = [];
  siteTables.forEach(function(siteResult, siteName) {
    var siteData = siteMappings[siteName];
    // basename: a site's `mapping:` may carry a directory (the parser resolves it against
    // mappingDir), and the baseline key plus the compiler's warning channel both use the
    // file's basename. Stamping the raw name would make `mappings/office` and
    // `office.yaml` disagree with every other consumer of the same file.
    var rawName = siteData && siteData.mappingName ? String(siteData.mappingName) : null;
    var mappingFile = rawName ? path.basename(rawName) + '.yaml' : null;
    siteResult.referenced.forEach(function(rec) {
      referencedElements.push({
        mappingFile: mappingFile,
        page: rec.page,
        element: rec.element,
        selector: rec.selector,
      });
    });
  });

  return {
    resolved: resolved,
    stats: stats,
    errors: errors,
    errorDetails: errorDetails,
    referencedElements: referencedElements,
  };
}

module.exports = { resolve: resolve, resolveMultiSite: resolveMultiSite, buildSymbolTable: buildSymbolTable };
