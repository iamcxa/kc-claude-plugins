---
id: z74a3zvpbdhekrdsmy5dgnm9
title: kc-nightwatch is deprecated in intent and fully published in fact
status: backlog
source: 'Captain ruling 2026-08-23 — "very close to A, but for now we use B": deprecate in place rather than retire, with retirement the intended destination'
product: kc-nightwatch
sprint:
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
---

## Problem

The Captain has stopped investing in `kc-nightwatch`, and nothing in the
repository records that. Measured against `origin/main` on 2026-08-23:

- `.claude-plugin/marketplace.json` lists it at `0.5.1` with `source:
  ./kc-nightwatch`, so anyone can still install it.
- `release-please-config.json` still carries it as one of seven components, so
  it still receives version bumps and tags on any change.
- `README.md` mentions it three times and the root `CLAUDE.md` twice, both
  describing it as one of the repository's seven plugins.
- Its last code commit is 2026-07-26.

The cost is not to a user today; it is to the next reader. This session counted
its 49 test files as an unmet CI-coverage obligation and shaped work around
them before the Captain said the plugin was deprecated. An agent reading the
repository has no signal that would have prevented that.

## The Captain's ruling, and what it excludes

**B, not A.** Mark it as not invested in; leave it published. Do **not** remove
the marketplace entry, do **not** remove the release-please component, and do
**not** hand-edit any version — release-please owns those, and removal is the
separate decision below.

**A is the intended destination.** Retirement — marketplace removal,
release-please component removal, README rewrite, directory disposition — is
where this is heading, and it is a different work item with a public
compatibility surface. Do not start it here. The trigger for opening it is the
Captain saying so, not a date and not this item's completion.

## What ideation must decide

Where the status is written so a reader meets it before investing. Candidates,
not a decision: the plugin's own `README.md`, its `CLAUDE.md`, the root
`README.md` row, the bespoke marketplace `description`. Each has a different
audience — a marketplace description is read before installing, a plugin
`CLAUDE.md` is read by an agent already working in the directory, and this
session's failure was the second kind.

## Value AC candidate

Not "a line was added". Something a reader or an agent would actually hit: a
grep or a read that a coverage or planning pass would perform, and that now
returns the deprecation, where before it returned nothing.

## Work profile receipt

## Accepted outcome and non-goals

## Acceptance evidence

## Measurement
