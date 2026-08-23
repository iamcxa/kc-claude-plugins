---
id: 8gz8mv84sgzvbp1mdd4c3qkj
title: Stage reports stack into one file, and the round recorder refuses the shape they stack in
status: backlog
source: found 2026-08-23 while checking whether a newer Spacedock release fixed the round recorder; it does not, and the recorder's refusal exposed the entity shape as the underlying question
product: repo-platform
sprint:
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
---

## Problem

Entities in this workflow are flat `<slug>.md` files, so every stage report of
every cycle appends to one document. Measured today in
`docs/dev/.spacedock-state`: 65 active entities, 52 archived.
`skill-ablation-harness.md` is 1,565 lines and
`verification-discipline-lost-in-the-rewrite.md` is 1,067 across eight stage
reports. Reading either one costs offset-scoped reads for the whole of a
session, and a First Officer that reads the wrong offset routes a worker on a
stale section.

Spacedock's folder form — `<slug>/index.md` with review artifacts beside it —
is the shape that answers this, and `spacedock` upstream now carries an
`entity-form: folder` declaration a workflow README can make (added by
spacedock#745). Upstream issue spacedock#221 is the open discussion of folder
form for feedback-cycle entities.

**What this does not buy, so it is not the reason to do it.**
`spacedock gate record --round` refuses flat entities, so this workflow's three
correction rounds on one entity were unrecordable and were written into the
entity body instead (filed upstream as spacedock#755). Converting to folder
form clears that refusal and still does not make the recorder usable: `--round`
consumes a caller-supplied `briefing.json` and `briefing.review.jsonl` pair that
this workflow's reviewers do not produce — they write Markdown stage reports.
Producing that pair is a separate review-provider integration, not a rename.

**What broke without it, honestly.** The recorder's absence cost nothing
observable across those three rounds; the rounds are readable in the entity
body and nothing consumed a machine-readable round history. The measured cost
is the file size above, not the recorder.

## Fit question for the Captain, before this is worked

The write-authority contract names split-root migration and workflow refit as
classes that do not belong in a product workflow unless the README names them as
an executable deliverable, and this README does not. It also keeps its one
existing refit requirement — the trunk-only delivery base — as a line in
`## Local Profile` rather than as a task. This item may belong there instead of
here. It is filed here because the Captain asked for it as a task; retiring it
in favour of a README refit line is a legitimate outcome of its backlog gate.

## Work profile receipt

## Accepted outcome and non-goals

## Acceptance evidence

## Measurement
