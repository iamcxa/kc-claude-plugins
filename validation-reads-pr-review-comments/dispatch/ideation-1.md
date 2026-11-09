# ideation-1
Dispatched: e7c9381f2ae7f11bc715a6f11a3e000b9b807e1e (workflow checkout, kc-dev-flow-2 0.36.0 README; batch 18)
Model: claude-opus-5-5 (Claude via Paseo, thinking high; repo roster .dev2/model-roster.json ideation row)
Roster: source=repository; role=ideation; provider=claude; model=claude-opus-5-5; effort=high; host=paseo; digest=sha256:c34a62cb3a56f3eded8c398ed469a2e43b69c95a84528aa7ab998ddb482f66a1; commit=e7c9381f2ae7f11bc715a6f11a3e000b9b807e1e

## Checklist
Design the validation skill's merge-readiness question (can the Captain merge this PR at this head?) and the replay comparison the stop condition names; reading every review comment must follow from that question, not from a new mechanical check; say what the replay counts, how many runs per host, and on which hosts. Batch overlap: name each file your design changes; siblings delivery-gate-ignores-url-paths-and-data-fences and delivery-check-before-ask-is-provable may touch kc-dev-flow-2/scripts/delivery_gate.py.
A `### Batch overlap` section naming each file the design would change and each other batch task (validation-reads-pr-review-comments, delivery-gate-ignores-url-paths-and-data-fences, delivery-check-before-ask-is-provable, counts-name-the-run-that-produced-them, merge-guard-stops-unasked-merges) and live task of other sessions (adr-required-statement, journey-server-host-pilot, domain-note-reaches-worker-poc) that changes the same file or check, so FO can order implementation
The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it

## Scope notes
Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.36.0

Start in the assigned worktree; verify pwd and git root before edits.

Profile: pilot. The Captain's words and the evidence are in the task file. This task is one of batch 18; read the other task files only as they stand, and do not edit them. Design against the current package source: kc-dev-flow-2/ in iamcxa/kc-claude-plugins at origin/main (read the released version from kc-dev-flow-2/.claude-plugin/plugin.json there) (read with `git -C /Users/kent/conductor/workspaces/kc-claude-plugins/colombo show origin/main:<path>` after `git fetch origin`). Check the chain first (Spacedock, then kc-dev-flow-2, then sibling adopters) and say what you found; for a third-party mechanism read its own docs or source, not an adopter's workaround.

Ideation writes no repository file, branch or commit; the design and criteria go in the task file. Do not comment on any PR or issue, and do not message any other session. Never run `git remote set-url` or any `git config` write in a worktree of this repository. Read adopter state (relay, web, qnow) only through read-only commands.

Your final reply is your completion message: Paseo delivers it to FO when your turn ends. End your turn with the Done line below as that reply; do not send it with SendMessage or send_agent_prompt.
Done line: Done: validation-reads-pr-review-comments completed ideation
