---
name: kc-write-issue
description: Write the body of a tracker issue so a person can act on it. Use whenever kc-plan-value or kc-plan-detail is about to write or revise an issue; not for deciding what the issue is, which those two own.
---

# Write the issue

Load `references/kernel.md` first. It owns how a claim is made and checked -- asking rather than confirming, citing by symbol with its ref, reading current state before judging it, checking rather than remembering, adding nothing without a reader, and one fact with one home. This file owns only what is left.

`kc-plan-value` decides what is true. `kc-plan-detail` decides how it gets built. This
decides whether either of them can be read.

They fail differently, which is why this is its own seat. When the first two are wrong
the ticket is **false**. When this is wrong the ticket is **true and unreadable**, and
nobody notices, because it passes every check and everyone skims it.

## The test

**For every sentence: whose action changes without it?**

Not "is it true", not "is it useful background". If no reader does anything differently,
it is spending attention and returning nothing.

One value issue lost sixty per cent of its body to this test with no action lost. What
went:

> This is milestone A's value point. It names no file and no symbol on purpose: the
> surfaces that deliver it are its sub-issues, and they are the ones allowed to name code.

That is the planning rule explaining itself. A reader who does not already know the rule
learns it here and still does nothing differently; a reader who knows it skips.

> so the proof that joins them has an owner rather than being implied by three green tickets

That is the design defending itself. The defence belongs in the thread where someone
challenged it, not in the body every future reader pays for.

## Shape

**Open with the user story.** `As a <who>, I want <what>, so that <why>.` One sentence,
first line, before any heading. A reader who stops there knows what this is for.

**Then a diagram, when there are more than three moving parts.** Linear renders mermaid.
A flow of five steps is a picture, not a paragraph; a paragraph describing five steps is
a picture the reader has to draw themselves.

**Acceptance as Given-When-Then.** `Given <state>, when <action>, then <result>.` It
forces the state you forgot to name and the result you were about to leave implied.

**Paragraphs under 300 characters.** Not a style preference: a long paragraph in a
tracker is where scope hides, because nobody re-reads the fourth sentence.

## What does not belong in the body

| Not this | Because |
| -- | -- |
| A rule explaining itself | The reader either knows it or does not need it here |
| The design defending itself | That belongs where it was challenged |
| Anything a structured field already holds | One project wrote `Owner: Kent` beside an assignee field saying the same name; two copies of one fact, waiting to disagree |
| The search that found the surfaces | It ages at the speed of the codebase. One six-surface list named a symbol renamed the same day work started against it |
| An outcome restating its own criteria | A reader checking whether two passages agree is doing the work the format was supposed to save |

The last two go to the comment thread rather than the bin. `plan-lint` reads the thread,
so a verification record still has to exist and still has to be fresh — it just stops
occupying the first screen.

## Voice

Write the way a person writes to another person who has to do something today.

**No bolded run-in on every paragraph.** It reads as generated, and when everything is
emphasised nothing is. Bold the one sentence that changes what someone does, or none.

**Say the narrow thing.** "Cannot be stated ahead" earned a correction; the true sentence
was "retention is per-deployment configuration that no read route reports". A limit
inherits the scope of whatever imposes it — this function, this client, this protocol, or
the domain — and only the last is a constraint on anyone else.

## Before you save

1. Delete every sentence that fails the test above.
2. Count the paragraphs over 300 characters. Split or cut them.
3. Find every fact that also lives in a field, and delete the prose copy.
4. Move the verification record to the thread.
5. Read the first three lines alone. Do they say what this is and who it is for?

## Boundaries

You do not decide scope, value, acceptance or ordering. If a sentence is unreadable
because the underlying decision is unclear, say so and stop — rewriting prose over an
undecided cut produces a clear description of a wrong plan, which is worse than an
unclear one because it stops looking like a question.
