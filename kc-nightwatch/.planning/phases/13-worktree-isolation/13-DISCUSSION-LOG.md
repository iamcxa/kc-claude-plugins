# Phase 13: Worktree Isolation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-03-24
**Phase:** 13-worktree-isolation
**Areas discussed:** Worktree storage location, Default branch detection, Error handling

---

## Worktree Storage Location

| Option | Description | Selected |
|--------|-------------|----------|
| App data dir (~/.claude/nightwatch/worktrees/) | Separate from target, matches existing memory/ layout, single safehouse entry | |
| OS temp dir (/tmp) | OS auto-cleanup on reboot, standard practice, but volatile and macOS path mismatch | |
| Under runs dir (runs/{id}/worktree/) | Everything in one place, existing cleanup handles it, but bloats runs/ and stale git metadata | |
| Near target repo ({target_parent}/.nw-worktrees/) | Same filesystem, easy to find, but creates dirs near user's projects | |

**User's choice:** Near target repo — but refined to `{target}/.worktrees/nw-{run_id}/` (inside target, generic `.worktrees/` path with `nw-` prefix)
**Notes:** User specifically requested `.worktrees/` as a composable generic path (not nightwatch-specific) inside the target directory. The `nw-` prefix namespaces nightwatch entries. Other tools can use the same `.worktrees/` dir with different prefixes.

---

## Default Branch Detection

| Option | Description | Selected |
|--------|-------------|----------|
| Config + auto fallback | Optional `default_branch` field, auto-detect chain: origin/HEAD → main → master → error | ✓ |
| Always auto-detect | No config field, always resolve from git refs, no escape hatch for unusual setups | |
| Always require config | `default_branch` required in target config, explicit but adds friction | |

**User's choice:** Config + auto fallback (recommended)
**Notes:** No additional notes — accepted as presented.

---

## Error Handling

| Option | Description | Selected |
|--------|-------------|----------|
| Prune + retry, then fail | git worktree prune → retry once → fail run if still broken, no in-place fallback | ✓ |
| Fail immediately | No retry, direct fail — too strict for stale lock scenario | |
| Fallback to in-place | Run in target dir on failure — defeats Phase 13 purpose, silent degradation | |

**User's choice:** Prune + retry, then fail (recommended)
**Notes:** No additional notes — accepted as presented.

---

## Claude's Discretion

- `worktree-manager.ts` internal structure
- How to pass worktree path through executor and policy
- Detached HEAD vs temporary branch approach
- Whether to `git fetch` before worktree creation

## Deferred Ideas

None — discussion stayed within phase scope.
