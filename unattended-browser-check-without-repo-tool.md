---
title: An unattended worker browser check in a repository that names no tool has a defined route
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「合併，另開任務（建議）」 (host question dialog, 2026-11-08), answering 「#810 的說明沒有規定「repo 自己沒指定瀏覽器工具、又沒人看著」時要用什麼，工人會自己挑；這種情況在 #810 之前就是這樣，#810 沒有讓它變差。要怎麼處理？建議先合併 #810（head fef217353），另開一張任務補上：沒指定工具時用 Paseo 分頁，背景做不到的步驟回報「沒跑」、交回流程主持人。」, after his question 「如果repo自己沒有指定工具，那要用什麼？」 at the #810 gate.
- Bite: none observed; the gap is in `kc-dev-flow-2/extensions/paseo/browser.md` as merged in #810 (4deaa2aa108adeaf3c934fd2309e69d90ac3a076), whose unattended sentence names only "the repository's supported adapter".
- Proposed route (his approved recommendation): with no tool named, use Paseo's browser tools; a step they cannot do on a background tab is reported not run and returned to FO.
- Non-goals: CI browser runs; editing any adopter's AGENTS.md; automating a human-verification challenge.

## Budget
- One package PR touching `kc-dev-flow-2/extensions/paseo/browser.md` within its 240-word bound; workflow word budget unchanged.

## Stop condition
- browser.md states the route for an unattended check in a repository that names no tool, and a falsifier without that sentence fails.

## FO alignment

Alignment: not needed; the Captain chose the route at the #810 gate.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
