'use strict';

const yaml = require('js-yaml');
const fs = require('node:fs');
const path = require('node:path');
const { isValidSiteName, siteBaseUrlVariable, validateSiteNames } = require('./site-name');

const VARIABLE_NAME_PATTERN = /^[A-Za-z_][A-Za-z0-9_]*$/;
const VARIABLE_NAME_FORMAT = '^[A-Za-z_][A-Za-z0-9_]*$';
const RESERVED_VARIABLE_NAMES = new Set(['__proto__', 'prototype', 'constructor']);

function validateFlowVariables(flow, errors) {
  if (flow.variables !== undefined && (
    flow.variables === null || typeof flow.variables !== 'object' || Array.isArray(flow.variables)
  )) {
    errors.push('Flow variables must be an object');
    return;
  }

  var variables = flow.variables || {};
  var variableKeys = Object.keys(variables);
  var sourcesByNormalizedKey = new Map();

  function register(sourceKey, sourceLabel, normalizedKey) {
    var prior = sourcesByNormalizedKey.get(normalizedKey);
    if (prior) {
      errors.push(
        prior.label + " '" + prior.key + "' and " + sourceLabel + " '" + sourceKey +
        "' collide on normalized shell variable '" + normalizedKey + "'"
      );
      return;
    }
    sourcesByNormalizedKey.set(normalizedKey, { key: sourceKey, label: sourceLabel });
  }

  for (var i = 0; i < variableKeys.length; i++) {
    var variableKey = variableKeys[i];
    if (RESERVED_VARIABLE_NAMES.has(variableKey)) {
      errors.push("Invalid flow variable key '" + variableKey + "': key is reserved");
      continue;
    }
    if (!VARIABLE_NAME_PATTERN.test(variableKey)) {
      errors.push(
        "Invalid flow variable key '" + variableKey +
        "': expected shell identifier matching " + VARIABLE_NAME_FORMAT
      );
      continue;
    }
    register(variableKey, 'Flow variable key', variableKey.toUpperCase());
  }

  if (flow.sites && typeof flow.sites === 'object' && !Array.isArray(flow.sites)) {
    var siteNames = Object.keys(flow.sites);
    for (var siteIndex = 0; siteIndex < siteNames.length; siteIndex++) {
      var siteName = siteNames[siteIndex];
      if (!isValidSiteName(siteName)) continue;
      var siteVariable = siteBaseUrlVariable(siteName);
      if (!Object.prototype.hasOwnProperty.call(variables, siteVariable)) {
        register(siteName, 'Injected site variable for', siteVariable);
      }
    }
  } else if (flow.mapping && !Object.prototype.hasOwnProperty.call(variables, 'base_url')) {
    register('base_url', 'Injected mapping variable', 'BASE_URL');
  }
}

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
  } else {
    var stepIndexesById = new Map();
    for (var stepIndex = 0; stepIndex < flow.steps.length; stepIndex++) {
      var step = flow.steps[stepIndex];
      var stepId = step && step.id;
      if (typeof stepId !== 'string' || stepId.trim().length === 0) {
        errors.push('Step at index ' + stepIndex + ' must have an id that is a non-empty string in ' + filePath);
        continue;
      }
      if (stepIndexesById.has(stepId)) {
        errors.push(
          "Duplicate step id '" + stepId + "' at indexes " +
          stepIndexesById.get(stepId) + ' and ' + stepIndex + ' in ' + filePath
        );
      } else {
        stepIndexesById.set(stepId, stepIndex);
      }
    }
  }
  validateFlowVariables(flow, errors);
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
