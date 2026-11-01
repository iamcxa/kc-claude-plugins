# 0047. Repository stage model rosters keep README defaults when absent

Date: 2026-10-30

## Status

Accepted

## Context

Batch 9 used Claude for First Officer (FO) and special roles, with Codex through
Paseo for stage workers: Astra/high, Sol/high and Astra/high. The Captain asked
for a repository choice to spread vendor usage and reduce single-model blind
spots, without measuring vendor usage. The model-roster-per-repo task's ideation
gate first proposed a broader design, then accepted a bounded shared-setting slice.

## Decision

**Words:** 「准」 — Captain, chat, 2026-10-30, joint batch-11 ideation sitting.

**Asked:** 「決定：六張全照建議，同意放寬 Paseo 規則和真實測試，並授權改完直接進實作？要改哪張直接說。」
The model-roster-per-repo row in ideation briefing 1 accepted the committed
`.dev2/model-roster.json`, one accept-or-customize question at adoption/sync,
read-only resolve, stage-worker tuples in existing dispatch records, an
informational same-family flag and batch-9 replay. The recorded revision grant
allowed FO to advance the conforming design without another sitting; ideation
attempt 2 applied that grant.

**Options considered:**
- Shared repository stage-worker choice, absent-file README compatibility and
  manual recovery; the accepted first slice.
- Personal layering, automated capacity recovery, law enforcement, special-role
  hosting and native roster routes together; deferred beyond this slice.
- Continue hand-selecting every stage tuple; does not deliver the requested choice.

**Recommended:** The bounded shared repository stage-worker slice, accepted by
the Captain's ideation revise and applied in ideation attempt 2.

**Protects:**
- `kc-dev-flow-2/scripts/model_roster.py` — absent-file return retains README defaults.

The shared schema records ideation Codex/gpt-6-astra/high/Paseo, implementation
(including repair) Codex/gpt-6.1-sol/high/Paseo and validation
Codex/gpt-6-astra/high/Paseo as the offered recommendation. Save an explicit
accept/customize answer through normal repository review; no answer writes
nothing. Preserve accepted settings across sync. Dispatch resolves the clean
committed choice; malformed or unsupported present data returns to FO. Absence
or committed deletion restores current README behavior.

Validation compares candidate author records, not the current implementation
recommendation. Sol and Astra share OpenAI lineage; report that warning without
adding a gate. Unknown author evidence stays unverified. FO and special roles
retain their current policy and publication duties. Personal overrides, capacity
automation, new laws, special-role hosting, native routes and other partner
providers remain deferred. Draft PR #674's native remainder is not delivered here.

## Consequences

Accepted shared choices replace repeated stage-model selection while existing
adopters keep their README behavior until they opt in. This adds dispatch reading
and makes no measured cost, total-token or diversity guarantee. Provider capability,
real child settings and human question behavior need observed evidence; resolver
tests establish none of them. Reopen expanded hosting or recovery as separate work.
