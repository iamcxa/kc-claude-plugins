# 0036. A reserved ADR may land on a named sibling PR of the same task

Date: 2026-10-25

## Status

Accepted

## Context

ADR 0025 D2 holds the merge ask while a reserved `ADR: NNNN` has no `<adr-path>/NNNN-*.md` at the PR head. A task that delivers a plugin and the package that consumes it through two PRs (new-work-starts-from-a-story-map, #704 and #705) reserved its ADR on one of them; `delivery_gate.py check` held the ask for the other, saved no record for it, and the Captain merged #704 after FO asked in chat. Spacedock 0.27.3 tracks one `pr:` string and one `pr-merge:N` sentinel per task, so the second PR is outside its tracking either way. One of the 141 task files here delivered through two PRs (read 2026-10-25).

## Decision

**Words:** 「全准」 — Captain, 2026-10-25, chat, answering the batch-6 ideation sitting, which listed this task's ideation briefing with D1 (may one task deliver through two PRs) and D2 (`dispatch_records.py` joins) as recommended.

**Options considered:**
- A: `delivery_gate.py check` takes a repeatable `--sibling-pr owner/repo#N`; a reserved ADR missing at this PR head passes when a named sibling is not closed, its head is a `Candidate:` line of the newest validation record, and the ADR directory at that head lists the number (chosen)
- B: a cross-plugin outcome is two tasks, the second `blocked-on` the first, the ADR on the second (not chosen)
- C: leave it; FO asks the Captain in chat to merge the first PR (not chosen: no ask record is saved)

**Recommended:** A, as the task design stated.

**Protects:** none

A reserved ADR may be satisfied by the file at the head of a named sibling PR of the same task, only when that head was dispatched for validation as a `Candidate:` of the task. ADR 0025 D2 otherwise stands: no flag, a closed sibling, a head that was not dispatched, or a file absent at the sibling all hold the ask with the existing line.

## Consequences

A task delivered through two PRs gets a saved ask record and the same gate path as any other. The check proves the file exists at the sibling's validated head when it runs, not that the sibling merges; merging the ADR-carrying PR last is the safe order and is not checked. Every validation record of such a task must carry one `Candidate:` line per PR head, written by FO, because only the newest record is read. Spacedock still tracks one PR. Reopen if a sibling PR merges without its ADR after a passing ask.
