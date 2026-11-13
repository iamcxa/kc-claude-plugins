# validation-2
Dispatched: 8ce0eb6050c889b21baccf50fec35231bc888d66 (workflow checkout, kc-dev-flow-2 0.39.1 README; route trial of 2026-11-13)
Model: gpt-6-astra (Codex via Paseo, thinking xhigh; repo roster .dev2/model-roster.json validation row)
Budget: 1 implementation and 2 validation cycles, in one package PR.
Roster: source=repository; role=validation; provider=codex; model=gpt-6-astra; effort=xhigh; host=paseo; digest=sha256:c34a62cb3a56f3eded8c398ed469a2e43b69c95a84528aa7ab998ddb482f66a1; commit=8ce0eb6050c889b21baccf50fec35231bc888d66
Candidate: 1fc2f05f88b18a62d4eda598158ffa385df9fae8
Symptom: validation finding: independent cold behaviour proof for AC-2 not established (validator setup unusable twice)

## Checklist
Independent verdict on PR #859 head 1fc2f05f against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
Recheck after Feedback Cycle 1, allowed by Captain amendment 1 (candidate and criteria unchanged; second validation cycle of the Budget): the product head is unchanged. Establish the one thing validation-1 could not: one history-free test subject reads a native dispatch built from an immutable export of the candidate and you observe whether it states what it checked and found before proposing a design (AC-2). Build one export, verify the package root path the dispatch names exists before starting the subject, and keep mutation controls in a separate copy. You may rely on validation-1's passed source, lint, ADR and acceptance-script evidence after confirming the head is unchanged, and say that you did; rerun what you judge necessary. One attempt at the cold observation plus at most one retry; if both are unusable, report it as not established
A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.39.1/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition

## Scope notes
Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.39.1

Number guards: ADR: 0083

Profile: pilot. Start in the assigned worktree; verify pwd and git root before edits. Candidate: iamcxa/kc-claude-plugins PR #859, head 1fc2f05f88b18a62d4eda598158ffa385df9fae8, base origin/main. This task; other PRs may be in flight and are not your candidate. Read and run the candidate from an export, not a git worktree: `git -C <repo> archive <head> | tar -x -C <new directory under /tmp>`, and diff with read-only `git -C <repo> diff <base> <head>`. Do not create or remove a git worktree; its metadata sits outside your sandbox and each one needs a Captain prompt. Commit your stage report with `spacedock state commit new-work-checks-what-exists-first --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2`. Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not push the product branch, comment on any PR, request reviews or mark ready; the state-branch push that `spacedock state commit` makes is expected and allowed.

Your final reply is your completion message: Paseo delivers it to FO when your turn ends. End your turn with the Done line below as that reply; do not send it with SendMessage or send_agent_prompt.
Done line: Done: new-work-checks-what-exists-first completed validation

Roster authors: implementation-1.md: codex/gpt-6.1-sol xhigh. Family: same-family: openai.
