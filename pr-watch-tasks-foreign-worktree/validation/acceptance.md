# Captain acceptance

Run from a fresh Bash shell on the declared machine, with Python 3, Git, the existing candidate repository, this state checkout, and /Users/kent/.local/bin/spacedock. No provider credentials are needed for these bounded checks.

```bash
bash --noprofile --norc "/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/pr-watch-tasks-foreign-worktree/validation/accept.sh"
```

The executable contains six steps: export the pinned commit; check absent worktree/no-field behavior; check three preserved PR paths; read both original public records through native status; compare five bounded lifecycle outputs; remove that run's exact export. Each step states its expected observation. This validator ran the command exactly as above in a fresh --noprofile --norc Bash; exit 0, output in accept.log and accept-AC-1.log through accept-AC-4.log.

The command creates a new archive each run. It does not depend on the validator's removed /tmp archive. PR_WATCH_SOURCE_REPO supplies only read-only Git history to the reused evidence helper; tested product bytes come from the exact archive. Temporary paths are captured in accept-scratch.txt and scratch-AC-*.json.

Expected terminal output:
```text
AC-1 PASS: absent worktree is factual; no action or watch entry
AC-2 PASS: local discovery, closed-only and recorded PR
AC-3 PASS: two original public records; no unknown-PR instructions
AC-4 PASS: no common-text change or bounded output growth
PASS: all four criteria; temporary export removed
```

Limits: original public metadata may legitimately change, in which case the script fails for reassessment; no hosted CI, external review, integrated overlapping branches, release, private adopters or complete live-fleet reading total is covered. See limits.md for the implementation report's individual limitations.
