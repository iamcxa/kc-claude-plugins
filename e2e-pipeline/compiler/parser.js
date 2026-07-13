'use strict';

const yaml = require('js-yaml');
const fs = require('node:fs');
const path = require('node:path');
const { isValidSiteName, siteBaseUrlVariable, validateSiteNames } = require('./site-name');

const VARIABLE_NAME_PATTERN = /^[A-Za-z_][A-Za-z0-9_]*$/;
const VARIABLE_NAME_FORMAT = '^[A-Za-z_][A-Za-z0-9_]*$';
const RESERVED_VARIABLE_NAMES = new Set(['__proto__', 'prototype', 'constructor']);
const HTTP_AUTH_SCHEME_PATTERN = /^[A-Za-z][A-Za-z0-9._~+-]*$/;

// Allowed validate types for capture-url-query steps (SC-1032)
const CAPTURE_VALIDATE_TYPES = new Set(['uuid']);
// Allowed on_fail values for finally steps (SC-1032)

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
  } else if (flow.mapping && !sourcesByNormalizedKey.has('BASE_URL')) {
    register('base_url', 'Injected mapping variable', 'BASE_URL');
  }
}

function hasUnpairedSurrogate(value) {
  for (var i = 0; i < value.length; i++) {
    var code = value.charCodeAt(i);
    if (code >= 0xD800 && code <= 0xDBFF) {
      var next = value.charCodeAt(i + 1);
      if (!(next >= 0xDC00 && next <= 0xDFFF)) return true;
      i++;
    } else if (code >= 0xDC00 && code <= 0xDFFF) {
      return true;
    }
  }
  return false;
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
      if (stepId.includes('\u0000')) {
        errors.push('Step at index ' + stepIndex + ' id must not contain NUL in ' + filePath);
        continue;
      }
      if (hasUnpairedSurrogate(stepId)) {
        errors.push('Step at index ' + stepIndex + ' id must not contain an unpaired surrogate in ' + filePath);
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
  validateRuntimeValues(flow, errors);
  validateFlowSteps(flow, filePath, errors);
  validateCrossSiteRuntimeFeatures(flow, errors);
}

function validateCrossSiteRuntimeFeatures(flow, errors) {
  if (!flow.sites) return;
  var steps = Array.isArray(flow.steps) ? flow.steps : [];
  if (flow.runtime_values !== undefined) {
    errors.push('Cross-site flows do not support runtime_values');
  }
  if (steps.some(function(step) { return step && step.type === 'capture-url-query'; })) {
    errors.push('Cross-site flows do not support capture-url-query');
  }
  if (flow.finally !== undefined) {
    errors.push('Cross-site flows do not support finally');
  }
}

/**
 * Validate typed, environment-backed runtime values.
 *
 * @param {object} flow - Parsed flow object
 * @param {string[]} errors - Error accumulator array (mutated in place)
 */
function validateRuntimeValues(flow, errors) {
  if (flow.runtime_values === undefined) return;
  if (flow.runtime_values === null ||
      typeof flow.runtime_values !== 'object' ||
      Array.isArray(flow.runtime_values)) {
    errors.push('Flow runtime_values must be an object of typed environment declarations');
    return;
  }
  var keys = Object.keys(flow.runtime_values);
  for (var i = 0; i < keys.length; i++) {
    var key = keys[i];
    var val = flow.runtime_values[key];
    if (!VARIABLE_NAME_PATTERN.test(key)) {
      errors.push(
        "Flow runtime_value key '" + key + "' is not a valid shell identifier"
      );
    }
    if (RESERVED_VARIABLE_NAMES.has(key)) {
      errors.push("Flow runtime_value key '" + key + "' is reserved");
    }
    if (!val || typeof val !== 'object' || Array.isArray(val)) {
      errors.push("Flow runtime_value '" + key + "' must be an object with from_env and sensitive");
      continue;
    }
    if (typeof val.from_env !== 'string' || !/^[A-Z_][A-Z0-9_]*$/.test(val.from_env)) {
      errors.push("Flow runtime_value '" + key + "' from_env must be an uppercase environment identifier");
    }
    if (typeof val.sensitive !== 'boolean') {
      errors.push("Flow runtime_value '" + key + "' sensitive must be boolean");
    }
  }
}

/**
 * Validate per-step fields that require new types (SC-1032: capture-url-query, finally http).
 *
 * @param {object} flow - Parsed flow object
 * @param {string} filePath - Source file path (for error messages)
 * @param {string[]} errors - Error accumulator array (mutated in place)
 */
function validateFlowSteps(flow, filePath, errors) {
  // Validate capture-url-query steps
  var steps = Array.isArray(flow.steps) ? flow.steps : [];
  for (var i = 0; i < steps.length; i++) {
    var step = steps[i];
    if (!step || step.type !== 'capture-url-query') continue;
    validateCaptureUrlQueryStep(step, filePath, errors);
  }

  var stateKeys = new Set(Object.keys(flow.runtime_values || {}));
  for (var stateIndex = 0; stateIndex < steps.length; stateIndex++) {
    var capture = steps[stateIndex];
    if (!capture || capture.type !== 'capture-url-query' || typeof capture.save_as !== 'string') continue;
    if (stateKeys.has(capture.save_as)) {
      errors.push("Step '" + capture.id + "': save_as '" + capture.save_as + "' collides with an existing runtime state key");
    }
    stateKeys.add(capture.save_as);
  }

  // Validate finally block
  if (flow.finally !== undefined) {
    if (!Array.isArray(flow.finally)) {
      errors.push('Flow finally must be an array of steps in ' + filePath);
      return;
    }
    for (var j = 0; j < flow.finally.length; j++) {
      validateFinallyStep(flow.finally[j], j, filePath, stateKeys, errors);
    }
  }
}

/**
 * Validate a capture-url-query step.
 */
function validateCaptureUrlQueryStep(step, filePath, errors) {
  var stepId = step.id || '(unnamed)';
  if (!step.query || typeof step.query !== 'string') {
    errors.push(
      "Step '" + stepId + "': capture-url-query must have 'query:' (string) in " + filePath
    );
  }
  if (typeof step.query === 'string' && !/^[A-Za-z0-9._~-]+$/.test(step.query)) {
    errors.push("Step '" + stepId + "': capture-url-query query must be a non-empty ASCII URL query key in " + filePath);
  }
  if (!step.save_as || typeof step.save_as !== 'string') {
    errors.push(
      "Step '" + stepId + "': capture-url-query must have 'save_as:' (string) in " + filePath
    );
  }
  if (typeof step.save_as === 'string' &&
      (!VARIABLE_NAME_PATTERN.test(step.save_as) || RESERVED_VARIABLE_NAMES.has(step.save_as))) {
    errors.push("Step '" + stepId + "': capture-url-query save_as must be a non-reserved identifier in " + filePath);
  }
  if (step.validate !== undefined) {
    if (!CAPTURE_VALIDATE_TYPES.has(step.validate)) {
      errors.push(
        "Step '" + stepId + "': capture-url-query validate type '" + step.validate +
        "' is not supported. Supported: " + Array.from(CAPTURE_VALIDATE_TYPES).join(', ') +
        " in " + filePath
      );
    }
  }
}

/**
 * Validate a finally step.
 */
function validateFinallyStep(step, index, filePath, stateKeys, errors) {
  if (!step || typeof step !== 'object') {
    errors.push('Finally step at index ' + index + ' must be an object in ' + filePath);
    return;
  }
  var stepId = step.id || '(unnamed)';
  if (step.type !== 'http') {
    errors.push("Finally step '" + stepId + "': unsupported type '" + (step.type || '') + "'");
    return;
  }
  var http = step.request;
  if (!http || typeof http !== 'object') {
    errors.push(
      "Finally step '" + stepId + "': http type step must have a 'request:' block in " + filePath
    );
    return;
  }
  if (!http.url || typeof http.url !== 'object' || !http.url.base_from_env || !Array.isArray(http.url.path_segments)) {
    errors.push(
      "Finally step '" + stepId + "': request.url must have base_from_env and path_segments in " + filePath
    );
  }
  if (!http.method || typeof http.method !== 'string') {
    errors.push(
      "Finally step '" + stepId + "': http block must have 'method:' (string) in " + filePath
    );
  }
  if (http.url && typeof http.url === 'object') {
    if (!/^[A-Z_][A-Z0-9_]*$/.test(http.url.base_from_env || '')) {
      errors.push("Finally step '" + stepId + "': request.url.base_from_env must be an uppercase environment identifier");
    }
    if (Array.isArray(http.url.path_segments)) {
      http.url.path_segments.forEach(function(segment) {
        if (segment && typeof segment === 'object') validateRuntimeRef(segment, stepId, stateKeys, errors);
      });
    }
  }
  Object.keys(http.headers || {}).forEach(function(headerName) {
    if (!/^[!#$%&'*+.^_`|~0-9A-Za-z-]+$/.test(headerName)) {
      errors.push("Finally step '" + stepId + "': invalid HTTP header name '" + headerName + "'");
    }
    var header = http.headers[headerName];
    if (!header || typeof header !== 'object' || typeof header.scheme !== 'string') {
      errors.push("Finally step '" + stepId + "': header '" + headerName + "' must declare scheme and runtime_ref");
    } else {
      if (!HTTP_AUTH_SCHEME_PATTERN.test(header.scheme)) {
        errors.push("Finally step '" + stepId + "': header '" + headerName + "' auth scheme is invalid");
      }
      validateRuntimeRef(header, stepId, stateKeys, errors);
    }
  });
  if (step.expect && step.expect.status !== undefined &&
      (!Number.isInteger(step.expect.status) || step.expect.status < 100 || step.expect.status > 599)) {
    errors.push("Finally step '" + stepId + "': expect.status must be an HTTP status integer");
  }
}

function validateRuntimeRef(value, stepId, stateKeys, errors) {
  if (!value || typeof value.runtime_ref !== 'string' || !stateKeys.has(value.runtime_ref)) {
    errors.push("Finally step '" + stepId + "': unknown runtime_ref '" +
      (value && value.runtime_ref ? value.runtime_ref : '') + "'");
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
