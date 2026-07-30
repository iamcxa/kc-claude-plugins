#!/usr/bin/env node
'use strict';

const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const {
  buildProposal,
  markerForFingerprint,
  recordObservation,
  validateCandidate,
} = require('../compiler/issue-promotion.js');

const LABEL = 'e2e-pipeline-improvement';
const ORIGIN_REPO = 'iamcxa/kc-claude-plugins';

function parseArgs(argv) {
  const options = {
    candidatePath: '',
    configPath: '',
    runId: '',
    stateDir: '',
  };
  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];
    if (value === '--candidate') {
      options.candidatePath = argv[++index] || '';
    } else if (value === '--config') {
      options.configPath = argv[++index] || '';
    } else if (value === '--run-id') {
      options.runId = argv[++index] || '';
    } else if (value === '--state-dir') {
      options.stateDir = argv[++index] || '';
    } else if (value === '--help' || value === '-h') {
      process.stdout.write(
        [
          'Usage: e2e-issue-promotion.js --candidate <path> --run-id <id> --state-dir <path> [--config <path>]',
          '',
          'Automatic GitHub filing is available only through an explicit mode:auto config.',
          '',
        ].join('\n')
      );
      process.exit(0);
    } else {
      throw new Error('unknown argument: ' + value);
    }
  }
  if (!options.candidatePath || !options.runId || !options.stateDir) {
    throw new Error('--candidate, --run-id, and --state-dir are required');
  }
  if (
    !path.isAbsolute(options.candidatePath) ||
    !path.isAbsolute(options.stateDir) ||
    (options.configPath && !path.isAbsolute(options.configPath))
  ) {
    throw new Error('candidate, config, and state paths must be absolute');
  }
  return options;
}

function readJson(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}

function defaultConfig() {
  return {
    version: 1,
    mode: 'propose',
    repo: '',
    min_distinct_runs: 2,
  };
}

function loadConfig(configPath) {
  if (!configPath) {
    return { config: defaultConfig(), warning: '' };
  }

  try {
    const value = readJson(configPath);
    const allowed = new Set([
      'version',
      'mode',
      'repo',
      'min_distinct_runs',
    ]);
    if (
      !value ||
      typeof value !== 'object' ||
      Array.isArray(value) ||
      Object.keys(value).some(function(key) {
        return !allowed.has(key);
      }) ||
      value.version !== 1 ||
      !['propose', 'auto'].includes(value.mode) ||
      !Number.isInteger(value.min_distinct_runs) ||
      value.min_distinct_runs < 2 ||
      value.min_distinct_runs > 100 ||
      (value.mode === 'auto' &&
        value.repo !== ORIGIN_REPO)
    ) {
      throw new Error('invalid version 1 config');
    }
    return {
      config: {
        version: 1,
        mode: value.mode,
        repo: typeof value.repo === 'string' ? value.repo : '',
        min_distinct_runs: value.min_distinct_runs,
      },
      warning: '',
    };
  } catch {
    return {
      config: defaultConfig(),
      warning:
        'Invalid issue-promotion config; falling back to propose mode.',
    };
  }
}

function writeProposal(stateDir, fingerprint, proposal) {
  const proposalDir = path.join(stateDir, 'proposals');
  fs.mkdirSync(proposalDir, { recursive: true, mode: 0o700 });
  const proposalPath = path.join(proposalDir, fingerprint + '.md');
  fs.writeFileSync(proposalPath, proposal.body, {
    encoding: 'utf8',
    mode: 0o600,
  });
  return proposalPath;
}

function ghRun(args) {
  const result = spawnSync('gh', args, { encoding: 'utf8' });
  return {
    ok: result.status === 0,
    stdout: (result.stdout || '').trim(),
  };
}

function findExistingIssue(repo, fingerprint) {
  const result = ghRun([
    'issue',
    'list',
    '--repo',
    repo,
    '--state',
    'all',
    '--search',
    fingerprint + ' in:body',
    '--limit',
    '100',
    '--json',
    'number,state,url,body',
  ]);
  if (!result.ok) {
    throw new Error('GitHub issue search failed');
  }
  let issues;
  try {
    issues = JSON.parse(result.stdout || '[]');
  } catch {
    throw new Error('GitHub issue search returned invalid JSON');
  }
  if (!Array.isArray(issues)) {
    throw new Error('GitHub issue search returned an invalid result');
  }
  const marker = markerForFingerprint(fingerprint);
  const matches = issues.filter(function(issue) {
    return typeof issue.body === 'string' && issue.body.includes(marker);
  });
  return (
    matches.find(function(issue) {
      return String(issue.state).toUpperCase() === 'OPEN';
    }) ||
    matches[0] ||
    null
  );
}

function ensureLabel(repo) {
  return ghRun([
    'label',
    'create',
    LABEL,
    '--repo',
    repo,
    '--color',
    '5319e7',
    '--description',
    'Recurring defect in the e2e-pipeline itself',
    '--force',
  ]).ok;
}

function createIssue(repo, proposal, proposalPath, labelReady) {
  let bodyPath = proposalPath;
  if (!labelReady) {
    bodyPath = proposalPath + '.unlabeled';
    fs.writeFileSync(
      bodyPath,
      '[LABEL CREATION FAILED — add `' + LABEL + '` manually]\n\n' +
        proposal.body,
      { encoding: 'utf8', mode: 0o600 }
    );
  }

  const args = [
    'issue',
    'create',
    '--repo',
    repo,
    '--title',
    proposal.title,
    '--body-file',
    bodyPath,
  ];
  if (labelReady) {
    args.push('--label', LABEL);
  }
  const result = ghRun(args);
  if (!labelReady) {
    fs.unlinkSync(bodyPath);
  }
  if (!result.ok || !/^https:\/\/github\.com\/[^/]+\/[^/]+\/issues\/\d+$/.test(result.stdout)) {
    throw new Error('GitHub issue creation failed');
  }
  return result.stdout;
}

function output(payload) {
  process.stdout.write(JSON.stringify(payload) + '\n');
}

function main() {
  const options = parseArgs(process.argv.slice(2));
  const candidate = validateCandidate(readJson(options.candidatePath));
  const loaded = loadConfig(options.configPath);
  const observation = recordObservation({
    candidate: candidate,
    runId: options.runId,
    stateDir: options.stateDir,
    minDistinctRuns: loaded.config.min_distinct_runs,
  });
  const base = {
    fingerprint: observation.fingerprint,
    distinct_runs: observation.distinctRuns,
    qualified: observation.qualified,
  };
  if (loaded.warning) {
    base.config_warning = loaded.warning;
  }
  if (!observation.recorded) {
    output(Object.assign(base, { status: 'duplicate_run' }));
    return;
  }
  if (!observation.qualified) {
    output(Object.assign(base, { status: 'recorded' }));
    return;
  }

  const proposal = buildProposal({
    candidate: candidate,
    fingerprint: observation.fingerprint,
    distinctRuns: observation.distinctRuns,
  });
  const proposalPath = writeProposal(
    options.stateDir,
    observation.fingerprint,
    proposal
  );
  base.proposal_path = proposalPath;
  if (loaded.config.mode !== 'auto') {
    output(Object.assign(base, { status: 'proposal' }));
    return;
  }

  try {
    const existing = findExistingIssue(
      loaded.config.repo,
      observation.fingerprint
    );
    if (existing) {
      output(
        Object.assign(base, {
          status:
            String(existing.state).toUpperCase() === 'CLOSED'
              ? 'suppressed_closed'
              : 'deduplicated',
          issue_number: existing.number,
          issue_url: existing.url,
        })
      );
      return;
    }

    const labelReady = ensureLabel(loaded.config.repo);
    const issueUrl = createIssue(
      loaded.config.repo,
      proposal,
      proposalPath,
      labelReady
    );
    output(
      Object.assign(base, {
        status: 'filed',
        issue_url: issueUrl,
        label_applied: labelReady,
      })
    );
  } catch (error) {
    output(
      Object.assign(base, {
        status: 'filing_failed',
        error: error.message,
      })
    );
  }
}

try {
  main();
} catch (error) {
  process.stderr.write('e2e-issue-promotion: ' + error.message + '\n');
  process.exit(1);
}
