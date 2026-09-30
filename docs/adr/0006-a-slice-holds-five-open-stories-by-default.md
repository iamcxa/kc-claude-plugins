# 0006. A slice holds at most five stories that do not exist yet by default, as an advisory

Date: 2026-09-30

## Status

Accepted

## Context

A reviewer of one adopter's journey could not discuss a release slice whose single
column mixed two actors' actions, and asked for at most five things per slice so a
reader can hold the whole slice in mind. The unit of a "thing" was never defined. On
that journey the first slice held 14 stories, 10 not yet existing, and an independent
read-only review found it was not a clear five-step demo. The Captain then asked for
the number as a default that gives slicing a basis: 「我覺得每片五件事最多可以開一個 PR
回去上游，讓切 slice時有依據，等於預設就是五件事。」 and sized a slice at about one to
two days of work.

The unit was measured on a second adopter's two journey files (2026-09-30). Counting
stories whose status is not `exists`, per journey file, flags one release. Counting all
stories flags two more that had already shipped. Counting the steps a release touches
flags none (the largest touches five). Counting tasks is not computable when a slice is
cut, because tasks exist only after the split. Counting a release id across both files
flags five, but the package qualifies a release by its journey file, so a shared id is
that adopter's own convention. That adopter's own size notes tag a release with 8 open
stories "about S" and one with 5 "about M", and call the estimates unmeasured, so count
and size do not line up.

## Decision

**Words:** 「還沒做好的故事，每張旅程圖分開算」 — Captain, ideation gate of this task, 2026-09-30.

**Options considered:**
- count stories whose status is not `exists`, per journey file (chosen)
- count all stories — rejected: it flags releases that already shipped
- count the steps a release touches — rejected: it flags nothing in the measured files
- count tasks — rejected: tasks exist only after the slice is cut
- count by release id across journey files — rejected: the package qualifies a release
  by its journey file; the review reference tells the reviewer to add counts by hand when
  releases in several files are one demo
- make the limit a gate that refuses a handoff — rejected: `release-slicing.md` already
  says story count does not establish fit, and this rule is a reading-load cue
- encode a day number for the slice — rejected: appetite is recorded per handoff by
  the user, not fixed by the package

`journey-lint.mjs` prints `slice-size (advisory)` for a release with more than five such
stories, without changing its exit code. A top-level `slice_limit` (a positive integer,
otherwise the `invalid-slice-limit` violation) replaces five; a release's non-empty
`slice_because` prints `slice-size (accepted)` instead. A slice over the limit splits
into sub-slices or says why not. `journey-handoff.mjs` checks no story count.

## Consequences

A release that mixes many finished stories with five new ones passes although a reader
still sees the finished cards. A per-file count misses a demo spread across journey
files; the reviewer adds those counts by hand. Whether five is the right number is
unmeasured beyond the two journeys above; `slice_limit` is the per-journey escape.
`slice-size` is a printed line that nothing forces anyone to read. Reopen if an
adopter's slices routinely carry `slice_because` (the default is wrong for them) or if
a slice within the limit is still reported unreadable (the unit is wrong).
