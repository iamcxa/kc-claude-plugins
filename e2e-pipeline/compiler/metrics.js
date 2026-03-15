'use strict';

var fs = require('node:fs');
var path = require('node:path');

/**
 * metricsFileName(flowName, timestamp) — produce a lexicographically-sortable metrics filename.
 *
 * Converts an ISO-8601 timestamp to compact format (no hyphens, no colons, no milliseconds).
 * Example: metricsFileName('login-flow', '2026-03-15T14:23:01.000Z')
 *          → 'login-flow-20260315T142301Z.json'
 *
 * The compact ISO8601 format sorts lexicographically by time, enabling windowed analysis
 * without parsing file contents.
 *
 * @param {string} flowName - Flow name (hyphens preserved).
 * @param {string} timestamp - ISO-8601 timestamp string (e.g., new Date().toISOString()).
 * @returns {string} - Filename with .json suffix.
 */
function metricsFileName(flowName, timestamp) {
  // Strip hyphens and colons, then strip milliseconds (.ddd before Z)
  var ts = new Date(timestamp).toISOString().replace(/[-:]/g, '').replace(/\.\d+/, '');
  return flowName + '-' + ts + '.json';
}

/**
 * readMetricsFiles(metricsDir, flowName, windowSize) — read last N metrics files for a flow.
 *
 * Reads all JSON files in metricsDir matching the flowName prefix, sorts them
 * lexicographically (ISO8601-compact timestamps sort correctly by time), and
 * returns the last windowSize entries as parsed JSON objects.
 *
 * Returns [] if directory does not exist or no matching files are found.
 *
 * @param {string} metricsDir - Directory containing metrics JSON files.
 * @param {string} flowName - Flow name used as file prefix filter.
 * @param {number} windowSize - Maximum number of files to return (most recent).
 * @returns {Array} - Array of parsed JSON objects.
 */
function readMetricsFiles(metricsDir, flowName, windowSize) {
  var files;
  try {
    files = fs.readdirSync(metricsDir);
  } catch (e) {
    return [];
  }

  var prefix = flowName + '-';
  var matching = files.filter(function(f) {
    return f.indexOf(prefix) === 0 && f.slice(-5) === '.json';
  });

  // Lexicographic sort — ISO8601-compact timestamps sort correctly by time
  matching.sort();

  // Take the last windowSize entries
  var windowed = matching.slice(-windowSize);

  // Read and parse each file
  return windowed.map(function(f) {
    var raw = fs.readFileSync(path.join(metricsDir, f), 'utf8');
    return JSON.parse(raw);
  });
}

module.exports = {
  metricsFileName: metricsFileName,
  readMetricsFiles: readMetricsFiles,
};
