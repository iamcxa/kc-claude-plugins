---
name: kc-plan-flow-kernel
---

# KC Plan Flow Shared Core

Load this for every seat in this plugin. It owns how a claim is made and checked;
each seat owns its own decision. Every rule here was stated in three or four skills
separately before it was pulled into one, and the duplication is what made it worth
extracting: the same sentence in four files drifts in four directions.

## A question is not a confirmation

**Ask what is there. Never ask whether what you believe is there.**

"Where does X live so we can move it" is a request to agree with you, and it comes
back agreed. "What decides X today, and on which ref" is a question, and it comes back
with an answer you did not have.

Measured once: a request to "confirm the two lanes have a clean boundary" returned a
confirmation that carried the asker's own error forward; a request to "say what would
make this rule unnecessary" returned five findings. The seat answers the shape it is
asked.

This applies to every seat, not only to the archaeologist. A captain asked to approve a
draft will approve it; a captain asked what the draft gets wrong will tell you.

## Every claim carries the command that produced it

A classification with no command is an opinion. A finding with no `did_not_check` is a
bounded search wearing an unbounded conclusion.

**Cite by greppable symbol and name the ref.** A line number is convenience and goes
stale silently; a symbol fails loudly. A file described as current that lives only on a
closed branch is the same failure one level up, and it has happened here three times: a
ticket describing a latent defect in code absent from the trunk, a ticket proposing to
replace a script absent from the trunk, and a merged protocol document describing a
route the trunk does not serve.

**Two searches bound a claim; they do not prove absence.** State what you searched and
where you stopped.

## Read the current state before answering a question about it

**An estimate measures the distance from the trunk. "Will it finish" measures the
distance from now.** Using the first to answer the second counts finished work as
outstanding.

One milestone was declared at risk on an arithmetic of points against days. The ticket
carrying more than half of them already had a pull request of 2150 lines across 17
files, with evidence recorded against every acceptance criterion, and its own body said
which downstream ticket could start immediately. Four conclusions rested on that
arithmetic and all four were wrong, because none of them cost more than one command to
check.

**The cheapest source of "where is it now" is the person doing it, then their pull
request body, then reasoning. Reasoning is last and it is where this went wrong.**

## Check, do not remember

A rule enforced by being read is enforced by whoever reads it, and a fresh session
carries nobody's corrections.

The session that added a mechanical gate for one rule went on, the same day, to add
five more with no gate at all and call them the same kind of thing. When a prose rule
fails again, that failure is the evidence for making it mechanical — not an argument
for reading harder.

**A rule that belongs to the work belongs in the contract, not in an agent's memory.**
Memory is remembering, and it reaches one agent.

## Nothing is added without a reader

A field added to a schema with nothing consuming it is the same defect as a rule with
nothing checking it. Both look like progress and neither changes an outcome.

Two fields were added here in one session with no reader, immediately after that
session had diagnosed exactly that pattern elsewhere. Before adding a field, name what
reads it; before adding a rule, name what fires.

## One fact, one home

The same fact in two places disagrees within the hour. Observed four times in one
session: an owner named in prose beside the field carrying the same name, a boundary
pasted into a description while a contract field held it, a read-back promise made by
two milestones and denied by a third, and a verification record duplicated between a
body and a thread.

**Declare once, cite everywhere else.** When a fact has a structured field, prose does
not get a copy.
