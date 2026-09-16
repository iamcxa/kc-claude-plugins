# backlog gate — release-please-exclude-paths

FO-authored admission record. This boundary has no worker report by workflow design.

## Variant and profile

- `variant: kc-dev-flow-2`
- `profile:` unset, pending the Captain's selection. Recommended: **prod**.

The recommendation comes from `kc-dev-flow-2:dev` invoked in a fresh Claude process
(sonnet) against the installed plugin, citing prod's deciding sentence: "Deliver an
operated capability with explicit long-term ownership." `release-please-config.json`
governs the real release pipeline for ten published plugins and runs unattended on
every push to `main`.

FO had leaned `pilot` on the reading that fixing existing config adds no new ownership.
That reading is weaker: pilot's own escalation list names release/rollback ownership,
and this change lands inside that boundary rather than beside it.

## Proposed outcome

`release-please-config.json` stops leaving `kc-dev-flow` as the one package a path-less
commit can bump, and the excluded set covers the second workflow-state path where
measurement shows attribution actually reaches it.

## Scope

`release-please-config.json` only.

## Exclusions

No version or manifest edits. No marketplace changes. No new CI job. No change to any
plugin's source. No retirement of the `kc-dev-flow` plugin.

## Budget and stop condition

Stop if the fixture measurement shows a `docs/dev2` exclusion is unnecessary: land the
`kc-dev-flow` half alone and record the measurement rather than adding config nothing
needs.

## Evidence needed before ideation starts

1. The Captain's selected profile recorded on the task.
2. The approved outcome, scope and exclusions above, unchanged or amended by the Captain.
3. Confirmation that the five-stage route matches the selected profile — `prod` and
   `pilot` both do; `poc` would require the separate four-stage adaptation and a
   different workflow directory.
