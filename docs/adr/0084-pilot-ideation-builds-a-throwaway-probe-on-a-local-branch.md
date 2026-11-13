# 0084. Pilot ideation builds a throwaway probe on a local branch

Date: 2026-11-13

## Status

Accepted

## Context

The Pilot ideation write ban in ADR 0005 required First Officer (FO) scope notes
to permit a working probe. Two recorded trial dispatches needed 184 words of
hand-written probe instructions each. A local probe showed the workflow could
carry those instructions without changing the POC route, but raised FO startup
reading by 66 words (6033 to 6099). The trial did not measure delivery speed or
defects. The Captain approved the seven design decisions at the ideation gate
of pilot-ideation-runs-a-probe-before-the-design.

## Decision

**Words:** 「核准，七項都照建議（建議）」 — Captain, host question dialog,
ideation gate, 2026-11-13.

**Asked:** 「決定：要不要核准「Pilot 設計階段先做試作」的設計並開始實作？建議核准，七個設計決定都照建議：一、試作是「預期要做，除非設計寫明為什麼不做」；二、試作只能在本機分支，不推送、不部署、不用密鑰、不碰共用環境，做不到的列在「現在無法證明」；三、設計裡記一行試作的分支、基底和最後提交，設計 worker 移除工作目錄、保留分支，實作 worker 做出成品後刪掉分支；四、試作一輪就是一次設計派工，第三次設計派工前我停下來問你，由程式檢查的預算寫法另開任務（你剛才選的分兩步）；五、流程文件增加 66 個字（6033 到 6099）；六、新增一份決策紀錄，只對 Pilot 取代舊紀錄 0005 裡「設計階段不得寫檔」那一條；七、Pilot 的文字指向 POC 既有的那一段規則（43 個字）而不重寫，「擴大方案」這一步留在 Pilot 的文字裡，不改 POC 流程。同意即接受：每次 Pilot 設計派工我少手寫 184 個字，但我每次啟動多讀 66 個字；worker 可以用一句話說明就跳過試作；輪數上限在後續任務做完前只靠我記得；沒有機器證明這會讓交付變快或缺陷變少；有三項驗收條件要等實作或發版後才能驗。」

**Words, Captain amendment 1:** 「可以，要同時加入預算與計時機制，我看目前你 X implementiation + Y valdiation cycle 方式還不錯」 — Captain, chat, 2026-11-13,
after asking whether Pilot would reuse the POC hypothesis, check and widening loop.
The gate settled that direction as decisions four and seven; the Captain chose
「分兩步（建議）」 for the budget follow-up.

**Options considered:**
- Expect a local probe unless the design says why not; reuse the first paragraph
  of POC implementation by pointer and keep widening in Pilot (chosen).
- Merely permit a probe, or require one without an exception; the former leaves
  the habit optional, the latter forces probes even when the design explains no need.
- Preserve the blanket ban and hand-write probe instructions in every dispatch.
- Count one ideation dispatch as one round and have FO hold a third, including
  design-gate revises; retain the existing stage timing and defer machine-enforced
  ideation budgets and per-round timing (chosen).
- Extend the budget grammar and timeline helper now, or use a total-dispatch cap
  that loses the Captain's preferred implementation/validation split.
- Raise the workflow budget by 66 words under ADR 0020 (chosen), rather than move
  the round rule out of the workflow FO reads.

**Recommended:** The seven design decisions as recommended and approved, including
the two-step budget delivery.

**Protects:**
- `kc-dev-flow-2/scripts/lint-skills.py` — the approved 66-word workflow budget step

This supersedes only ADR 0005's ideation write-ban clause and its rejection of a
throwaway ideation worktree for Pilot. Prod's ban, ADR drafting without a number,
amendment handling and the design gate remain in force. The POC route is unchanged.

Pilot probes use an unpushed local `poc/<slug>` branch, with no deployment,
credential or shared environment. Run each criterion's evidence command once and
record command, exit and output path; list unavailable proofs under
`Not provable now`. The design records branch, base, last commit, hypotheses and
results. Ideation removes the worktree but keeps the branch; implementation reads
it and deletes it after committing its candidate. A saved diff in the task folder
is the portable copy when the next worker cannot read that local branch.

## Consequences

The workflow replaces the blanket ban; its duplicate in ideation principles and
the lint overlap exception go. FO writes 184 fewer words per trial-style dispatch
but reads 66 more at startup and resume; the Pilot ideation worker reads 201 more
than the released text. A worker can skip a probe with a reason. The round hold,
probe bounds and branch cleanup are instructions, not script enforcement; lint
checks the budget arithmetic and quote presence, not the quote's authority.
The existing timeline reports dispatch count and the stage span, not each round's
own end or result. Live worker behavior and post-release cleanup remain to be
observed. Reopen if those observations contradict the intended behavior or the
follow-up cannot express the Captain's approved ideation bound.
