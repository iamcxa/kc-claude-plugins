A direct proof of concept (POC) changed to validation before gate preparation, leaving the selected artifact uncommitted. Generic review also selected a nonexistent validation report or rejected a POC with no declared acceptance criteria.

## Changes

- Commit the direct implementation-to-validation transition through Spacedock before native gate binding; stop when the setter or commit fails.
- Add the profile-owned, read-only `review` command. It selects the latest implementation report for direct proof or validation report for fresh proof, permits explicitly absent acceptance criteria, and refuses malformed or uncovered criteria and unfinished or unevidenced obligations. Negative `stop` and `change` outcomes remain valid evidence.
- Document the installed helper path and review/prepare sequence. Exactly three files change: `poc-close-guard.py`, its existing test, and `skills/continue-dev-flow/SKILL.md` under `kc-dev-flow`.

## Validation

The native close-guard regressions passed with real Spacedock 0.27.2, the complete dev-flow contract passed with Python 3.12.0, and `git diff --check` passed. The new regression first failed against the original guard at the uncommitted-artifact boundary. All three committed file fingerprints still match the tested candidate; no unchanged suite was repeated.

## Delivery boundary

This is a separate maintenance repair. The [archived POC outcome](https://github.com/iamcxa/kc-claude-plugins/blob/b1e54319daa3d64ec82045cce69fb3b32f58b108/_archive/skills-mcp-dev-flow-feedback-poc/index.md) records `change`; this patch does not demonstrate successful self-improvement experimentation.

Integrate after PR #390. Their skill edits are disjoint, but the combined static input reaches 40,065 bytes against the existing 40,000-byte ceiling. Keep this Draft until a bounded integration edit removes at least 65 bytes without weakening either behavior and the existing affected contract checks pass on that combined candidate. The individual candidate's passing evidence remains valid for its unchanged bytes.

Candidate: 1eae2f5a5467b4600783eaedc671cf5cd57d1969
