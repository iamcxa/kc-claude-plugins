# Ship-flow UAT Observations

This directory records observations from ship-flow User Acceptance Tests (UATs) for the hypothesis validation of the three ship-flow guarantees.

## Observation Record Format

One observation file per UAT PR in the format `<pr-number>.md`:

```markdown
---
pr: <PR number>
date: <ISO 8601 date>
rederived: yes|no
which: <description of which guarantee(s), if any, were re-derived>
---

## Observation

<Notes on the observation, if needed>
```

## Fields

- **pr** (required): The GitHub PR number for the ship-flow UAT
- **date** (required): The date of the observation (ISO 8601 format, e.g., 2026-09-15)
- **rederived** (required): `yes` if Kent re-derived any of the three guarantees during this UAT, `no` otherwise
- **which** (optional): If `rederived: yes`, describe which guarantee(s) were re-derived and any relevant context

## Verdict Rule

The hypothesis is **valid** if and only if across all three collected UAT observation records:
- Exactly three `.md` files exist in this directory
- All files have `rederived: no`

If any observation file records `rederived: yes`, the hypothesis is **invalidated**, and the finding routes back to planning as a falsifier hit.

## Collection

Observation records are produced by the First Officer at UAT time for each of the three ship-flow PRs following the landing of the README and pins. No observations are collected until all three UATs have been conducted.
