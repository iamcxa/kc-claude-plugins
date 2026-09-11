# Plan a story map

A journey YAML file names `journey`, `persona`, and `one_journey`. Its ordered
`steps` contain stable `id`, `card`, optional `activity`, and ordered `stories`.
A story is a string or `{id, card, release}`; give it an explicit id when moving
it between releases. Ordered `releases` contain `{id, name, goal}` and represent
user value across the activities, not time periods. Unassigned stories remain
visible. Optional `now` cards describe the person's existing world; `ownership`
bands name an owner and `from`/`to` activity ids.

`journey-render.mjs` draws the story map and reports each release's activity
coverage. Use `journey-read.mjs` to inspect canvas changes; `--out` saves a review
copy and `--write` applies supported wording, activity order, story priority, and
release movement. Release membership is read from the story's top edge relative
to release lines; retain those lines and their order when moving stories.

Duplicated activity or story identities are excluded from wording/membership
readback; an activity reorder is refused while identities are duplicated.
Unclaimed cards are reported with their column only when overlap is unambiguous.
They are never inserted into YAML automatically. A card straddling columns needs
a person's placement decision. Readback does not apply arbitrary page text.

Exercise these rules with `node --test lib/read.test.mjs lib/storymap.test.mjs`
and the server round trip with `bash scripts/canvas-smoke.sh`.
