---
id: 9ydm2mmakce2r49v40q98377
title: The 3.0 rewrite dropped four merged verification rules and no migration note said so
status: validation
source: found 2026-08-21 while answering the Captain's original question about issue #154, whose maintainer reply states these clauses had already shipped; they had, and then they were removed
product: kc-dev-flow
sprint:
started: 2026-08-22T09:54:50Z
completed:
verdict:
worktree: .worktrees/spacedock-ensign-verification-discipline-lost-in-the-rewrite
issue: 154
pr: "#279"
mod-block:
gates:
    version: 1
    records:
        - id: gate:9ydm2mmakce2r49v40q98377:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:9ydm2mmakce2r49v40q98377-backlog-1
              briefing:
                id: briefing:9ydm2mmakce2r49v40q98377:backlog:attempt-1:revision-1
                digest: sha256:fd06ba0dfce987aede3680ee83ae436a21e91e8abcfedd875b2261946801af4a
                request-digest: sha256:7fad7f4e15bae2d97a410d589518e32c1d17c870167a659c6632ad5e1bbcaf9d
                room-ref: ./verification-discipline-lost-in-the-rewrite/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:9ydm2mmakce2r49v40q98377:backlog:1
                briefing: briefing:9ydm2mmakce2r49v40q98377:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-08-22T09:52:15.262904Z"
                decision: approve
                reason: 'Captain approved the backlog gate in chat: Production profile, scope bounded to the four #156 clauses plus the #164 absolutes rule and a one-time migration record; standing enforcement excluded and the restoration form deferred to ideation. Direction accepted on verified evidence — kernel.md replaced 349->81 lines by #249, six recording surfaces searched with no removal note, three proof-stage contracts read in full with no re-siting.'
              application:
                target-stage: ideation
                state: consumed
        - id: gate:9ydm2mmakce2r49v40q98377:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:9ydm2mmakce2r49v40q98377-ideation-1
              briefing:
                id: briefing:9ydm2mmakce2r49v40q98377:ideation:attempt-1:revision-1
                digest: sha256:21f759bb1ec09cf57d4605a113d7e5b513989ec1f37b922780f3d87f4240d4f9
                request-digest: sha256:b5f85460c746b930a00f09d2aaadd6275c801f56858616d88e551595abc588e8
                room-ref: ./verification-discipline-lost-in-the-rewrite/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:9ydm2mmakce2r49v40q98377:ideation:1
                briefing: briefing:9ydm2mmakce2r49v40q98377:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-08-22T10:30:02.121436Z"
                decision: approve
                reason: 'Captain approved the compressed restoration in chat, with one condition attached: each clause must survive a without-it audit before it lands. Direction accepted on the ideation evidence — four literal diffable blocks, baseline set to the wording e634d3e7 deleted rather than #156''s original, measured price of +413 words to the shared core and +19.6% to +22.8% across all eight profile-stage bundles, five claims carrying a falsifier seen to fail and five named as carrying none. The condition routes into implementation: a clause with no evidence that its absence cost something is dropped, and the drop is recorded against the accepted blocks.'
              application:
                target-stage: implementation
                state: consumed
        - id: gate:9ydm2mmakce2r49v40q98377:validation
          stage: validation
          attempts:
            - id: gate-attempt:9ydm2mmakce2r49v40q98377-validation-1
              briefing:
                id: briefing:9ydm2mmakce2r49v40q98377:validation:attempt-1:revision-1
                digest: sha256:221d6b81cf07c3bdb873fc1a13d039fcb7af42e908f4f301775edcf3ea315fea
                request-digest: sha256:655aa6262f4c8d0b242c02e0345c2eb52547fbb758e8d099ed3b244d0f6afb9f
                room-ref: ./verification-discipline-lost-in-the-rewrite/review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:9ydm2mmakce2r49v40q98377:validation:1
                briefing: briefing:9ydm2mmakce2r49v40q98377:validation:attempt-1:revision-1
                by: person:captain
                at: "2026-08-22T15:31:11.815284Z"
                decision: revise
                reason: 'Captain rejected in chat. Finding: the restored ''a check is evidence only once it has been seen to fail'' bullet does not close the failure it is offered as closing. The byte-parity false claim that passed a Captain gate satisfied the sentence as written — the reviewer did see the check go red, one vendored copy at a time — because tampering one copy makes the copies diverge and divergence is the only axis that check has, so the wrongness and the detected condition coincide and cannot be told apart. The landed sentence derives the must-flag case from the CHECK; issue #154 section 4, which this item cites as the evidence for keeping this clause, derives it from the CLAIM: ''a check was run whose result could not have falsified the claim it was offered as proof of''. Concrete ask: carry that operative framing into the bullet''s wording, in the compressed register already accepted, so the negative control must be able to falsify the claim rather than merely produce a red. Do not restore the surrounding #154 prose, do not touch Sites 2, 3 or 4, and do not add a standing check. Re-measure only the figures the added words change.'
            - id: gate-attempt:9ydm2mmakce2r49v40q98377-validation-2
              briefing:
                id: briefing:9ydm2mmakce2r49v40q98377:validation:attempt-2:revision-1
                digest: sha256:51762192cbb7cc634dbe499c45dcca4adbe32d832d3a7f2d0e4ab6511a06a845
                request-digest: sha256:9109ac81decc69b60c4ad21e3697d40754ee3f5d5c1549424bd52927f538cf0d
                room-ref: ./verification-discipline-lost-in-the-rewrite/review/validation/briefing-2
              resolution:
                type: Resolution
                id: resolution:spacedock:9ydm2mmakce2r49v40q98377:validation:2
                briefing: briefing:9ydm2mmakce2r49v40q98377:validation:attempt-2:revision-1
                by: person:captain
                at: "2026-08-22T16:03:27.353515Z"
                decision: revise
                reason: 'Captain rejected in chat, on the FO recommendation. The re-review established that the amended wording re-certifies the byte-parity reviewer rather than stopping it, because the biconditional attaches to the chosen negative control where it is degenerate, and that issue #154 section 4''s own framing would not have stopped it either, being modal-existential over the check. That is a second occurrence of one failure shape — a wording written to close the parity class that does not close it — and the clause being restored in this same change excludes a third wording: at the second occurrence, restructure, and a stronger instruction does not count. Concrete ask: revert the ad37d51f sentence, return Site 1 to the wording approved at the ideation gate, and bound the claim to what is true — this bullet closes issue #154 section 4''s four field defects and does not close the parity class, which is carried by the absolutes rule at Site 2 and by a human diff. The minor finding is subsumed by the revert.'
            - id: gate-attempt:9ydm2mmakce2r49v40q98377-validation-3
              briefing:
                id: briefing:9ydm2mmakce2r49v40q98377:validation:attempt-3:revision-1
                digest: sha256:b33f4d917da5528fb798b85b5fb00485d2f25980dcc8cc3296c9ec488f83322d
                request-digest: sha256:0b2d1fe4e7677dda46b48cd74d6cde382aafcf60a50615b38115fb9cb659cefa
                room-ref: ./verification-discipline-lost-in-the-rewrite/review/validation/briefing-3
---

## Problem

`#156` ("bind the instrument, not only the claim", merged 2026-08-04) added a
`## Verification discipline` section to `kernel.md` carrying five clauses. Four
of them are absent from `origin/main` today. The fifth survives only in a
narrower place than it was written.

| Clause from `#156` | State on `origin/main` |
|---|---|
| A check is evidence only once it has been seen to fail | absent |
| Name the falsifier's kind — `refusal` / `mutation` / `existence-disproof` | absent (the word survives only in `CHANGELOG.md`) |
| Prefer the cheapest instrument that can fail | survives as one phrase in `profiles/production/verify.md`, so POC and Pilot never load it |
| When one failure shape repeats, change the work, not the wording | absent |
| An instruction that contradicts the governing contract loses | absent |

They were removed by `e634d3e7` (`#249`, the profile-native 3.0 rewrite).

## This was collateral, not a decision

`MIGRATION.md` — the document whose entire job is to tell adopters what changed
— does not mention the removal. Neither does `#249`'s body. A breaking rewrite
deleted five merged rules and told nobody, including the external repositories
that consume this package at a pinned tag.

The missing migration note is the more general defect. The rules can be
restored by hand; a rewrite that can silently drop merged behaviour will do it
again.

## Which clauses have earned restoration, with evidence

The session that found this is unusually direct evidence, because it ran a full
Production route without these clauses present and reproduced their subject
matter by hand.

- **Seen to fail.** Every advance in that session came from making a check fail
  first — six named mutants across two work items. The one place the rule was
  effectively not applied, a claim reached a Captain gate and was accepted while
  false: a byte-parity check between two vendored copies had been mutation-tested
  one copy at a time, which reddens on parity rather than on content, so
  corrupting both copies identically passed the whole suite. A cross-model
  interview found it after the gate. Strongest case. **Bound:** restoring this
  clause closes the four field defects issue `#154` §4 names; it does not close
  the byte-parity incident's own class, where a check's detectable failure mode
  is narrower than the claim it was offered for. Two attempts to close that
  class by wording the clause differently both failed, recorded in full in
  `## Acceptance evidence`: correction round 1 tied the required case to the
  claim's falsity per the *chosen* negative control, which the single-tamper
  control satisfies without ever ranging over the check's domain, so the
  amended sentence re-certified the same reviewer it was written to stop; and
  issue `#154` §4's own framing, checked directly, would not have stopped that
  reviewer either. This is a limit on the clause, not a guarantee that the
  parity check is fixed, and it stays open.
- **Name the falsifier's kind.** `#156`'s own text says `mutation` is the only
  kind that finds "a consumer silently duplicating a producer's derivation
  instead of consuming its output." That sentence describes the parity defect
  above exactly. The rule had already answered the question that later cost a
  correction round.
- **When one failure shape repeats, change the work.** The same session invented
  an ad-hoc stopping rule mid-flight because this clause was not available. This
  is also the subject of issue `#143`, so restoring it addresses two reports.
- **Cheapest instrument that can fail.** Restore to the kernel rather than
  leaving it inside one profile's stage contract.
- **Instruction contradicts the contract.** No occurrence observed. Weakest
  case; leave it out unless evidence appears.

## Not decided here

Whether the restored clauses return verbatim, compressed, or re-sited — the 3.0
kernel is deliberately small and pasting a long section back may fight that
decision. That is the shape question this task owes. What is not in question is
that four merged rules are gone and nothing recorded it.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v2
  selected: production
  recommended: production
  basis: "kernel.md is the shared core every profile loads. It is vendored byte-identical into each adopter and consumed at a pinned release tag, so restoring clauses changes what every adopter's every stage must obey and owes a MIGRATION entry -- the exact obligation whose omission is this task's subject. Doing this work under a profile with no release obligation would repeat the defect. No operational runtime is involved."
  route: [shape, build, verify]
  obligations:
    architecture:
      - "Restore into the shared core, not into one profile's stage contract. A clause sited under production/ is unreadable to POC and Pilot; that is exactly how `prefer the cheapest instrument that can fail` was lost in practice."
      - "Respect 3.0's small-core decision. Restored text competes for the same loaded bytes every stage pays for, so the restoration form -- verbatim, compressed, or re-sited -- is the shape question this stage owes, not a paste."
    implementation:
      - "Restore the four clauses named in this task body, plus the absolutes rule merged by #164, which has a live broken consumer at this repository's CLAUDE.md."
      - "Record the 3.0 removal once in MIGRATION.md, and repair the two citations in this repository's CLAUDE.md that point at sections which no longer exist."
      - "kc-dev-flow/references/kernel.md and docs/dev/_mods/kernel.md move together; scripts/kc-dev-flow-contract-test.py enforces their byte-identity."
    testing:
      - "Every falsifiable claim names a check that has been seen to fail. A presence-grep over prose the same change authored proves nothing and is refused."
      - "The byte-identity assertion is shown live -- tamper with one vendored copy, observe the named failure, restore -- rather than asserted from a passing suite."
  scope_boundary: "Excludes restoring the whole former `## Outcome discipline` section, excludes the `an instruction that contradicts the governing contract loses` clause (no observed occurrence), and excludes any standing check that a kernel deletion must carry a MIGRATION entry."
  promote_when:
    - "The accepted outcome starts to require a standing enforcement mechanism rather than restored prose; that is new permanent enforcement and needs its own Captain-authorized task."
    - "The restoration is found to require changing what a stage contract must emit, which moves the work from the shared core into the profile contracts."
  decision:
    authority: person:captain
    at: 2026-08-22T09:52:39Z
```

## Without-it audit

Run before writing any of the four accepted blocks, per the Captain's condition
at the ideation gate. Each of the five in-scope clauses is checked against a
real occurrence — a commit, a PR, an issue, or this entity's own stage report —
where its absence cost something. A clause with no such evidence is dropped and
recorded as a deviation from the accepted Site 1 / Site 2 blocks. Result: **zero
drops.**

- **A check is evidence only once it has been seen to fail** — KEEP. Issue
  `#154` §4 names four real occurrences where a check could not have falsified
  the claim it was offered as proof of: an exit code read from the wrong
  element of a pipeline; a log filter anchored on a start marker that reported
  "no output" while the sought lines were present, producing a wrong report to
  a human that a provider had disabled a subscription when it had not; a
  backup asserted as a rollback path without its size or contents ever
  compared to the original; a delete verified by a `count(*)` taken from the
  same connection that issued it while the process owning the resource still
  held the old rows. This entity's own `## Which clauses have earned
  restoration` section records a fifth, closer to home: a byte-parity check
  between two vendored copies, mutation-tested one copy at a time, passed a
  Captain gate while false — corrupting both copies identically passed the
  whole suite. A cross-model interview found it after the gate.
- **Name the falsifier's kind** — KEEP. Issue `#154` §5 names the class this
  clause exists to catch: a consumer that duplicates a producer's derivation
  formula, rather than consuming the producer's output, is silently correct
  until the formula changes — found only by mutating the producer and
  observing what breaks, never by an assertion over sampled inputs. The same
  parity defect above is that class verbatim: a check that reddens on
  divergence and never on content is a mutation-shaped check that was never
  exercised as one.
- **Prefer the cheapest instrument that can fail** — KEEP. Issue `#143`'s
  second gap, measured on one task: 19.4 minutes of construction against 58.3
  minutes of validation, a 3x inversion, because the governing stage
  prescribed an adversarial reviewer for every validation regardless of
  whether the defect class admitted a cheaper mechanical check. Once the
  defect class was cut, acceptance became a grep and the ratio inverted back.
  This is distinct from the siting evidence already recorded elsewhere in this
  entity (`prefer the cheapest instrument that can fail` survives only at
  `production/verify.md:8`, unreadable to POC and Pilot) — that shows the
  clause misplaced; this shows the clause's absence costing measured time.
- **When one failure shape repeats, change the work, not the wording** — KEEP.
  Issue `#143`'s first gap: three consecutive validation rejections on the same
  defect class, at 30%/47%/60% of the approved budget with acceptance criteria
  unchanged throughout — the budget-based design-reset trigger never came
  close to firing, because each round was individually cheap. A human ruling
  was required to stop correcting instances and delete the wrong-shaped
  deliverable. The session that is this entity's own source independently
  invented an ad-hoc stopping rule mid-flight, for the identical reason.
- **An absolute names its enforcement point or becomes a bounded claim** —
  KEEP. The currently-dangling `CLAUDE.md:91` citation (verified live on this
  tree before any edit — see `## Acceptance evidence`) proves the deletion left
  a live consumer, but that alone is the citation breaking, not the rule's own
  absence biting. Two occurrences of the rule's subject matter actually costing
  something: `#156`'s own original text wrote "this is the **only** kind that
  finds a consumer silently duplicating a producer's derivation," an
  undefended absolute a later revision had to bound; and this entity's own
  `## Stage Report: ideation` records a self-correction of exactly this
  failure — a claim that a sentence was "the first addition since `#249` to
  state its cost at all" was checked and found false, then rewritten to
  "weighed once in four changes."

No clause is dropped, so the four accepted blocks below land unamended: no
deviation-table addition, and no change to the Site 4 `MIGRATION.md` block
follows from this audit.

## Accepted outcome and non-goals

`kernel.md` regains four instrument rules and the absolutes rule, compressed, at
two named sites. `MIGRATION.md` records the 2026-08-18 removal once.
`CLAUDE.md`'s two dangling section citations resolve again.

### Restoration form: compressed, and the baseline it compresses

The baseline is the wording `e634d3e7` deleted (`e634d3e7^`), not `#156`'s
original. `#159`, `#161`, and `#162` revised these clauses after `#156` merged,
and those revisions are the merged behaviour. Restoring `#156` verbatim would
also reintroduce an undefended absolute: `#156` wrote "this is the **only** kind
that finds a consumer silently duplicating a producer's derivation", which a
later revision had already bounded to "this is the kind that reaches a consumer
silently duplicating a producer's derivation" — the exact defect class the
absolutes rule restored in this same change exists to catch.

Compression cuts three justificatory sentences and one reference to a retired
mechanism. Every bolded rule sentence lands verbatim from `e634d3e7^`, so the
vocabulary in `CHANGELOG.md`, in issues `#143` / `#154` / `#156`, and in this
repository's review history still resolves against the shipped text.

| Clause | Site in `kernel.md` | Deviation from `e634d3e7^` verbatim |
|---|---|---|
| A check is evidence only once it has been seen to fail | new `## Verification discipline`, bullet 1 | cut "A probe that returns a plausible result where it should have errored is worse than none, because its output reads as a conclusion." |
| Name the falsifier's kind | new `## Verification discipline`, bullet 2 | none; verbatim |
| Prefer the cheapest instrument that can fail | new `## Verification discipline`, bullet 3 | none; verbatim |
| When one failure shape repeats, change the work, not the wording | new `## Verification discipline`, bullet 4 | cut the final sentence, which routes a repeated hazard through `dispatch_hazard_assignment` — a mechanism `git grep dispatch_hazard_assignment origin/main` finds nowhere, so restoring it verbatim ships a dangling reference |
| An absolute names its enforcement point or becomes a bounded claim | last bullet of existing `## Shared boundaries` | cut "Apply it to claims adopted from reports, reviewers, or contributors too, and record what was checked." and the closing "Rephrasing factual behavior as a command does not change its class."; the factual-vs-prohibition test is kept and tightened into one sentence |

The absolutes rule does not go under `## Verification discipline`: it governs the
claim, not the instrument. `## Shared boundaries` is where the current kernel
already keeps standing authoring and working rules, so it lands there and
`CLAUDE.md`'s citation is repointed to that section rather than to a revived
`## Outcome discipline` heading that would promise the other seventy lines it no
longer holds.

### Site 1 — new `## Verification discipline`, inserted between `## Shared boundaries` and `## Communication`

```markdown
## Verification discipline

Shared boundaries govern the claim. These govern the **instrument** — the check,
the reviewer, the instruction — because an instrument that cannot fail reports
the same way whether or not the thing it watches is broken.

- **A check is evidence only once it has been seen to fail.** Run it against a
  case it must flag before running it against the case in question; its silence
  carries information only after you have heard it speak. This binds the check,
  not only the artifact: a round that cannot say what would have reddened its own
  instrument has measured nothing.
- **Name the falsifier's kind.** `refusal` — drive the system and read its
  rejection. `mutation` — change the producer and observe what breaks; this is
  the kind that reaches a consumer silently duplicating a producer's derivation
  instead of consuming its output. `existence-disproof` — show that no value
  satisfies both requirements, which no assertion over sampled inputs
  establishes. Treating all three as "write an assertion" lets two appear covered
  when they are not.
- **Prefer the cheapest instrument that can fail.** Reserve an expensive one — an
  adversarial reviewer, a fresh-context panel — for claims no cheap check can
  settle. An expensive instrument whose output is a work order for a cheap one
  was misapplied, and that cost is paid every round it repeats.
- **When one failure shape repeats, change the work, not the wording.** At the
  second occurrence, restructure so the reproducer is eliminated; a stronger
  instruction, another case against the same reproducer, or an unchanged
  deliverable shape do not count. Cheapness hides this: a tolerance sized for
  expensive rounds does not fire on cheap ones, so the trigger is repetition of
  shape, not spend.
```

The preamble's first two words change from `Outcome discipline` to
`Shared boundaries`, because the section it pointed at no longer exists and
`## Shared boundaries` is its successor for claim-level rules.

### Site 2 — appended as the last bullet of the existing `## Shared boundaries`

```markdown
- **An absolute names its enforcement point or becomes a bounded claim.**
  "Exactly", "only", "always", "never", "cannot", or "byte-for-byte", written
  into a reference, a code comment, or a commit message, names the mechanism
  that makes it true or is rewritten to what the artifact supports. An
  enforcement point is a permission check, a schema constraint, an unreachable
  branch, or a fail-closed check — not "I checked", and not its author. This is
  an authoring discipline, not an assertion that an automatic gate exists.
  Classify by falsifier, not by grammatical form: if contrary execution would
  make the sentence false, it is factual and needs an enforcement point or
  bounded wording; if contrary execution instead violates a duty assigned to a
  named authority, it is a prohibition.
```

### Site 3 — `CLAUDE.md` line 91, two section names substituted, no other word changed

| Now (dangling) | After |
|---|---|
| ``` `kc-dev-flow/references/kernel.md` § Outcome discipline ``` | ``` `kc-dev-flow/references/kernel.md` § Shared boundaries ``` |
| ``` `docs/dev/README.md` § Proof Policy ``` | ``` `docs/dev/README.md` § Proof and delivery checks ``` |

`## Proof Policy` was renamed, not deleted: `e634d3e7^:docs/dev/README.md` line
141 carries it, and `e634d3e7` renames it to `## Proof and delivery checks`,
which still holds the same list of this repository's local checks. The repaired
citation therefore resolves *and* is true.

### Site 4 — `MIGRATION.md`, one dated entry appended, following the `2026-08-21` precedent

```markdown
## 2026-08-18 — the shared core's verification discipline was dropped, and this note is late

`e634d3e7` (`#249`) replaced `kernel.md` wholesale and removed its
`## Verification discipline` section along with the absolutes rule in
`## Outcome discipline`. That removal was collateral: neither this file nor
`#249`'s body recorded it, so an adopter bumping across that tag lost merged
rules with no signal. Four of those clauses are restored, compressed, by the
change carrying this note: a check is evidence only once it has been seen to
fail; name the falsifier's kind; prefer the cheapest instrument that can fail;
when one failure shape repeats, change the work, not the wording — plus the
absolutes rule, now sited in `## Shared boundaries`. Not restored: `an
instruction that contradicts the governing contract loses`, which `#249` removed
from `## Authority model` in the same sweep, excluded here on one ground only —
no observed occurrence; and the six verification clauses whose subject matter the
profile stage contracts now carry.
An adopter that vendored `kernel.md` between `kc-dev-flow-v3.0.0` and the release
carrying this note has been running without those five rules.
```


### Accepted journey

1. **OBSERVED** — an operator runs `docs/dev/_mods/profile-contract-loader.py`
   with the exact work item. It emits `kernel.md` in full for every
   profile-stage combination. Run against the candidate kernel it emits the new
   `## Verification discipline` heading; run against today's tree it does not.
2. **OBSERVED** — `scripts/kc-dev-flow-contract-test.py` reads both `kernel.md`
   copies with `read_bytes()` and compares them. With the candidate text in both
   copies it exits `0`; with it in one copy it exits `1` printing
   `kc-dev-flow contract: self-adopted shared core differs from package source`.
3. **OBSERVED** — the same script pins three `kernel.md` phrases and the
   Production route-table row by substring. The candidate insertion leaves all
   four intact, so the script still passes.
4. **DESIGNED** — a reviewer at validation diffs the landed `kernel.md`,
   `MIGRATION.md`, and `CLAUDE.md` hunks against the four blocks recorded above.
5. **DESIGNED** — release-please cuts a `kc-dev-flow-vX.Y.Z` tag; an adopter
   bumping to it re-vendors both copies and reads `MIGRATION.md`.

Unhappy paths. If only one `kernel.md` copy is edited, step 2 exits `1` and CI
blocks the merge — this is the failure mode the change is most likely to hit and
it is caught. If **both** copies are corrupted identically, step 2 still exits
`0`: the parity check reddens on divergence, never on content (reproduced on
this tree — appending one byte to both copies leaves the suite green). Nothing
mechanical then catches a wrong restoration, which is why step 4 is a named
human diff against recorded text and not an afterthought. If nobody reads
`MIGRATION.md`, the entry is inert; the change makes the record exist, it cannot
make it read.

### Observable semantics this work may change

The loader emits more bytes and a different `sha256` attribute for `kernel.md`
in every profile-stage result. Nothing else: no command grammar, no receipt
schema, no route table, no file path, no stage contract. Two searches bound the
claim that no consumer pins the kernel's content hash — `git grep 2ba2a47e
origin/main` returns nothing, and `git grep kernel.md origin/main -- '*.py'
'*.sh' '*.json' '*.toml' '*.yml' '*.yaml'` returns only path references,
read-time hashing, and test fixtures that write their own kernel. Boundary: files
tracked on `origin/main`. External adopter repositories are outside it; they
consume at a pinned tag and see nothing until they bump.

### Where it touches

Diff base `origin/main` = `9fee712c`. The FO fast-forwarded this worktree past
`8ddd794d` before dispatching implementation because `556e08fc` and `9fee712c`
merged in the interval and `9fee712c` edits both `kernel.md` copies (`##
Authority` gains seven lines; `## Shared boundaries` and `## Communication`,
this change's two insertion sites, are untouched — confirmed live on this tree
before editing). Every figure below is re-measured at `9fee712c`, not adjusted
by arithmetic on the old base.

| Path | lines now | lines after |
|---|---:|---:|
| `kc-dev-flow/references/kernel.md` | 124 | 165 |
| `docs/dev/_mods/kernel.md` | 124 | 165 |
| `kc-dev-flow/MIGRATION.md` | 101 | 119 |
| `CLAUDE.md` | 103 | 103 |

`lines now` and `lines after` both counted on the landed tree at commit
`053eddb0` (this change's own commit on
`spacedock-ensign/verification-discipline-lost-in-the-rewrite`), not estimated.
`CLAUDE.md` changes two section names inside line 91 and adds no line.

Reconciled against the journey in both directions: every file in the table
appears in the journey, and every file the journey depends on
(`profile-contract-loader.py`, `scripts/kc-dev-flow-contract-test.py`,
`docs/dev/README.md`) is read, never written, so it is correctly absent here.

### Stop numbers

Measured as the diff against `origin/main` = `9fee712c` (the base this
worktree was fast-forwarded to before implementation; see `### Where it
touches`). The thresholds themselves are unchanged — the Captain accepted them
at ideation and this stage does not revisit them.

- **changed files: 5.** Four above plus this work item. Stop and report at 6.
- **changed lines: 101.** Measured on the landed commit
  (`git diff --stat 9fee712c 053eddb0`): 41 added to each of the two kernel
  copies (82 total), 18 added to `MIGRATION.md`, 1 changed in `CLAUDE.md`.
  Stop and report at 140.
- **runaway area: the two kernel prose blocks.** Compression is the thing most
  likely to grow back under review pressure. Stop and report if the two blocks
  together exceed 47 added lines — the measured size of the verbatim
  alternative, past which the compression decision has been reversed without a
  ruling. Landed: 28 lines (Site 1) + 11 lines (Site 2) = 39, under the stop
  number.

These are stop conditions, not budgets.

### Lifecycle, rollback, and release obligations

Docs-only; no runtime, schema, migration, credential, or data surface.
Rollback is `git revert` of one squash commit; forward recovery is a follow-up
commit. Adopters are unaffected until they bump the pinned tag, and the
`MIGRATION.md` entry is the signal they read when they do. Release authority
stays with the Captain through the Production validation gate and
`spacedock merge guard`. No specialist risk (security, privacy, reliability,
data, compatibility) applies beyond the vendored-copy parity already gated.

### Non-goals

- The whole former `## Outcome discipline` section, and the six verification
  clauses whose subject matter the profile stage contracts now carry.
- `an instruction that contradicts the governing contract loses` — present at
  `e634d3e7^` in `## Authority model` and removed by `#249` like the other five,
  so it is excluded on one ground only: no observed occurrence.
- Any standing check that a kernel deletion must carry a `MIGRATION.md` entry.
- Any standing citation-integrity check. The falsifier in
  `## Acceptance evidence` is run once, by hand, at validation. Making it
  standing is new permanent enforcement and fires this item's first
  `promote_when` clause; it is named there as a candidate for the Captain, not
  taken here.
- Restoring `absolutes.registry` or its checker, both deleted by `#249`.

### Conditional-reference receipts

```yaml
reverse_recovery:
  trigger: "restore five clauses removed from kc-dev-flow/references/kernel.md by e634d3e7 (#249)"
  boundary: "the text every profile-stage loader result emits, plus its two vendored copies and their in-repo citations; files tracked on origin/main; excludes external adopter repositories, which consume at a pinned tag"
  layers:
    - surface: "the four instrument clauses in the shared core"
      location: MISSING
      completeness: MISSING
      need: REQUIRED
      evidence: "present at e634d3e7^:kc-dev-flow/references/kernel.md, bullets starting at lines 245, 252, 273, and 295 under the section at line 221; absent from origin/main; two searches — `git grep 'seen to fail\|falsifier\|cheapest' kc-dev-flow/references/profiles/` returns one hit, and `grep '^## ' kc-dev-flow/references/kernel.md` shows no verification section. Required by issues #143 and #154."
      disproof_hook: "grep -c 'seen to fail' kc-dev-flow/references/kernel.md  # 0 today"
    - surface: "`prefer the cheapest instrument that can fail`, as a Production-only phrase"
      location: "kc-dev-flow/references/profiles/production/verify.md:8"
      completeness: EXISTS_BROKEN
      need: REQUIRED
      evidence: "the only surviving occurrence anywhere under profiles/; POC and Pilot never load that file, so the rule is unreachable on two of three routes"
      disproof_hook: "grep -rn cheapest kc-dev-flow/references/profiles/  # one hit, production/verify.md only"
    - surface: "the absolutes rule and its citation from CLAUDE.md"
      location: "CLAUDE.md:91 cites kc-dev-flow/references/kernel.md § Outcome discipline"
      completeness: EXISTS_BROKEN
      need: REQUIRED
      evidence: "a live in-repo consumer citing a section deleted by #249; the citation-resolution falsifier below exits 1 on today's tree"
      disproof_hook: "the citation resolver in `## Acceptance evidence`, run on origin/main"
    - surface: "a record of the removal for adopters"
      location: MISSING
      completeness: MISSING
      need: REQUIRED
      evidence: "`grep -n 'Verification discipline\|absolute' kc-dev-flow/MIGRATION.md` returns nothing; #249's PR body does not mention it either"
      disproof_hook: "grep -c 'Verification discipline' kc-dev-flow/MIGRATION.md  # 0 today"
    - surface: "byte parity between the package and adopted kernel copies"
      location: "scripts/kc-dev-flow-contract-test.py:345-348"
      completeness: WORKING
      need: REQUIRED
      evidence: "exercised live on this tree: tamper one copy -> exit 1 with `self-adopted shared core differs from package source`; restore -> exit 0"
      disproof_hook: "printf X >> docs/dev/_mods/kernel.md && python3 scripts/kc-dev-flow-contract-test.py"
    - surface: "a standing guard that kernel content is not silently wrong"
      location: MISSING
      completeness: MISSING
      need: NO_OBSERVED_CONSUMER
      evidence: "the parity check is blind to identical corruption of both copies — reproduced by appending one byte to each and observing the suite stay green. Two searches for a content guard: `grep -n 'kernel' scripts/kc-dev-flow-contract-test.py` finds only path parity plus three substring pins, and `git grep absolutes origin/main` finds the registry only in CHANGELOG and retired plan documents. Boundary: origin/main; a repository-external guard would not be visible."
      disproof_hook: "printf X >> both kernel copies && python3 scripts/kc-dev-flow-contract-test.py  # still exit 0"
  decision: recover
```

```yaml
project_context:
  impact: update
  authority: "root CLAUDE.md, per docs/dev/README.md `## Local Profile`"
  claim_locator: "CLAUDE.md:91, the two section citations in the absolute-claim rule"
  surface: "the rule's own wording and behaviour are unchanged; only the two cited section names move"
  stale_claim: "`kc-dev-flow/references/kernel.md` § Outcome discipline ... `docs/dev/README.md` § Proof Policy"
  approved_change: "`kc-dev-flow/references/kernel.md` § Shared boundaries ... `docs/dev/README.md` § Proof and delivery checks"
  landed_change: "commit 053eddb0 on spacedock-ensign/verification-discipline-lost-in-the-rewrite; CLAUDE.md:91 now reads `kc-dev-flow/references/kernel.md` § Shared boundaries ... `docs/dev/README.md` § Proof and delivery checks"
  planned_check: "the citation resolver in `## Acceptance evidence`; it exits 1 on origin/main naming both citations and must exit 0 after"
  validation_evidence: pending
```

`multi_slice_required` is **false**: one integrated slice — the two kernel copies,
the migration note, and the citation repair land together or the parity check
blocks the merge. No `journey_slices` receipt.

## Acceptance evidence

### Claims with a check that has been seen to fail

**1. The two vendored `kernel.md` copies move together.**
Check: `python3 scripts/kc-dev-flow-contract-test.py`.
Seen to fail on this tree, not asserted from a passing suite: appending one byte
to `docs/dev/_mods/kernel.md` produced exit `1` and
`kc-dev-flow contract: self-adopted shared core differs from package source`;
restoring the byte produced exit `0`. It was also run with the full candidate
kernel in both copies — exit `0`, so the restoration does not break the gate it
depends on.
Named limit, also reproduced: appending the same byte to **both** copies leaves
the suite at exit `0`. The check reddens on divergence, never on content.
Bound: restoring the **seen to fail** clause closes the four field defects
issue `#154` §4 names (see `## Which clauses have earned restoration`); it
does not close this incident's own class, where a check's detectable failure
mode is narrower than the claim it is offered for. Two attempts to close that
class by amending the clause's wording, rather than the check, both failed:
`ad37d51f` tied the required case to the claim's falsity, but as a per-case
biconditional over the *chosen* negative control, which the single-tamper
control satisfies without ever ranging over the check's domain — it
re-certified the same reviewer it was written to stop. And issue `#154` §4's
own "could not have falsified the claim" framing, checked directly, would not
have stopped that reviewer either, since one falsity mode (divergence)
narrowly clears its modal-existential bar. The gap is that a parity check was
offered as evidence for a content claim, and parity is the correct check for
parity — no wording of this clause reaches that. It is a limit on this
clause, not a guarantee about the parity check, and it stays open.

**2. `CLAUDE.md`'s section citations resolve.**
Check: a resolver that extracts every `` `<path>.md` § <Section> `` citation from
`CLAUDE.md` and asserts a matching `^#{1,4} <Section>$` heading in the cited
file, exiting non-zero on any miss.
Seen to fail on today's tree — it exits `1` reporting
`DANGLING kc-dev-flow/references/kernel.md § Outcome discipline` and
`DANGLING docs/dev/README.md § Proof Policy`. It reddens on either side of the
citation moving, so it is a mutation over the reference, not a presence-grep
over prose this change authors: the change writes `## Verification discipline`,
which this resolver never looks for.
Run once by hand at validation, before and after. It is not added to CI — see
the fourth non-goal.

**3. The restored text is loadable and does not break the kernel's existing
content pins.** Check: `python3 docs/dev/_mods/profile-contract-loader.py
--contracts-root docs/dev/_mods --work-item <this item>` plus the substring pins
at `scripts/kc-dev-flow-contract-test.py:349-358`.
Exercised with the candidate kernel in place: the loader emitted the new
`## Verification discipline` heading in the Production shape result, and the
contract test passed, so the three subtraction-rule phrases and the Production
route-table row survived the insertion. The falsifying change: delete any of
those three phrases while inserting, and the test exits `1` with
`kernel omits subtraction rule`.

**4. Every historical assertion the Site 4 `MIGRATION.md` block makes is true.**
The falsifier set is per sentence, not per block. An earlier version of this
claim named three commands that between them touched only part of the block, and
a false sentence survived in the uncovered part — the correction is recorded in
the stage report. Each assertion below now names the command that covers it. All
grep history this change did not author, so a wrong SHA or a wrong claim returns
the wrong text or nothing.

| Assertion in the Site 4 block | Covering command | Result |
|---|---|---|
| `#249` removed the `## Verification discipline` section | `git show e634d3e7^:kc-dev-flow/references/kernel.md \| grep -c '^## Verification discipline'` vs the same on `origin/main` | `1` then `0` |
| `#249` replaced `kernel.md` wholesale | `git show e634d3e7 --stat` | `kernel.md`, 422 changed lines |
| the absolutes rule was removed from `## Outcome discipline` | `git log --oneline -S "An absolute names its enforcement point" -- kc-dev-flow/references/kernel.md` | two commits; `e634d3e7` is the removal |
| the four named clauses were merged, then removed | `git show f228f76f -- kc-dev-flow/references/kernel.md` | shows the section added by `#156` |
| `MIGRATION.md` did not record the removal | `grep -c 'Verification discipline' kc-dev-flow/MIGRATION.md` | `0` |
| `#249`'s body did not record it either | `gh pr view 249 --json body -q .body \| grep -ic 'verification discipline\|absolute'` | `0` |
| `an instruction that contradicts the governing contract loses` was removed by `#249`, not earlier | `git show e634d3e7^:kc-dev-flow/references/kernel.md \| grep -n 'contradicts the governing contract'` and `git log --oneline -S 'contradicts the governing contract' -- kc-dev-flow/references/kernel.md` | line 29 under `## Authority model`; two commits, `f228f76f` added and `e634d3e7` removed |
| adopters were exposed from `kc-dev-flow-v3.0.0` onward | `git tag --contains e634d3e7 \| grep '^kc-dev-flow-'` | `kc-dev-flow-v3.0.0`, the only one |
| the restored bullet keeps no reference to a retired mechanism | `git grep dispatch_hazard_assignment origin/main` | no match |

One assertion in the block has **no** command behind it: that the six unrestored
verification clauses have their "subject matter" carried by the profile stage
contracts. That is a reading judgment about whether two differently worded texts
cover the same ground, and no grep decides it. A reviewer settles it at
validation, or the phrase is dropped from the block.

**5. The compression is smaller than the verbatim alternative it replaces.**
Check: build both candidate texts and count. Run — see `## Measurement`. The
falsifying result: a compressed block at or above 47 lines, which is also the
runaway stop number.

### Claims with no check, named plainly

- **That these five rules are worth the bytes every stage now loads.** Judgment.
  `## Measurement` gives the price exactly; nothing decides whether it is worth
  paying except the Captain at this gate.
- **That the restored prose changes what a worker does.** Prose in a loaded
  contract has no runtime. `#249`'s own success metric was input size, not
  behaviour, and this change is measured the same way. No check here reaches
  worker behaviour.
- **That the absolutes rule is enforced.** It is not. `absolutes.registry` and
  its checker were deleted by `#249` and are not restored; `git grep -l absolutes
  origin/main` returns four files — `kc-dev-flow/CHANGELOG.md` and three retired
  plan documents under `docs/plans/` — and no runnable check.
  The rule returns as authoring discipline only — which its own text says, and
  which is stated here so the gate is not reading a stronger claim than the
  change makes.
- **That the landed patch matches the wording accepted here.** No mechanical
  check compares them; claim 1's limit is exactly why. A reviewer diffs the four
  recorded blocks against the hunks at validation. This is a human check, named
  as one.
- **That the restored words stay present after merge.** Nothing standing keeps
  them there; the same silent deletion could happen again. Excluded by this
  item's `scope_boundary`, and the general defect stays open in issue `#154`.

## Measurement

All counts are `wc`-style words on the exact files, so the before and after
figures are produced the same way.

**The two restoration forms.**

| Form | lines | bytes | words |
|---|---:|---:|---:|
| Verbatim from `e634d3e7^` (4 clauses + section head + absolutes rule) | 47 | 3296 | 516 |
| Compressed, as recorded above | 40 | 2621 | 413 |

Compression saves 103 words, 20% of the verbatim block. One of the four cuts is
mandatory regardless of form: the `dispatch_hazard_assignment` sentence names a
mechanism that no longer exists.

**What the shared core costs, at diff base `9fee712c`.** `kernel.md`: 124 lines
/ 7022 bytes / 1058 words now; 165 / 9645 / 1471 after (measured on the landed
commit `053eddb0`). `+413` words, `+39.0%`. The word delta is unchanged from
the figure recorded at ideation (`+413`) because the restored text is fixed
bytes; only the base it lands on, and therefore the percentage, moved — lower,
not higher, because the denominator grew.

**What every stage loads.** Measured as the `## Local Profile` section of
`docs/dev/README.md` (666 words, unaffected by this change or by the base
move) plus `kernel.md` plus the selected profile base plus the selected stage
contract, re-measured at `9fee712c` and on the landed commit.

| Profile / stage | now | after | change |
|---|---:|---:|---:|
| `poc-exploration` / `build` | 2072 | 2485 | +19.9% |
| `poc-exploration` / `prove` | 2025 | 2438 | +20.4% |
| `pilot-product-slice` / `shape` | 2290 | 2703 | +18.0% |
| `pilot-product-slice` / `build` | 2032 | 2445 | +20.3% |
| `pilot-product-slice` / `verify-deliver` | 1997 | 2410 | +20.7% |
| `production` / `shape` | 2270 | 2683 | +18.2% |
| `production` / `build` | 2007 | 2420 | +20.6% |
| `production` / `verify` | 2062 | 2475 | +20.0% |

**Against `#249`'s own record — and a correction to how it is being cited.**
`#249`'s PR body claims "required policy input fell from about 6,100 words to
960–1,007 words for the Local Profile plus one selected build contract:
**83.5%–84.3% less input**." That 960–1,007 figure is **not reproducible from the
tree.** At `e634d3e7` the closest reconstructions are 845–900 words without the
`## Local Profile` section and 1,274–1,329 with it; neither brackets the quoted
range. These `e634d3e7` figures are historical and unaffected by the base
move. So the restoration is not measured against `#249`'s own number. It is
measured before and after by one method, above.

What the tree does show at `e634d3e7`: `kernel.md` was 597 words and the
Local-Profile-plus-base-plus-build bundle was 1,274–1,329 words. Today, at diff
base `9fee712c` with no part of this change landed, `kernel.md` is 1058 words
(`+77%`) and that build-stage bundle is 2,007–2,072 (`+56%` to `+58%`,
low-to-low and high-to-high). Both figures moved up from what was recorded at
ideation (`986` words / `+65%`; `1,820–1,885` / `+43%` to `+48%`) because the
base moved, not because anything about this restoration changed. The small
core has already grown by roughly the same amount this restoration adds, now
across five intervening commits — `#267`, `#271`, `#272`, `#276`, `#277`.
Bounded claim, checked by
`git log --format='%B' -1 <sha> | grep -in 'word\|load\|byte\|input'` over
each: four of the five state no size accounting at all (`#277`'s two hits are
about decision input, not text size), and `#272` does — it records `kernel.md`
dropping 47 words. So growth here has been weighed once in five changes, not
never. That is the honest frame for the price: `+413` words is real, and it is
about `+20%` on every route.

**Why the cost is earned, and why it lands in the shared core.** The four
clauses govern the instrument, and the instrument is what every profile uses;
they are not Production ceremony. The one clause that did survive `#249` proves
the siting argument by counterexample: `prefer the cheapest instrument that can
fail` exists today only inside
`kc-dev-flow/references/profiles/production/verify.md:8`, and `grep -rn cheapest
kc-dev-flow/references/profiles/` returns that single hit — so a POC or a Pilot
item, which never loads that file, cannot read a rule about choosing cheap
checks. Putting these clauses in a profile stage contract is how the last one
was lost in practice.

### Feedback Cycles

- **Cycle 1 — `validation` rejected, routed to `implementation`.** Captain decision `revise`,
  recorded against `briefing:9ydm2mmakce2r49v40q98377:validation:attempt-1:revision-1`
  (`sha256:221d6b81`) at delivery revision `053eddb0`. One finding: the restored
  `a check is evidence only once it has been seen to fail` bullet was satisfied by the very
  incident it was offered as closing, because tampering one vendored copy makes the copies
  diverge and divergence is the only axis that check has. Disposition: accepted, fix in place,
  carrying issue `#154` section 4's framing into the bullet. Corrected at `ad37d51f`; PR #279
  updated in place. Sites 2, 3 and 4 untouched; the without-it audit was not reopened.
- **Recorder unavailable, recorded here instead.** `spacedock gate record --round validation/1`
  refuses on this workflow: `gate record --round requires folder-form entity <slug>/index.md
  because review artifacts accumulate beside the entity`. This workflow files flat `<slug>.md`
  entities, so the neutral round recorder cannot address any entity it owns. The round is
  therefore recorded in this FO-owned section, and the gap is reported to the Captain rather
  than treated as a round failure.

- **Cycle 2 — `validation` rejected again, routed to `implementation`.** Captain decision `revise`
  on the First Officer's recommendation, recorded against
  `briefing:9ydm2mmakce2r49v40q98377:validation:attempt-2:revision-1` (`sha256:51762192`) at
  delivery revision `ad37d51f`. The fresh reviewer established that correction round 1's sentence
  re-certifies the reviewer it was written to stop, because the biconditional attaches to the
  chosen negative control rather than ranging over the check's domain, and that issue `#154`
  section 4's own framing would not have stopped it either. That is the second occurrence of one
  failure shape, so the clause being restored by this change excludes a third wording. Disposition:
  revert `ad37d51f`, return Site 1 to the wording approved at the ideation gate, and bound the
  claim to what is true. Reverted at `d55d6a4d`; PR #279 updated in place. The cycle-2 minor
  finding — an unbounded "no mechanical check distinguishes them" — is subsumed by the revert.
  The round recorder remains unusable for the reason recorded under cycle 1.

## Stage Report: ideation

- DONE: Name the exact restored words and their site: for each clause in scope, state the wording that will land and which section of kernel.md it lands in.
  Four literal blocks recorded under `## Accepted outcome and non-goals` (Sites 1-4) plus a per-clause deviation table naming what each cuts from the `e634d3e7^` baseline; a reviewer diffs hunks against those blocks.
- DONE: Justify the load the restoration adds: state what the chosen form adds to what every stage loads, and why that cost is earned given that PR #249 recorded its own success as an 83.5%-84.3% cut in required policy input.
  `## Measurement` prices both forms (verbatim 516 words vs compressed 413), the shared core (986 -> 1399, +41.9%), and all eight profile-stage bundles (+19.6% to +22.8%); it also records that #249's 960-1,007-word figure is not reproducible from the tree, so the delta is measured before/after by one method instead.
- DONE: State in the same place why these clauses belong in the shared core rather than a profile stage contract, citing that the one clause which did land in production/verify.md is unreadable to POC and Pilot.
  Same section, closing paragraph: `grep -rn cheapest kc-dev-flow/references/profiles/` returns exactly one hit, `production/verify.md:8`, which POC and Pilot never load.
- DONE: For every falsifiable claim in the acceptance evidence, name a check that can be seen to fail, and name plainly the claims that have no such check.
  `## Acceptance evidence` carries five checked claims and five explicitly unchecked ones (worth-the-bytes, behaviour change, absolutes enforcement, patch-matches-accepted-wording, post-merge persistence).
- DONE: A presence-grep over prose this change itself authors is refused.
  The citation resolver keys on `CLAUDE.md`'s cited section names, never on `## Verification discipline`; it exits 1 on today's untouched tree naming both dangling citations. The falsifying change: move either side of a citation.
- DONE: The byte-identity assertion between kc-dev-flow/references/kernel.md and docs/dev/_mods/kernel.md is shown live by tampering with one copy and observing the named failure, not asserted from a passing suite.
  Ran on this tree: one-byte append to the adopted copy -> exit 1, `kc-dev-flow contract: self-adopted shared core differs from package source`; restore -> exit 0. Also ran the inverse mutation: the same byte appended to BOTH copies leaves the suite at exit 0, so the check reddens on divergence and never on content. Worktree restored, `git status` unchanged.

### Summary

Shaped the restoration as compressed rather than verbatim, at two sites in
`kernel.md`, with the baseline set to the wording `e634d3e7` deleted rather than
`#156`'s original — because later merged revisions had already bounded an
undefended absolute that `#156` carried, and because one restored sentence would
otherwise cite `dispatch_hazard_assignment`, a mechanism no longer on
`origin/main`. Two findings arrived from exercising rather than reading: the
parity gate is blind to identical corruption of both vendored copies (reproduced
live), which is why the wording match is named as a human check; and `#249`'s
own 83.5%-84.3% headline is not reproducible from the tree, so the load argument
is rebuilt from measurements taken the same way before and after. Open for the
Captain: the price is about +22% loaded words on every route, and a standing
citation-integrity check is named as a candidate but not taken, since it would
fire this item's first `promote_when` clause.

- DONE: (post-report correction) the Measurement section's own absolute was checked and bounded.
  Claimed "the first addition since #249 to state its cost at all"; `git log --format=%B -1` over the four intervening kernel commits (#267, #271, #272, #276) showed #272 records `kernel.md` dropping 47 words, so the sentence is now bounded to "weighed once in four changes". Site 4's MIGRATION heading is also recorded as the single line that will land, so every one of the four blocks is byte-diffable against the patch.
- DONE: (FO review, finding 1) a false cause inside adopter-facing text was removed.
  Wrong sentence, in both the Site 4 `MIGRATION.md` block and the second `### Non-goals` bullet: `an instruction that contradicts the governing contract loses` "had already left the kernel before `#249`". Falsified by `git show e634d3e7^:kc-dev-flow/references/kernel.md | grep -n "contradicts the governing contract"` -> hit at line 29 under `## Authority model`, and `git log --oneline -S "contradicts the governing contract" -- kc-dev-flow/references/kernel.md` -> `f228f76f` added, `e634d3e7` removed. My original search was scoped to the `## Verification discipline` span, which is why it missed a clause sited in `## Authority model` — the same sampling error the restored `name the falsifier's kind` clause exists to prevent. Bounded replacement: `#249` removed it in the same sweep, and it stays excluded on one ground only, no observed occurrence. The exclusion itself is unchanged.
- DONE: (FO review, finding 2) acceptance claim 4's falsifier set did not cover the claim's own scope.
  The three named commands touched the merge, the removal stat, and the retired mechanism — none touched the sentence in finding 1, which is exactly how it survived. Claim 4 is now a per-sentence coverage table: nine assertions, each with the command that covers it and the result it returned, including the `git show ... | grep` and `git log -S` pair above. Four assertions not previously covered were run for the first time and all hold: `gh pr view 249` mentions the removal 0 times, `git tag --contains e634d3e7` returns `kc-dev-flow-v3.0.0` as the only kc-dev-flow tag, the section count goes 1 -> 0 across the commit, and `git log -S` puts the absolutes-rule removal at `e634d3e7`. One assertion is now named as having no command at all — that the six unrestored clauses' subject matter is carried by the profile stage contracts, which is a reading judgment.
- DONE: (FO review, finding 3) a miscount in the unchecked-claims list was corrected.
  Wrong: `git grep absolutes origin/main` finds them "in `CHANGELOG.md` and two retired plan documents". `git grep -l absolutes origin/main` returns four files — `kc-dev-flow/CHANGELOG.md` plus three under `docs/plans/`. Corrected to three, and the bullet now states the count as file names rather than a bare number.

## Stage Report: implementation

- DONE: Run the without-it audit per clause BEFORE writing any of them, and record it in the work item.
  `## Without-it audit` (committed state-checkout `91bb198e`, before any code edit). All five clauses KEEP, each against a real occurrence: seen-to-fail and falsifier-kind cite issue #154 §4/§5 (four field defects a non-falsifying check missed, plus this entity's own parity-check defect); cheapest-instrument cites issue #143's second gap (19.4min build vs 58.3min validation, 3x inversion from a mandated adversarial reviewer); repeated-failure-shape cites #143's first gap (three same-class rejections, budget trigger never fired); the absolutes rule cites #156's own undefended "only" and this entity's own ideation self-correction. Zero drops, so no deviation-table or Site 4 change follows.
- DONE: Apply the surviving accepted blocks as recorded, byte-for-byte, at the four named sites.
  Sites 1/2/4 extracted from the entity by `sed` into `/tmp/site{1,2,4}.md` and inserted programmatically (never retyped); Site 3 is two exact substring swaps on `CLAUDE.md:91`. Hand diff against the landed spans: `diff /tmp/site1.md <(sed -n '129,156p' kernel.md)`, `diff /tmp/site2.md <(sed -n '117,127p' kernel.md)`, `diff /tmp/site4.md <(sed -n '103,119p' MIGRATION.md)` — all three empty. Both kernel copies `diff`-identical; `python3 scripts/kc-dev-flow-contract-test.py` exits 0 (`kc-dev-flow contract: PASS`). Re-tampered one copy after landing to re-earn the seen-to-fail proof on the changed tree: `printf 'X' >> docs/dev/_mods/kernel.md` -> exit 1 `self-adopted shared core differs from package source`; restored via `cp` from the sibling copy (an initial `git checkout --` reverted to the pre-restoration committed blob, caught immediately via `diff`, re-applied) -> exit 0. Committed as `053eddb0` on `spacedock-ensign/verification-discipline-lost-in-the-rewrite`: exactly the 4 named files, 101 insertions / 1 deletion.
- DONE: If the audit changed the text, re-measure the load the same way the Measurement section did and update every figure it changed, including the per-route percentages.
  The audit dropped nothing, but the FO fast-forwarded this worktree from the entity's declared base `8ddd794d` to `9fee712c` before dispatch (`556e08fc`, `9fee712c` merged in the interval; confirmed live that `## Shared boundaries` and `## Communication` both still resolve at `9fee712c`, so both insertion sites hold). Re-measured everything at the new base, not by arithmetic on the note: `kernel.md` 124/1058 lines/words now, 165/1471 after (+413 words, +39.0%, down from the stale +41.9% because the denominator grew); `## Local Profile` 666 words (unaffected); all eight profile-stage bundle rows recomputed (now 18.0%-20.7%, was 19.6%-22.8%); `## Where it touches` lines-now/after for all four files (kernel x2 124->165, MIGRATION.md 101->119 actual not estimate, CLAUDE.md 103->103); `### Stop numbers`' stated base and measured-today line (101 changed lines, 39 lines across the two prose blocks); the `#249`-record paragraph's two "today" figures (kernel `986 words +65%` -> `1058 words +77%`; bundle `1,820-1,885 +43%-48%` -> `2,007-2,072 +56%-58%`) and its intervening-commit count (four -> five, `#277` added and checked — no size accounting, matching the other three).
- DONE: Run the citation resolver from acceptance evidence claim 2 and show it failing first: on the pre-change tree it must exit non-zero naming both dangling citations, and on the changed tree it must pass.
  BEFORE (untouched tree, `/tmp/citation-resolver.py .`): `checked 2 citation(s): kc-dev-flow/references/kernel.md § Outcome discipline, docs/dev/README.md § Proof Policy` then `DANGLING kc-dev-flow/references/kernel.md § Outcome discipline` and `DANGLING docs/dev/README.md § Proof Policy`, exit 1. AFTER (post-commit tree): `checked 2 citation(s): kc-dev-flow/references/kernel.md § Shared boundaries, docs/dev/README.md § Proof and delivery checks` then `all citations resolve`, exit 0. Resolver lives only at `/tmp/citation-resolver.py`, outside the repo; not committed, not added to CI.

### Summary

Restored the four `## Verification discipline` clauses plus the absolutes rule at the accepted compressed wording, unamended — the without-it audit found real evidence for all five in issues #143 and #154 plus this entity's own record, so nothing was dropped. Applied byte-for-byte at the four sites via extract-and-insert (never retyped), verified by hand diff, contract-test pass, and a re-earned tamper/restore cycle on the landed tree. The FO's base move to `9fee712c` (two intervening merges, one touching `kernel.md` outside the two insertion sites) required re-measuring every figure in `## Measurement` and `## Where it touches` from scratch rather than adjusting the ideation numbers by arithmetic; all now reflect the landed commit `053eddb0`. The citation resolver, run by hand and never committed, failed naming both dangling citations before the change and passed after.

## Delivery

Base: `main`. `origin/main` = `9fee712c`; this branch carries exactly one
commit on top of it (`053eddb0`, confirmed via `git log --oneline
origin/main..HEAD`), so no rebase is needed to open against `main`.

`delivery-branch-base.md`'s "prefer a stacked base" rule was checked against
every open delivery artifact sharing a file with this change
(`kc-dev-flow/references/kernel.md` and its adopted copy):

- **PR #277**, "stop the FO's verdict boundary reading as a licence to
  relay" — MERGED into `main` at `2026-08-22T10:18:27Z` as `9fee712c`, which
  is this branch's own base. Not a stacking candidate; already landed, and
  its only files were the two `kernel.md` copies.
- **PR #275**, same title as #277, is OPEN with `mergeable: CONFLICTING`,
  based on `feat/kc-dev-flow-size-tripwire` — the branch PR #272 ("let a
  declared size threshold stop work and hand back") squash-merged from on
  2026-08-22 (landed as `ef808a91`). #275's diff against `main` re-expands
  content already landed separately: the phrase `size threshold` appears 4
  times in `ef808a91`'s own `kernel.md` hunk and 6 times in #275's still-open
  diff of the same file; #275's other visible hunks match bullets that landed
  via #269 and #271. This is the squash-merge stacked-PR failure — the base
  PR squash-merged, so the stacked PR's diff re-expanded to show everything
  already on `main` as if still unmerged. #275 shares the file `kernel.md` by
  name, not by content or dependency: its live hunks insert a queue-exit-bar
  paragraph and two `## Shared boundaries` bullets at insertion points this
  change does not touch; this change's two sites (new `## Verification
  discipline`; last bullet of `## Shared boundaries`) neither build on,
  depend on, nor re-deliver anything #275 adds. Stacking onto a conflicting,
  stale-diffed PR based on an already-merged feature branch would pull
  someone else's already-landed work back into this review as if unmerged —
  exactly the cost `delivery-branch-base.md` names as the reason the rule
  exists. Target: `main`.

Residual, not this task's to resolve: PR #275 looks superseded by #269, #271,
#272, and #277 and worth closing or retargeting by its owner. Flagged for the
Captain; not acted on here.

Draft PR opened; not marked ready, not merged. No version, `CHANGELOG`, or
marketplace file touched — release-please owns those.

## Stage Report: validation

- DONE: For each of the five KEEP verdicts in the without-it audit, open the cited source and confirm the occurrence is real and shows the clause's absence costing something; name the weakest and say whether it survives alone.
  All five checked against source directly: `gh issue view 143` confirms the exact 19.4min/58.3min and 30%/47%/60% figures cited for KEEP 3 and 4 verbatim; `gh issue view 154` confirms the four field defects cited for KEEP 1 verbatim, and its falsifier-kind proposal for KEEP 2. `grep -rn cheapest kc-dev-flow/references/profiles/` independently reproduces the one-hit siting claim. KEEP 5 (the absolutes rule) rests on the weakest evidence: of its two "closer to home" occurrences, one (`#156`'s undefended "only", bounded by #159/#161/#162) predates the rule's removal — all four PRs' `mergedAt` checked via `gh pr view`: #156/#159/#161/#162 merged 2026-08-04, #249 merged 2026-08-18 — so it shows the rule's subject matter being refined while the rule was *present*, not its *absence* costing anything, which the audit's own stated bar excludes. The other occurrence (this entity's own ideation-stage self-correction) is genuine but self-referential and caught internally at no external cost. KEEP 5 likely survives on that occurrence alone, but with materially less weight than the other four, each backed by external field evidence.
- DONE: Re-derive the byte-for-byte match for Sites 1, 2, and 4 independently, and check Site 3's two substring swaps.
  Extracted Sites 1/2/4 from the entity myself via fresh `sed` ranges (the implementer's `/tmp` extracts no longer exist). Diffed against the landed spans: Site 1 (`kernel.md:129-157`) and Site 2 (`kernel.md:117-127`) both empty-diff (one benign trailing-blank-line offset at the section boundary, confirmed by direct inspection of the surrounding lines); Site 4 (`MIGRATION.md:103-119`) empty-diff. Site 3: `git diff 9fee712c 053eddb0 -- CLAUDE.md` shows exactly the two named section-name substitutions on one line, nothing else. Both `kernel.md` copies remain byte-identical (`diff` exit 0) and `wc -l` on all four touched files matches the entity's stated after-counts (165/165/119/103) exactly.
- DONE: Re-earn one seen-to-fail proof myself.
  `python3 scripts/kc-dev-flow-contract-test.py` on the clean tree: `PASS`, exit 0. Appended one byte to `docs/dev/_mods/kernel.md`: exit 1, `self-adopted shared core differs from package source`. `git checkout -- docs/dev/_mods/kernel.md`: exit 0 again; `git status --porcelain` empty.
- DONE: Verify the re-measured `## Measurement` and `## Where it touches` figures against the landed revision by recounting, not by checking the arithmetic.
  Recomputed from scratch, not by checking the entity's own addition: `kernel.md` word/byte/line counts at `9fee712c` and `HEAD` via independent `git show`/`wc`, matching 124/1058/7022 now and 165/1471/9645 after exactly. All eight profile-stage bundles rebuilt from their own components (`## Local Profile` 666 words + kernel + base + stage file, each word-counted independently, none of the eleven profile/base/stage files touched by this change) — all eight now/after totals and all eight percentages match the entity to the stated precision. `MIGRATION.md` (119) and `CLAUDE.md` (103) line counts confirmed via `wc -l`. `git diff --stat 9fee712c 053eddb0` independently reproduces the claimed 4 files / 101 insertions / 1 deletion.
- DONE: Deliver: open a Draft PR against the base `delivery-branch-base.md` selects, with the base evidence recorded in the entity.
  `## Delivery` section added to this entity (state-checkout commit `0b7aeba`, pushed): target `main`, with PR #277 (merged, this branch's own base) and PR #275 (open, `mergeable: CONFLICTING`, based on an already-squash-merged feature branch, its diff re-expanding #269/#271/#272/#277's already-landed content — confirmed by `gh pr diff 275` matching phrases from `ef808a91`) checked and ruled out as a stacking target. Draft PR opened: https://github.com/iamcxa/kc-claude-plugins/pull/279 (`base: main`, `isDraft: true`, `state: OPEN` — confirmed via `gh pr view`). Body carries the measured price, the five-KEEP audit result including the KEEP-5 finding above, and both named residuals (nothing standing keeps the restored words in place; the absolutes rule returns as authoring discipline with no enforcement). Not marked ready, not merged; no version/CHANGELOG/marketplace file touched.

### Summary

Independently re-verified the without-it audit, the byte-for-byte landing at all four sites, one seen-to-fail proof, and every recomputed Measurement/Where-it-touches figure — all confirmed against primary source (issues, PR metadata, git blobs, live command output), none taken on the implementer's word. One finding: the absolutes-rule KEEP rests on materially weaker evidence than the other four — one of its two supporting occurrences predates the rule's removal and shows presence, not absence, costing something — though it likely survives on its remaining occurrence alone. Delivery targets `main`: PR #275, despite sharing `kernel.md` by name, is a stale squash-merge artifact whose live content is unrelated to this change's two insertion sites and whose already-landed content duplicates #269/#271/#272/#277; stacking onto it would have pulled already-merged work back into this review as if unmerged. Draft PR #279 opened, unready, base evidence recorded in `## Delivery`.

## Stage Report: implementation (cycle 2)

- DONE: Amend the first bullet of `## Verification discipline` in both `kc-dev-flow/references/kernel.md` and `docs/dev/_mods/kernel.md`, which must stay byte-identical.
  Added one sentence: "That case must be one the check fails on if and only if the claim under test is false — not any case that reddens the check by an unrelated route," carrying issue #154 §4's framing. `diff kc-dev-flow/references/kernel.md docs/dev/_mods/kernel.md` empty both before commit and after (`ad37d51f`). `python3 scripts/kc-dev-flow-contract-test.py`: PASS, exit 0. Re-earned the seen-to-fail proof on the amended tree: appended one byte to `docs/dev/_mods/kernel.md` -> exit 1 `self-adopted shared core differs from package source`; restored via `cp` from the sibling copy (not `git checkout --`, which on an uncommitted edit reverts past it to the pre-amendment blob — hit this exact mistake once mid-task, caught via `diff`, re-applied from the sibling copy per the prior cycle's own recorded pitfall). Committed as `ad37d51f` on `spacedock-ensign/verification-discipline-lost-in-the-rewrite`: exactly the two kernel copies, 10 insertions / 6 deletions. Pushed; PR #279 head now `ad37d51f`, still `isDraft: true`, `state: OPEN` (`gh pr view 279`).
- DONE: Update the Site 1 literal block and the deviation table in the entity so the accepted text and the landed text still diff empty, and say the accepted wording changed under this authorized correction.
  Site 1 block (entity lines 273-302) and the bullet-1 deviation-table cell both updated; `diff` against `sed -n '129,158p' kernel.md` (post-commit) is empty for Site 1, and against `sed -n '117,127p'` for Site 2 (unchanged, confirming it wasn't touched). Deviation table cell now states the correction-round addition explicitly. This report and the Site 1 prose both name the change as an authorized correction under `#279`.
- DONE: Re-measure by recounting every figure the added words move: kernel word/line counts, all eight profile-stage bundle rows, `## Where it touches` after-counts, and the stop numbers' measured-today line.
  All recounted via `wc`/`git diff --stat`/`git show`, never adjusted by arithmetic on the prior cycle's numbers: `kernel.md` 167 lines / 9798 bytes / 1502 words after (was 165/9645/1471), delta `+444` words `+42.0%` (was `+413`/`+39.0%`); all eight bundle rows recomputed from `cat`ted component files (18.0-20.7% range -> 19.4-22.2%); `## Where it touches` kernel `after` 165->167, MIGRATION.md and CLAUDE.md unchanged (out of scope this round, confirmed via `git diff 9fee712c --stat` showing only the two kernel files moved); stop numbers `changed lines` 101->105 (43+43+18+1, `git diff --stat 9fee712c`), runaway area Site1+Site2 39->41 lines (30+11, both under the 47 stop number). Also recomputed, beyond the four named items, the `## Measurement` two-restoration-forms table (compressed row 40/2621/413 -> 41/2774/444, re-derived by extracting the exact Site1+Site2 spans and diffing empty against the committed kernel.md) and the closing `#249`-comparison sentence (`+413` -> `+444`), since both are figures the added words move and leaving them stale would itself be the class of defect this correction fixes.
- DONE: State in `## Acceptance evidence` which check would have reddened on the OLD wording but not the new one, or state plainly that no mechanical check distinguishes them.
  Added an explicit "Claims with no check, named plainly" entry: none of the three existing checks (contract-test parity, citation resolver, loader pins) inspect this bullet's content, so none reddens on the old wording and passes on the new one — the discrimination is a human read against issue #154 §4, and no standing check is proposed for it. Also extended claim 1 with the re-earned tamper/restore run and a note that the check's named limit is unchanged by the wording amendment.

### Summary

Correction round 1: amended bullet 1 of `## Verification discipline` in both kernel.md copies so the required negative-control case must falsify the claim under test, not merely redden the check by an unrelated route — closing the gap the validation gate's rejected finding named (the byte-parity check's own divergence-only limit satisfied the old wording without ever testing content correctness). Landed at `ad37d51f`, byte-identical copies, contract test green, seen-to-fail proof re-earned with the correct restore path (`cp`, not `git checkout --`, after hitting that exact pitfall once live). Re-measured every figure the ~31 added words move, by recounting rather than arithmetic, including two figures beyond the four named in the dispatch (the two-restoration-forms table and the `#249`-comparison closing sentence) because leaving them stale would reproduce the class of defect under correction. Acceptance evidence now states plainly that no mechanical check distinguishes the old and new bullet wording. Pushed to the existing branch; PR #279 updated in place, still Draft, still targeting `main`. Sites 2, 3, and 4 untouched, confirmed via diff scope.

## Stage Report: validation (cycle 2)

- DONE: Settle the question the rejection turned on, and answer it falsifiably rather than approvingly. …
  The amended bullet does **not** stop the reviewer it was written to stop, and the sentence is genuinely
  ambiguous at exactly the point the dispatch named. Reconstruction: claim = "the copies' content is right";
  check = byte parity between the two copies; negative control = tamper one copy → red. Apply the landed
  sentence — "That case must be one the check fails on if and only if the claim under test is false — not any
  case that reddens the check by an unrelated route." Under the reading the text licenses, "that case" is an
  anaphor whose antecedent is the single negative control one sentence earlier; the trailing "not any case…"
  is also a per-case constraint on selecting that control; and no quantifier ranges over the check's domain.
  Per-case, the biconditional is satisfied by any control where red and false coincide — which the
  single-tamper case does: the claim is false there (one copy corrupted) and the check is red. The
  unrelated-route guard does not fire either, because divergence is not an unrelated route in that
  constructed case; it *is* the claim's falsity as the reviewer produced it. So the reviewer clears the
  amended bar and still reports the false claim as proven. Only the global reading — the check must fail
  across the claim's falsity modes, so a both-copies-corrupted state disqualifies it — stops the incident,
  and nothing in the bullet forces that reading. Worse, per-case the biconditional is degenerate: it holds
  whenever (red ∧ false) or (green ∧ true), so relative to the pre-correction wording the amendment adds only
  the unrelated-route guard and never reaches the "the check cannot detect this class at all" failure. A
  careful agent follows the per-case reading, because a kernel reader has none of this rejection's context to
  import. Candidate direction for implementation, not a spec: quantify over falsity — no way for the claim to
  be false may leave the check silent.
- DONE: (bounded observation, in scope of the above) issue `#154` §4's own framing would also not have
  stopped it. "A check was run whose result could not have falsified the claim it was offered as proof of" is
  modal-existential over the check; the parity check narrowly clears it, since one falsity mode (divergence)
  does redden it. The bar that catches the incident is coverage of the claim's falsity modes, which is
  stronger than §4's literal phrasing. Carrying §4 faithfully was necessary and not sufficient.
- DONE: Verify the correction's mechanics independently, by re-deriving rather than by reading the implementer's account …
  All pass. Both copies byte-identical (`diff` exit 0, 167/1502/9798 each); `python3
  scripts/kc-dev-flow-contract-test.py` → `PASS`, exit 0. Site 1 (entity 273-302) vs `kernel.md:129-158`,
  Site 2 (322-332) vs `kernel.md:117-127`, Site 4 (350-366) vs `MIGRATION.md:103-119` — all three `diff`
  empty against my own fresh `sed` extracts. Deviation-table cell closed on both halves: the added sentence
  is absent from `e634d3e7^` and from `#156` (`git show f228f76f:… | grep -c 'if and only if'` → `0`).
  Recounted, not arithmetic-checked: kernel 124/1058/7022 at `9fee712c` → 167/1502/9798 at HEAD (+444 words,
  +42.0%); all eight bundle rows rebuilt from independently word-counted components (`## Local Profile` body
  666 + kernel + base + stage) reproduce 19.4%–22.2% and every now/after total exactly; compressed block
  41/444/2774 and verbatim 516 words both reproduce (verbatim lines/bytes 48/3298 vs the recorded 47/3296 —
  span-boundary noise in my reconstruction, word count exact); `git diff --shortstat 9fee712c HEAD` → 4
  files, 105 insertions, 1 deletion; runaway area 30+11 = 41 < 47. Sites 2/3/4 untouched this round:
  `git diff --name-only 053eddb0 ad37d51f` returns only the two kernel copies. PR #279 head `ad37d51f`,
  `base: main`, `isDraft: true`, `state: OPEN`; `gh pr list --head <branch> --state all` returns exactly one
  PR, so no second PR was opened.
- DONE: Test the honesty of the new acceptance-evidence statement that no mechanical check distinguishes the old wording from the new one. …
  The statement is wrong as opened, right as closed. I built two discriminators and ran both live with the
  pre-correction wording restored to **both** copies (parity intact) and again on HEAD: (A) `grep -q 'if and
  only if the claim under test is false'` — red on old, green on new; (B) a word floor `wc -w ≥ 1502` — 1471
  on old (red), 1502 on new (green). So "No mechanical check distinguishes them" is falsified by
  construction. Neither is evidence, which is why the paragraph's closing sentence ("No check *here* …") is
  the true one: A is a presence-grep over prose this change itself authors, which this item's own ideation
  report explicitly refuses; B is content-blind and passes on any 31-word addition of arbitrary text. I found
  no third construction that reads the bullet's meaning rather than its bytes or its size. Confirmed
  non-discrimination of the existing checks by running them, not by trusting the account:
  `kc-dev-flow-contract-test.py` (which also carries the claim-3 loader pins) exits `0` on the old wording in
  both copies, identically to new. The citation resolver's non-discrimination is **derived, not re-run** —
  its only inputs are `CLAUDE.md`'s two citations and the cited headings, and `git diff 053eddb0 ad37d51f`
  touches neither file nor any heading line. Ask: bound the opener to match the closer.

### Summary

One blocking finding, and it is the one this round existed to produce: the amended bullet 1 is ambiguous at
the exact point the rejection turned on, and under the reading its own grammar licenses it re-certifies the
byte-parity reviewer rather than stopping it — "that case" attaches the biconditional to the chosen negative
control, where it is degenerate, instead of to the check across the claim's falsity modes. A bounded
observation alongside it: issue `#154` §4's literal framing would not have stopped that reviewer either, so
the fix needs coverage of falsity modes, not a faithful carry of §4. Everything mechanical passes and was
re-derived rather than read — byte-identical copies, contract test green, all three literal blocks diffing
empty, every moved figure recounted from the files, Sites 2/3/4 untouched, PR #279 updated in place at
`ad37d51f` and still Draft. One minor finding: the new acceptance-evidence statement opens with an unbounded
"No mechanical check distinguishes them" that two cheap constructions falsify literally, though neither
construction is evidence; its own closing sentence already carries the honest bound. Working tree left clean
(`git status --porcelain` empty) after the old-wording experiment; no code was changed by this stage.

## Stage Report: implementation (cycle 3)

- DONE: Revert the sentence `ad37d51f` added to bullet 1 of `## Verification discipline` in both kernel.md copies, returning the bullet to the wording approved at the ideation gate and landed at `053eddb0`. Prove it by diffing the restored bullet against `053eddb0`'s span rather than by retyping it; both copies stay byte-identical and `python3 scripts/kc-dev-flow-contract-test.py` must pass. Restore the Site 1 literal block and the per-clause deviation table in the work item so the accepted text and the landed text diff empty again.
  Both `kc-dev-flow/references/kernel.md` and `docs/dev/_mods/kernel.md` restored to `053eddb0`'s exact bytes: `git show 053eddb0:<path>` written over the working copy, then `diff` against `git show 053eddb0:<path>` for each — empty. `diff kc-dev-flow/references/kernel.md docs/dev/_mods/kernel.md` empty. `python3 scripts/kc-dev-flow-contract-test.py`: PASS, exit 0. Re-earned the seen-to-fail proof: appended one byte to `docs/dev/_mods/kernel.md` -> exit 1 `self-adopted shared core differs from package source`; restored via `cp` from the sibling copy -> exit 0. Committed as `d55d6a4d` on `spacedock-ensign/verification-discipline-lost-in-the-rewrite`: exactly the two kernel copies, 6 insertions / 10 deletions. Pushed; PR #279 head now `d55d6a4d`, still `isDraft: true`, `state: OPEN` (`gh pr view 279`); `gh pr list --head <branch> --state all` returns exactly one PR. Site 1 (entity 298-325) diffs empty against `kc-dev-flow/references/kernel.md:129-156`; Site 2 (entity 335-345) diffs empty against `kc-dev-flow/references/kernel.md:117-127`. Deviation-table cell for bullet 1 reverted to its `053eddb0` wording (no correction-round-1 clause).
- DONE: Bound the claim where the item makes it — in `## Acceptance evidence` and in `## Which clauses have earned restoration`. This bullet closes the four field defects issue #154 §4 names; it does NOT close the class where a check's detectable failure mode is narrower than the claim it is offered as proof of. Name the byte-parity incident as the worked example, record that two attempts to close it by wording both failed and why, and write the limit as a limit — not as an absolute and not as a guarantee. Confirm the acceptance-evidence paragraph about the amended wording is gone rather than leaving a bounded version of a paragraph about a sentence that no longer exists.
  Added a "Bound:" paragraph to the "Seen to fail" bullet under `## Which clauses have earned restoration` and to claim 1's "Named limit" paragraph under `## Acceptance evidence`: both state the clause closes issue #154 §4's four field defects but not the byte-parity incident's own class (a check's detectable failure mode narrower than the claim offered), name both failed wording attempts (`ad37d51f`'s per-case biconditional over the chosen negative control, and #154 §4's own framing checked directly), and phrase the close as "a limit ... not a guarantee." The "That correction round 1's amended bullet 1 wording is what actually landed" bullet under "Claims with no check, named plainly" is deleted outright — `grep -n "correction round 1's amended"` on the pre-stage-report body returns nothing.
- DONE: Re-measure by recounting from the files, never by reverting numbers from memory: kernel word and line counts, all eight profile-stage bundle rows, `## Where it touches`, the stop numbers' measured-today line, the two-restoration-forms table and the `#249`-comparison sentence all return to their `053eddb0` values. Push to the same branch so PR #279 updates in place; do not open a second PR, do not mark it ready, do not merge, and leave Sites 2, 3 and 4 untouched.
  All recounted via `wc -l -w -c` on the restored files, not by reverting the prior cycle's numbers by hand: `kernel.md` 165 lines / 1471 words / 9645 bytes, matching both copies (`wc -l -w -c kc-dev-flow/references/kernel.md docs/dev/_mods/kernel.md`). `## Where it touches` table reverted to 124->165 for both kernel copies, MIGRATION.md and CLAUDE.md unchanged. Stop numbers reverted to 101 changed lines (`git diff --stat 9fee712c` on the tree after this commit reproduces exactly `4 files changed, 101 insertions(+), 1 deletion(-)`, matching the entity), runaway area 28+11=39. `## Measurement` two-restoration-forms table reverted to compressed row 40/2621/413; shared-core cost reverted to `+413` words `+39.0%`; all eight profile-stage bundle rows reverted to their `053eddb0` now/after/percentage values; closing `#249`-comparison sentence reverted to `+413` words / about `+20%`. Sites 2, 3, and 4 confirmed untouched this round: `git diff --name-only 053eddb0 d55d6a4d` returns only the two kernel copies. Pushed to the existing branch (`git push origin spacedock-ensign/verification-discipline-lost-in-the-rewrite`); PR #279 not marked ready, not merged, no second PR opened.

### Summary

Reverted `ad37d51f`'s wording amendment on the Captain's ruling that a second wording attempt would repeat the same failure shape the restored "when one failure shape repeats, change the work, not the wording" clause exists to catch. Both kernel.md copies restored to `053eddb0`'s exact bytes (verified by diff, not retyping), contract test green, seen-to-fail proof re-earned. The entity's Site 1 block, deviation table, and every figure the correction-round-1 words moved (kernel word/line counts, all eight bundle rows, `## Where it touches`, stop numbers, the two-restoration-forms table, the `#249`-comparison sentence) reverted to their `053eddb0` values by recounting the restored files, not by arithmetic. Added a bounded claim, in both `## Which clauses have earned restoration` and `## Acceptance evidence`, that the seen-to-fail clause closes issue #154 §4's four field defects but not the byte-parity incident's own class — a check whose detectable failure mode is narrower than the claim it is offered for — naming both failed wording attempts and why, phrased as a limit rather than a guarantee. Deleted the cycle-2 acceptance-evidence paragraph about the amended wording outright, per the ruling that it is subsumed by the revert rather than needing a bounded replacement. Pushed to the existing branch; PR #279 updated in place at `d55d6a4d`, still Draft, still targeting `main`. Sites 2, 3, and 4 untouched throughout.

## Stage Report: validation (cycle 3)

- DONE: Confirm the revert is exact and complete, by re-deriving rather than reading the implementer's account.
  `git diff 053eddb0 HEAD -- kc-dev-flow/references/kernel.md docs/dev/_mods/kernel.md` empty; `git show HEAD:kc-dev-flow/references/kernel.md | shasum -a 256` equals `git show HEAD:docs/dev/_mods/kernel.md | shasum -a 256` (`e99d55ad…`); `python3 scripts/kc-dev-flow-contract-test.py` -> `PASS`, exit 0; `git diff --stat 053eddb0 HEAD` empty (whole-tree, not just kernel); `git diff --shortstat origin/main HEAD` = `4 files changed, 101 insertions(+), 1 deletion(-)`, identical to `git diff --shortstat origin/main 053eddb0`. `git diff --name-only origin/main HEAD` = `CLAUDE.md`, `docs/dev/_mods/kernel.md`, `kc-dev-flow/MIGRATION.md`, `kc-dev-flow/references/kernel.md` — the same four Site 1-4 files, confirming Sites 2, 3, 4 are untouched (the whole-tree diff against `053eddb0` being empty covers them too, not just Site 1). Site 1 literal block (entity 298-326) diffed byte-for-byte against `sed -n '/^## Verification discipline$/,/^## Communication$/p' kc-dev-flow/references/kernel.md` — identical. Deviation-table cell for bullet 1 (entity line 282, "cut 'A probe that returns...'") checked against `git show e634d3e7^:kc-dev-flow/references/kernel.md` — the landed bullet is exactly `e634d3e7^`'s bullet 1 minus that one sentence, as claimed. PR #279: `gh pr view 279 --json headRefOid,isDraft,state` = head `d55d6a4d…`, `isDraft: true`, `OPEN`; `gh pr list --head <branch>` returns exactly one PR.
- DONE: Judge the new bounded claim as a claim, in both `## Which clauses have earned restoration` and `## Acceptance evidence`.
  Fetched issue #154 (`gh issue view 154 --json body`). Section 4 ("Rule 3 generalizes: pair every check with a negative control") names exactly four field examples (wrong-pipeline exit code, log-filter false negative, unverified backup, same-connection delete count) and its own proposed addition — "prefer the cheapest check that can fail, and pair it with a negative control that demonstrates it can" — closes with "Every instance above would have been caught by it," directly matching the restored bullet's negative-control framing. First question: true, on the issue's own text. Second question: the two sections are NOT phrased identically, contrary to the implementer's report. `## Which clauses have earned restoration` (line ~134) already reads "Two attempts to close that class by wording the clause differently both failed" — bounded to the two named attempts, no universal claim. `## Acceptance evidence` claim 1 (line 586) instead reads "no wording of this clause reaches that" — a universal/factual claim (its contrary — someone finding a wording that does reach it — would falsify it) with no enforcement point of the four kinds Site 2 itself now names (permission check, schema constraint, unreachable branch, fail-closed check). The paragraph's own reasoning ("parity is the correct check for parity") is a structural argument, not one of those four mechanism types — it is closer to "I checked," which Site 2's own text excludes as a qualifying enforcement point. Verdict: not defensible as written under the rule this same change restores; it should be bounded to the two attempts actually made, matching how the sibling section already states it. This is a first occurrence of this specific failure shape (an unbounded absolute in the work-item's own claim about the clause, not a third wording of the clause itself), so a targeted reword of one sentence is proportionate — not a restructure, and not something this ensign is doing here per the checklist's own instruction not to fold a bullet-1 wording fix into this item.
- DONE: Do not propose, draft, or evaluate a third wording of bullet 1.
  No alternative kernel.md clause text proposed. Observation for a future work item, not folded in here: if a wording were ever attempted to close the parity-class gap, it would need to bind the check's *demonstrated falsity domain* to the *scope of the claim it is cited for*, not merely require that the check have failed on some case — which is closer to the absolutes-rule's scope-matching test (Site 2) than to the seen-to-fail clause's subject matter, suggesting the gap may not be a bullet-1 wording problem at all.

### Summary

Re-derived: the revert is exact and complete — both kernel.md copies are byte-identical to each other and to their `053eddb0` span, the contract test is green, and the whole-tree diff against `053eddb0` is empty, so Sites 2-4 are confirmed untouched by the same evidence that confirms Site 1. PR #279 is updated in place at `d55d6a4d`, Draft, sole PR from the branch. The bounded claim's first half (closes issue #154 §4's four field defects, does not close the byte-parity incident's own class) is true and matches the issue's own text. Its second half is a finding: `## Acceptance evidence` claim 1 carries an unbounded absolute ("no wording of this clause reaches that") that fails the enforcement-point test the restored absolutes rule itself defines, while the parallel sentence in `## Which clauses have earned restoration` is already correctly bounded to "two attempts... both failed." Recommend correction round 3 reword the one sentence at `## Acceptance evidence` line ~586 to match the sibling section's bounded phrasing; no other defect found. No third wording of bullet 1 proposed or evaluated.
