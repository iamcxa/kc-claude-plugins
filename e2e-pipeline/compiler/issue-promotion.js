'use strict';

const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');

const CANDIDATE_FIELDS = [
  'version',
  'kind',
  'code',
  'source_skill',
  'target',
  'summary',
  'proposed_change',
];
const SAFE_TEXT_RE =
  /[<>]|https?:\/\/|\/(?:Users|home|private|tmp|var)\/|~\/|[A-Za-z]:\\(?:Users|Documents and Settings)\\|(?:token|password|secret|authorization|cookie)\s*[:=]/i;

function containsControlCharacter(value) {
  return Array.from(value).some(function(character) {
    const codePoint = character.codePointAt(0);
    return codePoint < 32 || codePoint === 127;
  });
}

function requireBoundedText(value, field, minimum, maximum) {
  if (
    typeof value !== 'string' ||
    value.length < minimum ||
    value.length > maximum ||
    containsControlCharacter(value) ||
    SAFE_TEXT_RE.test(value)
  ) {
    throw new Error(field + ' contains unsafe or project-specific text');
  }
  return value;
}

function validateCandidate(candidate) {
  if (!candidate || typeof candidate !== 'object' || Array.isArray(candidate)) {
    throw new Error('candidate must be an object');
  }

  const keys = Object.keys(candidate).sort();
  const expected = CANDIDATE_FIELDS.slice().sort();
  if (JSON.stringify(keys) !== JSON.stringify(expected)) {
    throw new Error('candidate fields must match the version 1 contract');
  }
  if (candidate.version !== 1) {
    throw new Error('candidate version must be 1');
  }
  if (candidate.kind !== 'pipeline-defect') {
    throw new Error('candidate kind must be pipeline-defect');
  }
  if (!/^[a-z0-9][a-z0-9-]{2,79}$/.test(candidate.code)) {
    throw new Error('candidate code must be a stable lowercase identifier');
  }
  if (!/^[a-z0-9][a-z0-9-]{2,63}$/.test(candidate.source_skill)) {
    throw new Error('source_skill must be a lowercase skill identifier');
  }
  if (
    typeof candidate.target !== 'string' ||
    !candidate.target.startsWith('e2e-pipeline/') ||
    candidate.target.length > 240 ||
    !/^[A-Za-z0-9._/-]+$/.test(candidate.target) ||
    candidate.target.endsWith('/') ||
    !path.posix.basename(candidate.target).includes('.') ||
    candidate.target.includes('\\') ||
    candidate.target !== path.posix.normalize(candidate.target) ||
    candidate.target.includes('../')
  ) {
    throw new Error('candidate target must name a file under e2e-pipeline');
  }

  requireBoundedText(candidate.summary, 'candidate summary', 12, 160);
  requireBoundedText(
    candidate.proposed_change,
    'candidate proposed_change',
    12,
    300
  );

  return {
    version: candidate.version,
    kind: candidate.kind,
    code: candidate.code,
    source_skill: candidate.source_skill,
    target: candidate.target,
    summary: candidate.summary,
    proposed_change: candidate.proposed_change,
  };
}

function fingerprintCandidate(candidate) {
  const normalized = validateCandidate(candidate);
  return crypto
    .createHash('sha256')
    .update(
      JSON.stringify([
        normalized.version,
        normalized.kind,
        normalized.code,
        normalized.target,
      ])
    )
    .digest('hex');
}

function validateRunId(runId) {
  if (typeof runId !== 'string' || !/^[a-z0-9][a-z0-9-]{2,127}$/.test(runId)) {
    throw new Error(
      'run-id must contain lowercase letters, digits, and hyphens'
    );
  }
}

function validateThreshold(minDistinctRuns) {
  if (
    !Number.isInteger(minDistinctRuns) ||
    minDistinctRuns < 2 ||
    minDistinctRuns > 100
  ) {
    throw new Error('min_distinct_runs must be an integer from 2 to 100');
  }
}

function recordObservation(options) {
  const normalized = validateCandidate(options?.candidate);
  validateRunId(options?.runId);
  const stateDir = options?.stateDir;
  if (typeof stateDir !== 'string' || !path.isAbsolute(stateDir)) {
    throw new Error('state-dir must be an absolute path');
  }
  const observedAt = options.observedAt || new Date().toISOString();
  if (Number.isNaN(Date.parse(observedAt))) {
    throw new Error('observed-at must be an ISO timestamp');
  }
  const minDistinctRuns =
    options.minDistinctRuns === undefined ? 2 : options.minDistinctRuns;
  validateThreshold(minDistinctRuns);

  const fingerprint = fingerprintCandidate(normalized);
  const observationDir = path.join(
    stateDir,
    'observations',
    fingerprint
  );
  fs.mkdirSync(observationDir, { recursive: true, mode: 0o700 });
  const observationPath = path.join(observationDir, options.runId + '.json');
  const observation = {
    version: 1,
    fingerprint: fingerprint,
    run_id: options.runId,
    observed_at: new Date(observedAt).toISOString(),
    candidate: normalized,
  };

  let recorded = true;
  try {
    fs.writeFileSync(
      observationPath,
      JSON.stringify(observation, null, 2) + '\n',
      { encoding: 'utf8', flag: 'wx', mode: 0o600 }
    );
  } catch (error) {
    if (error.code !== 'EEXIST') {
      throw error;
    }
    recorded = false;
  }

  const runIds = fs.readdirSync(observationDir).map(function(fileName) {
    const payload = JSON.parse(
      fs.readFileSync(path.join(observationDir, fileName), 'utf8')
    );
    validateRunId(payload.run_id);
    if (payload.fingerprint !== fingerprint) {
      throw new Error('observation fingerprint does not match its directory');
    }
    return payload.run_id;
  });
  const distinctRuns = new Set(runIds).size;

  return {
    fingerprint: fingerprint,
    distinctRuns: distinctRuns,
    qualified: distinctRuns >= minDistinctRuns,
    recorded: recorded,
    observationPath: observationPath,
  };
}

function markerForFingerprint(fingerprint) {
  if (!/^[a-f0-9]{64}$/.test(fingerprint)) {
    throw new Error('fingerprint must be a lowercase SHA-256 digest');
  }
  return '<!-- e2e-pipeline-improvement:v1:' + fingerprint + ' -->';
}

function buildProposal(options) {
  const normalized = validateCandidate(options?.candidate);
  const fingerprint = options?.fingerprint;
  const distinctRuns = options?.distinctRuns;
  markerForFingerprint(fingerprint);
  if (!Number.isInteger(distinctRuns) || distinctRuns < 2) {
    throw new Error('proposal requires at least two distinct runs');
  }

  return {
    title:
      'e2e-pipeline: ' + normalized.summary.replace(/[.!?]+$/, ''),
    body: [
      markerForFingerprint(fingerprint),
      '',
      '## Pipeline defect',
      '',
      normalized.summary,
      '',
      '- Stable code: `' + normalized.code + '`',
      '- Source skill: `' + normalized.source_skill + '`',
      '- Target: `' + normalized.target + '`',
      '- Recurrence: Observed in ' + distinctRuns + ' distinct runs.',
      '',
      '## Proposed change',
      '',
      normalized.proposed_change,
      '',
      '---',
      '*Promoted by e2e-pipeline after repeated, independently identified runs.*',
      '',
    ].join('\n'),
  };
}

module.exports = {
  buildProposal,
  fingerprintCandidate,
  markerForFingerprint,
  recordObservation,
  validateCandidate,
};
