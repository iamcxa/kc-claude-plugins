# 0049. Special roles and stage defaults follow one model table

Date: 2026-11-02

## Status

Accepted

## Context

The trigger check recognized Claude leading model words only: a recorded
`gpt-6-astra` engineering-reviewer call needed a waiver. Four agent files used
`reasoning`, which Claude Code did not apply. The Captain approved the table and
five decisions in special-roles-follow-the-model-table's ideation gate.

## Decision

**Words:** 「我認為 codex 的實作者可以預設比 claude 多高一個推理等級，例如 Sonnet / high，對應 Sol / xhigh，總監也是」 and 「不要用到 max，最高就是 xigh 就好」 — Captain, chat, 2026-11-02.
「可以，但不用寫了就報錯，接受 `max` 和 `ultra`沒關係，等於就是不建議，但使用者真的想要也可以」 — Captain, backlog sitting, 2026-11-02.
「可以」 — Captain, ideation revision, 2026-11-02; 「照建議」 — Captain, ideation approval, 2026-11-02.

**Asked:** Backlog: 「決定：五件事都照建議，第 5 項用這張表，並把 xhigh 上限寫進設定檔檢查，可以嗎？」.
Ideation revision: 「決定：多開「完成通知」和「挑剔使用者可用 Gemini」兩張票，先前五件事照建議，可以嗎？」.
Ideation approval: 「決定：五張設計進實作、Gemini 這張停在這裡，四個決定都照建議嗎？要改哪件直接說。」.
The task's approved Design records D1 to D5 under these gate resolutions.

**Options considered:**
- D1: rank Astra with Fable; retaining Claude-only recognition would keep the waiver.
- D2: require opus rank or above for chief-engineer calls; any-model calls previously cleared.
- D3: default ideation and validation to Opus; implementation keeps Sonnet.
- D4: use the table for per-task director passes, retiring design-director-model-follows-task; retain release-walk passes under ADR 0033.
- D5: require chief-engineer and engineering-reviewer to use a family other than the implementation workers'; requiring a different family from every worker was replaced.
- Reject roster efforts above xhigh; not chosen, the Captain permits explicit max and ultra.

**Recommended:** D1 to D5 as recorded in the approved design, with the Captain's explicit max/ultra exception.

**Protects:**
- `kc-dev-flow-2/scripts/role_triggers.py` — Astra rank and chief-engineer model floor.
- `kc-dev-flow-2/scripts/lint-skills.py` — agent effort and table comparison.
- `kc-dev-flow-2/agents/chief-engineer.md` — model and effort defaults.
- `kc-dev-flow-2/agents/engineering-reviewer.md` — model and effort defaults.
- `kc-dev-flow-2/agents/design-director.md` — model and effort defaults.
- `kc-dev-flow-2/agents/observer.md` — model and effort defaults.
- `kc-dev-flow-2/references/model-roster.md` — seven approved rows and family rule.

The seven rows live in `kc-dev-flow-2/references/model-roster.md`, under
`## Model table`. Claude agents use `effort`; Codex special-role calls carry
model and Paseo `settings.thinkingOptionId` manually. Chief-engineer and
engineering-reviewer run at xhigh by default, without requesting a higher level.
The trigger check reads the first recognized word in a recorded model token;
Astra meets the Fable floor, and chief-engineer calls need opus rank or above.
Dates and waivers are unchanged. These model-floor clauses amend ADR 0026.
The table replaces the 2026-10-23 per-task director rule; release walks retain
ADR 0033's one-model-per-walk rule and existing implementation.

## Consequences

Claude effort now reaches its agent turn setting; an explicit dispatch model
can still override the file. Stage model defaults reach Spacedock dispatch, but
stage effort has no dispatch field and remains with dispatch-sets-reasoning-effort.
Astra equaling Fable is a ruling without a measured equivalence claim. An Opus
call still does not meet a prod/database engineering-reviewer floor. Ideation
and validation adopters pay an unmeasured increase; no CI trigger changes here.
Opus may review an Opus-written design under the implementation-worker family
rule. Release walks designed on Astra still follow the existing Claude-name
matching behavior; broadening that rule requires separate work.
