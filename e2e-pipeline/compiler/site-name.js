'use strict';

const SITE_NAME_PATTERN = /^[A-Za-z_][A-Za-z0-9_]*$/;
const SITE_NAME_FORMAT = '^[A-Za-z_][A-Za-z0-9_]*$';

function isValidSiteName(siteName) {
  return typeof siteName === 'string' && SITE_NAME_PATTERN.test(siteName);
}

function siteNameValidationError(siteName) {
  return "Invalid site name '" + siteName + "' in sites: block: expected shell identifier matching " + SITE_NAME_FORMAT;
}

module.exports = {
  SITE_NAME_FORMAT,
  isValidSiteName,
  siteNameValidationError,
};
