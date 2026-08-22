---
id: 9ydm2mmakce2r49v40q98377
title: The 3.0 rewrite dropped four merged verification rules and no migration note said so
status: ideation
source: found 2026-08-21 while answering the Captain's original question about issue #154, whose maintainer reply states these clauses had already shipped; they had, and then they were removed
product: kc-dev-flow
sprint:
started: 2026-08-22T09:54:50Z
completed:
verdict:
worktree:
issue: 154
pr:
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
  interview found it after the gate. Strongest case.
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

Diff base `origin/main` = `8ddd794d`, which equals this worktree's `HEAD`.

| Path | lines now | lines after |
|---|---:|---:|
| `kc-dev-flow/references/kernel.md` | 118 | 158 |
| `docs/dev/_mods/kernel.md` | 118 | 158 |
| `kc-dev-flow/MIGRATION.md` | 101 | ~117 |
| `CLAUDE.md` | 103 | 103 |

`lines now` counted in the current tree. `lines after` for both `kernel.md`
copies is measured, not estimated: the candidate file was built and counted.
`MIGRATION.md` is an estimate. `CLAUDE.md` changes two section names inside line
91 and adds no line.

Reconciled against the journey in both directions: every file in the table
appears in the journey, and every file the journey depends on
(`profile-contract-loader.py`, `scripts/kc-dev-flow-contract-test.py`,
`docs/dev/README.md`) is read, never written, so it is correctly absent here.

### Stop numbers

Measured as the diff against `origin/main` = `8ddd794d`.

- **changed files: 5.** Four above plus this work item. Stop and report at 6.
- **changed lines: 100.** Measured today: 80 added to the two kernel copies,
  about 16 to `MIGRATION.md`, 1 changed in `CLAUDE.md`. Stop and report at 140.
- **runaway area: the two kernel prose blocks.** Compression is the thing most
  likely to grow back under review pressure. Stop and report if the two blocks
  together exceed 47 added lines — the measured size of the verbatim
  alternative, past which the compression decision has been reversed without a
  ruling.

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
  landed_change: pending
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

**What the shared core costs.** `kernel.md`: 118 lines / 6593 bytes / 986 words
now; 158 / 9215 / 1399 after. `+413` words, `+41.9%`.

**What every stage loads.** Measured as the `## Local Profile` section of
`docs/dev/README.md` plus `kernel.md` plus the selected profile base plus the
selected stage contract.

| Profile / stage | now | after | change |
|---|---:|---:|---:|
| `poc-exploration` / `build` | 1885 | 2298 | +21.9% |
| `poc-exploration` / `prove` | 1838 | 2251 | +22.5% |
| `pilot-product-slice` / `shape` | 2103 | 2516 | +19.6% |
| `pilot-product-slice` / `build` | 1845 | 2258 | +22.4% |
| `pilot-product-slice` / `verify-deliver` | 1810 | 2223 | +22.8% |
| `production` / `shape` | 2083 | 2496 | +19.8% |
| `production` / `build` | 1820 | 2233 | +22.7% |
| `production` / `verify` | 1875 | 2288 | +22.0% |

**Against `#249`'s own record — and a correction to how it is being cited.**
`#249`'s PR body claims "required policy input fell from about 6,100 words to
960–1,007 words for the Local Profile plus one selected build contract:
**83.5%–84.3% less input**." That 960–1,007 figure is **not reproducible from the
tree.** At `e634d3e7` the closest reconstructions are 845–900 words without the
`## Local Profile` section and 1,274–1,329 with it; neither brackets the quoted
range. So the restoration is not measured against that number. It is measured
before and after by one method, above.

What the tree does show at `e634d3e7`: `kernel.md` was 597 words and the
Local-Profile-plus-base-plus-build bundle was 1,274–1,329 words. Today, with no
part of this change landed, `kernel.md` is 986 words (`+65%`) and that bundle is
1,820–1,885 (`+43%` to `+48%`). The small core has already grown by roughly
the same amount this restoration adds, across four commits — `#267`, `#271`,
`#272`, `#276`. Bounded claim, checked by
`git log --format='%B' -1 <sha> | grep -in 'word\|load\|byte\|input'` over
each: three of the four state no size accounting at all, and `#272` does — it
records `kernel.md` dropping 47 words. So growth here has been weighed once in
four changes, not never. That is the honest frame for the price: `+413` words is
real, and it is about `+22%` on every route.

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
