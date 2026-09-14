# Planning from a conversation or an existing story map

For a new map, use the intent-only four passes below. For an existing board being
prepared for development, use **Prepare one release for development** instead.
Map-only use needs neither code evidence nor Spacedock; release preparation reuses
recorded decisions and investigates facts that could change the selected value.

You are facilitating, not deciding. The map is theirs; the discipline is yours.

## New-map boundaries

- **Do not ask for citations, and do not check anything against code.** This stage asserts
  intent. `references/cell-contract.md` explains why the three pages have different bars.
- **Do not set `status` on a story.** `gap` belongs to draw mode, where there is a codebase
  a story can be absent from.
- **Do not decide the first release.** Show the whole journey first, then follow
  `release-slicing.md` to propose a smaller complete slice in prose. Change boundaries
  after the human accepts. A broad release can remain drawn without being ready for
  development; an oversized candidate must return to reduction before handoff.
- **Do not restart.** If a map already exists, take it as given and extend it. Re-asking
  what they already answered is how a facilitator loses the room.
- **One question at a time.** A list of six questions gets one answer and five shrugs.

## The four passes

**1. The person.** Who is this for, in their words? One persona. If two names come up,
ask which one this map is about — a map serving two people serves neither.

**2. The backbone.** What does that person *do*, left to right, in the order they do it?
Verb phrases, ≤ 12 words, their language not the system's. Keep asking "and then?" until
they reach the end, then ask "and what happens before the first one?"

Write these as `steps[].activity`.

**3. The stories.** Under each activity: what are the different ways that gets done, and
what else has to happen for it to work? Go activity by activity, left to right. Variants
and edge cases go under the main path, not beside it.

Write these as `steps[].stories[]`, each with an `id`.

**4. Propose the first release after showing the whole map.** Render the backbone and
stories with unplaced or explicitly provisional release membership first. Follow
`release-slicing.md`: analyze the smallest complete outcome, explain retained and
deferred stories in prose, resolve the one remaining human choice, then write accepted
`releases[]` and `stories[].release` boundaries. Keep deferred paths visible. Do not make
the user discover the whole journey through a sequence of scope questions.

## What to say when a release leaves an activity empty

Rendering prints the coverage per release. An empty activity in release 1 is not
automatically wrong — an activity belonging to a later release's outcome is not part of an
earlier one's journey. But it is the question the map exists to make askable, so ask it:

> Release 1 does not touch *«activity»*. Is that because a person does not do it yet, or
> because we have not decided?

The first answer is a plan. The second is a decision someone owes, and it goes in the file
as an unplaced story rather than being resolved by you.

## What the room gets

Render it, put the board in front of them, and let them move the cards. Read it back with
`journey-read` and the file follows. Do not retype what they moved.

## When the conversation is a document instead of a room

Prose is a legitimate input — a brief, a ticket, a transcript. Read it, draft the backbone
and the stories from it, and then **show the draft and name what you invented**. A story
map drafted from prose is a proposal with an author, and the author is you until somebody
in the room says otherwise.


## Prepare one release for development

**1. Reuse the source.** Read the repository journey YAML and select the release ID
from the request or recorded context; ask if that selection is unresolved. Reuse
its persona, one journey, release goal, story membership and decisions. Do not run
the four-pass interview again. Inspect relevant existing boards on explicit
planning/resume requests, without adding background monitoring.

**2. Investigate before proposing a choice.** Inspect selected-release gap and
unverified stories, unresolved questions in every status, and dependencies that
could affect this release's outcome. Read accessible evidence symbols, source
models and existing task observations; cite the repository/ref and what was read.
A model executed through an agent may have no standalone handler. Missing evidence
is not missing implementation, and a non-green card is not a task request.
Distinguish authored implementation uncertainty from unavailable or incomplete
Spacedock task observation; preserve each unknown independently. Reuse assigned or
deferred dispositions unless a changed premise affects them. Keep later-release
unknowns visible without blocking an independent current release.

**3. Propose the minimum complete slice.** Follow `release-slicing.md` for the
removal test, necessary constraints, factual dependencies and appetite/fit assessment.
Explain the reduction in prose before changing the map; an optional retained story or
an oversized/incomplete candidate returns to a smaller proposal. Then ask one unresolved value, scope or acceptance
question at a time, with a recommendation and its effect. Use the host's available
interaction tool; when unavailable, ask in plain text. Do not reopen settled
answers unless their premises changed. No answer, interruption or abandonment
leaves the decision unresolved: keep dependent scope out of a ready brief and name
what keeps it draft. A fixture answer is exercise evidence, not live approval.

**4. Retain the answer.** Re-read the source before editing to detect intervening
changes. Preserve story/release IDs and nonselected content. Record the answer and
its affected IDs in the existing decision container, or existing note/rule content;
do not require a new schema. If a canvas was edited, use the supported readback and
ambiguity handling in `canvas.md`: disposition conflicting, duplicated or unclaimed
edits before applying. Function-model changes use source edits followed by redraw,
not direct function-map writeback. Resume from recorded decisions; retry by checking
the current source instead of replaying writes. Show the decision diff for review.

**5. Prepare one Development Brief.** Load the existing five-section admission
format from the active `kc-dev-flow:adopt-dev-flow` skill
(`kc-dev-flow/skills/adopt-dev-flow/SKILL.md`, adoption step 3). Reuse that format,
including ordered `AC-N` identifiers; do not create another template or schema.
If the format is unavailable, report that and leave the handoff draft. Within
those existing sections, include:

- source path, committed revision (or explicit uncommitted content hash), and the
  selected release/story IDs;
- observed facts with evidence, separately labeled assumptions and unresolved
  technical questions;
- the reviewed value and scope, observable acceptance, and route-back conditions.

Generate the snapshot after reviewing decisions. Before handing it off, re-read
the source and compare revision, membership and decision premises with the brief;
a stale pairing needs review/regeneration. The generated release contract supplies
evidence; it is not the Development Brief. A current-scope decision still missing
keeps the brief draft, while a technical unknown can pass to shaping if it does not
change the accepted value, scope or acceptance.

**6. Check, then hand off technical shaping once.** Run the guarded
`journey-handoff.mjs` command in `release-slicing.md` against the final source, pre-cut
baseline, accepted assessment and existing brief. A refusal keeps the handoff draft;
return to the reduction proposal or missing decision, without bypassing the guard with
the input brief. On pass, give that unchanged brief and factual evidence
to existing dev-flow ideation under its selected profile. It owns technical gaps,
dependencies and without-it analysis: what necessary work remains if a proposed
change is omitted. Journey planning does not pre-split cards into implementation
tasks or run a separate plan-detail pass. Carry shared/integration work's multiple
release/story origins in task prose; omit unsupported scalar `journey-story`
progress mapping rather than inventing one story owner. Task counts remain
observations: all tasks done means pending delivery acceptance, not usable journey.

Existing profile, admission and implementation authority applies; a drawn card or
prepared brief grants none of it. Standalone dev-flow still accepts a valid brief
without a board. Source provenance belongs in brief prose, not an incomplete
provider Planning Receipt. After admission, changed planning premises return a
planning delta naming the premise, affected acceptance evidence and recommended
change or stop; do not automatically rewrite running tasks.

This route keeps the journey YAML and dev-flow brief formats; its guarded handoff
command checks the selected release without migrating existing map consumers.
Render when requested using the existing canvas contract; if unavailable, deliver
the source and Markdown with that limit stated. Do not claim rendered, deployed
or usable behavior from source inspection or local checks.
