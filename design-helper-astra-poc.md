---
title: A gpt-6-astra medium design helper, given the same previews and brief, finds ui problems the sonnet design review missed
variant: kc-dev-flow-2
profile: poc
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:design-helper-astra-poc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:design-helper-astra-poc-backlog-1
              briefing:
                id: briefing:design-helper-astra-poc:backlog:attempt-1:revision-1
                digest: sha256:483d0b686312ba00cc7324126db011cdf66da64c0675cb5772619dd7822b3504
                room-ref: ./design-helper-astra-poc/review/backlog/briefing-1
---

## Scope

- Source: the Captain 「在可用前提，平行多派一個 gpt astra mid 來做設計輔助夥伴，合理嗎？」 (chat, 2026-10-22), then 「可以」 to FO's 「開一張「設計總監」任務，astra 輔助先用 POC 驗證，模型等量測結果再定，可以嗎？」 (chat, 2026-10-22). Consumer: dev2 task design-director-runs-ui-design-review.
- What exists: kc-dev-flow-2 `skills/ideation/design-review.md` (brief, eight dimensions, YAML output); `codex exec -i <FILE>` attaches images (checked with `codex exec --help`, 2026-10-22); the read-only measurement of ui design reviews 2026-10-08 to 2026-10-22, which lists each later-found ui problem judged a miss.
- The run: for the ui tasks that measurement names with at least one miss, give the saved previews and the `UI proposal:` line to two arms with the same brief: a fresh `general-purpose` sonnet agent and `codex exec --sandbox read-only -m gpt-6-astra -c model_reasoning_effort='"medium"' -i <previews>`. A scorer that is told neither arm nor model, and whose dispatch names neither, marks which recorded misses each answer catches and which findings are ungrounded.
- Bar: report per arm the misses caught, ungrounded findings, and tokens and wall time per run; the helper is worth adding only if astra catches a miss sonnet does not; a difference within one miss is read as no difference.
- Budget: one run per arm per task, one scoring pass; stop there. If the measurement names no miss, close without running.
- Non-goals: changing the brief; an opus or fable arm.

## Acceptance criteria

**AC-1** Both arms ran on the same inputs with the pinned flags. Evidence: the astra rollouts carry `"model":"gpt-6-astra"` and `"effort":"medium"`; the sonnet runs name model sonnet; each arm's input list equals the task's previews. Falsifier: another model, effort or input set.

**AC-2** The scoring is blind. Evidence: the scorer's dispatch record and the answer files carry no arm, model or vendor name; scores cite the recorded miss each catch matches. Falsifier: an arm or model name in the scorer's dispatch or in a scored file.

## FO alignment

Alignment: not needed before implementation; the Captain approved the run (「可以」, 2026-10-22) after FO stated its arms and comparison, restated above.
Release review: not needed: the task belongs to no release.
Surfaces: none
Visible change: none
