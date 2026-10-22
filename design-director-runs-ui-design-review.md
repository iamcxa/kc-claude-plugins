---
title: A named design-director role runs the ui design review in place of a general-purpose sonnet agent
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:design-director-runs-ui-design-review:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:design-director-runs-ui-design-review-backlog-1
              briefing:
                id: briefing:design-director-runs-ui-design-review:backlog:attempt-1:revision-1
                digest: sha256:a26c4da383fb5f17a359d53ce8aeccd8035d5bc3e1fcedfb55edc67fda39a563
                room-ref: ./design-director-runs-ui-design-review/review/backlog/briefing-1
---

## Scope

- Source: the Captain 「我還是希望開設計總監，讓它來做目前指示的內容，等於派出的 general purpose sonnet 改成設計總監。此外，在可用前提，平行多派一個 gpt astra mid 來做設計輔助夥伴，合理嗎？」 (chat, 2026-10-22), then 「可以」 to FO's 「開一張「設計總監」任務，astra 輔助先用 POC 驗證，模型等量測結果再定，可以嗎？」 (chat, 2026-10-22).
- Shape asked for: `skills/ideation/design-review.md` dispatches a named `kc-dev-flow-2:design-director` agent, with an agent file that declares its model like chief-engineer and engineering-reviewer, carrying the existing brief unchanged; a parallel `gpt-6-astra` medium-effort design helper joins only if dev2-poc task design-helper-astra-poc shows it adds findings.
- Inputs before ideation: the read-only measurement of ui design reviews 2026-10-08 to 2026-10-22 (FO-dispatched, 2026-10-22) decides the declared model; dev2-poc task design-helper-astra-poc decides the helper.
- Upstream first: no design-director role in the installed plugins (searched 2026-10-22: `grep -rli 'design director'` over ~/.claude/plugins/cache and ~/.claude/skills found none); gstack `plan-design-review` is interactive, for a person, not a dispatched reviewer; the kc-dev-flow-2 chief-engineer and engineering-reviewer agent files are the pattern.
- Non-goals: changing the brief's eight dimensions or severities; a design review for tasks without `Surfaces: ui`.

## Captain amendments

### Amendment 1 — 2026-10-22, chat
Captain: 「設計總監照建議。這個角色會叫什麼？GPT 同伴仍保留提案，之後再討論」 (chat, 2026-10-22)
Asked: 「設計總監任務的範圍要不要照量測結果調整？」, with FO's four points: (1) the named design director runs the design review and stays on sonnet, since the measurement shows no evidence the model is the problem; (2) the author cannot decline a review finding alone: the design director rules on each finding the author would decline, and the ones it still declines are listed together at the design gate for the Captain; (3) at validation the design director reviews screenshots of the built screen; (4) dev2-poc task design-helper-astra-poc closes without running.
Supersedes: none
Design: the role runs the existing brief on sonnet; the author's declines go to the design director, and the ones it upholds are listed at the ideation gate; validation adds a design director review of screenshots of the built screen; the astra helper is dropped from this task. Evidence: intake/ui-design-review-measurement-2026-10-22.md.

## FO alignment

Alignment: needed at ideation; the declared model and whether the helper joins are his, after the measurement and the POC.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
