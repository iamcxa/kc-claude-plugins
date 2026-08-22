---
id: 9ydm2mmakce2r49v40q98377
title: The 3.0 rewrite dropped four merged verification rules and no migration note said so
status: backlog
source: found 2026-08-21 while answering the Captain's original question about issue #154, whose maintainer reply states these clauses had already shipped; they had, and then they were removed
product: kc-dev-flow
sprint:
started:
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
                state: pending
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

## Accepted outcome and non-goals

## Acceptance evidence

## Measurement
