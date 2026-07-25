---
id: q8mtmw73f265x67564gpwend
title: Fill the empty candidates list for unknown element and page names
status: backlog
source: FO finding while gating gz, 2026-07-25 — restores the headline promise of [[e2e-json-diagnostics]]'s Problem statement, which its own approved scope cut
started:
completed:
verdict:
worktree:
issue:
pr:
design:
---

## Problem

[[e2e-json-diagnostics]] opens by promising that an agent hitting an unknown-element error
has no path to the fix except reading the whole mapping YAML back into context to discover
the real name was `submit_button`. It shipped without solving that: for the not-found class
`candidates` is `[]` by design, and the error still reads `not found in mapping` with nothing
after it. Nearest-match was cut in the FO's own ideation scope note and ratified at the gate —
a defensible cut, but it removed exactly the entity's headline promise, so the promise now has
no owner.

This entity fills that array: when an element or page name is absent from the symbol table,
propose the closest names the table does contain.

    today:  expect element 'submit_btn' not found in mapping
    after:  { got: "submit_btn", candidates: ["submit_button", "submit_btn_secondary"] }

The channel to carry this already exists — [[e2e-json-diagnostics]] built it. This is what
flows through it for the not-found class.

**Do not size this from the corpus count.** The corpus shows only 4 not-found cases, which
reads as "rare" and is misleading: the corpus samples flows that already exist and mostly
already work, while a not-found error is what an author hits when writing a NEW flow with a
typo. The corpus structurally cannot see the population this feature serves. Ideation must
find a different instrument — authoring-time observation, seeded typos, or session history —
before concluding the value is small. Getting this measurement wrong in either direction is
the main risk.

Note the sibling constraint from [[e2e-json-diagnostics]]: no `code` field until
[[e2e-schema-contract]] lands. This entity adds data to an existing field and does not need
to reopen that.
