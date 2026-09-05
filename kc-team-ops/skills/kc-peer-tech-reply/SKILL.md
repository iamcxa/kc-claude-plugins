---
name: kc-peer-tech-reply
description: "Use when drafting a technical reply Kent will send under his own name to a peer maintainer — a PR comment answering an architecture proposal, a cross-repo boundary negotiation, an issue reply about a contract between two codebases. Produces a diagram + table + pseudocode reply sized to the incoming message, with every technical claim verified against source first."
---

# Peer Technical Reply

For a reply between two maintainers who each own a repo. Not for a status update, not for a review comment on code you own, not for a message to a non-technical reader.

Kent sends it under his own name. You never send it.

## The failure this skill exists to prevent

One session, 2026-09-04, drafting a reply to a peer's architecture proposal. Eleven separate push-backs before it was sendable, and only one of them was about tone. Counted by cause:

| Cause | Count | Example |
|---|---|---|
| Claimed something about the codebase without reading it | 4 | Said one command was required to read feedback back. It was not: the other resolved the record from the URL directly. Two separate commands that happened to share a file. |
| Wrote a question I already had the answer to | 2 | Asked who would own a set of scripts after a split. The peer's own proposal answered it: the component that calls them sits beside them and knows its own path. |
| Reasoned about scope from a fact I never checked | 2 | Asserted nine PRs were three independent roots with none built on a particular one. `merge-base --is-ancestor`, run on every branch rather than two, showed one had merged that line into itself. |
| Length | 2 | 1397 words against an incoming 407. Cut to 573 with nothing lost. |
| Tone read as AI | 1 | Bolded run-in on every paragraph, "Agreed on the boundary" where a person writes "Yes to the boundary". |

Six of those eight were the same thing: **I answered from memory of the code instead of from the code**, and each was settled by one grep or one git command. The other two were answers sitting in the peer's own message, which is why re-reading it is a separate step below.

Then the reply came back and found a ninth, of a kind none of the above catches. See the next section.

## A limit found in code is scoped to that code

The message said the expiry could not be stated before publishing. That is what the code does, and a comment in it said so outright:

> *The expiry is deliberately absent: readExpiry is a second GET issued after the publish commits, so this prompt cannot know the date and will not invent one.*

Reading that felt like verification, so the sentence went out as a constraint. The peer replied that the expiry can be stated ahead, and he was right: the server derives it as `createdAt + retention`. The comment was accurate about why *that function* does not know the date, and I relayed it as why *nobody* can.

**The rule this needs already exists** in `kc-dev-flow/references/reverse-recovery-audit.md`: every non-runtime claim gets one command or observation that could disprove it. A sentence saying something cannot be done is exactly such a claim, and its hook is not "does the code say this" — it is *what would make this false*. Here that was one grep for where the expiry is computed. Finding a comment that agrees with you is not running the hook.

Two things follow for a reply specifically:

**A limit inherits the scope of the thing that imposes it.** Before writing "cannot", say who and when: this function, this client, this protocol, or the domain. Only the last is a constraint on the conversation. The others are things you could change or ask for, and stating one as impossible forecloses the cheapest route in front of the person it constrains.

**Say the narrow version.** The real limit here was that retention is per-deployment configuration no read route reports, which is why a smoke check has to publish something and derive the window from the result. That sentence asks for one route. "Cannot be stated ahead" earned a correction instead.

## Before drafting: the reverse-recovery pass

Adapted from `kc-dev-flow/references/reverse-recovery-audit.md`. In a peer reply the audit runs on your own questions rather than on planned work, and its limits axis is the section above.

**Assume the answer already exists.** For every question you are about to ask, and every gap you are about to name:

1. **Hunt for it in your own repo first.** Two search strategies minimum, domain nouns in every language the repo uses. "Not found after one grep" is the easiest false claim to make.
2. **Hunt for it in their message.** A proposal often answers its own downstream question. Re-read their text after you have drafted the question.
3. **Classify what you found** before writing about it: `WORKING` (runtime evidence — unit tests never qualify), `WORKING_UNIT_UNPROVEN`, `EXISTS_BROKEN`, `STUB`, `MISSING`.
4. **Two searches bound a claim; they do not prove absence.** State what you searched and where you stopped, and write the bounded sentence: not found across these branches, by these two strategies. In the 2026-09-04 session both "open questions" survived on exactly that evidence, and one still dissolved afterwards when a workaround turned up in a test file. That is the rule working, not failing.
5. **Carry a disproof hook** for anything you assert. The one command that would flip it. If you cannot name that command, you are not ready to assert it.
6. **Run the disproof hook on every limit**, not just on every gap. For "X cannot be done", the hook asks what would make that false, and the code that implements X today is not the answer.

A question that survives this pass is worth their attention. A question that does not survive it costs you credibility you will need later.

**One broken layer is not a missing capability.** It is broken at that seam, and the fix scopes to that seam. Saying "there is no mechanism for X" when the mechanism exists and has one bug reads as not having looked.

## Structure

Three parts, in this order. Nothing else.

1. **Respond to their proposal.** Adopt, or disagree with a reason. Name the one thing they contributed that you did not have — specifically, not as flattery. Then one sentence listing what you agree with and will not restate.
2. **What you bring to it.** A diagram, a table, or pseudocode. Existing argv and output, existing contracts, what changes and what carries over unchanged. Show, do not narrate.
3. **What needs them.** Only what genuinely crosses the boundary. Everything you can decide alone goes in a ticket instead, and say so in one clause.

If they said "we can settle X after we agree on this architecture", do not answer X. Acknowledge the sequencing in one line and stop.

## Length

**Target the incoming message's length. 1.5× is defensible; 3× is not.**

Measure it: `wc -w`. A reply three times longer than the proposal it answers signals that most of it is not about the proposal.

What earns space, in order: a diagram, existing contracts they will design against, a question only they can answer. What does not: your implementation choices, your schema designs, restating what you agree with, and the internal symbol names of files they do not maintain.

## Diagrams, tables, pseudocode

**A diagram carries the shape.** Mermaid. Every node and edge traceable to a line in their proposal or a file in the repo. Mark the uncertain edge as uncertain — a dotted edge labelled with the open question is worth a paragraph. Escape angle brackets as `&lt;` `&gt;` or GitHub eats them.

**A table carries a contract.** Existing argv and stdout lines, one row each. This is what they will design against, so every row is verified verbatim from source, and note when only part is consumed.

**Pseudocode carries a mechanism.** Two uses only: showing what happens today (so a change is visible as a diff), and showing where a gap is (so it names itself). Not for designing their side of the interface — proposing a schema for a surface they own reads as overreach even when the schema is right.

Do not write pseudocode for something a sentence carries.

## Voice

Run `kc-blog-voice` before presenting the draft, not after Kent asks. It ships separately, in `~/.claude/skills/kc-blog-voice`; if it is not installed, apply the bullets below directly and say in your handover that the voice pass was manual.

Two carve-outs for correspondence: keep it in the recipient's language (no bilingual mixing in a message to an English-only reader), and do not manufacture an analogy — that skill's own rule is that analogies must be the argument, not decoration.

What transfers, and what the 2026-09-04 session got wrong until told:

- **No bolded run-in on every paragraph.** `**Where rr lives.**` is navigation for a stranger. Two maintainers who both know the subject do not need a table of contents.
- **Kent uses a heading plus a newline, not a bullet with an em-dash.** `- argv shape` then the explanation on the next line. Not `- **argv shape** — explanation`.
- **No hard-wrapped prose.** One line per paragraph. Wrapping at 80 columns is a file-writing habit; GitHub rewraps, and your breaks only corrupt quotes and diffs.
- **Em-dashes: near zero.** Diagram labels may keep one. Prose uses a colon, a full stop, or a comma.
- **State a concession as a concession.** "That is the difference between moving code and actually gaining something", not a tidy technical proposition that happens to agree.
- **Honest uncertainty stays uncertain.** "Neither reads as obviously right to me" beats a preference politely deferred.

## Ownership boundaries

Between two maintainers, five things go wrong:

**Do not narrate the division of labour.** "Those are yours to rule; relay's wire is mine" states a fact that does not change by being said, and reads as drawing a line. The contract is implicit; leave it implicit.

**Do not hand back a decision they cannot execute.** If you will be the one opening the PR, "your pick" is hollow. Give your assumption and your reason, and ask them to redirect it if they disagree.

**Different focus is not disagreement.** When your list is longer than theirs, the reason is usually that you enumerated your repo's whole surface while they scoped to what ships. Say that. Do not frame it as them having missed items.

**Your repo's internal defects are not their evidence.** A bug in your own unmerged branch is not an argument about their interface, and citing it that way reads as blame. State the structural fact ("that surface has three phrasings, one of which our own consumer misses") and own the fix.

**Do not carry your own implementation questions into their message.** Whether to generate an OpenAPI, how to encode a filesystem-safe origin slug, which retention window applies — decide those, ticket them, and keep them out. A peer asked to weigh in on something they do not own has to spend effort to hand it back.

## Verification gate

Dispatch a fresh-context reviewer when the reply carries a contract the peer will build against, contradicts something they proposed, or makes a claim about their repo. A short adoption or a scheduling note does not need one — the kernel's rule is the cheapest instrument that can fail, and this is an expensive one.

When it fires: `codex:codex-rescue` at high effort or an equivalent, given the draft, their original message, and repo paths. Ask for a paragraph-by-paragraph audit grouped as factual errors, overstated claims, mischaracterisations of the peer, internal contradictions, design concerns. Require `file:symbol` evidence per finding.

On 2026-09-04 that pass returned eleven factual errors in a draft already revised four times. Two were mine to own specifically:

- **I had deleted a true claim** because my own search was too shallow to confirm it. The reviewer found `invocation_finish.go` writing the validated Result to stdout, with a comment saying so. Shallow verification is not only a false-positive risk.
- **My ancestry claim was half-tested.** I checked two branches and generalised to three.

Do not accept its findings unchecked either. Verify each against source before acting: in that same pass the reviewer called a `TMPDIR`-based discovery "a test-harness privilege" when setting a child's environment is something any parent process can do — and that error, once caught, dissolved one of the two remaining open questions.

## Checklist

- [ ] Every codebase claim has a file or symbol behind it, checked this session, supporting the exact proposition and not a neighbouring one
- [ ] Any claim quantified over a set ("all three", "none of them") checked member by member
- [ ] Reverse-recovery pass run on every question; each survivor has a disproof hook
- [ ] Every "cannot" carries its scope: this function, this client, this protocol, or the domain
- [ ] Re-read their message after drafting your questions; deleted the ones it answers
- [ ] `wc -w` on both; ratio under 2×
- [ ] Diagram nodes trace to their proposal or to source; uncertain edges marked
- [ ] Table rows verified verbatim; partial consumption noted
- [ ] No pseudocode designing their side of the interface
- [ ] `kc-blog-voice` applied; no bolded run-ins, no hard wraps, em-dashes near zero
- [ ] Nothing you can decide alone is in the message; it is in a ticket
- [ ] Fresh-context audit run if the reply carries a contract or a claim about their repo; every finding verified against source before acting
- [ ] Kent sends it
