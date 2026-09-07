# kc-plan-flow

The planning unit of the fleet. `kc-ship-flow/references/kernel.md` has named it
since DEV-117 — "three independent units — plan-flow, kc-dev-flow and
kc-ship-flow, connected only by versioned input/output contracts" — and this is
where it lands.

`docs/plan-flow/` already holds the mechanical half: `plan-lint.py` with rules
L1–L10 over a Linear project snapshot, a receipt schema, and an approval schema.
That half has no caller. This plugin is the half that produces a plan worth
linting, and the seat that keeps its facts true.

## What is here now

### `code-archaeologist` — skill + agent

Answers one bounded question about what a codebase holds today, with the command
and the ref that prove it. Sonnet, addressable across a planning session.

It reports; it does not judge. Contested judgment stays with
`kc-dev-flow:science-officer`, delivery advice with
`kc-dev-flow:chief-engineer`, and both of those are Opus seats for that reason.

**What breaks without it.** A planning session on 2026-09-07 produced three
tickets describing a source file as current. The file exists only on a closed
branch; the trunk has never held it. The tickets passed two product-side reviews
and a cross-model verification pass, and none of them looked. One
`git ls-tree` against the trunk settled it afterwards.

The seat's two questions come straight out of that: what is this, and which
layer is it from. The inventory answer was right — the probe did exist. The
dating was wrong, and dating is what a review does not check.

## What is not here yet

Two skills, in the order they will be built:

- **`kc-plan-value`** — align initiative, project and issue to user value. Each
  issue is one value point, and its acceptance is something a person does. It
  names no file; the moment a path appears, the author has stepped into the
  archaeologist's seat without the archaeologist's evidence.
- **`kc-plan-detail`** — cut each value issue into sub-issues against what the
  archaeologist found. Verification lives here rather than in a downstream gate:
  deciding how to build something is the same act as finding out what is already
  built.

Four rules for `plan-lint` follow them, each earned by a defect in that same
session: milestone/repo coherence, parent-not-earlier-than-child, state backed
by a merged PR, and a `Supersedes:` line on every new issue.
