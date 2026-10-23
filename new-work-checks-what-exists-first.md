---
title: Before any new work, the worker finds what already exists, states what it checked and found, and designs the new part as an addition to it
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「照上面這個理解，開「先查上游」這張任務」 (chat, 2026-10-23), after his correction 「這裡的問題是，做新需求時應該要先查上游，不管幹嘛都要先確認已有的東西才去評估怎樣加入新的東西。說明一下你的理解是怎樣」 and FO's restatement: before building anything new, find what already exists, say where it looked and what it found, then judge how the new part joins it; the places to look are what this project actually depends on and sits beside (its own repository, the packages or frameworks it uses, sibling projects, the third-party tools it will use, read from their own docs or source, not from a neighbour's usage); what was found decides whether the new part extends, changes or replaces it.
- Port: his global instructions "Upstream first" (check the chain, say what you checked and found) and "A sibling's usage is not a tool's contract", stated for any adopter's own chain rather than his fleet's.
- What exists: kc-dev-flow-2 implementation principles "Existing-code capability check" (this repository only, and only when existing code adds, replaces or removes a capability); FO's own dispatch text has carried a chain-check line, which adopters' FOs do not get. A grep of the kc-dev-flow-2 0.28.0 markdown and of kc-dev-flow on origin/main for an upstream-first clause found none (2026-10-23).
- Bite: none recorded in dev2, because FO's dispatch line supplied it; his global instructions record the class costing two days in his fleet.
- Rulings are existing state: the Captain 「都准」 (chat, 2026-10-23, kc-adr FO's Paseo session) to the kc-adr FO's 「准不准我在 dev2 那張任務的範圍裡加上「ADR 也算既有狀態」這一句」, whose proposed sentence was 「生效中的 ADR 也算既有狀態，worker 必須列出管到這次要動的檔案或行為的 ADR，沒有就寫「無」。」, after his 「讓 agent 務必先查既有狀態的機制，ADR也是一種既有狀態」. Related: dev2 task `adr-protected-path-guard` adds an optional ADR field listing the files it protects, which this check can read.
- Non-goals: naming any particular project's upstream in the package.

## FO alignment

Alignment: needed at ideation; where the check sits (ideation principles, the seed, the gate content) is his to accept.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
