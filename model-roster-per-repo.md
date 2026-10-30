---
title: Each repository records which model, reasoning level and host each role runs on, from a dev2-recommended default set, and every dispatch reads it
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:model-roster-per-repo:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:model-roster-per-repo-backlog-1
              briefing:
                id: briefing:model-roster-per-repo:backlog:attempt-1:revision-1
                digest: sha256:06eed18a04605d81221a7ea83c9339242dac970a8dad36a55d9b4b517503dde9
                room-ref: ./model-roster-per-repo/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:model-roster-per-repo:backlog:1
                briefing: briefing:model-roster-per-repo:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-30T08:18:37.78097Z"
                decision: approve
                reason: The Captain 「對，全准且全確認」 (chat, 2026-10-30), answering FO's joint batch-11 backlog sitting of six gates whose ask was 「決定：六張全准進設計，並確認上面三件事？要改哪張直接說。」; accepts FO's recommendation and the confirmations stated in the gate question.
              application:
                target-stage: ideation
                state: consumed
---

## Scope

- Source: the Captain (chat, 2026-10-29): 「我想延伸這個設計，最近我們用codex作為ensign worker好幾天了，我想可以在paseo ext，夥伴ext之間，例如都有啟用 paseo, gemini, codex時，構築一個可能是by repo可以指定什麼情況下用哪個模型，一來平衡用量，二來避免單模型盲點？例如dev2 會開始建議fo預設都是Claude，不同角色可以用ui問使用者哪個模型，推理等級也可以改，但就是預設以我建議的組合為主，等於最後會產生一個設定檔，派工時就以此為主，你覺得如何？」; then 「可以，就這樣做。平衡用量不用量，你想看看，Claude 做fo，codex做worker ，兩者使用量是否明顯比都只用單一模型更少？」, answering FO's proposal to combine the existing pieces below into one task.
- Outcome he named: a per-repository setting, from a default set dev2 recommends (FO on Claude by default), where each role's model and reasoning level can be chosen through a question UI and changed later; dispatch reads it. Two aims: spread usage across vendors, and avoid one model's blind spots. On spreading usage he said 「平衡用量不用量」 and asked whether Claude as FO plus Codex as worker clearly uses less of each than one model alone; FO's reading, to confirm at the sitting: no usage measurement is owed for that aim.
- Pattern to reuse (relay FO's answer, 2026-10-29, Spacedock tag v0.28.0-pre5 at 230c77e43): Spacedock Review's per-project review mode is owned by the spacedock binary (`internal/cli/review_mode.go`), stored outside the repository keyed by a hash of the repo root, set through `spacedock review-mode get|set|clear`, asked by the skill only when nothing is recorded, and records only an explicit answer. It is per user and machine; a team-shared choice does not fit it. FO's proposal, not ruled: the recommended set lives in the repository (team rules, changed by PR) and a personal override lives outside it like Review's mode (quota is personal).
- Absorbs, for the Captain to confirm at the backlog sitting: Draft PR iamcxa/kc-claude-plugins#674 (Codex model and effort policy per stage, parked since 2026-10-19 behind Spacedock transport spacedock#845), backlog tasks dispatch-sets-reasoning-effort, design-director-model-follows-task, and the multi-model part of gpt-partner-extension-proposal. FO retires none of them without his ruling.
- Evidence: batch 9 (2026-10-28) ran FO on Claude, ideation and validation workers on Codex gpt-6-astra high, implementation on gpt-6.1-sol high, special roles on Claude, all by hand under the Captain's interim directive 「接下來派工結束後新的派工盡量用 sol / astra，推理等級可以比 claude 高一級」; reviewer family differed from worker family by FO's choice, with no rule enforcing it; a sol worker stopped on "Selected model is at capacity" and FO switched it to astra by hand.
- Upstream first: the workflow README `defaults: model:` Spacedock reads at dispatch (`dispatch build` prints `effective_model ... (from defaults)`); kc-dev-flow-2 extensions paseo, peers and the partner proposals; Paseo's provider and model list; spacedock#845.

## Non-goals

- Measuring per-vendor usage (see the Captain's words above); changing hosts or Spacedock itself; choosing models for adopters without their answer.

## Budget

- One package PR for the setting, its question flow and the dispatch read; #674 is reopened or closed inside this task, not in parallel.

## Stop condition

- Batch 9's hand-chosen roster replays from the setting with no FO judgment, a reviewer on the same family as its worker is refused or flagged, and a capacity stop falls back by rule; return to the Captain if per-repo sharing versus per-user storage cannot both hold.

## FO alignment

Alignment: needed before ideation; the default set, where each layer is stored and which roles the UI asks about are the Captain's.
Result: aligned at backlog: the Captain 「對，全准且全確認」 (chat, 2026-10-30) to FO's batch-11 backlog sitting, which asked 「決定：六張全准進設計，並確認上面三件事？要改哪張直接說。」, approved the outcome and bounds in this file. He confirmed no per-vendor usage measurement is owed and that this task absorbs Draft #674, dispatch-sets-reasoning-effort, design-director-model-follows-task and the multi-model part of gpt-partner-extension-proposal. The default set, where each layer is stored and which roles the UI asks about stay his: ideation returns them as decisions at the ideation gate.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
