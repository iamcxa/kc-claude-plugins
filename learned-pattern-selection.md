---
title: Every review pays for all 104 learned patterns whether or not any applies
status: backlog
source: agent-native audit of the kc-pr-review kit, 2026-07-26; sprint slice 2 of 2, planned with a cross-vendor (agy) pass
started:
completed:
verdict:
worktree:
issue:
pr:
design:
id: v52dgtngxnthwah7tvbeawsz
---

`reference/learned-patterns.md` is 1193 lines and 104 entries with embedded code blocks. Two
skills auto-append to it with **no confirmation gate** (`skills/kc-pr-review/SKILL.md:1834`
"No confirmation gate"; `skills/kc-pr-review-resolve/SKILL.md:575` "appended … without gate"),
and `kc-pr-review-resolve:133` reads the **whole file** on every run. There is no index, no
relevance selection, and no eviction. The file's own header instructs a human to "curate
periodically"; that has never happened.

So the corpus is a context tax that every run pays in full regardless of relevance, and it
grows monotonically forever by design. This is the one item in the agent-native audit that
gets strictly worse with time on its own.

Scope is the **read path only**: give the corpus trigger metadata and an index, select against
it, and migrate the 104 existing entries. Bounding the write path (dedup / supersede on
append) is a sibling entity — the cross-vendor sizing pass judged both together to exceed a
single implementation session, and they split cleanly along read/write.

## Two design constraints carried in from the cross-vendor pass

**Selection must be aggressively high-recall, and the design should be asymmetric about it.**
The two error directions are not comparable. Over-retrieval costs tokens. Under-retrieval is a
silent regression: the review misses a known defect pattern and a defect passes. Broad tag
matching, a low threshold, and a mandatory always-loaded core tier are the right posture;
over-retrieving by half is acceptable where under-retrieving at all is not.

**Index failure must fall back to reading the whole file, with a warning.** This is a
deliberate exception to the repo's fail-closed norm, and the reason must be recorded next to
the code: here the failure direction is cost, not correctness, so failing open preserves the
guarantee while failing closed would silently empty the corpus.

## Acceptance criteria

An earlier draft of AC-1 asked for "no loss of the entries that would have applied", which the
cross-vendor pass correctly called unmeasurable — it needs the counterfactual of a full-context
run. Replaced with a criterion that can fail:

**AC-1 — A pattern whose trigger metadata matches the diff is never omitted from the loaded context.**
Verified by: a fixture set of diffs and tagged patterns where every expected match is asserted
present in the selected set, including at least one pattern matched only by its secondary tag.
Falsified by: any matching pattern absent from the selection.

**AC-2 — Loaded learned-pattern bytes drop measurably against today's whole-file read, on a real diff.**
Verified by: the byte count entering context for a recorded real review, before and after,
with the selection recorded so the drop is attributable. Falsified by: no measurable drop, or
a drop that AC-1's fixture set does not survive.

**AC-3 — All 104 existing entries carry trigger metadata after migration, and an untagged entry is loud.**
Verified by: a checker reporting zero untagged entries post-migration, and reporting a
deliberately untagged fixture entry as untagged. Falsified by: an untagged entry that neither
loads unconditionally nor is reported.

## Out of scope

Bounding the append path — dedup, supersede, eviction (sibling entity). Any judgement about
which of the 104 entries deserve to survive; migration tags them, it does not curate them.
Step 4.5 pre-scan coverage (sprint slice 1). General telemetry beyond the byte measurement
AC-2 already needs.

## Notes for the implementing session

Sequence after `prescan-coverage-honesty` rather than in parallel: both slices edit
`skills/kc-pr-review/SKILL.md` — slice 1 at Step 4.5, this one at Step 8 — and the cross-vendor
sizing pass flagged the shared-file overlap as a guaranteed conflict if run concurrently.
Re-measure the suite baseline first; main has moved past the 920/0 recorded on 2026-07-26.
