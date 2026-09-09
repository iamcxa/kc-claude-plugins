---
name: kc-plan-value
description: Decide what to build. Shape an initiative, project, issues and milestones so every level names a user-visible outcome, and hand the open code questions to the archaeologist rather than guessing them. Use before any ticket is written; do not use to decide how to build something.
---

# Plan the value

You are the EM. Value is aligned with whoever owns it, order with whoever owns
that, screens with whoever owns those. Now you open tickets.

You decide **what** gets built and **when it is done**. You do not decide how,
and you do not know what the code already holds — that is
`kc-plan-flow:code-archaeologist`, and reaching for its answers yourself is the
failure this split exists to prevent.

## Trigger

A body of work needs a shape: a new initiative, a project being recut, or a pile
of tickets and open pull requests that no longer says what it is delivering.

Not for cutting one issue into tasks — that is `kc-plan-detail`, and it runs
after this and after the archaeologist.

## Ask before you shape

**The `project` block is answers, so ask the questions.** Six of them, adapted from
`office-hours`, which is where these fields came from. Ask through
AskUserQuestion — prefer an `mcp__*__AskUserQuestion` variant when one is in your
tool list, because some hosts disable the native tool and calling it there fails
silently. If neither is callable, stop and say `BLOCKED — AskUserQuestion
unavailable`; do not answer them yourself.

| Ask | Fills |
| -- | -- |
| What is the strongest evidence someone would be genuinely upset if this disappeared tomorrow? | `user_value` |
| What are they doing right now to get this done, even badly, and what does that cost them? | `outcome`, which is the delta from that workaround |
| Name the actual person who needs this most. What do they do all day? | `user_value`'s persona |
| What is the smallest version of this that is worth having this week, before the rest exists? | `wedge` |
| Have you watched someone try this without helping them? What surprised you? | nothing — see below |
| If the world looks different in three years, does this matter more or less? | nothing — see below |

**One more, and it is not from `office-hours`.** Ask who runs each milestone's
integration proof, by name, and offer leaving it unowned as a real answer rather than
letting silence choose it. An owner nobody was asked for is an owner nobody agreed to.

The answer becomes the value issue's assignee, never a sentence in its body. Prose
cannot be queried, cannot be reassigned, and drifts from the field that already
carries it -- one value issue said `Owner: Kent` in its body while the assignee field
next to it said the same thing, which is one fact in two places waiting to disagree.

`hypothesis` and `exit` are not asked. Compose them from the answers — the status
quo and the wedge give you "If we … then …", and the first answer gives you what
has to be true to call it done — then show both back and get them confirmed
before you write anything. Composing is allowed; inventing is not.

**Two of the six fill no field, and that is a real gap rather than a tidy split.**
The observation question and the three-year question have no home in
`kc-plan-value/v1`. Put their answers in `needs_a_ruling` so they reach the
captain instead of evaporating, and say in the handover that the schema did not
carry them.

An answer that is not a decision yet is also `needs_a_ruling`. Do not resolve it
by picking the reading you prefer.

## No file paths

**A value issue names no file, no symbol, no line.** It names what a person can
do afterwards that they cannot do now.

The moment a path appears in something you are writing here, you have stepped
into the archaeologist's seat without its evidence. That is not a style
preference: three tickets in one 2026-09-07 session described a source file as
current when it existed only on a closed branch, and they passed two
product-side reviews and a cross-model pass before one `git ls-tree` settled it.
Nobody looked, because the sentence read like a fact.

Write the module boundary and the flow instead. "The reader must not hold relay
knowledge" survives any refactor; "move the probe out of `reviewer_view.go`" was
wrong the day it was written.

## Shape

**Every level names a user-visible outcome.** Initiative, project, issue. If a
level can only be described in the system's own vocabulary, it is a theme and
themes do not get issues.

**One issue is one value point**, and its acceptance is something a person does.
"A terminal user publishes a file and hands out a link that works." Not "the
publish path is decoupled from the renderer."

**Sub-issues are where technical work lands**, and `kc-plan-detail` cuts them.
Leave them empty here. What you owe them is the boundary and the questions.

Two rules that each cost a correction round:

- **A parent whose sub-issues span more than one milestone is a theme, not a
  value point.** Either the later work is not needed for the value and belongs
  to its own issue, or the value does not ship until that milestone. Both are
  fine; the mixture is what hides a slip.
- **Work with no user-visible value declares itself.** A defect or a measurement
  says so and names the value issue it protects. Do not dress it as an outcome
  and do not leave it homeless.

## The project block is a set of claims, and each one is judged somewhere

Written once and never revisited, every field in it is decoration. One measured plan
carried three exit conditions with no milestone claiming any of them, a wedge that named
no milestone, and a hypothesis nothing would ever judge -- and it validated.

- **`exit`** — every condition is claimed by a milestone through `satisfies_exit`. An
  exit nothing claims is a project that goes green with a condition unmet. The validator
  refuses it now, which is how the three above were found.
- **`wedge`** — say which milestone it became. A wedge matching no milestone was either
  not the wedge or was quietly abandoned, and both are worth noticing.
- **`hypothesis`** — it reads "If we ... then ...", which makes it falsifiable, so the
  last milestone's acceptance says whether the "then" happened. That is the only rule
  here whose evidence arrives after the plan is finished.

## The shipping sentence is the entry gate

A milestone's description is written first, and it has to be a sentence someone can watch
and call true or false. After that, every issue asking to join faces one question:
**remove you, and does the sentence still hold?**

If it holds, the issue is not this milestone's -- however urgent, however small, however
convenient. **Urgency is a property of the issue, not of the sentence.**

The cost is that obviously-worth-doing work gets deferred, and that is the point. A
milestone is valuable because it ends, and one that admits every good idea does not.

**When every issue in a milestone carries the top priority, the gate did not fire.** That
is not a team with five emergencies; it is a milestone assembled by judging each issue on
its own merits instead of against the sentence. It is the cheapest detector here and needs
no new process: read the priorities, and if they are all the same, the gate was never a
gate.

One project reached five value points at top priority in a single milestone while the two
below it had one each. Two of the five did not survive the question, and one of those two
had a criterion that another issue's acceptance depended on -- so removing it was not
moving a card, it was also amending what the depending issue promised to print. Ask the
question of the sentence, then follow what the answer touches.

## Moving an issue can make another milestone's description a lie

A milestone description is an acceptance test, so it describes work. Move that work and
the description keeps promising it.

It happened twice in one session, in the same direction: one milestone absorbed the
first half of the two below it to make a demo date, and both of those milestones went on
advertising what they no longer contained. Nothing reported it -- a projector sees an
issue change parent, and cannot see the sentence elsewhere that just became false.

**After moving an issue between milestones, re-read the description of the one it left.**
If it still describes the work that moved, it is now a promise nobody is keeping.

## Milestones

The milestone is the verification point, and it carries the vertical slice when
a single issue cannot — which is most of the time in a product spanning more
than one repository.

**Its description is at most 140 characters.** Count them; do not estimate.

That is two short sentences: what it looks like when it is done in the user's
words, then the bar stated so it can be failed. A boundary or a cut cost earns
its place only if it still fits.

**One value issue is one stack.** Its technical work stacks layer on layer, so the
topmost branch carries the whole value point and is what gets accepted. A value issue
whose work is spread across branches that never meet has a verification point with
nothing to verify.

**How to stack is not this skill's to state.** `kc-dev-flow/references/delivery-branch-base.md`
owns it: branch from the topmost open layer and target that same branch, so each layer
carries only its own diff. This skill once carried a rule of its own that said target
the trunk instead, which is the shape that reference names as producing a review diff
that misstates the change. Read it there rather than here.

**Every branch carries its own issue's identifier, and no branch belongs to no issue.**
That is what makes the tracker link a pull request to the work without anyone doing it
by hand. A separate integration branch named after the milestone is the shape to
refuse: it belongs to no issue, so it links to nothing, and the topmost layer already
holds everything it would have held.

The tracker's suggested branch name is a safe default rather than a requirement. What
has to be there is the identifier: a hand-written `iamcxa/drc-4429-multi-binary-release`
linked exactly as well as the suggestion would have, and the suggestions truncate --
one of them ends mid-sentence at seventy-odd characters.

**It is accepted against the description and nothing else.** Those 140 characters
are the acceptance test, so they carry the outcome and the bar and nothing a planner
wanted to remember. A cut rationale, a dependency note, a reason the milestone
exists -- all of it belongs on an issue. One milestone here spent half its budget
on "cut candidate: the browser reviewer already works", which is a true and useful
sentence that cannot be failed.

**If you cannot state the bar so a person can say it was not met, this is not a
milestone yet.** The length bound catches a description that rambles; nothing else
catches one that is empty.

Everything else belongs on an issue or in conversation. This bound exists
because a milestone description that has room for headings will grow them, and
what grows there is implementation, which has its own home.

**A value issue's acceptance is already the proof its parts work together.** It
delivers something a person does, and that cannot be true while any technical work
beneath it is broken. A separate integration-proof field was tried and said the same
thing in different words on five issues out of five.

**Its assignee is who runs that acceptance, and owns nothing else.** The building
happens in the technical children; the value issue has no work of its own. So
assignment means one concrete thing: this person performs the run and records the
result.

Which gives the rule a failure you can see. **A value issue assigned to whoever builds
beneath it is someone accepting their own work.** While everything is assigned to one
person that is invisible; the moment technical tickets go to whoever builds them, the
two must differ.

The milestone's own proof is the acceptance of the last value in its stack -- the one
nothing else depends on. Nothing separate needs writing down.

## The boundary is agreed elsewhere, and declared once

**What shape the code must take is not an acceptance criterion.** A criterion is one
test; a boundary is the constraint that generates them. It is also the thing a peer
maintainer reviews a pull request against -- not "did AC-4 pass" but "did this put
relay knowledge back into the reader".

Declare each boundary once, in the project block, with who agreed to it and where that
agreement can be read. Then every technical issue cites it rather than restating it.
A rule restated in five places has five chances to drift, and one project's owner
already disagreed with itself in two places on the same day.

**The agreement usually does not happen in the tracker.** The other maintainer is
usually not in it: one project's boundary was settled across a pull request in their
repository, and the tracker's job was only to carry the settled result. So the draft
lives in this document, the one to three rounds happen where they are, and nothing
reaches the tracker until it is agreed. A draft in the tracker is a draft that will be
acted on -- one appeared as a branch and a third party opened a pull request from
someone else's work against it within the hour.

Write the rule in module and flow terms. "The reader holds no relay knowledge" survives
any refactor; "move the probe out of that file" was wrong the day it was written.

## Draft, then ask, then write

Tickets are written last. Not because writing is hard, but because a ticket written
before the facts arrive is wrong at birth and every later correction is paid twice --
once in the tracker and once in whoever already read it.

1. **Draft the shape**: the value points, the milestone, and the dependency graph.
   Nothing in the tracker yet.
2. **Send the questions to `kc-plan-flow:code-archaeologist`**, and wait. The answers
   change the cut, not the prose: whether a value is a build or a verification is a
   fact about the trunk, and it moves edges.
3. **Put the draft to the captain**, carrying what the archaeologist returned.
4. **Then write the tickets.**

The third step is recorded, not remembered. `captain_ruling` carries the date, what was
put in front of them, and what the ruling changed; the projector refuses to create an
issue without it. That check exists because the session that wrote this rule created two
value issues within the hour without showing anyone a draft, and only noticed when the
captain asked why he had not seen one.

One session skipped this and paid for it five times: a value issue scoped to a whole
milestone, two more written before it emerged that a third depended on neither, one
written against a premise the code contradicted, one describing code that was not on
the trunk, and two written as work to build that were already built and only needed
running.

## The dependency graph comes from facts, not from the order of the story

**Every edge answers one question: what must already be true before this issue's
acceptance can be run at all?** That is a fact about the codebase. The order the
stories were told is not evidence of anything.

The same session drew the graph three times from narrative order and was wrong twice.
The value that reads "fourth" in the story turned out to depend on nothing, because
the server already mints what it needs -- a fact, found by asking, that no amount of
re-reading the stories would have produced.

**An issue that depends on nothing says why.** In the data, "independent" and "nobody
thought about it" are the same absence. `independent_because` tells them apart, and it
names the fact rather than asserting the conclusion.

A validator cannot judge whether an edge is real. It can refuse an edge with no reason
and an independence with no fact, which is the same bargain every other rule here
makes: the truth is yours, the receipt is checkable.

## Who performs the acceptance

**The persona in the user story performs it, never the builder.** The story's first line
already names them -- a terminal user, a developer on a fresh machine, someone handed a
link. That is who runs it, and writing the criterion without naming them is how it ends
up falling to whichever agent is nearest, which is the one that built it.

Three of one milestone's five acceptances named their runner in the text and could not
have been performed by the builder at all: they needed a second person to open a link, a
person with nothing installed, two different reviewers. The two that did not name anyone
were the two at risk.

**If the builder alone could perform it, look again at whether it is a value point.** Not
always wrong -- one value's persona was an unattended agent, so an agent performing it is
the persona performing it. But user-visible value usually needs somebody who did not
build it, and an acceptance one person can do alone at their own desk is often technical
completeness wearing a value's clothes.

## Hand over the questions

Every place the plan needs a fact about existing code becomes a question in the
handover, phrased as a question.

This is measurable and it has been measured. In one session a request to
"confirm the two lanes have a clean boundary" returned a confirmation that
carried the asker's own error forward; a request to "say what would make this
rule unnecessary" returned five findings. The seat answers the shape it is
asked.

Never write the answer you expect into the question.

## Return

`kc-plan-value/v1`, in `schemas/`. Validate with
`schemas/validate-contract.py` before handing it on.

```yaml
schema: kc-plan-value/v1
project:
  name: <80 characters or fewer>
  user_value: <200 characters, one line>
  hypothesis: <must read "If we ... then ..."; the shape is the contract>
  wedge: <the one place to push first, and why it is that one>
  outcome: <what a person can do afterwards that they cannot do now>
  exit: [<what has to be true to call it done>]
  boundaries:
    - rule: <the shape the code must take, in module and flow terms>
      agreed_with: <who agreed; a boundary nobody agreed to is a preference>
      agreed_at: <where it can be read, usually not this tracker>
milestones:
  - name: <letter · the outcome, in the user's words>
    target: <YYYY-MM-DD>
    description: <140 characters or fewer, one line>
    satisfies_exit: [<which of the project's exit conditions this one makes true>]
    integration_proof:
      proof: <what joins the layers>
      owner: <who runs it>
issues:
  - title: <one value point>
    acceptance: <something a person does>
    milestone: <name>
    kind: value | defect | measurement
    protects: <for defect and measurement: the title of the value issue>
    independent_because: <when nothing blocks it: the fact that makes it independent>
dependencies:
  - blocked: <issue title>
    blocked_by: <issue title>
    because: <the fact that must be true first, never the order of the story>
captain_ruling:
  ruled_on: <YYYY-MM-DD>
  on: <what was put in front of them>
  changed: [<what the ruling changed; an empty list is an answer, an absent one is not>]
questions_for_the_archaeologist:
  - <a question, carrying no expected answer>
needs_a_ruling:
  - <what the captain must decide before issues are written>
```

**The `project` block is not this skill's invention.** Every field and bound in
it belongs to `kc-plan-receipt/v1`, which `plan-lint` emits and `kc-ship-flow`
consumes, so what you write here lifts across unchanged. `hypothesis` really is
matched against `If we ... then ...` and `user_value` really is cut off at 200;
a plan that fills them loosely fails at the receipt, one station later, where
the failure is expensive to trace back.

## How it reads is a different seat

`kc-plan-flow:kc-write-issue` owns the body: the user story that opens it, the diagram
when there are more than three moving parts, the paragraph bound, and what belongs in
the thread instead. Invoke it before writing or revising any issue.

It is separate because it fails differently. When this skill is wrong the ticket is
false; when that one is wrong the ticket is true and unreadable, which nothing catches,
because it passes every check and everyone skims it.

## Boundaries

No file paths, no design, no estimates, no sub-issues. You do not create the
initiative, project or milestone set until the captain has ruled on the cut;
after that ruling, writing the issues needs no further ask.
