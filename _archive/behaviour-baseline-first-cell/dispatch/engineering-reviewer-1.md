# engineering-reviewer-1
Dispatched: 88f86f2749dadb6f4ef0cf9aa089c1827096865b (workflow checkout, kc-dev-flow-2 0.41.0 README; reform scope 1, second FO)
Model: gpt-6-astra (Codex via Paseo, thinking xhigh; model table engineering-reviewer row on Codex, a different family from the Claude implementation worker)

## Checklist
Run, do not read: at candidate 16af27c27b19a5ece4979454de46a229f2f928cb of the private working repository, run each of the six stub-agent proofs (ctrlc, sigkill, wallcap, progress, token, signalled) through behaviour/prove_launch.py with python3 -B and record each exit code and what you observed yourself (process lists after the kill, timings against the cap, the progress lines, the scan for the dummy token value)
Try to break the claim "the agent cannot outlive the runner or its caps": at least three attacks of your own with the stub (for example a child that ignores SIGTERM, a child that starts its own session, the runner killed during start-up before the guard is ready) and say for each whether a process survived past the cap
State plainly whether a paid run may be asked of the Captain again: yes, or no with the failing command; list what stays unproven with a stub

## Scope notes
Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.41.0

Question for the engineering reviewer: the Captain stopped a paid run with Ctrl-C and the agent survived as an uncapped orphan holding his credential. The implementation worker says the fixed launch path makes that impossible on every exit path its proofs exercise. Is that true when you run the proofs and attack it, and may a paid run be asked of him again? The reform session, under the Captain's grant, requires these proofs to be validated by a different worker running them before any further paid run. Read-only for the candidate: change no file in the private working repository; work in a scratch copy if you need to modify a stub. No credential, no paid agent run; a dummy token only. FO gives the private working repository's local path in the message that starts you; this record does not hold it, and nothing from it goes onto this state branch beyond file paths relative to its root and commit SHAs. Do not signal any process you did not start.

roborev not run: a role call reviews by running proofs; no candidate of this repository is involved.

Start in the assigned worktree; verify pwd and git root before edits. Commit locally and report the branch, base, candidate SHA and prepared PR text; do not push the product branch or open its PR. FO owns those steps and, when roborev is listed, its review. Report delegated checks as not run, never clean. Split-root state commits and sync still follow the ensign contract. Before using Paseo's browser tools, read extensions/paseo/browser.md under your Package root.

Your final reply is your completion message: Paseo delivers it to FO when your turn ends. End your turn with the Done line below as that reply; do not send it with SendMessage or send_agent_prompt.
Done line: Done: behaviour-baseline-first-cell engineering review complete

Scratch: /tmp/dev2/kc-claude-plugins-3042bb224e995ded/behaviour-baseline-first-cell/engineering-reviewer-1
Put files and checkouts outside the task worktree or state checkout under that folder. Copy cited evidence into evidence/engineering-reviewer-1/ in the task folder. Never archive private repository evidence, secrets or personal data; instead write `Not archived (private): <what>; reproduce: <command>`. Before reporting, run `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.41.0/scripts/scratch.py close /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/behaviour-baseline-first-cell engineering-reviewer-1` and paste its output.
