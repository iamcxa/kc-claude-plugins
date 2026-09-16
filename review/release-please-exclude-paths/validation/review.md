# validation gate — release-please-exclude-paths

Candidate: `b6774358` on `spacedock-ensign/release-please-exclude-paths`.
One line added to `release-please-config.json`: `"exclude-paths": ["docs/dev"]` on the
`kc-dev-flow` package entry.

FO recommendation: **approve, with AC-2's verification clause amended to the evidence
that exists.** The validator's verdict is PASS; the one open finding is a defect in a
criterion FO wrote, not in the candidate.

## FO independent verification

Re-checked the validator's load-bearing claim rather than accepting the report.

- No file under `scripts/` or `.github/` references `CommitSplit`, `CommitExclude`,
  `commit-split` or `commit-exclude`. Nothing in this repository resolves a commit's
  package list.
- `scripts/version-parity-check.sh` never invokes node, npm or release-please. Its own
  header states the design constraint: "Cheap by design — python3 only". It delegates
  to `scripts/release-please-config-check.sh`, also static validation.
- The pinned fixture at `scripts/fixtures/release-please-runtime` has exactly one
  consumer, `scripts/release-metadata.test.sh`, and that script is wired into
  `marketplace-parity.yml`'s "Validate release config, first-release contract, and
  version parity" step. It resolves a first-release tag string, not a commit's
  package routing.
- The candidate worktree is clean and HEAD is unchanged at `b6774358`. No probe
  artifact was left behind.

## Finding: AC-2 names an instrument that does not exist

**Owner: FO.** At backlog admission FO wrote AC-2's verification clause as "the pinned
release-please fixture inside `scripts/version-parity-check.sh` run against a commit
that touches only a workflow-state path". That conflated two different things: a
fixture harness that does exist and does run in CI, and a commit-routing instrument
that has never existed here. Three stages then produced the same class-level
reproduction because it is the only evidence obtainable, and FO already withdrew the
ideation report's claim that AC-2 was satisfied by it.

Classification under Review-finding disposition: **Needs decision.** An
acceptance-criteria change requires the Captain. It is not Material against the
candidate — the candidate delivers the approved outcome — and it cannot use the
record-only lane because it changes a criterion.

Three routes:

1. **Amend AC-2's clause to the evidence actually produced** — release-please 17.3.0
   from this repository's own pinned lockfile, its own `CommitSplit`/`CommitExclude`,
   constructed as `manifest.js` constructs them, run against the candidate config with
   a `HEAD~1` control. That control is the decisive part: before the fix an empty
   commit resolved to `[kc-dev-flow]`; after it, to no package. Independently
   reproduced at ideation, implementation and validation, and separately by FO.
2. **Keep AC-2 as written** — requires building a commit-routing probe and wiring it
   into CI, which the entity's own approved Non-goals forbid ("no new CI job").
3. **Drop AC-2** — loses the measurement that justified adding nothing for `docs/dev2`.

The Captain ruled route 1 on 2026-09-16. AC-2's verification clause on the task is
amended accordingly, with the original wording and the reason preserved beside it. The
amendment names the pre-change control as required evidence, which the original clause
did not. This gate was withdrawn before that edit and re-prepared afterwards.

With AC-2 amended, both criteria are met on `b6774358`: AC-1 by the parity check and the
config read, AC-2 by the resolved package lists for four commit shapes against the
candidate and against the pre-change revision.

## Goal sufficiency

The approved outcome had two halves. `kc-dev-flow` stops being the one package a
path-less commit can bump: delivered, with a before/after control. The excluded set
covers the second workflow-state path where measurement shows attribution reaches it:
measurement shows it never reaches, so nothing is owed. Sufficient.

## Minimal necessity

One key, one package, one file, matching every sibling's existing value byte for byte.
Nothing smaller closes the empty-commit route, and nothing larger was added — no
`docs/dev2` entry, no script, no CI job, no version or manifest edit. The bite is on
record: one empty commit bumped seven plugins with the same changelog line on
2026-09-03. The consumer is the release pipeline and everyone publishing from it.

## Evidence limits to carry forward

All routing evidence is library-level: release-please's own classes at the pinned
version, driven directly. Nothing here observes a real release-please run against this
repository's committed config on GitHub. The first empty commit merged after this lands
would be the only end-to-end observation, and this repository's own rules forbid making
one deliberately.

## Delivery

The workflow's Delivery authority holds: approving this gate is not permission to push
or create a PR. The exact candidate and PR body are presented to the Captain
separately for that authorization.
