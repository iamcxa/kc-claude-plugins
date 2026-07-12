'use strict';

const yaml = require('js-yaml');
const fs = require('node:fs');
const path = require('node:path');
const { isValidSiteName, validateSiteNames } = require('./site-name');

/**
 * Load and parse a YAML file, returning the parsed object or null on error.
 * Errors are pushed into the provided errors array.
 *
 * @param {string} filePath - Absolute or relative path to the YAML file
 * @param {string[]} errors - Error accumulator array (mutated in place)
 * @returns {object|null} Parsed object, or null if load/parse failed
 */
function loadYaml(filePath, errors) {
  let content;
  try {
    content = fs.readFileSync(filePath, 'utf8');
  } catch (e) {
    errors.push('File not found: ' + filePath);
    return null;
  }

  try {
    return yaml.load(content);
  } catch (e) {
    if (e instanceof yaml.YAMLException) {
      errors.push('YAML parse error in ' + filePath + ': ' + e.message);
    } else {
      errors.push('Failed to parse ' + filePath + ': ' + e.message);
    }
    return null;
  }
}

/**
 * Validate required flow fields. Errors are pushed into the errors array.
 *
 * @param {object} flow - Parsed flow object
 * @param {string} filePath - Source file path (for error messages)
 * @param {string[]} errors - Error accumulator array (mutated in place)
 */
function validateFlow(flow, filePath, errors) {
  if (!flow || typeof flow !== 'object') {
    errors.push('Invalid flow YAML structure in ' + filePath);
    return;
  }
  if (!flow.name) {
    errors.push('Flow missing required field "name" in ' + filePath);
  }
  // mapping is optional when sites: block is present
  // but both mapping: and sites: together is an error
  if (flow.mapping && flow.sites) {
    errors.push("Flow has both 'mapping:' and 'sites:' — use one or the other in " + filePath);
  }
  if (!flow.mapping && !flow.sites) {
    errors.push('Flow missing required field "mapping" in ' + filePath);
  }
  if (!Array.isArray(flow.steps) || flow.steps.length === 0) {
    errors.push('Flow missing required field "steps" (must be non-empty array) in ' + filePath);
  }
}

/**
 * Validate required mapping fields. Errors are pushed into the errors array.
 *
 * @param {object} mapping - Parsed mapping object
 * @param {string} filePath - Source file path (for error messages)
 * @param {string[]} errors - Error accumulator array (mutated in place)
 */
function validateMapping(mapping, filePath, errors) {
  if (!mapping || typeof mapping !== 'object') {
    errors.push('Invalid mapping YAML structure in ' + filePath);
    return;
  }
  if (mapping.version !== 2) {
    errors.push('Mapping must have version: 2 in ' + filePath + ' (got: ' + mapping.version + ')');
  }
  if (!mapping.pages || typeof mapping.pages !== 'object') {
    errors.push('Mapping missing required field "pages" (must be object) in ' + filePath);
  }
}

/**
 * Parse a flow YAML file and its associated mapping YAML file(s).
 *
 * Supports two flow formats:
 *   - Single-site: flow has top-level mapping: field
 *   - Cross-site:  flow has top-level sites: block (no mapping: field)
 *
 * @param {string} flowPath - Path to the flow YAML file
 * @param {string} mappingDir - Directory containing mapping YAML files
 * @returns {{ flow: object|null, mapping: object|null, sites: object|null, errors: string[] }}
 *   - Single-site: { flow, mapping, sites: null, errors }
 *   - Cross-site:  { flow, mapping: null, sites: { siteName: { mappingName, mapping } }, errors }
 */
function parse(flowPath, mappingDir) {
  const errors = [];

  // Load flow YAML
  const flow = loadYaml(flowPath, errors);
  if (flow === null) {
    // Could not load flow at all — return early with errors
    return { flow: null, mapping: null, sites: null, errors };
  }

  // Validate flow structure
  validateFlow(flow, flowPath, errors);

  // --- Cross-site flow: sites: block ---
  if (flow.sites && !flow.mapping) {
    var sitesMap = {};
    var siteNames = Object.keys(flow.sites);
    errors.push.apply(errors, validateSiteNames(siteNames));

    for (var i = 0; i < siteNames.length; i++) {
      var siteName = siteNames[i];
      var siteEntry = flow.sites[siteName];
      var mappingName = siteEntry && siteEntry.mapping;

      if (!isValidSiteName(siteName)) {
        continue;
      }

      if (!mappingName) {
        errors.push("Site '" + siteName + "' in sites: block has no mapping field in " + flowPath);
        continue;
      }

      var mappingPath = path.join(mappingDir, mappingName + '.yaml');
      var mappingObj = loadYaml(mappingPath, errors);
      if (mappingObj !== null) {
        validateMapping(mappingObj, mappingPath, errors);
        sitesMap[siteName] = { mappingName: mappingName, mapping: mappingObj };
      } else {
        // loadYaml already pushed the error
        sitesMap[siteName] = { mappingName: mappingName, mapping: null };
      }
    }

    return { flow, mapping: null, sites: sitesMap, errors };
  }

  // --- Single-site flow: mapping: field ---
  let mapping = null;
  if (flow.mapping) {
    const mappingName = flow.mapping;
    const mappingPath = path.join(mappingDir, mappingName + '.yaml');
    mapping = loadYaml(mappingPath, errors);
    if (mapping !== null) {
      validateMapping(mapping, mappingPath, errors);
    }
  }

  // If there were validation errors, return with nulled objects to signal failure
  // but preserve the flow/mapping for partial diagnostics
  return { flow, mapping, sites: null, errors };
}

module.exports = { parse };
