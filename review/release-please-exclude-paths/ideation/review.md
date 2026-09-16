# ideation gate — release-please-exclude-paths

FO review of the ideation stage report. Recommendation: **approve, with one
acceptance-evidence correction carried into implementation.**

## FO independent verification

The worker's central finding was re-run by FO independently, not accepted on
report. Installed `release-please@17.3.0` from this repository's own pinned
fixture lockfile (`scripts/fixtures/release-please-runtime/package-lock.json`,
tracked since PR #134) into a throwaway directory, then drove `CommitSplit`
(`includeEmpty: true`) and `CommitExclude` over four commit shapes against five
`exclude-paths` values.

Result matches the worker exactly:

| commit shape | bucketed to |
| --- | --- |
| empty, no `exclude-paths` key on `kc-dev-flow` | every configured package |
| empty, key present with any value | every package except `kc-dev-flow` |
| touches only `docs/dev` | no package |
| touches only `docs/dev2` | no package |
| touches `kc-dev-flow/` | `kc-dev-flow` only |

`["docs/dev"]`, `["docs/dev2"]`, `["unrelated-string"]` and `[]` produced an
identical drop. The guard is the presence of the key, not its content.

## Findings

1. **The Stop-condition narrowing is correct and already authorized.** The
   `backlog` gate approved the Stop condition verbatim, and the measurement is
   the evidence it names. Implementation edits `kc-dev-flow`'s entry only; no
   package gains a `docs/dev2` entry.

2. **AC-2 is not yet satisfied — the stage report overreaches.** AC-2's own
   verification clause names "the pinned release-please fixture inside
   `scripts/version-parity-check.sh` run against a commit that touches only a
   workflow-state path, with its resolved package list captured in the stage
   report". Both the worker's probe and this FO re-run drove the two library
   classes directly. That is a narrower claim than the fixture harness running
   end-to-end on this repository's actual config. The stage report's sentence
   "AC-2 is satisfied by the recorded measurement above" is withdrawn as a
   claim; AC-2 carries into implementation and is satisfied there by the
   harness run, not by a class-level probe.

3. **Routine, no decision needed:** AC-1's phrase "non-empty `exclude-paths`" is
   now a documentation choice rather than a functional requirement, since `[]`
   behaves identically. Matching the siblings' `["docs/dev"]` value keeps the
   config self-describing. No AC text change proposed.

4. **No preview applies.** This change has no interface surface.

## Evidence limit to preserve

Every measurement in this stage is library-level: release-please's own classes,
at the pinned version, driven directly. Nothing here establishes what a real
release-please run does against this repository's committed config. That is
implementation's obligation under AC-2.
