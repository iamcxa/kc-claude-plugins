# 0087. Public state writes carry no personal or private identifiers, and a per-checkout git guard refuses them

Date: 2026-11-14

## Status

Accepted

## Context

The public state-branch audit of 2026-11-14 found home paths in generated
dispatch records and sealed evidence, and private names in authored text.
ADR 0070 owns the record writer and ADR 0079 owns evidence sealing.
ADR 0003 rejects a plugin-wide secret-read hook because its trigger applies
across projects, its patterns depend on the adopter, and its host is Claude-only.
An explicitly installed Git hook on a state checkout has different boundaries;
ADR 0003 remains in force for secret reads.

## Decision

**Words:** 「先做甲止血。要不要換新分支，等我看過外洩清單再決定。」
and 「我在想的是在這個新的綁定一個hook，裡面過濾掉關鍵字，出現就不準推」
— Captain, chat with the reform session, 2026-11-14; relayed in the task's Scope.

**Words, delegated design approval:** 「改革工作階段（Paseo 代理 26215d96，就是開你出來的那一個）可以替我給你工作範圍。它給的範圍內，進場、設計、預算、結案這些關卡你不必停下來等我，記為「依艦長授權」，一路做到它指定的終點。」
— Captain, chat with the second dev2 First Officer, 2026-11-14; quoted by that
officer in this task's backlog and ideation gate resolutions, both attempt 1.
The ideation resolution approves this design under that grant and leaves the
live installation's initial refusing classes and commit-metadata email to the
Captain at the merge question.

**Options considered:**
- Rewrite new generated records and changed text evidence, with an explicit
  Git guard installed per state worktree (chosen).
- Refuse every class immediately on the live checkout: deferred to the Captain;
  the ideation replay showed home-path writes still in flight.
- Rewrite public history or start another state branch: outside this task.
- Ship a plugin-wide hook: rejected for ADR 0003's scope and host reasons.

**Recommended:** the chosen writer change and opt-in guard; ship with every
class at warn and install nothing during release. FO proposes the live modes
separately after the two sessions receive the compatible package.

**Protects:**
- `kc-dev-flow-2/scripts/dispatch_stage.py` — `record_text`, home rewrite only in the saved record
- `kc-dev-flow-2/scripts/dispatch_records.py` — `PARTS` and `ROOT`, accepting absolute and home-relative roots
- `kc-dev-flow-2/scripts/scratch.py` — `evidence`, rewrite before hashing/compression while keeping matching old digests
- `kc-dev-flow-2/scripts/state_guard.py` — `install`, per-checkout hooks and an external identifier list

Records write the home directory as `~`; runtime scope notes retain real paths.
Role prompts are rendered from the original inputs after the sanitized record
is committed.
New or changed UTF-8 evidence without NUL bytes is rewritten before sealing,
including supplied gzip text. Evidence matching an existing digest is preserved.
Binary evidence is left to the guard, which scans its bytes and decompresses gzip.

Installation uses a linked state worktree's own Git directory and
`git config --worktree core.hooksPath`; enabling `extensions.worktreeConfig`
is the clone owner's separate decision. The explicit `--shared` alternative
chains shared hooks and exits on branches outside `spacedock-state/*`.
The private-name list stays outside Git repositories. Each class warns or refuses
by its installed mode. Refusals identify the file, class and pushed commit without
printing matched text; push checks examine each commit, including transient lines.

## Consequences

Existing records and matching evidence remain valid; runtime prompts keep usable
paths. Rewritten evidence stays readable, but a retained patch may no longer apply
verbatim. Missing, stale or partial protection is visible at dispatch without
blocking adopters who never install it. No push is refused until installation,
and warn-mode classes can still reach the remote. Gate summaries are stored
verbatim by Spacedock (inferred from stored bytes, not traced in its source),
and commit-metadata email is unchanged. Those limits and the live install decision
remain with the Captain; this decision does not authorize installation or history
rewriting on an existing clone.
