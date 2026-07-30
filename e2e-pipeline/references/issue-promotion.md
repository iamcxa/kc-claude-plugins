# Recurring Pipeline Issue Promotion

Use this post-run path only for a defect in `e2e-pipeline` itself. The common,
correct output is silence.

## Qualification

A candidate qualifies only when all of these are true:

1. It happened in this run and has concrete execution evidence.
2. The cause points to a specific `e2e-pipeline/` target file or contract.
3. It cost a rerun, manual workaround, incorrect artifact, or other real rework.
4. The same defect could affect an unrelated project.

Do not promote application bugs, ordinary test failures, model mistakes,
project-specific setup, or one-off environment failures. Do not include URLs,
credentials, selectors, test data, absolute user paths, or raw logs.

## Candidate Contract

Write a JSON file with exactly these fields:

```json
{
  "version": 1,
  "kind": "pipeline-defect",
  "code": "stable-lowercase-defect-code",
  "source_skill": "e2e-test",
  "target": "e2e-pipeline/bin/e2e-browser-runtime.js",
  "summary": "Generic one-line symptom.",
  "proposed_change": "Exact generic change that would prevent recurrence."
}
```

The `code` and `target` define identity. Keep them stable when the same root
cause recurs; wording changes do not create a new fingerprint.

## Execution

The executable records one observation per run. A retry with the same run ID
does not increase the count. Promotion requires two distinct run IDs by
default.

The default mode is `propose`: the executable writes a local Markdown proposal
and never calls GitHub. `auto` is accepted only from an explicit
`.claude/e2e/issue-promotion.json` configuration naming the plugin origin repo,
`iamcxa/kc-claude-plugins`. Other repositories fail closed to proposal mode.

Before filing, the executable searches open and closed issues for its hidden
fingerprint marker. An open match is reused. A closed match is not reopened.
GitHub failure preserves the local proposal and never changes the E2E verdict.

Example authorization:

```json
{
  "version": 1,
  "mode": "auto",
  "repo": "iamcxa/kc-claude-plugins",
  "min_distinct_runs": 2
}
```
