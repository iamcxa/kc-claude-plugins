---
title: A merge gatekeeper reviews each PR, lets FO merge one it judges safe, and tells the Captain what to look at
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:merge-gatekeeper:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:merge-gatekeeper-backlog-1
              briefing:
                id: briefing:merge-gatekeeper:backlog:attempt-1:revision-1
                digest: sha256:52c1227978e4bda4653bb324f98a2a0ff7ab4e7bb34ecc048a756e417d5e7d5d
                room-ref: ./merge-gatekeeper/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:merge-gatekeeper:backlog:1
                briefing: briefing:merge-gatekeeper:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-17T06:10:37.776694Z"
                decision: approve
                reason: Captain approved in chat (「准」) the six batch-2 backlog gates presented together in one message, accepting the recommended profiles (pilot; merge-gatekeeper prod) and the stated order
              application:
                target-stage: ideation
                state: pending
---

Filed on the Captain's request (chat, 2026-10-16): 「我想新增一張票，設計一個 codex 的 PR 守門員，它的任務是確保 P R 可以合併，類似 JEV 那樣的工作，只要例如 PR 超過 95% 沒問題，那就讓它帶我授權 FO 合併 PR，相應的但是也要讓它負責提出我需要注意的點……這件事的目的是，減低 FO 自己合併 PR 的意外，以及減低我每次都要肉眼 review PR 的負擔」

## Scope

- Two goals in his words: fewer accidents when FO merges PRs itself, and less of his own eye review of every PR.
- Asked shape: a Codex-run gatekeeper judges whether a PR can merge; above a confidence bar (his example: 95%) it grants FO, on his behalf, the merge; it also lists the points he should look at.
- JEV, per the Captain (chat, 2026-10-16: 「jev 是這個 https://typesafe.ai/blog/introducing-system-one-models-and-jev 這是特殊的 agent 類型，只負責斷機率不回話」): TypeSafe AI's "System One" model, early access. Read by FO on 2026-10-16 from that page: it takes unstructured state and returns a typed decision from choices defined in advance, each with a probability and confidence score, and no free text; stated 70 to 500 ms and $0.042 per million input tokens, output free; calibration is claimed only in words ("higher confidence means higher accuracy"), with no number, and its evals were built by the vendor. It judges the state it is given; it does not read code, so it would sit after the reviewers, not replace them.
- Open at backlog: which model or product the gatekeeper runs on ("Codex", or a GPT or Claude model he recalls doing the same job); how the 95% is measured and calibrated (a reviewer's stated confidence is not a measured rate).
- Conflict to settle first: ADR 0011 (accepted) says "Authority, gate approval, merge, outward-facing actions, irreversible changes and money are never delegated at any level." A merge grant needs a new ADR that supersedes that clause for this case, with his Words; ideation drafts it.
- Existing pieces to check before building (upstream first): kc-pr-flow `kc-pr-review` (Codex source, confidence gates), the Codex PR review already read by `pr_watch.py`, `delivery_gate.py` (head equals the validated candidate), `spacedock merge guard`, ADR 0011's L3 "decide by record" (a Captain grant per decision class on ledger evidence), and today's batch-1 record of FO merge asks (four PRs, each Captain-merged).
- Data leaving the machine: sending PR diffs or review text to an outside service is an outward-facing data share (relay and qnow are private); the Captain decides it per repository.
- The bite to measure: FO-merge accidents so far (count them from state and chat-free evidence) and the Captain's review time per PR.

## Options found (FO, 2026-10-17)

- OpenAI Decisions API, verified on https://developers.openai.com/api/docs/guides/decisions (read 2026-10-17): `POST /v1/decisions`, public beta ("we expect to GA in the coming weeks"), `gpt-6-luna` the only model. A `choice` question takes `name`, `instructions` and `choices` (`value`, `description`); the answer returns `choice`, a `probabilities` array over the options and a separate `confidence` field. No calibration claim: the page advises setting thresholds from labelled examples. Input $0.10 per million tokens, output free. Zero Data Retention supported for eligible customers; US and EU data residency.
- Codex (`codex exec`, 2026-10-17) suggested the Decisions API plus: enforce the deterministic checks first (head equals the validated candidate, required CI green); calibrate on labelled historical PR snapshots split by time (logistic or isotonic on a held-out set, tested on untouched history); allow a merge only where calibrated P(merge) >= 0.95 and the lower confidence bound of precision on the accepted subset meets the target; otherwise "needs human". Codex's other claims (logprobs on `gpt-6-sol` / `gpt-6-luna` only at reasoning effort none; Evals graders) are unverified.
- TypeSafe Jev: see Scope.

## FO alignment

Alignment: not needed before ideation; the Captain approved filing it (his words are at the top of this file).
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none
