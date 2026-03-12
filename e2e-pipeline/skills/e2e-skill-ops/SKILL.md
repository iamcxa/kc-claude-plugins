---
name: e2e-skill-ops
description: Use when debugging e2e-test/e2e-map/e2e-walkthrough failures, maintaining or adding features to these skills, or evaluating execution results against skill expectations. Triggers on "e2e skill broke", "fix e2e skill", "update e2e skill", "add feature to e2e", "e2e gap analysis", "skill drift", "e2e pipeline issue".
---

# E2E Skill Operations — Debug, Maintain, Extend, Evaluate

## Overview

Meta-skill for the `e2e-map` / `e2e-test` / `e2e-walkthrough` pipeline. Enforces known-issue lookup, cross-skill impact scanning, post-fix verification, and persistent learning.

## When to Use

- e2e skill execution fails and root cause isn't immediately obvious
- After editing any e2e skill, need to ensure cross-skill consistency
- Adding a new capability to the e2e pipeline (e.g., trace analysis, new output format)
- Running gap analysis after e2e suite execution

**When NOT to use:**
- Simple mapping selector fix (edit the yaml directly)
- Normal e2e-test / e2e-map / e2e-walkthrough execution (invoke those skills directly)
- Non-e2e agent-browser operations

## Invocation

```
/e2e-skill-ops --debug       # Diagnose e2e execution failure
/e2e-skill-ops --maintain    # Sync changes across skills after edit
/e2e-skill-ops --add-feature # Add capability to one or more e2e skills
/e2e-skill-ops --evaluate    # Gap analysis: execution results vs skill expectations
```

No args: infer mode from context. If ambiguous, ask.
Unknown mode (e.g., `--fix`): list the 4 available modes with one-line descriptions.
Multiple modes (e.g., `--debug --maintain`): run in the order given, sequentially.

## The 5 Rules (apply to ALL modes)

Every mode enforces these. Skipping any one is a violation.

| # | Rule | Why |
|---|------|-----|
| 1 | **Search before diagnose** — query journal + `e2e-reports/skill-quality-findings.md` + MEMORY.md for prior findings. If `skill-quality-findings.md` doesn't exist, create it with a `# E2E Skill Quality Findings` heading. | Prevents re-discovering known issues |
| 2 | **3-skill impact scan** — check all files in the Impact Matrix below | Prevents silent drift between skills |
| 3 | **Verify after fix** — run the failing scenario (or subagent pressure test) after changes | Prevents "fix and forget" |
| 4 | **Write back findings** — append new findings to `skill-quality-findings.md` + journal | Prevents session amnesia |
| 5 | **Propose, don't ship SKILL.md changes** — present skill file changes for human approval before writing. Mapping/flow fixes can be applied directly. | Skills are shared infrastructure |

## Impact Matrix (mandatory scan)

When ANY e2e skill changes, scan every row:

| File | Check for |
|------|-----------|
| `e2e-pipeline` plugin: `skills/e2e-test/SKILL.md` | Auth flow, expect grammar, action patterns, common mistakes |
| `e2e-pipeline` plugin: `skills/e2e-map/SKILL.md` | Mapping format, selector conventions, common mistakes |
| `e2e-pipeline` plugin: `skills/e2e-walkthrough/SKILL.md` | Auth flow, smoke mode, self-repair, common mistakes |
| `e2e-pipeline` plugin: `skills/*/reference.md` | Execution details, output procedures, templates |
| `e2e-pipeline` plugin: `agents/` | `e2e-test-runner.md`, `e2e-mapper.md`, `e2e-trace-analyzer.md` — startup flow, auth, recording |
| `e2e-pipeline` plugin: `references/` | `commands.md`, `common-patterns.md` |
| `<project>/.claude/e2e/mappings/*.yaml` | Selector conventions match skill guidance |
| `<project>/e2e-reports/skill-quality-findings.md` | Past findings for this exact pattern |

**Quick skip rule**: Purely cosmetic changes (typo, formatting) — scan only "common mistakes" in the other two skills. All other changes require full scan.

## Modes — Summary

Each mode has detailed checklists in [reference.md](./reference.md).

| Mode | Purpose | Key steps |
|------|---------|-----------|
| `--debug` | Diagnose e2e failure | Search known → classify symptom → fix → verify → write back |
| `--maintain` | Sync after skill edit | Describe change → impact scan → propose all → verify → record |
| `--add-feature` | Extend pipeline | Feasibility PoC → impact scan → design → implement → RED test → evaluate |
| `--evaluate` | Gap analysis post-run | Collect results → classify failures → identify skill gaps → prioritize → report. For comprehensive skill/agent re-verification, cross-reference `VERIFICATION-SOP.md` checklists. |

## Completion Gate (mandatory)

**You are NOT done until all conditions are met.** Proposing a fix is not finishing.

| Mode | NOT DONE until... |
|------|-------------------|
| `--debug` | (1) Fix applied to file, (2) **re-ran failing step** — passes, (3) finding written |
| `--maintain` | (1) All changes applied (after approval), (2) **ran a relevant flow** — no regression, (3) findings updated |
| `--add-feature` | (1) Feature implemented, (2) **subagent RED test executed** — behavior matches, (3) feature documented |
| `--evaluate` | (1) Findings report written, (2) **fix priorities presented**, (3) recurring vs new compared |

**Evidence format** — don't say "verified", show:
```
Verification: `/e2e-test catalog-browse` -> 7/7 PASS (previously 5/7 FAIL on step 3, 6)
```

If verification fails, loop back to `--debug`. Write-back is not optional — at minimum a journal entry.

## Red Flags — STOP and Reconsider

| Thought | Reality |
|---------|---------|
| "I know what this error is, skip the search" | That's what all 3 baseline agents did. Search first. |
| "Only one skill needs updating" | OTP change touched 3 skills + 1 reference. Always scan. |
| "Fix works, we're done" | No verification = no confidence. Run the failing step. |
| "I'll remember this for next time" | You won't. Write it to findings.md. |
| "This is just a mapping fix, not a skill issue" | Mapping patterns come from skill guidance. Check if the skill taught the wrong pattern. |
| "I proposed the fix, human can verify later" | Proposing is step 4 of 7. You own verification. |
| "Context is running low, skip write-back" | Journal entry is ~500 tokens. Always enough. No excuse. |

## Quick Reference

| Need | Command |
|------|---------|
| Search past findings | `Read e2e-reports/skill-quality-findings.md` |
| Search journal | `mcp__private-journal__search_journal` query: "e2e skill" |
| List all e2e skills | `ls ~/.claude/plugins/*/e2e-pipeline/*/skills/*/SKILL.md ~/.claude/plugins/local/e2e-pipeline/skills/*/SKILL.md 2>/dev/null` |
| List project mappings | `ls .claude/e2e/mappings/*.yaml` |
| List project flows | `ls .claude/e2e/flows/*.yaml` |
| Verify a single flow | `/e2e-test <flow-name>` |
| Verify full suite | `/e2e-test --suite smoke` |
| View trace interactively | `npx playwright show-trace <trace.zip>` |

<!-- Last updated: 2026-03-12 -->
