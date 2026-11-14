# implementation-1-message-2

Dispatched: 88f86f2749dadb6f4ef0cf9aa089c1827096865b (workflow checkout, kc-dev-flow-2 0.41.0 README); reform scope 1, second FO; follow-up message to the implementation-1 worker (Paseo b2274684), the third implementation cycle under Captain amendment 2
Symptom: the operator stopped a paid run with Ctrl-C and the agent kept running as an orphan with no cap and the credential in its environment, because the child runs in its own session and the runner printed nothing while the run was in flight
Model: claude-sonnet-5-5 (Claude via Paseo profile 'dev2 worker', thinking high; the same worker as implementation-1)

## Checklist

- Captain amendment 2 (in the task file): third and last implementation cycle. Fix the launch path: the child's whole process group is killed on interrupt and on runner death; the wall-clock and tool-call caps still fire if the runner dies, so the child cannot outlive its cap under any exit path; one progress line while a run is in flight (arm, trial, elapsed, tool calls); "operator abort" is its own recorded status, counted toward the 18 launches and not as one of the two INVALID trials that halt the cell; the existing aborted launch record is read as that status.
- Operator experience: before the first launch the command prints how many runs it will launch, the cap per run, the expected total minutes and how to stop it safely.
- Five proofs with a stub agent command in place of the real one (no credential, no spend), each a command with its exit code that another worker can run: Ctrl-C during a run leaves no process in the group; SIGKILL of the runner leaves no child past the cap; the wall cap fires on a stub that never exits; progress lines appear; the value of a dummy token set the same way is absent from every file the runner writes (manifest, stream, logs, run directory).
- Re-run the earlier unpaid checks; commit on the same branch in the private working repository; report the new candidate SHA; append a complete new stage report that supersedes the earlier ones. No paid run and no credential handling by you.

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.41.0

Start in the assigned worktree; verify pwd and git root before edits.

Everything in implementation-1 stands, including: nothing from a case, a run or a private adopter goes onto this state branch; FO commits state. Never run `git remote set-url` or any `git config` write in a worktree of this repository. Do not stop or signal any process you did not start in this turn.

roborev not run: the candidate lives in a different, private repository that this repository's review daemon does not cover.

Your final reply is your completion message: Paseo delivers it to FO when your turn ends. End your turn with the Done line below as that reply; do not send it with SendMessage or send_agent_prompt.
Done line: Done: behaviour-baseline-first-cell completed implementation
