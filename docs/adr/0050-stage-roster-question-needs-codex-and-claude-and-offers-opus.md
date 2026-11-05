# 0050. Stage roster question needs Codex and Claude and offers Opus

Date: 2026-11-02

## Status

Accepted

## Context

The repository roster offered only Codex models and asked when only Codex was
available. It could not record the Captain's chosen Claude ideation model.
The task model-roster-question-needs-both-families records the approved design,
its provider capability probes and the ideation gate's five decisions.

## Decision

**Words:** 「主動詢問不必拿掉，但是應該是條件式的，也就是必須要是有 paseo + codex +cladue 都存在時才可以用」 and 「構思改用 opus high」 — Captain, chat, 2026-11-02.
「可以，但不用寫了就報錯，接受 `max` 和 `ultra`沒關係，等於就是不建議，但使用者真的想要也可以」 — Captain, backlog sitting, 2026-11-02.
「可以」 — Captain, ideation revision, 2026-11-02; 「照建議」 — Captain, ideation approval, 2026-11-02.

**Asked:** Backlog: 「決定：五件事都照建議，第 5 項用這張表，並把 xhigh 上限寫進設定檔檢查，可以嗎？」.
Ideation revision: 「決定：多開「完成通知」和「挑剔使用者可用 Gemini」兩張票，先前五件事照建議，可以嗎？」.
Ideation approval: 「決定：五張設計進實作、Gemini 這張停在這裡，四個決定都照建議嗎？要改哪件直接說。」.
The accepted recommendations include Opus only for Claude rows, Claude ultra
mapping to ultracode, and building with the row provider's host (D5). Publication
and completion follow ADR 0048; special-role families follow ADR 0049.

**Options considered:**
- Ask with Paseo, Codex and Claude present; offer Opus/high, Sol/xhigh and Astra/xhigh (chosen).
- Remove the proactive question; the Captain retained it conditionally.
- Reject max and ultra; the Captain permits an explicit choice.
- Keep the generated host implicit; it can conflict with the chosen provider.

**Recommended:** The conditional question and mixed recommended set, with D1
through D5 recorded in the task's approved design.

**Protects:**
- `kc-dev-flow-2/scripts/model_roster.py` — the absent-file return keeps README defaults.

This supersedes ADR 0047. Adoption or introducing sync asks once only when the
workflow lists Paseo, both providers are available and no roster exists. Save
only an explicit accept/customize answer through normal repository review.
No answer writes nothing; preserve an accepted roster across ordinary sync.
Resolve a clean committed snapshot without changing it; malformed or unsupported
present choices return to FO. Absence or committed deletion keeps README
behavior, with workers following FO's family.

The recommendation is Claude/claude-opus-5-5/high for ideation,
Codex/gpt-6.1-sol/xhigh for implementation (including repair), and
Codex/gpt-6-astra/xhigh for validation, all on Paseo. The accepted efforts remain
low, medium, high, xhigh, max and ultra. Claude ultra emits Paseo's ultracode;
the stored tuple retains ultra. Family reporting compares the validator with
the candidate's recorded authors, and remains informational or unverified.

## Consequences

The question and resolver can express the approved set. Live provider settings,
child runtime and completion still need observed proof; resolver tests establish
none of them. No measured cost or diversity guarantee follows. Native model
passthrough, capacity automation and personal overrides remain separate work.
