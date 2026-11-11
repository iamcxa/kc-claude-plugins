# 0075. Release rollout reports adopters and the laws pin follows each merged README

Date: 2026-11-11

## Status

Accepted

## Context

The package reached 0.38.0 while this repository's state laws workflow remained
pinned to 0.26.0. No release step reported the gap. The design's read-only private-adopter
trial found 14 state pushes, 15 rounded runner minutes and one real violation;
installing on every private adopter could exceed the owner's included allowance.
The task release-rollout-reaches-adopters-and-laws-pin records that measurement,
the alternatives and the Captain's ideation gate of 2026-11-11.

## Decision

**Words:** 「照建議核准（建議）」 — Captain, host question dialog, 2026-11-11.

**Asked:** 「決定：要不要核准「發版後鋪開到採用 repo 與法規檢查」的設計並開始實作。我建議照設計的建議核准：每次發版後跑一個唯讀指令，列出每個採用 repo 的說明檔和法規釘選要不要動；法規檢查維持你點名才裝，釘選在每次說明檔同步合併後跟著移；採用 repo 的清單放在這個 repo 狀態分支的一個檔案，只列已經公開提過的；由我在你每次發版說一聲後派同步 PR，你合併後我移釘選。核准即接受這三項。」

The Captain amended the list's home later that day:

**Words:** 「這個清單列在本地就好了，那是因為我是作者同時又是這些 repo 的維護者，放進去 dev2 repo 不是很怪嗎」 — Captain, host question dialog, 2026-11-11 (task amendment 1).

**Options considered:**
- B: install on the Captain's word; the installed pin follows README sync merges (chosen).
- A: install on every adopter by default; pins follow sync merges, with private runner costs.
- C: install and every pin move each need a separate Captain instruction, leaving silent drift.
- A local list committed nowhere (chosen by amendment 1), instead of a package, trunk or state-branch file.
- Keep release sync dispatch in off-package prompts instead of a named package step.

**Recommended:** B and package FO dispatch/pin ownership as approved. The original
state-branch list recommendation was superseded by the Captain's local-only ruling;
the maintainer supplies an explicit path outside any repository.

**Protects:**
- `kc-dev-flow-2/scripts/package_version.py` — an absent laws install reports no installation debt.

`package_version.py rollout <list>` reads and reports against published tag
commits. Workflow text differences, excluding the release marker, owe a README
sync; differences in the three laws files owe a pin move. Unreadable rows cannot
be called current. An unrecognised pin owes a move. Search supplements the
Captain-approved list and grants no authority to publish a discovered repository.
The execution step lives in maintain-flow § Observe adopters; installation and
pin sequencing live in adoption.md § State laws check.

## Consequences

Adopters not chosen for installation have no hosted laws report. The command
neither writes adopters nor grants merge authority. Pins wait for merged README
rules, so the package FO writes one disjoint path on adopters' shared state
branches after their sync merges. Search can miss adopters or be unavailable;
the explicit list remains the reporting boundary. Reopen when a pin falls behind
a merged README or private laws minutes exceed the included allowance.
