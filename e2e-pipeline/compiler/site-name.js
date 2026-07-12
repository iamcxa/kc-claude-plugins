'use strict';

const SITE_NAME_PATTERN = /^[A-Za-z_][A-Za-z0-9_]*$/;
const SITE_NAME_FORMAT = '^[A-Za-z_][A-Za-z0-9_]*$';
const RESERVED_SITE_NAMES = new Set(['__proto__', 'prototype', 'constructor']);

function isValidSiteName(siteName) {
  return typeof siteName === 'string' &&
    SITE_NAME_PATTERN.test(siteName) &&
    !RESERVED_SITE_NAMES.has(siteName);
}

function siteNameValidationError(siteName) {
  if (RESERVED_SITE_NAMES.has(siteName)) {
    return "Invalid site name '" + siteName + "' in sites: block: alias is reserved";
  }
  return "Invalid site name '" + siteName + "' in sites: block: expected shell identifier matching " + SITE_NAME_FORMAT;
}

function siteBaseUrlVariable(siteName) {
  return siteName.toUpperCase() + '_BASE_URL';
}

function validateSiteNames(siteNames) {
  var errors = [];
  var aliasesByVariable = Object.create(null);

  for (var i = 0; i < siteNames.length; i++) {
    var siteName = siteNames[i];
    if (!isValidSiteName(siteName)) {
      errors.push(siteNameValidationError(siteName));
      continue;
    }

    var variableName = siteBaseUrlVariable(siteName);
    var priorAlias = aliasesByVariable[variableName];
    if (priorAlias && priorAlias !== siteName) {
      errors.push(
        "Site aliases '" + priorAlias + "' and '" + siteName +
        "' collide on normalized base URL variable '" + variableName + "'"
      );
    } else {
      aliasesByVariable[variableName] = siteName;
    }
  }

  return errors;
}

module.exports = {
  SITE_NAME_FORMAT,
  isValidSiteName,
  siteBaseUrlVariable,
  siteNameValidationError,
  validateSiteNames,
};
