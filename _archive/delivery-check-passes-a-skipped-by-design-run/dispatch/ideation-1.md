# ideation-1

Dispatched: ba055b8a7a55a787ac989c4cef52d07dd75661ad (workflow checkout, kc-dev-flow-2 0.35.0 README); batch 16
Model: claude-opus-5-5 (Claude via Paseo, thinking high; repo roster .dev2/model-roster.json ideation row)
Roster: source=repository; role=ideation; provider=claude; model=claude-opus-5-5; effort=high; host=paseo; digest=sha256:c34a62cb3a56f3eded8c398ed469a2e43b69c95a84528aa7ab998ddb482f66a1; commit=ba055b8a7a55a787ac989c4cef52d07dd75661ad

## Checklist

Design how /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/scripts/delivery_gate.py check tells a workflow run skipped by its own conditions on purpose from a failed, pending or unexpectedly skipped required check, with a replay of qnow #1338's skipped Release Gate (read-only from iamcxa/qnow) passing and a failing required check still held
A `### Batch overlap` section naming each file the design would change and each other batch task (codex-security-only-prompts-code-review, delivery-check-resolves-links-from-the-task, adr-reservation-crosses-workflows, decline-becomes-task-only-with-a-bite) and live task of other sessions (adoption-asks-which-extensions, adr-silent-undo-probe, captain-ruling-sources-checked (held), comment-check-reaches-delivery-gate, dispatch-carries-reserved-adr-number, fo-write-checks-parse-top-level, gate-summary-names-each-decline (held), step-back-answer-has-a-record-line (held), merge-guard-stops-unasked-merges (held), journey-canvas-hosted-poc, picky-reviewers-may-run-on-gemini, seed-check-requires-alignment-result, archive-waits-for-observer-report, ops-inbox-r1-setup-and-isolation, pr-review-lite-value-pilot, adr-required-statement, journey-server-host-pilot (stalled, held or driven by other sessions; read only)) that changes the same file or check, so FO can order implementation
The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0

Start in the assigned worktree; verify pwd and git root before edits.

Profile: pilot. The Captain's words and the evidence are in the task file. This task is one of batch 16; read the other task files only as they stand, and do not edit them. Design against the current package source: kc-dev-flow-2/ in iamcxa/kc-claude-plugins at origin/main (read the released version from kc-dev-flow-2/.claude-plugin/plugin.json there) (read with `git -C /Users/kent/conductor/workspaces/kc-claude-plugins/colombo show origin/main:<path>` after `git fetch origin`). Check the chain first (Spacedock, then kc-dev-flow-2, then sibling adopters) and say what you found; for a third-party mechanism read its own docs or source, not an adopter's workaround.

Ideation writes no repository file, branch or commit; the design and criteria go in the task file. Do not comment on any PR or issue, and do not message any other session. Never run `git remote set-url` or any `git config` write in a worktree of this repository. Read adopter state (relay, web, qnow) only through read-only commands.

Your final reply is your completion message: Paseo delivers it to FO when your turn ends. End your turn with the Done line below as that reply; do not send it with SendMessage or send_agent_prompt.
Done line: Done: delivery-check-passes-a-skipped-by-design-run completed ideation
