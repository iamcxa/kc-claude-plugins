# implementation-4

Dispatched: e2524e93025dd0d5d9217b4d722c2b169d01fda6 (workflow checkout, kc-dev-flow-2 0.21.0 README); candidate #633 a7fa7f1b
Model: sonnet

Follow-up message to the live implementation worker: FO fix authorization after its phase-1 reproduction confirmed the Codex round-2 P2.

## Checklist

Same checklist as implementation-3.

## Scope notes

Fix 1-3 as proposed: MAIN_LINE appended by default in scripts/replay_dispatch.py build(), with `--no-completion-line` for AC-4's control arm; tests (a) default includes the line and matches dispatch_records.py's pattern, (b) the flag omits it, (c) present once with --scope, with mutations; one sentence in skills/maintain-flow/SKILL.md (budget raised only additively, stated). Merge 7679ab7a first (never rebase). Roborev gate (base 7679ab7a), push (no force), CI green, stage report committed, completion to `main`.
