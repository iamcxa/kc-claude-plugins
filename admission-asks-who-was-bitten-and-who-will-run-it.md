---
title: "Admission asks who was bitten and who will run it: a brief carries `bite:` and `consumer:` lines, and a fixture that copies an existing file is refused"
status: ideation
source: "Captain 2026-09-15 「目前 dev flow 合約 or kernel 是否沒有 yagni 原則？為何會做出用不到的測試？」 then 「立這張 r4 票」"
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: ship-cloud-wrapper-r4
sprint-readiness: ready
started:
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: gzrgwdxkh6zkenkswkhasmjc
gates:
    version: 1
    records:
        - id: gate:gzrgwdxkh6zkenkswkhasmjc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:gzrgwdxkh6zkenkswkhasmjc-backlog-1
              briefing:
                id: briefing:gzrgwdxkh6zkenkswkhasmjc:backlog:attempt-1:revision-1
                digest: sha256:b52c60eac0ce49a09a95c4f58679f4e081cfc0f3d3f60cad211deb21d63275e7
                room-ref: ./admission-asks-who-was-bitten-and-who-will-run-it/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:gzrgwdxkh6zkenkswkhasmjc:backlog:1
                briefing: briefing:gzrgwdxkh6zkenkswkhasmjc:backlog:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-09-14T22:29:57.599568Z"
                decision: approve
                reason: 'backlog admission on the batch conn: brief carries bite, consumer, AC-1..4, non-goals, route-back. Enter ideation.'
                conn:
                    quote: r4 現在開
                    source: Captain chat 2026-09-15, opening the ship-cloud-wrapper-r4 batch of three (pilot profile)
              application:
                target-stage: ideation
                state: consumed
---

Two PRs in the ship-cloud-wrapper-r3 batch passed every gate — backlog admission, ideation, the
implementation-exit `surface-map-check.py`, validation, and the ship first officer's verification at
the pinned SHA — and were closed unmerged by the Captain within one question each on 2026-09-15:
iamcxa/kc-claude-plugins#446 (2136 lines, 1946 of them three copies of a released `pr-merge.md`; the
0.27.0 pin row had no consumer once adopter-side checks were removed) and #450 (1117 lines, 618 a
byte-identical copy of `docs/dev/_mods/pr-merge.md`; its checks duplicated the installed loader and
#446, and the only measured bite was one sentence in `MIGRATION.md`). The kernel's Minimal necessity
(`references/kernel.md` § Completion invariant) grades every retained surface against the brief's
accepted outcome, so a surface the brief asked for is necessary by construction; nothing in the
kernel, `choose-work-profile`, or the pilot contract asks who was bitten before the brief was
written or who executes the change after merge (`grep -rn consumer` finds only the compatibility
definition). A one-word mutant that makes a test fail satisfies the without-it observation while
proving only that the test detects change, not that anyone needs the detection.

## Accepted outcome

Admission refuses a brief that cannot name its bite and its consumer, and the fixture copy escape
is closed, without touching the kernel's Minimal necessity text.

## Acceptance criteria

* **AC-1** A brief entering the backlog gate carries `bite:` (the command, date and cost of the failure it repairs, or the Captain's verbatim ask) and `consumer:` (the program, workflow step or person that executes the change after merge). `plan-lint.py` (or the backlog-gate check the package already runs) refuses a brief missing either, naming the line. Verified by: the two closed PRs' briefs, replayed, are refused; the merged #445/#448/#451 briefs pass once the two lines are added. Falsified by: any of the five r3 briefs passing unchanged.
* **AC-2** `surface-map-check.py` refuses a changed file whose bytes are identical to another file in the repository at the candidate, or to a file in the cached Spacedock plugin, unless the `SURFACE:` line names it as a generated copy with the generating command. Verified by: #446's and #450's diffs, replayed, are refused on the fixture paths. Falsified by: either diff passing.
* **AC-3** The ship first officer's verification step (kc-ship-flow `run-batch` skill, accept-by-evidence) adds one line: the consumer named in the brief is shown to exist at the candidate (a path or symbol that invokes it). Verified by: the r3 questions log's two closures reproduce as a refusal in the dry run.
* **AC-4** No new receipt, harness or LOC gate; the kernel's "LOC is diagnostic, never a gate" sentence stands.

## Non-goals

- No change to `references/kernel.md` Minimal necessity wording.
- No retroactive edit of merged r3 briefs beyond adding the two lines as the AC-1 fixture.

## Route-back conditions

- Back to backlog if `plan-lint.py` no longer owns admission after `retire-the-provider-backed-planning-path` (#444) lands its committed-brief intake — re-point AC-1 at that intake's check.

Profile recommendation: pilot.
