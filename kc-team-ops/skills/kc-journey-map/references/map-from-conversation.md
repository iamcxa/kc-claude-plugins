# Drawing a story map from a conversation

For the stage before any code exists: a room full of people who know what they want and
have not agreed on it yet. The output is a story map file that can be planned with.

You are facilitating, not deciding. The map is theirs; the discipline is yours.

## What you must not do here

- **Do not ask for citations, and do not check anything against code.** This stage asserts
  intent. `references/cell-contract.md` explains why the three pages have different bars.
- **Do not set `status` on a story.** `gap` belongs to draw mode, where there is a codebase
  a story can be absent from.
- **Do not decide the first release.** Draw what they say the first release is, including
  when you think it is too big. If you think it is too big, say so once, in one sentence,
  and then draw theirs.
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

**4. The first release — the one that makes it plannable.** Ask it in these words, or as
close as the room allows:

> If we could only ship a thin line through this whole story, what is the smallest set of
> these that a person could still complete the journey with?

Then draw the line. Everything above it is release 1; everything below is later. A release
is a horizontal band across every activity, which is why the question is about a *line*
and not about a list of features.

Write these as `releases[]` and `stories[].release`.

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
