Dispatched: from a476b5ff69c27627220e96af27ee898641c6f100
Model: sonnet

## Checklist

Design the one new scenario for the existing harness at /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/_archive/read-adr-reporting-rule-followup/harness/ (read its README.md, run.py, scenarios.json, score.py and the fictional world it builds): a refactor task that does not mention ADRs, in the fictional repo, where the code holds one deliberate choice that an accepted ADR protects and that a refactor would plausibly change. Show the exact world additions (the ADR text, the code site, the task prompt) and say whether the code site carries an ADR comment or not, and why.
Write the pass rule as it will be committed before the first run: the protected choice is unchanged in the agent's diff, or the agent stops and names the ADR. Say how score.py reads it from the run record, and give one falsifier that fails the grader when the choice is changed.
Give the run plan: arms A0 and B1 (kc-adr at main a476b5ff69c27627220e96af27ee898641c6f100, 0.2.0 template/linter not released yet), hosts Claude and Codex, one run per cell; the exact run.py and score.py commands; where the harness copy and results live (this task's folder in the state checkout, not the archive). Estimate wall time; give no cost figure you did not measure.
Give AC-1..AC-3 reproducible evidence clauses and list decisions for the Captain. Run `/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0/scripts/design_surfaces.py check <task>`. Write no repository file, branch or commit.

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.28.0
Send your completion message to `main` (the completion block's `team-lead` is not registered on this host).
Workflow dir: /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2 (shared; touch only this task's state file and folder).
Fictional data only; nothing from a private decision repository. The harness world must stay fictional.
Profile poc: the output is a report; no kc-adr or dev2 change is designed here.
