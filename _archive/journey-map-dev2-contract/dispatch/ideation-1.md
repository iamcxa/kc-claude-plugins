# ideation-1

Dispatched: from workflow checkout at 6d344bcb6ced154fb1aeb3b4e362676c80aec443 (kc-claude-plugins, detached; the workflow README there was the 2026-10-08 copy, not the 0.21.0 sync)
Model: sonnet
Recorded: 2026-10-13, after the fact by FO; the original dispatch files were under /tmp/spacedock-dispatch/

## Checklist

A design that names each schema's producer, version string and consumer pin (journey-map: story/release/question ids and drawn-commit provenance; dev2: task tuple, footprint records, ADR references), consistent with the Captain's accepted direction in the task and subspace-relay ADR 0046's one-version rule
Every new step in the loop (release-to-task, gate footprint, ADR reference, archive fold, out-of-task ruling) carries its one-command write, its gate line (done or not-needed with reason), and its reconcile-script count; a step with none of the three is cut
Acceptance criteria with reproducible evidence clauses, including one conformance run against a slug-id and an id workflow and a reconcile-script baseline run on qnow's map, plus the unresolved decisions listed for the Captain

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.20.0

Profile: pilot (Captain, 2026-10-13). Variant: kc-dev-flow-2.

Design against the task's "Direction the Captain accepted, 2026-10-13" section; do not reopen it. Treat relayed Captain words in the task as relayed, not as rulings.

Read-only references (do not edit other repositories; read at origin refs):
- kc-journey-map at this repository's origin/main (lib/progress.mjs, skills/kc-journey-progress/SKILL.md, skills/kc-journey-map/references/canvas.md, docs/adr/0008-*).
- kc-dev-flow-2 references/sd/workflow.md "Release review" section at origin/main.
- subspace-relay ADR 0046: `git -C /Users/kent/conductor/repos/subspace-relay show origin/main:docs/adr/0046-relays-http-contract-has-one-version.md`.
- qnow journey file: `git -C /Users/kent/conductor/repos/qnow show origin/next:docs/journey/qnow.yaml` (no customer or person identifiers in the design).

Out of scope: hosting the canvas (task journey-canvas-hosted-poc), and the release walk-through (task release-acceptance) except where the two contracts touch.
