# Blind read 1 of contract-draft.md (asks.jsonl format version 1)

Reported to the First Officer by the reader's First Officer in another repository, 2026-11-14; a fresh worker (Claude Sonnet, no prior context) read the draft only, built a reader and nine fictional fixtures, 93 seconds by its harness clock. Not re-run by either First Officer. Counts and field names only.

Verdict: the draft alone was enough to build a working reader; no blocking gap; 28 questions or assumptions, all edge behaviour.

## Contradictions (two readers would differ): 5
1. Section 4 "withdrawn: has withdraw and no answer" against "reader keeps the first closing event": withdraw-then-answer reads differently under each.
2. Section 4 allows `acted` after `withdraw`; then both "done" and "withdrawn" hold. `acted` with no prior `answer` is undefined.
3. Section 5 "blocked or continuing" collapses `holds` to two values while section 3.1 has three; a reader following the section 5 table loses the `acceptance` hold.
4. Section 5 `version` as "number of lines with this key" against "rises on every change" (a `reask` changes nothing).
5. Section 5 "last shown" counts `ask` and `reask` but not `revise`, though a revise is also shown to the Captain.

## Under-specified (an assumption was needed)
- `revise`: is an omitted `options`, `recommend`, `grounds` or `refs` cleared or unchanged? `recommend` may point at an option no longer in `options`.
- `answer.revision`: who determines it for a Review resolution; nothing ties a `resolution` to the `briefing` of a specific `reask`.
- An answer to an older revision whose chosen `option` a later revise removed: may the First Officer act on it?
- `option` null with `resolution` set on a multi-option revision: the approved option is unknowable from the file.
- Older revisions must stay readable for `answer.revision` to mean anything; the draft only says take the latest.
- `asked_at` null: where an unknown sorts in a waiting-since order; it can never be corrected later.
- No forward-compatibility rule for a higher `v`, an unknown `event` or unknown fields.
- Whether an "answered" row (the step is the First Officer's) belongs in "what waits on the Captain".
- Section 2: a flat task file whose folder exists only for the record; archived tasks; enumeration over `git show`.
- A duplicate key from a second `ask`, events before their `ask`, `asked_at` later than `at`, fractional seconds.
- `refs.kind: record`: what the id resolves against.

## The six defects of the first hand-run sample
1. Estimated ask time: covered; gap: no later correction.
2. Blocking beyond two values: covered by `holds`, undone by the section 5 table; cannot name which acceptance item is held.
3. Mixed or pending evidence: covered; gap: a reference becoming ready needs a whole `revise`.
4. Re-asks and channels: covered.
5. Options changed after asking: covered by `revise`; the three revise and answer gaps above apply.
6. An answer with no words: partly; needs old revisions kept, and fails when `option` is null on a multi-option list.

## Never needed by the blind reader
`acted.refs`; `by.agent_id`; `refs.kind` beyond display; `said_at` beyond display; section 5 `version`, `kind` and `task`; the writer section.

## The reader's own First Officer, on what its decision-table reader would use
- Would read: `asked`, `options`, `recommend`, `grounds`, `holds`, `refs` with `ready`, `by.name`, `asked_at`, interruptions, last shown and `briefing`, state, `answer.revision`, `option`, `words`.
- Would not read: `acted.what`, `acted.refs`, `by.agent_id` (unless a reader is meant to ask that First Officer by id; say so or drop it), `said_at`.
- Missing: (a) a per-option effect, what happens if he picks it; (b) what a plain approve accepts when a recommendation exists; (c) a question that belongs to no task, which the motivating sample was; say it is filed under the task that raised it, or version 1 does not cover it; (d) no workflow or project identity in the line: fine if stated that the reader carries it from the checkout.
