# Run B — fallback questions, Input A (ship-flow contract enforcement), pm-skills uninstalled

`claude plugin list` confirms `problem-statement@pm-skills`, `epic-hypothesis@pm-skills`, and
`user-story-splitting@pm-skills` are no longer installed (only `kc-dev-flow`, `kc-pr-flow`, `spacedock` remain).
Only the fallback questions written into `kc-plan-flow/references/dialectic.md` are used below. Station 2 is not
re-asked of the Captain: Input A did not change between Run A and Run B, and the Captain's Q1–Q4 answers are
evidence about the requirement, not an artifact of which stations-1/3/4 skill produced the Brief — so this run
reuses the same verbatim station-2 answers from Run A (see `dialectic.md`'s note that station 2 is always the
FO's, independent of the stations-1/3/4 toggle) and applies only the station 1/3/4 fallback questions.

---

## Station 1 fallback

1. **Who specifically hits this, and what were they doing the last time it happened?** Ship-flow's only user is
   Kent (given directly by the raw requirement's context paragraph). "Last time it happened" is not a single
   incident — the raw material describes an ongoing gap (every PR ship-flow dispatches without these
   guarantees), not a one-off.
2. **What do they do today instead, and what does that cost them?** (Reusing the verbatim station-2 evidence,
   since it already answers this): Kent asks on every PR whether it is the smallest stack, whether without-it
   ran, and what was verified; he UATs by hand, reading the diff and LOC for stray files, excess comments, and
   keyword mismatch, but not the logic.
3. **What in the raw requirement is a fact you can point to, versus something you're assuming?** Fact: the three
   sentences are prose in a Spacedock entity's change list and nothing enforces them (stated directly). Assumed:
   *why* they were left unenforced — still unverified, same gap as Run A.

**Produced → `## The problem` (fallback draft):**

> Kent hands ship-flow a lint-passing plan receipt expecting three guarantees — verified-before-dispatch
> ordering, isolated `without-it` execution, and a hard stop on security/data-loss/compatibility findings — but
> today they are unenforced prose from a Spacedock entity's change list, so Kent re-asks the same three
> questions on every PR and UATs by hand instead of only doing final UAT.

**Verbatim vs. rewritten:** the three fallback answers fuse directly into one paragraph matching this
repository's `## The problem` convention with **0 sentences rewritten after the fact** — because the questions
were authored with that prose shape as their direct target, there is no separate template (no I-am/trying-to/
because/feel bullets) to convert afterward.

---

## Station 2 (reused verbatim from Run A — not re-asked; see header note)

> - Demand evidence (Q1): PRs pass surface verification but carry excess comments and unnecessary file changes;
>   security has no explicit verification mechanism; kc-pr-review's security pass exists but dev-flow never
>   invokes it because it is too heavy and manual steering is slow and fragmented.
> - Status quo (Q2): the Captain asks on every PR whether it is the smallest stack, whether without-it ran, what
>   was verified; UATs by hand; reads the diff and LOC for stray files, excess comments, keyword mismatch; does
>   not read logic.
> - Target human (Q3): resolved to Kent, at UAT, who today re-asks three questions on every PR.
> - Wedge (Q4): all three sentences into the ship-flow runtime README with contract-test pins, Pilot depth;
>   script enforcement deferred.

**Produced → `User value:`** (same line as Run A, since the evidence is identical):

> User value: Kent stops re-asking three verification questions per PR because ship-flow enforces dispatch
> order, isolated without-it, and a security/data-loss/compatibility stop.

---

## Station 3 fallback

1. **If this ships, what's the one thing you expect to become true that isn't true now, and how would you check
   it?** Kent stops re-asking the three questions on ship-flow PRs; check by watching the next 3 UATs.
2. **What's the cheapest way to find out you're wrong before you build the whole thing?** Write the three
   sentences into the README plus contract-test pins (no script enforcement yet) and watch the next 3 PRs before
   considering Alternative B (script enforcement).
3. **What number or observation, and by when, tells you this worked?** Zero of the next three UATs where Kent
   re-asks any of the three questions.

**Produced → `## Accepted outcome` + `Falsifier:` (fallback draft):**

> Once the three DEV-67 sentences are written into the ship-flow README with contract-test pins, Kent should
> stop re-asking any of the three verification questions across the next three ship-flow UATs.
>
> **Falsifier:** Kent re-asks one of the three questions on any of the next three PRs after the README and pins
> land.

**Verbatim vs. rewritten:** **0 sentences rewritten after the fact** — the three fallback answers were authored
to land directly as accepted-outcome prose plus a falsifier line, with no separate if-then / Tiny-Acts-of-
Discovery / Validation-Measures block to collapse afterward.

---

## Station 4 fallback

1. **Does this only make sense as one shippable piece, or can you point to a natural seam?** Three seams:
   writing the README sentences, pinning them to a contract test, and observing the next 3 UATs — the same
   workflow-step seam Run A found via `user-story-splitting` Pattern 1.
2. **Which piece has to exist before another piece can be tested?** README before the pin; the pin before the
   observation is meaningful (observation without the pin can't attribute a re-ask to drift vs. never having
   been written).
3. **If you could only ship one of these pieces this week, which one, and does it alone deliver something the
   target user notices?** The README sentences alone: Kent gets something to point to at UAT even before the
   pin exists.

**Produced → Issue cut (identical to Run A):**

1. Write the three ship-flow contract sentences into the runtime README — blockedBy: none
2. Pin the three contract sentences to a contract test — blockedBy: Issue 1
3. Confirm Kent stops re-asking the three questions across 3 PRs — blockedBy: Issue 1, Issue 2

Written directly in this repository's Development Brief Issue shape (problem/goal/non-goals/AC-N/route-back) —
bodies omitted here since they are identical in content to Run A's (see `run-A.md` station 4); only the
authoring path differs (fallback questions rather than the borrowed skill's own template).

**Verbatim vs. rewritten:** **0 sentences rewritten** — no competing per-issue template (the borrowed skill's
As-a/I-want-to/Given-When-Then shape) was ever produced to be discarded, since the fallback questions don't
carry one.

---

## AC-2 per-field table (Run B)

| Brief field | Verbatim transfer | Sentences rewritten after the fact |
|---|---|---|
| `## The problem` | fallback answers fuse directly | 0 |
| `User value:` | reused from Run A (unchanged evidence) | 0 |
| `## Accepted outcome` + `Falsifier:` | fallback answers fuse directly | 0 |
| Issue cut | identical to Run A | 0 |

**Run B / AC-2 verdict:** every field lands at 0 rewritten sentences — the fallback questions were authored with
this repository's own Brief prose shape as their direct target, so there is no competing output template to
convert. No falsifier hit for Run B in isolation; see `compare.md` for the run-to-run diff against Run A.
