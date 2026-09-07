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

### `kc-plan-value` — decide what to build

Initiative, project and issue each name a user-visible outcome. One issue is one
value point and its acceptance is something a person does. It names no file: the
moment a path appears, the author has stepped into the archaeologist's seat
without the archaeologist's evidence.

Milestone descriptions are three sentences — what done looks like, when it
ships, and the boundary or the cost of cutting it.

It ends by handing the archaeologist a list of questions, phrased as questions.
A request to confirm returns a confirmation; the seat answers the shape it is
asked.

### `kc-plan-detail` — decide how to build it

Cuts each value issue into sub-issues along what the archaeologist found
missing, not along architectural layers. Slicing by layer produces a serial
chain where no single ticket delivers the value.

Verification lives here rather than in a downstream gate. Deciding how to build
something is the same act as finding out what is already built, and a reviewer
catching a wrong file afterwards means two people did the job badly.

It writes in the format `plan-lint.py` reads, and runs it. That format is not
negotiable and a near miss is silent: seven acceptance criteria once reported as
`0 ACs` for want of a bullet marker.

## What is not here yet

Four rules for `plan-lint`, each earned by a defect in the same session:
milestone/repo coherence, parent-not-earlier-than-child, state backed by a
merged pull request, and a `Supersedes:` line on every new issue.
