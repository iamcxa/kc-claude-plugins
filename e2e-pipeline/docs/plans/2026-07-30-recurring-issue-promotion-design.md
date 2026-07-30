# Recurring Pipeline Issue Promotion Design

## Goal

Let an E2E pipeline run record a concrete defect in the pipeline itself and
promote the defect to a GitHub issue only after the same defect occurs in two
distinct runs. The default remains local proposal generation. Automatic filing
requires durable, repository-local authorization.

## Scope

The first version handles only `pipeline-defect` candidates:

- the defect happened during the current run;
- the cause points to a specific `e2e-pipeline/` file or contract;
- the defect caused real rework, a rerun, or an incorrect artifact;
- the proposed issue text is generic and contains no project URL, credential,
  selector, test data, or absolute user path.

Application bugs, ordinary test failures, model mistakes, one-off environment
failures, and project-specific lessons remain in the existing result and D2
knowledge-capture paths.

## Architecture

The agent writes one small candidate JSON file, then invokes
`bin/e2e-issue-promotion.js`. A pure module validates and fingerprints the
candidate, records one observation file per run, counts distinct run IDs, and
renders an issue proposal.

Observation state is stored below
`.claude/e2e/reports/issue-promotion/observations/`. Each observation has an
independent file, so concurrent runs do not contend on one JSON document. The
fingerprint is a SHA-256 digest of the contract version, candidate kind,
stable defect code, and target path.

At the second distinct run:

- `propose` mode writes a local Markdown proposal and performs no GitHub call;
- `auto` mode searches open and closed issues for the fingerprint marker;
- an open match suppresses duplicate creation;
- a closed match stays closed and suppresses resurrection;
- no match creates one labeled issue.

The hidden marker is:

```html
<!-- e2e-pipeline-improvement:v1:<sha256> -->
```

## Authorization

The default mode is `propose`. Command-line flags cannot elevate it to `auto`.
Automatic filing is allowed only when a checked-in or project-local config
explicitly contains:

```json
{
  "version": 1,
  "mode": "auto",
  "repo": "iamcxa/kc-claude-plugins",
  "min_distinct_runs": 2
}
```

This config is the operator's durable affirmative authorization. The repository
must be the plugin origin, `iamcxa/kc-claude-plugins`; other repositories fail
closed to proposal mode. Missing,
malformed, or unsupported config fails closed to proposal mode.

## GitHub Failure Semantics

Issue management is a post-run improvement path and never changes the E2E
verdict. Authentication, label, search, or create failures are reported as a
structured `filing_failed` result while preserving the proposal locally.
Invalid local input is a contract error and exits non-zero.

The label is `e2e-pipeline-improvement`. If label creation fails, filing is
retried without the label and the issue body starts with an explicit manual
label warning.

## Skill Integration

`e2e-test` runs the promotion check after normal results and knowledge capture.
It stays silent when no candidate qualifies. When a candidate exists, the
skill writes only the strict JSON contract and invokes the executable. The
executable, not prose, owns threshold counting, authorization, deduplication,
and remote mutation.

## Verification

- Pure tests cover validation, stable fingerprints, two-distinct-run
  thresholding, same-run retry deduplication, safe proposal rendering, and
  closed-issue suppression.
- CLI integration tests use an isolated fake `gh` executable to prove proposal
  mode makes zero remote calls and auto mode searches before creating.
- A skill contract test requires the post-run integration and disqualifying
  rules.
- The full plugin test and lint suites remain green.
