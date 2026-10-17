# implementation-1

Dispatched: 6ea3a4724515b974c34beb16bc3382683b6d45b9 (POC workflow checkout, kc-dev-flow-2 0.23.0 README)
Model: sonnet

## Checklist

Upstream check first, written into the task file before any run: what Spacedock's first-officer contract loads at boot (whole workflow README or not), what `spacedock dispatch show-stage-def` and the stage `context-sections:` frontmatter deliver per stage, what kc-dev-flow-2's `_mods` startup and idle hooks load, and what the 0.14.0 split of workflow.md by reader already moved; say what each gives and whether the index arm needs anything new
Pre-registration committed to the state branch before any run: the five probes (each a fixed FO situation with one checkable right action, drawn from the rule classes the observer reports most), the two arms (A: the whole README of docs/dev2 at origin/main; B: an index README plus per-moment files, built in a scratch copy only), the scoring rule per probe, and the Captain's bar verbatim from the backlog gate
Thirty runs on Sonnet (five probes, three per arm), each recorded with the arm, the probe, followed or not with the line of output that decides it, words loaded at startup and at the probe's moment, tokens, seconds and cost
Result against the bar, pass or fail, without moving the bar; what the index arm's file layout was; what the POC does not show
## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.24.0

Profile: poc. The Captain's words, scope and non-goals are in the task file. Bar (Captain, 2026-10-17, 「按你建議的 poc 標準可以」 to the backlog gate question): five probes, three runs per arm on Sonnet (30 runs); pass when the index arm follows the probed rules at least as often as the whole-README arm in total, is worse on no probe by more than one run, and loads at most a quarter of the whole-README words at startup.

Change no package file (kc-dev-flow-2/**) and no adopter README; build arm B under the task folder or /tmp only. Check the existing replay tooling first (kc-dev-flow-2/scripts/replay_dispatch.py and maintain-flow's behaviour replay) before writing a runner. Deliverable: the pre-registration, run records and result in the task folder on the state branch; open no PR. Commit with `spacedock state commit readme-index-attention-poc --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-poc-route/docs/dev2-poc`. Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not comment on any PR or issue.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).