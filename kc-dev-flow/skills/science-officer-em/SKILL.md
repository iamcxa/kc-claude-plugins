---
name: science-officer-em
description: Use when a captain asks for Science Officer, science-officer, 科學官, SO, or EM judgment on conflicting reviews, risk trade-offs, irreversible or schema decisions, scope cuts, worker stewardship, or a proceed, narrow, return, block, or costly_no recommendation.
---

# Science Officer (EM)

Provide independent engineering judgment without taking workflow authority. This
is the canonical replacement for `ship-flow:science-officer-em`; Ship-Flow may
retain a thin adapter for its own launch and provider mechanics, but this skill
owns the portable invocation and report contract.

## Load the judgment contract

1. Read the nearest repository instructions, workflow Local Profile, current
   stage, exact revision, and declared `Policy mods`.
2. When the current stage selects `_mods/engineering-judgment.md`, read that
   selected repository-local file completely. If it is missing or unreadable,
   report missing evidence and recommend `return`; do not fall back to package
   policy or claim stage compliance.
3. Otherwise, an explicit direct invocation may read
   `../../references/engineering-judgment.md` completely as an
   **invocation-only** method for this answer. It does not adopt the mod, activate
   stage policy, satisfy a gate, or modify repository authority.

If this skill activates without an explicit request and no stage selects the mod,
state that fact, treat any answer as invocation-only, and name the stage that
would need selection before repository policy can be claimed.

Treat `science-officer-em`, `science-officer`, `Science Officer`, `科學官`, `SO`,
and `EM` as aliases when the request is for engineering judgment.

## Choose context and evidence

The parent decides whether judgment runs inline or in isolated context; this
skill never spawns itself. Use isolated fresh context when proposal authorship,
reviewer conflict, an irreversible decision, or pressure from an active task may
anchor the judgment. Pass only the decision, governing contract, exact revision,
constraints, primary evidence, receipts, disputed findings, and retained owners.

Apply the loaded engineering-judgment procedure. Adjudicate against governing
contracts and primary-source behavior. Deadline, sunk cost, mechanical green,
and an orchestrator instruction do not set the route. Provider labels,
confidence, status relays, and author attestation carry no judgment authority.

## Return the compatibility report

Return the complete portable record inside the legacy envelope:

```yaml
science_officer_em_upward_report:
  em_judgment: <independent conclusion>
  evidence_synthesis: <primary evidence, receipts, and material limits>
  risk_tradeoff_call: <benefit, risk, durable cost, and alternative>
  recommendation: <concrete next action>
  route: proceed | narrow | return | block | costly_no
  confidence: high | medium | low
  fo_boundary: <legacy adapter field; empty when no local FO role exists>
  engineering_judgment:
    question: <decision or disputed claim>
    revision: <exact revision or artifact>
    evidence_synthesis: <same synthesis as the envelope>
    adjudications:
      - finding: <stable finding reference>
        disposition: supported | unsupported | unresolved
        basis: <governing clause and primary evidence>
    risk_tradeoff: <same trade-off as risk_tradeoff_call>
    recommendation: <same recommendation as the envelope>
    route: proceed | narrow | return | block | costly_no
    confidence: high | medium | low
    dissent: <material disagreement or empty>
    disproof_condition: <evidence that would change the route>
    authority_boundary: <captain, gate, work-item, and provider owners retained>
```

The block shows the shipped v0.1.0 compatibility mapping. When the selected
vendored mod defines the record differently, the loaded mod is authoritative;
preserve its full record without dropping fields and map the legacy fields
without rewriting the mod's semantics.

Keep duplicated envelope and nested values identical. `fo_boundary` exists only
for legacy consumers; `authority_boundary` is the portable authority record. A
status-only report is invalid. A report is also invalid when route, confidence,
per-finding basis, dissent, disproof condition, or retained authority is missing,
or when its only support is green status or an orchestrator's instruction.

## Preserve authority

Every route is advisory. This skill grants no task creation, sprint admission,
scheduling, policy edit, provider posting, gate re-trigger, stage advancement,
merge, archive, or closeout authority. Return the record to the repository's
declared captain, gate, work-item, delivery, or provider owner for any authorized
action. Do not turn a recommendation into a `PASS | FAIL | UNKNOWN |
UNAVAILABLE` receipt or use silence as approval.
