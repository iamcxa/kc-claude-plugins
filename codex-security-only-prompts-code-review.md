---
title: When Codex posts only a security summary, the codex reader names the code-review request as the next step
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:codex-security-only-prompts-code-review:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:codex-security-only-prompts-code-review-backlog-1
              briefing:
                id: briefing:codex-security-only-prompts-code-review:backlog:attempt-1:revision-1
                digest: sha256:036c3c1b1b763868cc783b981196ebe1f30eb7c13e00854355254de2297a8618
                room-ref: ./codex-security-only-prompts-code-review/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:codex-security-only-prompts-code-review:backlog:1
                briefing: briefing:codex-security-only-prompts-code-review:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-11-06T14:28:36.977647Z"
                decision: approve
                reason: 'The Captain chose 「核准（建議）」 (host question dialog, 2026-11-06), answering 「決定：第 16 批這五張（跳過的 CI 不擋、Codex 只貼安全摘要時提醒、交付檢查的相對路徑、ADR 編號跨流程預留、婉拒只在出過事時開任務）都用 Pilot，照各自寫下的範圍、預算與停止條件進入構想嗎？核准即接受「婉拒只在出過事時開任務」任務裡寫的標準（指出真的錯並說得出誰受害、再次出現、或你要求）。要改哪張直接說。」. Recommendation: followed.'
              application:
                target-stage: ideation
                state: pending
---

When Codex has posted only its security-review summary on a PR head, codex_review.py (or pr_watch.py) prints a next line that asks FO to request `@codex review`, so a merge ask is not prepared on a head with no code review.

## Scope

- Source: the Captain 「開」 (chat, 2026-11-06), answering 「要開這 4 張嗎？」 after fo-feedback round 005 (.notes/fo-feedback/round-005.md, closed 2026-11-06).
- Bite: ops-inbox PR #727 merged 2026-10-27 with Codex's code review only on an earlier commit d7eeeef26 (unresolved findings) and only a security review on the merged head 5dee91fb7 (Codex review-state comment, read by FO 2026-11-06); kc-paseo-plugins lost about 10 minutes per PR on #71 #72 #73 #75 waiting on exit 4 (operator report); Bridge outcome gap 7 (_l3-dogfood/OUTCOME.md, a94f9cd).
- Upstream first: kc-dev-flow-2 extensions/codex codex_review.py (exit 4 "not reviewed") and scripts/pr_watch.py.
- Non-goals: requesting the review automatically (a PR comment stays FO's step).

- Batch 16: the Captain 「可以，就這樣」 (chat, 2026-11-06), answering 「這批做 2、3、4、5、9 這 5 張，可以嗎？」, which named this task.

## Budget
- One package PR; the workflow word budget does not rise unless the design names a raise for the Captain.

## Stop condition
- A replay of a security-only head prints the code-review next line; a head with a code review prints none.

## FO alignment

Alignment: needed at ideation; the design choice is his to accept.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
