# 0063. A merge no record carries is stopped by a user-registered hook

Date: 2026-11-06

## Status

Accepted

## Context

Release PR #672 merged although the delivery question did not name its merge.
The task merge-guard-stops-unasked-merges proved with fake gh commands that
Claude's pre-tool hook can ask under auto mode, while Codex 0.162.1 ignores
ask and honors deny even against an allow rule. Codex gaining a pre-tool hook
meets ADR 0003's reopen condition; secret-read enforcement stays adopter-owned.
ADRs 0023 and 0062 still govern what a question grants.

## Decision

**Words:** 「補」 — Captain, chat, 2026-11-06, first ideation gate revision.

**Asked:** 「要照我的建議退回補這兩件事嗎？」 The recorded revision kept
D1 (Codex deny) and D2 (user registration), and requested the Paseo phone
observation and a record route for chat-approved ancillary PRs.

**Words:** 「准」 — Captain, chat, 2026-11-06, second ideation gate.

**Asked:** 「決定：「合併前擋下沒人問過的合併」第二輪設計進入實作嗎？核准即接受 D1（Codex 上沒有紀錄的合併一律拒絕）、D2（套件出腳本，由你在每台機器的使用者設定註冊）、D3（Release、同步、learning PR 在你核准、問句寫明編號和版本後，由 FO 先存紀錄再合併）與 D4（Paseo 上的 Claude FO 被擋時用「要問人」，請求會送到你手機）四個建議。」

**Options considered:**
- D1: deny an uncarried Codex merge; ask is ignored by the tested host.
- D2: ship a package script with per-machine user registration; shipping a
  plugin hook would also affect unrelated projects.
- D3: save a Release, workflow-sync or learning PR's question, answer, number
  and full head before merging; without this route they stop each time.
- D4: keep Claude ask in Paseo; deny would require manual merges instead.

**Recommended:** D1 through D4 as recorded in the approved second ideation gate.

**Protects:**
- `kc-dev-flow-2/scripts/merge_guard.py` — host decisions and record checks.

The package supplies the script, record command and registration instructions;
the operator installs the user hook. A parsed merge passes this guard when
some folder's newest merge ask carries its PR and head prefix. An uncarried
merge asks on Claude and denies on Codex. Missing or failing scripts block
through the documented `|| exit 2` wrapper. Other host permission checks remain.
FO saves a chat-approved ancillary PR before merging, after a question naming
its number and head. Records do not authenticate the Captain or judge intent.

## Consequences

The ideation replay stopped 30 of 84 merges; synthetic ancillary-PR questions
reduced it to 10, with #672 still stopped because its question lacked the head.
About nine further stops per fourteen days is an assumption from that sample.
The Captain reported 「看得到，也答了」 on his phone; the recorded fake gh ran
once after his yes. Paseo shows the command without the reason, and another
agent can answer the request. This guard catches a mistaken merge request,
not a malicious agent with the same filesystem or permission tools.

Each machine stays unguarded until registered. A Release PR's changed head
needs another approval. A text mention may stop too; a merge of another repo
from this cwd stops if its records are not among this repo's state worktrees.
No Captain settings, workflow template, mods or parked Merges line change.
Revisit if the host decision behavior or Paseo phone delivery changes.
