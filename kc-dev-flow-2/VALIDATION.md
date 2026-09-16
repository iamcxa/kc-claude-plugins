# Validation scope

This is an optional experimental package, not a replacement certification for
kc-dev-flow. The packaged core comes from source commit
179b54eea2694806e9c268affb67c573dfdda632 (30 files before packaging). That source
added the thin `dev` entry and conditional document/check guidance after the
historical trials below. Those trials did not execute this final package.

## Historical bounded evidence

| Case | Observed result | Limit |
| --- | --- | --- |
| Claude Pilot, source f28873465da36159a30dd0e129423a665df295ad | Implementation, fresh independent validation, a same-candidate removal control, human approval, and local archive closure | No remote merge, pull request, deployment, or production delivery; completion messages required recipient correction |
| Claude existing-code Pilot, same source | Reused an existing CSV formatter, retained a manually used archive check, recovered from a real Git lock refusal, and passed implementation/independent checks including column-order and output-encoding controls | Design needed human correction; nonblocking finding disposition was incomplete and the validation gate remained unapproved |
| Codex profile trial, source c600daed70c54babd85dfa9f67b115427384ae71 | POC implementation, invalid-profile refusal before dispatch, and Production validation that rejected acceptance despite five passing local test groups because exercised recovery evidence was missing | Stage-scoped cases needed command corrections and an authorized replacement worker; no accepted gate or delivery |

A separate Claude correction replay on the latter source was **partial**:
record-only disposition was exercised and an actual defect with stale evidence
was held, but the design diagram still omitted a rejection branch and two cases
retried after preparation failed. This is not a complete gate-lifecycle pass.

An earlier local Codex test package, version `0.0.0-poc.c600daed`, installed and
exposed six skills. Native reads verified the three stage skills, version and
source bytes. It predates the seventh `dev` skill, so it is not evidence for
that entry, the final package's loading, or remote marketplace distribution.
It is not a published release.

The three trials use different tasks and source snapshots. Their results cannot
be combined into a same-version, full-lifecycle, two-host acceptance claim.
Timing and list-price telemetry do not establish lower cost or a size reduction.

## Current checks and exclusions

A model-free native Codex check installed this local candidate through the
repository marketplace, matched all 33 package files to the candidate, and found
all seven enabled skills through the host's `skills/list` interface, including
`dev`. A pre-install control found no skills for this plugin. Removal restored
the prior configuration and removed the temporary cache. This establishes local
installation and discovery, not model invocation, shorthand resolution, reference
following, worker inheritance, or remote publication.

Candidate checks passed: routing lint, 15 mutation tests, repository skill
frontmatter, the native Codex manifest validator, and six model-free Spacedock
stage/host dispatch handoffs with refusal controls (CLI 0.27.2). Claude marketplace
schema and installation checks passed in a temporary home; no model smoke test
ran. Release configuration and version parity passed using a temporary validation
index to include the new files without staging the review candidate.
Public-content checks found no blocking or secret-pattern hits; a heuristic email
warning refers to the synthetic fixture author `fixture@example.invalid`.

Transport tests exercise synthetic stage state and emitted artifacts, not models,
independent review, gate presentation, or successful delivery. Maintenance lint
requires the full source repository's frontmatter checker.

Learning automation is unimplemented. The baseline skipped-stage-pin bug is not
fixed; historical stage-entry content sealing is omitted. Direct POC eligibility,
Production recovery exceptions, retained-role execution across hosts, automated
gate correctness, and complete Claude/Codex lifecycle parity remain unproven.
Use explicit workflow paths and check the live worker roster after resuming an
orchestrator; a resumed orchestrator does not establish that an old worker exists.
These limits remain until separately scoped evidence establishes otherwise.
