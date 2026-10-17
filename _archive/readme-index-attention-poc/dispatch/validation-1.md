# validation-1

Dispatched: 6ea3a4724515b974c34beb16bc3382683b6d45b9 (POC workflow checkout, kc-dev-flow-2 0.23.0 README)
Candidate: none (POC result on the state branch; no code candidate)
Model: sonnet

## Checklist

Confirm from state-branch history that the pre-registration (probes, arms, scoring rule, the Captain's bar verbatim) was committed before the first scored run, and that no scored run was rerun or dropped
Re-score all 30 saved runs yourself from readme-index-attention-poc/poc/runs/ against the registered scoring rule, without using the implementer's scorer output; report per probe and arm, and any run where your reading differs from the registered rule's
Judge the P1 result: whether the two B runs that dropped checklist item 3 after reading number-guards.md failed the rule the probe tests or only the scorer's two-script-name proxy; the verdict stays against the registered bar, and any alternative reading is reported as such
Verdict against the Captain's bar (PASSED or REJECTED for the POC as registered), the startup-word ratio recomputed from arm-a and arm-b, and what the POC does not show
## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.24.0

Profile: poc. Task readme-index-attention-poc; the implementation report, pre-registration and runs are in the task file and its poc/ folder on the state branch spacedock-state/dev2-poc. Bar (Captain, 2026-10-17, 「按你建議的 poc 標準可以」): five probes, three runs per arm on Sonnet; pass when the index arm follows the probed rules at least as often in total, is worse on no probe by more than one run, and loads at most a quarter of the whole-README words at startup. Do not move the bar and do not run new model runs; read only. Commit your stage report with `spacedock state commit readme-index-attention-poc --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-poc-route/docs/dev2-poc`. Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not comment on any PR or issue.

Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).