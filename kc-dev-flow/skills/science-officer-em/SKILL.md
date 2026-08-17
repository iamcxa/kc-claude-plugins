---
name: science-officer-em
description: Compatibility alias for callers that explicitly request the legacy science-officer-em report envelope. New delivery guidance uses chief-engineer; new independent technical assurance uses science-officer.
---

# Science Officer EM Compatibility

Do not treat `EM` as an alias for this skill. Use `kc-dev-flow:chief-engineer` for
normal next-step and delivery advice. Use `kc-dev-flow:science-officer` for new
independent technical assurance.

When an existing consumer explicitly requires `science_officer_em_upward_report`,
read `../science-officer/SKILL.md`, perform that bounded assurance, and map it
without changing its conclusion:

```yaml
science_officer_em_upward_report:
  em_judgment: <science_officer_report.conclusion>
  evidence_synthesis: <science_officer_report.material_evidence>
  risk_tradeoff_call: <science_officer_report.risk_tradeoff>
  recommendation: <science_officer_report.recommendation>
  route: proceed | narrow | return | block | costly_no
  confidence: high | medium | low
  multi_model: recommended | not_needed
  fo_boundary: <FO retains orchestration; empty when none exists>
  engineering_judgment:
    question: <science_officer_report.question>
    revision: <science_officer_report.revision>
    evidence_synthesis: <same synthesis as the envelope>
    adjudications:
      - finding: <material disputed claim>
        disposition: supported | unsupported | unresolved
        basis: <primary evidence>
    risk_tradeoff: <same trade-off as the envelope>
    recommendation: <same recommendation as the envelope>
    route: proceed | narrow | return | block | costly_no
    confidence: high | medium | low
    dissent: <material disagreement or empty>
    disproof_condition: <evidence that would change the route>
    authority_boundary: <Captain, gate, work-item, and provider owners retained>
```

Map canonical `adjust` to `narrow` or `return`, `hold` to `block`, and `escalate`
to the route matching the named owner decision. Preserve the legacy closed keys
and duplicated values for the consumer. The envelope remains advisory and grants
no workflow, provider, scope, spend, merge, release, or closeout authority.
