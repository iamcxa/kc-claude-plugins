# implementation-1-message-4

Dispatched: ba055b8a7a55a787ac989c4cef52d07dd75661ad (workflow checkout, kc-dev-flow-2 0.35.0 README); batch 17, follow-up message to the implementation-1 worker (Paseo 5f791677), routing validation-2 F1 with the chief-engineer's class fix
Symptom: validation-2 F1 on PR #812: an immediate retry reuses the committed record without checking the index; the stamp replaces a staged-only edit
Model: gpt-6.1-sol (Codex via Paseo, thinking xhigh; the same worker as implementation-1)

## Checklist

1. Validation-2 found F1 (Material): an immediate retry reuses the committed record without checking the index, and the stamp then replaces a staged-only edit (/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/dispatch-build-writes-the-dispatch-record/validation-2/evidence.md). It is the same class as the Codex P2 repaired at 0d84d5d1b96fd674dba3a442d69c2e7898cceccd. Close the class, not the instance: follow /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/dispatch-build-writes-the-dispatch-record/review/chief-engineer-1.md, which FO adopts as this repair's design.
2. Add one precondition, called once after read-only scope resolution and before select_record, on fresh dispatch, retry, new round and --advance alike: the stamp's whole commit scope for this task (the task file and its companion directory, as Spacedock's entityCommitPaths defines it) must match HEAD in both the index and the worktree, with no untracked non-ignored file in it. On refusal, name the path and its condition, exit nonzero with "dispatch_stage: dispatch not built;", print no envelope, call neither builder nor cleanup, and change nothing.
3. Prove it with the chief-engineer report's matrix (locations, states, refusal oracle with snapshots, allowed paths through the real Spacedock 0.27.2 builder) and its falsifiers (guard removed, index comparison omitted, worktree or untracked check omitted, scope narrowed to the record or dispatch directory, guard placed after record creation, guard bypassed on retry or advance), each failing its matching assertion. State the exclusive-writer limit in the report and the PR text; claim no concurrency safety.
4. Rerun the existing acceptance runner and package tests, commit locally on the same branch, and append an implementation stage report with the new candidate SHA. Reply on nothing in the PR; FO pushes.

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0

Start in the assigned worktree; verify pwd and git root before edits.

Everything in implementation-1 stands. Never run `git remote set-url` or any `git config` write in a worktree of this repository.

Your final reply is your completion message: Paseo delivers it to FO when your turn ends. End your turn with the Done line below as that reply; do not send it with SendMessage or send_agent_prompt.
Done line: Done: dispatch-build-writes-the-dispatch-record completed implementation
