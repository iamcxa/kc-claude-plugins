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
    pattern: /snapshot/i,
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
};

function buildSymbolTable(mapping) {
  var table = new Map();
  var errors = [];
  var collisions = new Map();

  var pages = mapping.pages || {};
  for (var pageName in pages) {
    var pageData = pages[pageName];
    var elements = pageData.elements || {};
    for (var elemName in elements) {
      var elemData = elements[elemName];
      if (table.has(elemName)) {
        if (!collisions.has(elemName)) {
          collisions.set(elemName, [table.get(elemName).page]);
        }
        collisions.get(elemName).push(pageName);
      } else {
        table.set(elemName, { selector: elemData.selector, page: pageName });
      }
    }
  }

  collisions.forEach(function(pages, elemName) {
    errors.push("element '" + elemName + "' is ambiguous -- found on: " + pages.join(', '));
  });

  return { table: table, errors: errors };
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

function resolveExpects(expects, symbolTable, stepId) {
  var resolvedExpects = [];
  var activeCount = 0;
  var deferredCount = 0;
  var errors = [];

  var ACTIVE_PATTERN = /^(\w+) is visible$/;

  for (var i = 0; i < expects.length; i++) {
    var expectStr = expects[i];
    var match = ACTIVE_PATTERN.exec(expectStr);
    if (match) {
      var elemName = match[1];
      var entry = symbolTable.get(elemName);
      if (!entry) {
        errors.push("Step '" + stepId + "': expect element '" + elemName + "' not found in mapping");
      } else {
        resolvedExpects.push({
          type: 'active',
          raw: expectStr,
          elementName: elemName,
          selector: entry.selector,
        });
        activeCount++;
      }
    } else {
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
  var tableErrors = symbolResult.errors;
  for (var i = 0; i < tableErrors.length; i++) {
    errors.push(tableErrors[i]);
  }

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
        var entry = table.get(elemName);
        if (!entry) {
          errors.push("Step '" + stepId + "': element '" + elemName + "' not found in mapping");
          skipStep = true;
        } else {
          resolvedOperands = Object.assign({}, rawOperands, { selector: entry.selector });
        }
      }

    } else if (step.type === 'verify-external') {
      skipped++;
    }

    if (skipStep) continue;

    var stepExpects = [];
    if (Array.isArray(step.expect) && step.expect.length > 0) {
      var expectResult = resolveExpects(step.expect, table, stepId);
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

module.exports = { resolve: resolve };
