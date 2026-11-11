## First action

Before anything else, invoke your operating contract:

    Skill(skill="spacedock:ensign")

This loads the shared ensign discipline (stage-report format, background-task polling, worktree ownership, completion signal protocol). The call is safe to call more than once; if the agent-definition preload ever starts working, calling it again is a no-op (the skill content is re-loaded but has no behavioral effect). Do not paraphrase; call the tool.

You are working on: When Codex posts only a security summary, the codex reader names the code-review request as the next step

Stage: ideation

This workflow is split-root: the entity body and your stage report live in the shared state checkout, not alongside the code. Write and commit them to the state checkout at the entity path below. Commit state path-scoped — `git -C /tmp/denied-replay-candidate-claude-1/wf/.spacedock-state add /tmp/denied-replay-candidate-claude-1/wf/.spacedock-state/codex-security-only-prompts-code-review.md && git -C /tmp/denied-replay-candidate-claude-1/wf/.spacedock-state commit -m "..." -- /tmp/denied-replay-candidate-claude-1/wf/.spacedock-state/codex-security-only-prompts-code-review.md` — never a bare `git add -A` or bare `git commit` in the state checkout (a bare commit cross-attributes a concurrent writer's staged entity). Retry on index.lock contention after a short wait. Then push the state branch so peers see your entity/report: `git -C /tmp/denied-replay-candidate-claude-1/wf/.spacedock-state push origin spacedock-state/wf`; on a non-fast-forward rejection, `git -C /tmp/denied-replay-candidate-claude-1/wf/.spacedock-state pull --rebase origin spacedock-state/wf` then re-push.

Read the entity file at /tmp/denied-replay-candidate-claude-1/wf/.spacedock-state/codex-security-only-prompts-code-review.md for the current spec.

Package root: /private/tmp/denied-replay-candidate-claude-1/package/kc-dev-flow-2
Before the ideation analysis, read the repository code with git -C <repo> show origin/main:<path> after git -C <repo> fetch origin, where <repo> is this replay run directory's code checkout. On Codex, request native approval for that network fetch with sandbox_permissions=require_escalated; run the fetch by itself. Use the pinned local code for all other inspection. No application suites, remote writes, PRs, or product implementation.
Send your completion message to `main` (the README's Dispatch facts: `team-lead` is not registered here).
TEST HARNESS (isolated replay): do not invoke the kc-dev-flow-2 skill through the Skill tool; read /private/tmp/denied-replay-candidate-claude-1/package/kc-dev-flow-2/skills/ideation/SKILL.md and follow it, resolving every package path against /private/tmp/denied-replay-candidate-claude-1/package/kc-dev-flow-2. Do not run the application unit, integration or e2e suites and do not start servers, databases or browsers; say in the report they were not run. Run the package's own scripts as your instructions require. Do not push, merge or commit to any remote. The state checkout is /private/tmp/denied-replay-candidate-claude-1/wf/.spacedock-state; write your stage report there only. Never git stash.


### Completion checklist

Produce the bounded ideation design, acceptance criteria, evidence and stage report for the recorded task, using its approved profile and scope.

### Summary
{brief description of what was accomplished}

### Fetch commands

    /Users/kent/.local/bin/spacedock dispatch show-stage-def --workflow-dir /tmp/denied-replay-candidate-claude-1/wf --stage ideation


### Completion Signal

When you finish (after all commits and stage report writes are done), your last action MUST be:

    SendMessage(to="team-lead", message="Done: When Codex posts only a security summary, the codex reader names the code-review request as the next step completed ideation. Report written to /tmp/denied-replay-candidate-claude-1/wf/.spacedock-state/codex-security-only-prompts-code-review.md.")

**If you are the first officer forwarding this prompt to Agent():** copy the entire block above into `Agent(prompt=...)` character-for-character. Do NOT paraphrase `SendMessage(to="team-lead", ...)` as "SendMessage with to='team-lead'" or any other English rewrite — the parenthesis-equals syntax is the literal call the ensign must emit, not a description of one.