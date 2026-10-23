# 0032. A release-changed mark with no later review line holds the first implementation dispatch

Date: 2026-10-23

## Status

Accepted

## Context

An implementation was dispatched after its release changed (signals 1 and 2 recorded in the task's `## FO alignment`) with no new release review: qnow R4, 2026-10-08, record shape `journey:` only, a prose `Release: <journey>/<release>. Signal 1 (...)` line and no `Release review:` line. A first design compared the journey map at the review record's commit with the map now; the replay showed R4's signals were not map edits, so it would not have caught R4. Spacedock 0.27.2 `dispatch build --help` lists no precondition input, and with a held task in a scratch workflow `spacedock status --next --json` still listed it as dispatchable (2026-10-23), so a refusal at build is not available. Replayed on the committed state branches of four repositories (the first commit with `status: implementation` and `worktree:` set, 2026-10-23), the rule held 17 of 196 dispatches: 3 verified true (the R4 shape), 1 verified false (a Captain ruling that added no map story), 13 not classifiable from the state branches. The measurements are in the task's `## Design`.

## Decision

**Words:** 「重做檢查」 — Captain, 2026-10-23, chat, answering whether to rebuild the check on the task's own record or close the task; 「可以」 — Captain, 2026-10-23, ideation gate, accepting the three decisions the gate question named (regex recognition of the mark, deleting "no script checks that line", the known false holds).

**Options considered:**
- `pr_watch.py tasks` reads only the dispatched task's own file and prints one `next:` line naming each task at `implementation` with no worktree and no `dispatch/implementation-*.md` whose `## FO alignment` has a line matching `signal 1` or `signal 2` (case-insensitive) with no review line after the last such line; a review line is `Release review:` then `not needed:` and a reason, or `<journey>/<release> at <commit>` (chosen)
- Compare the map at the record's commit with the map now (not chosen: it misses R4, whose signals left the map unchanged)
- A pinned mark format in `workflow.md` (not chosen: +11 words under the budget of ADR 0020, and none of the 17 replayed marks match it)
- Hold only when no `Release review:` line exists (not chosen: it misses a verified true hold whose mark line itself starts `Release review:`)
- A precondition in Spacedock `dispatch build` (not designed: none exists as of 0.27.2; a request is filed only if the Captain asks)

**Recommended:** the first option, with `workflow.md` losing `; no script checks that line` and gaining no word.

The hold is advice at the strength of the seed line (ADR 0027), not a gate: nothing refuses `dispatch build`, and an FO that does not read the idle `next:` line still dispatches. ADR 0029 D2 (no seed-time hold) is the earlier moment and stays.

## Consequences

A task whose review ran but whose line was never written is held until FO writes the line, and so is one whose ruling changed no map; each clears with one `Release review:` line. A mark written without the words `signal 1` or `signal 2` is not read, and a Captain ruling not written into `## FO alignment` is invisible. The review's content is not read. The line costs FO 49 fixed words plus one per held slug on each idle pass while a task is held, and nothing otherwise. Reopen when a held task shows the line cleared without a review having run, or when a dispatch after a release change goes unheld because its mark used other words.
