'use strict';

var fs = require('node:fs');
var path = require('node:path');

/**
 * analyzeCoverage(mapping, resolvedSteps) — static coverage analysis.
 *
 * Walks a resolved flow's steps to determine which mapping elements were
 * reached (via action operands) or verified (via expect assertions).
 *
 * @param {object} mapping - Parsed mapping object with pages and elements.
 * @param {Array} resolvedSteps - Array of resolved step objects.
 * @returns {{ elements: Array, summary: object }}
 */
function analyzeCoverage(mapping, resolvedSteps) {
  // Build element registry from mapping.pages
  var registry = {};
  var pages = (mapping && mapping.pages) || {};

  Object.keys(pages).forEach(function(pageName) {
    var page = pages[pageName];
    var elements = (page && page.elements) || {};
    Object.keys(elements).forEach(function(elemName) {
      registry[elemName] = {
        name: elemName,
        page: pageName,
        reached_count: 0,
        verified_count: 0,
      };
    });
  });

  // Track unique pages navigated to
  var navigatedPages = {};

  // Walk steps
  var steps = Array.isArray(resolvedSteps) ? resolvedSteps : [];
  steps.forEach(function(step) {
    // Skip verify-external steps entirely
    if (step.type === 'verify-external') {
      return;
    }

    // Track page-level coverage from navigate steps
    if (step.type === 'navigate') {
      var target = step.operands && step.operands.target;
      if (target && pages.hasOwnProperty(target)) {
        navigatedPages[target] = true;
      }
      // Navigate steps do not contribute to element coverage
      return;
    }

    // Element-level: increment reached_count when step.operands.element exists
    var operandElement = step.operands && step.operands.element;
    if (operandElement && registry.hasOwnProperty(operandElement)) {
      registry[operandElement].reached_count += 1;
    }

    // Element-level: increment verified_count from expects
    var expects = Array.isArray(step.expects) ? step.expects : [];
    expects.forEach(function(expect) {
      // or-visible: increment all elements in the elements array
      if (expect.type === 'or-visible' && Array.isArray(expect.elements)) {
        expect.elements.forEach(function(e) {
          var eName = e && e.elementName;
          if (eName && registry.hasOwnProperty(eName)) {
            registry[eName].verified_count += 1;
          }
        });
        return;
      }

      // Standard expect with elementName
      if (expect.elementName && registry.hasOwnProperty(expect.elementName)) {
        registry[expect.elementName].verified_count += 1;
      }
    });
  });

  // Compute summary
  var elements = Object.values(registry);
  var total = elements.length;
  var reached = 0;
  var verified = 0;
  elements.forEach(function(el) {
    if (el.reached_count > 0) reached += 1;
    if (el.verified_count > 0) verified += 1;
  });

  var percent = total === 0 ? 0 : Math.round((verified / total) * 100);
  var pages_total = Object.keys(pages).length;
  var pages_reached = Object.keys(navigatedPages).length;

  return {
    elements: elements,
    summary: {
      total: total,
      reached: reached,
      verified: verified,
      percent: percent,
      pages_total: pages_total,
      pages_reached: pages_reached,
    },
  };
}

/**
 * appendCoverageHistory(historyPath, entry) — append one entry to coverage-history.json.
 *
 * Creates the file and any missing parent directories if they don't exist.
 * Never overwrites existing entries — always appends.
 *
 * @param {string} historyPath - Absolute path to coverage-history.json.
 * @param {object} entry - Coverage entry to append.
 */
function appendCoverageHistory(historyPath, entry) {
  var history = [];
  try {
    var raw = fs.readFileSync(historyPath, 'utf8');
    history = JSON.parse(raw);
    if (!Array.isArray(history)) {
      history = [];
    }
  } catch (e) {
    // File missing or unreadable — start fresh
    history = [];
  }

  history.push(entry);

  var dir = path.dirname(historyPath);
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(historyPath, JSON.stringify(history, null, 2) + '\n', 'utf8');
}

/**
 * checkCoverageRegression(historyPath, flow, currentPercent) — compare against previous run.
 *
 * Returns a ::warning:: annotation string when coverage drops > 5% from the
 * previous entry for the same flow. Returns null otherwise.
 *
 * @param {string} historyPath - Path to coverage-history.json.
 * @param {string} flow - Flow name to filter history entries by.
 * @param {number} currentPercent - Coverage percent from current run.
 * @returns {string|null}
 */
function checkCoverageRegression(historyPath, flow, currentPercent) {
  var history = [];
  try {
    var raw = fs.readFileSync(historyPath, 'utf8');
    history = JSON.parse(raw);
    if (!Array.isArray(history)) {
      return null;
    }
  } catch (e) {
    return null;
  }

  // Filter to entries for this flow only
  var flowHistory = history.filter(function(h) { return h.flow === flow; });

  // Need at least 2 entries to compare (the previous and the one before it)
  if (flowHistory.length < 2) {
    return null;
  }

  // The "previous" entry is the last one in history for this flow
  var previous = flowHistory[flowHistory.length - 1];
  var previousPercent = previous.percent;
  var drop = previousPercent - currentPercent;

  if (drop > 5) {
    return '::warning:: Coverage regression detected for flow "' + flow + '": ' +
      previousPercent + '% → ' + currentPercent + '% (dropped ' + drop + '%)';
  }

  return null;
}

module.exports = {
  analyzeCoverage: analyzeCoverage,
  appendCoverageHistory: appendCoverageHistory,
  checkCoverageRegression: checkCoverageRegression,
};
