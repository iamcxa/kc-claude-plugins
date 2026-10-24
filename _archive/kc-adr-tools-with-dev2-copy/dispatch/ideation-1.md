# ideation-1

Dispatched: c27e76590c1d2dc910e7fa2d332242a7534df0b0 (workflow checkout, kc-dev-flow-2 0.27.0 README); batch 5 addition
Model: sonnet

## Checklist

Design dev2's side of the ADR-tool copy per Captain Amendments 1 and 2: first run the two-host install test of a copied kc-adr directory (a real copied directory inside the kc-dev-flow-2 plugin, not a link) on Claude Code and Codex with isolated configs, and report what installs and resolves; then design the sync script that copies kc-adr/references/adr-template.md and kc-adr/scripts/adr_lint.py (with the #712 Protects label, writing.md steps 4 to 6 reference and the two new checks) to kc-dev-flow-2/references/adr-template.md and kc-dev-flow-2/scripts/adr_lint.py, the byte compare placed in a required check (verify whether version-parity in marketplace-parity.yml runs on every PR) with a failure message naming kc-adr as the place to edit, CI on kc-adr/ paths, and whether kc-adr/scripts/test_adr_lint.py runs in CI; state how the next kc-adr linter change (the peer task adr-protected-path-guard) reaches dev2; read intake/kc-adr-fo-interface-2026-10-23.md
A `### Batch overlap` section naming each file the design would change and each other batch task (new-work-starts-from-a-story-map, codex-reader-reads-receipt-marker, merge-ask-holds-missing-clauses, fo-write-checks-parse-top-level, idle-names-failing-seeds, agent-reads-governing-adr) and live task of other sessions (kc-decision-log-p1, kc-decision-log-cli, kc-decision-log-handoff-trial, pr-review-lite-value-pilot, release-acceptance, journey-canvas-hosted-poc, journey-server-host-pilot (driven by other sessions; read only)) that changes the same file or check, so FO can order implementation
The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0

Profile: pilot. The Captain's words and the evidence are in the task file. This task is one of batch 5 addition; read the other task files only as they stand, and do not edit them. Design against the current package source: kc-dev-flow-2/ in iamcxa/kc-claude-plugins at origin/main, released as 0.28.0 (read with `git -C /Users/kent/conductor/workspaces/kc-claude-plugins/colombo show origin/main:<path>` after `git fetch origin`). Check the chain first (Spacedock, then kc-dev-flow-2, then sibling adopters) and say what you found; for a third-party mechanism read its own docs or source, not an adopter's workaround.

Ideation writes no repository file, branch or commit; the design and criteria go in the task file. Do not comment on any PR or issue, and do not message any other session. Never run `git remote set-url` or any `git config` write in a worktree of this repository. Read adopter state (relay, web, qnow) only through read-only commands.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
