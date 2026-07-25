---
id: 1dztkbg5b487th0pk31czm6q
title: One machine-readable contract for mapping and flow YAML
status: backlog
source: captain note — e2e-pipeline agent-native audit, 2026-07-25 (session analysis + agy cross-model review)
started:
completed:
verdict:
worktree:
issue:
pr:
design:
---

## Problem

There is no machine-readable schema for either artifact the pipeline produces. No
`*.schema.json`, no ajv/zod/joi anywhere — `e2e-pipeline/package.json` declares only
`commander`, `js-yaml`, `xmlbuilder2`. All validation is hand-rolled imperative JS split
across `compiler/parser.js` (`validateFlow`, `validateMapping`, `validateFlowSteps`, …)
and semantic checks scattered through `compiler/resolver.js`. Because the contract is not
an artifact, it is enforced by restatement: the banned-selector rules alone appear in 13
markdown files (CLAUDE.md, four agent definitions, references/common-patterns.md, three
skills, docs/). Every restatement is drift surface, and the v1-vs-v2 format confusion that
recurs in three separate "Common Mistakes" tables is the same class.

The sharpest instance is `agents/e2e-flow-writer.md:210` "Step 4 — Validation Pass": a
prose instruction telling the LLM to check its own generated flow against the mapping. The
agent has no Bash tool by design, so it cannot run any validator — it self-certifies. Under
the workflow's own proof policy that is a self-issued stamp, not a check that can fail.

Shape to decide at ideation: publish JSON Schema for mapping v2 and flow v2, collapse
parser/resolver validation onto one shared validator module, fold the banned-token classes
from `scripts/lint-mapping.sh` in as pattern constraints, and expose `--validate`. Then
replace the flow-writer's prose self-check with the orchestrator running the real validator
against the artifact the writer produced — an independent check on a self-written artifact,
which is the distinction the proof policy actually turns on.

## Notes for ideation

- Sequencing argument from the cross-model reviewer, adopted: this must land before
  [[e2e-json-diagnostics]], because the structured error codes should be derived from the
  schema's validation vocabulary rather than invented ad hoc and then migrated.
- Depends on [[e2e-typed-operands]] settling whether operands stay in the prose `action:`
  string or move to typed fields — the schema shape differs materially between the two.
- Deleting the restated rules from 13 files is part of the deliverable, not follow-up. A
  schema that coexists with the prose copies has added a source of truth rather than
  replaced one.
