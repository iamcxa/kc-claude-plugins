---
title: POC — FO follows the workflow rules at least as well when it starts from an index and reads each rule at the moment it applies
variant: kc-dev-flow-2
profile: poc
merge: pr
status: implementation
gates:
    version: 1
    records:
        - id: gate:readme-index-attention-poc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:readme-index-attention-poc-backlog-1
              briefing:
                id: briefing:readme-index-attention-poc:backlog:attempt-1:revision-1
                digest: sha256:6ee60a805ace07c0d5f6fadb33187cd393901d1c1da8938e477c801b6c744af4
                room-ref: ./readme-index-attention-poc/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:readme-index-attention-poc:backlog:1
                briefing: briefing:readme-index-attention-poc:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-17T13:58:03.918571Z"
                decision: approve
                reason: 'Captain approved in chat (「按你建議的 poc 標準可以」) the POC with the recommended bar stated in the gate question: five probes, three runs per arm on Sonnet; pass when the index arm follows the probed rules at least as often in total, is worse on no probe by more than one run, and loads at most a quarter of the whole-README startup words'
              application:
                target-stage: implementation
                state: consumed
---

Filed on the Captain's words (chat, 2026-10-17), after FO said #658 (workflow-budget-ratchet) only cuts words and does not change how the README is read: 「長度的問題是，不應該讓 llm一次讀麽多字，應該只讀必要的，就算是第一次讀入的東西應該是一個索引，讓新的 llm 一直知道去哪裡找什麼，不是一次餵給他一大堆現在還用不到的東西……如果能先解決前面的問題，那文件長度可能就不是核心問題」, then 「合併且開任務，先走poc證明真的比較好再繼續」.

## Scope

- Question the POC answers: does an FO that loads a short index at startup, and each rule passage only at the moment it applies, follow the workflow rules at least as well as an FO that loads the whole README (5447 words on origin/main 6ea3a472), while loading fewer words at each moment?
- Upstream first, before building: whether Spacedock's first-officer contract requires the whole workflow README at boot; what `spacedock dispatch show-stage-def` and the stage `context-sections:` frontmatter already deliver per stage; what kc-dev-flow-2's `_mods` startup and idle hooks load; and the 0.14.0 split of workflow.md by reader (worker vs FO). Say what each already gives.
- Arms: (A) today's whole README; (B) an index README (where each rule lives and when to open it) plus per-moment files, built in a scratch copy only. No change to `kc-dev-flow-2/references/sd/workflow.md` or any adopter README in this POC.
- Probes: the rule classes the observer most often reports as not followed (32 violation lines in 15 observer reports since 2026-10-13, per workflow-budget-ratchet's ideation), for example an ADR number reserved after the first implementation dispatch, a `Reviewer:` line under the wrong heading, a grant quoted from the wrong gate question, a bare package script name in a dispatch record, a dispatch missing the completion line to `main`. Each probe is a fixed FO situation with a checkable right action; the existing replay mechanism in `kc-dev-flow-2/scripts/replay_dispatch.py` and maintain-flow's behaviour replay are checked first.
- Measures: per probe, the rule followed or not per arm, over a pre-registered number of runs; words loaded at each moment per arm; tokens and cost per run.
- Bar: written and committed before any run, and shown at the backlog gate for the Captain to set; the POC reports pass or fail against it without moving it.
- Non-goals: no package or adopter change; no production README restructure; the follow-up task that restructures the README is filed only if the POC passes.
