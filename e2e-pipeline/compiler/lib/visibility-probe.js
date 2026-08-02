'use strict';

const POLICIES = new Set(['strict', 'retained-zero-rect']);
const ASSERTIONS = new Set(['visible', 'not-visible']);
const TERMINAL_RESULTS = new Set([
  'probe_error',
  'invalid_selector',
  'raw_multi_match',
  'multiple_rendered',
]);

function normalizePositiveInteger(value, fallback, maximum, name) {
  if (value === undefined) return fallback;
  if (!Number.isInteger(value) || value < 1 || value > maximum) {
    throw new TypeError(name + ' must be an integer from 1 through ' + maximum);
  }
  return value;
}

function buildProbeExpression(cssSelector, evidenceLimits) {
  if (typeof cssSelector !== 'string') {
    throw new TypeError('cssSelector must be a string');
  }
  const limits = evidenceLimits || {};
  const candidateLimit = normalizePositiveInteger(
    limits.candidateEvidenceLimit,
    10,
    100,
    'candidateEvidenceLimit'
  );
  const rectLimit = normalizePositiveInteger(
    limits.clientRectEvidenceLimit,
    5,
    50,
    'clientRectEvidenceLimit'
  );
  const labelLimit = normalizePositiveInteger(
    limits.labelLengthLimit,
    120,
    1000,
    'labelLengthLimit'
  );

  const configuration = JSON.stringify({
    selector: cssSelector,
    candidateLimit: candidateLimit,
    rectLimit: rectLimit,
    labelLimit: labelLimit,
  });

  return '(' + function probeVisibility(config) {
    function cleanText(value, limit) {
      const input = String(value == null ? '' : value);
      let output = '';
      for (let index = 0; index < input.length && output.length < limit; index++) {
        const code = input.charCodeAt(index);
        output += code <= 31 || (code >= 127 && code <= 159) ? ' ' : input[index];
      }
      return output;
    }

    function numberOrNull(value) {
      return typeof value === 'number' && Number.isFinite(value) ? value : null;
    }

    function attributeEvidence(element, name) {
      const value = element.getAttribute(name);
      return value == null ? null : cleanText(value, 120);
    }

    function rectEvidence(rect) {
      return {
        x: numberOrNull(rect?.x),
        y: numberOrNull(rect?.y),
        width: numberOrNull(rect?.width),
        height: numberOrNull(rect?.height),
      };
    }

    function errorEvidence(kind, error) {
      return {
        probe_version: 1,
        probe_scope: 'current-document',
        match_count: null,
        nonzero_layout_visible_count: null,
        style_visible_zero_rect_count: null,
        non_style_visible_count: null,
        candidate_evidence_limit: config.candidateLimit,
        candidate_evidence_truncated: false,
        candidates: [],
        error: {
          kind: kind,
          name: cleanText(error?.name ? error.name : 'Error', 80),
          message: cleanText(error?.message ? error.message : error, 240),
        },
      };
    }

    let matches;
    try {
      matches = document.querySelectorAll(config.selector);
    } catch (error) {
      return errorEvidence(
        error && error.name === 'SyntaxError' ? 'invalid_selector' : 'probe_error',
        error
      );
    }

    const evidence = {
      probe_version: 1,
      probe_scope: 'current-document',
      match_count: matches.length,
      nonzero_layout_visible_count: 0,
      style_visible_zero_rect_count: 0,
      non_style_visible_count: 0,
      candidate_evidence_limit: config.candidateLimit,
      candidate_evidence_truncated: matches.length > config.candidateLimit,
      candidates: [],
    };

    try {
      for (let index = 0; index < matches.length; index++) {
        const element = matches[index];
        if (!element || typeof element.checkVisibility !== 'function') {
          throw new Error('Element.checkVisibility is unavailable');
        }
        const checkVisibility = element.checkVisibility({
          opacityProperty: true,
          visibilityProperty: true,
        });
        if (checkVisibility !== true && checkVisibility !== false) {
          throw new Error('Element.checkVisibility returned a non-boolean value');
        }

        const rectList = element.getClientRects();
        let hasPositiveAreaRect = false;
        const clientRects = [];
        for (let rectIndex = 0; rectIndex < rectList.length; rectIndex++) {
          const rect = rectList[rectIndex];
          if (rect && rect.width > 0 && rect.height > 0) hasPositiveAreaRect = true;
          if (index < config.candidateLimit && rectIndex < config.rectLimit) {
            clientRects.push(rectEvidence(rect));
          }
        }

        const nonzeroLayoutVisible = checkVisibility && hasPositiveAreaRect;
        if (nonzeroLayoutVisible) {
          evidence.nonzero_layout_visible_count++;
        } else if (checkVisibility) {
          evidence.style_visible_zero_rect_count++;
        } else {
          evidence.non_style_visible_count++;
        }

        if (index < config.candidateLimit) {
          const style = getComputedStyle(element);
          const ariaLabel = element.getAttribute('aria-label');
          evidence.candidates.push({
            index: index,
            tag: cleanText(String(element.tagName || '').toLowerCase(), 80),
            role: attributeEvidence(element, 'role'),
            data_testid: attributeEvidence(element, 'data-testid'),
            label: cleanText(ariaLabel == null ? element.textContent : ariaLabel, config.labelLimit),
            aria_hidden: attributeEvidence(element, 'aria-hidden'),
            inert: element.inert === true,
            check_visibility: checkVisibility,
            nonzero_layout_visible: nonzeroLayoutVisible,
            computed_style: {
              display: cleanText(style?.display, 80),
              visibility: cleanText(style?.visibility, 80),
              opacity: cleanText(style?.opacity, 80),
            },
            client_rect_count: rectList.length,
            client_rects_truncated: rectList.length > config.rectLimit,
            client_rects: clientRects,
            bounding_rect: rectEvidence(element.getBoundingClientRect()),
          });
        }
      }
    } catch (error) {
      return errorEvidence('probe_error', error);
    }

    return evidence;
  } + ')(' + configuration + ')';
}

function sanitizeErrorText(value) {
  const input = String(value || '');
  let output = '';
  for (let index = 0; index < input.length && output.length < 240; index++) {
    const code = input.charCodeAt(index);
    output += code <= 31 || (code >= 127 && code <= 159) ? ' ' : input[index];
  }
  return output;
}

function probeError(message, details) {
  return Object.assign({
    probe_version: 1,
    probe_scope: 'current-document',
    result: 'probe_error',
    match_count: null,
    nonzero_layout_visible_count: null,
    style_visible_zero_rect_count: null,
    non_style_visible_count: null,
    candidate_evidence_limit: 0,
    candidate_evidence_truncated: false,
    candidates: [],
    error: {
      kind: 'probe_error',
      message: sanitizeErrorText(message),
    },
  }, details || {});
}

function hasDuplicateJsonObjectKeys(text) {
  let index = 0;
  let duplicate = false;

  function skipWhitespace() {
    while (/\s/.test(text[index] || '')) index++;
  }

  function parseString() {
    const start = index;
    index++;
    while (index < text.length) {
      if (text[index] === '\\') {
        index += 2;
      } else if (text[index] === '"') {
        index++;
        return JSON.parse(text.slice(start, index));
      } else {
        index++;
      }
    }
    return '';
  }

  function parseValue() {
    skipWhitespace();
    if (text[index] === '{') {
      parseObject();
      return;
    }
    if (text[index] === '[') {
      index++;
      skipWhitespace();
      while (index < text.length && text[index] !== ']') {
        parseValue();
        skipWhitespace();
        if (text[index] === ',') {
          index++;
          skipWhitespace();
        }
      }
      index++;
      return;
    }
    if (text[index] === '"') {
      parseString();
      return;
    }
    while (index < text.length && !/[\],}]/.test(text[index])) index++;
  }

  function parseObject() {
    const keys = new Set();
    index++;
    skipWhitespace();
    while (index < text.length && text[index] !== '}') {
      const key = parseString();
      if (keys.has(key)) duplicate = true;
      keys.add(key);
      skipWhitespace();
      index++;
      parseValue();
      skipWhitespace();
      if (text[index] === ',') {
        index++;
        skipWhitespace();
      }
    }
    index++;
  }

  parseValue();
  return duplicate;
}

function unwrapEvalEnvelope(raw, transportExit) {
  if (!Number.isInteger(transportExit)) {
    return probeError('transport exit must be an integer');
  }
  if (transportExit !== 0) {
    return probeError('browser transport exited nonzero', { transport_exit: transportExit });
  }

  let payload;
  if (raw && typeof raw === 'object' && !Buffer.isBuffer(raw)) {
    payload = raw;
  } else {
    const text = Buffer.isBuffer(raw) ? raw.toString('utf8') : String(raw || '');
    if (text.trim() === '') return probeError('eval envelope is empty');
    try {
      payload = JSON.parse(text);
    } catch (_error) {
      return probeError('eval envelope is not valid JSON');
    }
    if (hasDuplicateJsonObjectKeys(text)) {
      return probeError('eval envelope contains a duplicate JSON field');
    }
  }

  if (!payload || typeof payload !== 'object' || payload.success !== true) {
    return probeError('eval envelope is not a successful response');
  }
  if (
    !payload.data ||
    typeof payload.data !== 'object' ||
    !Object.hasOwn(payload.data, 'result')
  ) {
    return probeError('eval envelope is missing data.result');
  }
  if (
    !payload.data.result ||
    typeof payload.data.result !== 'object' ||
    Array.isArray(payload.data.result)
  ) {
    return probeError('eval envelope data.result must be an object');
  }
  return payload.data.result;
}

function classifyVisibility(evidence, policy) {
  if (!POLICIES.has(policy)) {
    return probeError('unsupported visibility policy: ' + String(policy), { policy: policy });
  }
  if (!evidence || typeof evidence !== 'object' || Array.isArray(evidence)) {
    return probeError('probe evidence must be an object', { policy: policy });
  }

  if (evidence.error && evidence.error.kind === 'invalid_selector') {
    return Object.assign({}, evidence, { result: 'invalid_selector', match_count: null, policy: policy });
  }
  if (evidence.error) {
    return Object.assign({}, evidence, { result: 'probe_error', match_count: null, policy: policy });
  }

  if (
    evidence.probe_version !== 1 ||
    evidence.probe_scope !== 'current-document' ||
    !Number.isInteger(evidence.candidate_evidence_limit) ||
    evidence.candidate_evidence_limit < 1 ||
    typeof evidence.candidate_evidence_truncated !== 'boolean' ||
    !Array.isArray(evidence.candidates)
  ) {
    return probeError('probe evidence is missing required protocol fields', { policy: policy });
  }

  const countNames = [
    'match_count',
    'nonzero_layout_visible_count',
    'style_visible_zero_rect_count',
    'non_style_visible_count',
  ];
  const countsValid = countNames.every(function (name) {
    return Number.isInteger(evidence[name]) && evidence[name] >= 0;
  });
  if (!countsValid) {
    return probeError('probe evidence has invalid aggregate counts', { policy: policy });
  }
  const aggregateCount =
    evidence.nonzero_layout_visible_count +
    evidence.style_visible_zero_rect_count +
    evidence.non_style_visible_count;
  if (aggregateCount !== evidence.match_count) {
    return probeError('probe aggregate counts do not equal match_count', { policy: policy });
  }

  let result;
  if (evidence.match_count === 0) {
    result = 'no_match';
  } else if (evidence.nonzero_layout_visible_count === 0) {
    result = 'all_non_rendered';
  } else if (evidence.nonzero_layout_visible_count > 1) {
    result = 'multiple_rendered';
  } else if (evidence.match_count === 1) {
    result = 'unique_rendered';
  } else if (
    policy === 'retained-zero-rect' &&
    evidence.style_visible_zero_rect_count === evidence.match_count - 1 &&
    evidence.non_style_visible_count === 0
  ) {
    result = 'unique_rendered_with_retained_zero_rect';
  } else {
    result = 'raw_multi_match';
  }

  return Object.assign({}, evidence, { result: result, policy: policy });
}

function judgeVisibility(result, assertion) {
  const classified = typeof result === 'string' ? { result: result } : Object.assign({}, result);
  if (!ASSERTIONS.has(assertion)) {
    return Object.assign(classified, {
      result: 'probe_error',
      assertion: assertion,
      judgment: 'terminal',
      exit_code: 2,
      error: { kind: 'probe_error', message: 'unsupported visibility assertion: ' + String(assertion) },
    });
  }

  let judgment;
  if (TERMINAL_RESULTS.has(classified.result)) {
    judgment = 'terminal';
  } else {
    const rendered =
      classified.result === 'unique_rendered' ||
      classified.result === 'unique_rendered_with_retained_zero_rect';
    const nonRendered =
      classified.result === 'no_match' || classified.result === 'all_non_rendered';
    if (!rendered && !nonRendered) {
      judgment = 'terminal';
    } else if (assertion === 'visible') {
      judgment = rendered ? 'satisfied' : 'retryable';
    } else {
      judgment = nonRendered ? 'satisfied' : 'retryable';
    }
  }

  return Object.assign(classified, {
    assertion: assertion,
    judgment: judgment,
    exit_code: judgment === 'satisfied' ? 0 : judgment === 'retryable' ? 1 : 2,
  });
}

function renderStandaloneSupport() {
  return [
    '(function () {',
    "'use strict';",
    "const POLICIES = new Set(['strict', 'retained-zero-rect']);",
    "const ASSERTIONS = new Set(['visible', 'not-visible']);",
    "const TERMINAL_RESULTS = new Set(['probe_error', 'invalid_selector', 'raw_multi_match', 'multiple_rendered']);",
    normalizePositiveInteger.toString(),
    buildProbeExpression.toString(),
    sanitizeErrorText.toString(),
    probeError.toString(),
    hasDuplicateJsonObjectKeys.toString(),
    unwrapEvalEnvelope.toString(),
    classifyVisibility.toString(),
    judgeVisibility.toString(),
    'return {',
    '  buildProbeExpression: buildProbeExpression,',
    '  unwrapEvalEnvelope: unwrapEvalEnvelope,',
    '  classifyVisibility: classifyVisibility,',
    '  judgeVisibility: judgeVisibility,',
    '};',
    '})()',
  ].join('\n');
}

module.exports = {
  buildProbeExpression: buildProbeExpression,
  unwrapEvalEnvelope: unwrapEvalEnvelope,
  classifyVisibility: classifyVisibility,
  judgeVisibility: judgeVisibility,
  renderStandaloneSupport: renderStandaloneSupport,
};
