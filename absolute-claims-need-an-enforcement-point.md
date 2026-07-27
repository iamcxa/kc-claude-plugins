---
title: An absolute claim in prose needs an enforcement point or a bound
status: done
source: EM validation gate on qh (#67), 2026-07-27 — third and fourth occurrence of the class in two days, across two different authoring agents
design:
id: 4nrx4be9bt2741zrwqase1nf
started: 2026-07-27T17:27:03Z
pr: direct-commit:2527c78
verdict: passed
completed: 2026-07-27T17:27:43Z
---

Four times in two days a document or comment asserted a guarantee its enforcement point does not
make. Each shipped: each passed CI, each was read by a reviewer, and each was caught only by a
later adversarial pass that went looking for it.

- `sv` (#63) wrote "leaves **exactly one path** to the POST" into `reference/review-runtime.md`.
  Feeding `{"reviews":[42]}` walks a second path and reaches a live POST.
- `qh` (#67) wrote "mirror the helper's calendar semantics **exactly**" into a commit message.
  `18446744073709551616` returned `1970-01-01T00:00:00Z` where the Python reference raises
  OverflowError — in both signs.
- `qh` wrote "temp_events **is** byte-for-byte the log validated above" into a code comment. It is
  an assumption about a window, not a property the code establishes.
- `qh` wrote that the batch falls back "whenever ... its record count disagrees with the file" into
  `reference/review-runtime.md`. That cross-check runs on neither caller-supplied path.

The authors were **different agents**, which is what makes this a class rather than a habit.

The repo already has the downstream half of the rule: `docs/dev/README.md`'s validation stage
requires a doc diff stating an absolute to name the input that would falsify it. That clause works
— it caught all four. But it is a *gate-side* rule, so the cost is paid every time by a reviewer
hunting for a counterexample, and it covers doc diffs only: two of the four above are a commit
message and a code comment, which no gate reads.

The missing half is authoring-side: an absolute — "exactly", "only", "always", "never",
"byte-for-byte", "cannot" — written into a reference, a comment, or a commit message must either
name the enforcement point that makes it true, or be rewritten as the bounded claim the code
actually supports. `qh`'s return round did exactly this by hand for all four sites and it cost
minutes; the differential test it added converts one of them from asserted to checked, which is
the shape to generalise.

Open question for the captain, not for the FO: whether this is a prose rule in
`docs/dev/README.md` plus `kc-pr-flow/CLAUDE.md`, or also a diff-time lint that greps added lines
in `reference/**`, `*.md`, and comment bodies for the absolute vocabulary and asks for a citation.
A lint is mechanically cheap and would be the first check in this repo that reads prose for a
claim rather than a format — that is either the point or the reason not to.

**AC-1 — An absolute claim added to a reference, comment, or commit message names its enforcement point or is bounded.**
Verified by: the rule stated in the canonical doc, plus a re-audit of the four sites above showing each now cites a test, a code path, or a stated exception. Falsified by: a new absolute landing with neither.

## Rule landed 2026-07-27 — remaining scope is the lint question only

The prose half shipped in `2527c78` as **Proof Policy #6** in `docs/dev/README.md`, with a
one-line pointer in the repo-root `CLAUDE.md` (that file loads every session; commit messages
pass through no gate). Placed in Proof Policy rather than the validation stage deliberately: it
is rule 2 — *evidence must be able to fail* — applied to prose, and Proof Policy binds in every
stage report rather than at one gate, which is what moves it from gate-side backstop to
authoring-time control.

All four originating sites are already corrected: `sv`'s "exactly one path" in its validation
round, and `qh`'s "mirror exactly", "byte-for-byte", and "record count disagrees" in its EM
return round.

One clause was added that the original entity did not have, earned the same day: **a claim
inherited from a report, a reviewer, or an external contributor is not exempt.** Maintainer
feedback on `kc-pr-review` reported that a `codex exec` output file "stays 0 bytes for the whole
run". Measuring it before adopting the wording showed that is true only for plain mode — with
`--json` the file grows within four seconds — which relocated the fix from "document the
ambiguity" to "stop prescribing the mode that has it". Adopting the claim unchecked would have
written a wrong fix into the skill, inside the very slice about incomplete failure-mode docs.

**What remains for the captain**: whether a diff-time lint should also grep added lines in
`reference/**`, `*.md`, and comment bodies for the absolute vocabulary and demand a citation.
That is the only open scope; the rule itself no longer needs a slice. Arguments both ways are in
the section above — cheap to build, and it would be this repo's first check that reads prose for
a claim rather than a format.

## Process note: this entity did not pass a validation gate

Recorded because the alternative is a `done` that implies a ceremony which did not happen — the
failure mode Proof Policy #6 itself exists to prevent.

The rule landed as a **captain-approved direct commit to `main`** (`2527c78`), decided in session
when the captain asked where the rule belonged. It had no PR, no CI gate beyond the repo-wide
checks that run on `main`, and no validation stage. That is defensible for a canonical-doc
revision the README already assigns to "captain-approved revision", and the change is prose with
no executable surface — but it is not the `done` the README defines, which is "merge after a
passed validation gate (merge policy: PR to `main`)".

`status: done` is set with `--force` for that reason. The ledger row records 0 dispatches and 0
rework rounds, which is accurate and also the tell: nothing reviewed this but the captain.

Worth deciding separately, and not decided here: whether canonical-doc revisions should route
through a PR at all, or whether the README should say plainly that captain-authored doc changes
are exempt. Right now the flow has neither, so each one is improvised.
