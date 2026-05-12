# Design Spec Flow (Step DS)

> Read by `design-spec-writer` agent at runtime.

**Trigger**: 2+ of: schema change, cross-domain impact, architectural decision, 8+ files touched.

**Why not just a comment**: Complex changes need formal review before implementation. A comment buries decisions; a spec document surfaces them for async review.

**Process**:
1. Synthesize all exploration findings (code + docs + knowledge layers) into architectural decisions
2. Produce a design spec document (`docs/superpowers/specs/YYYY-MM-DD-<slug>.md`) covering: schema change, domain impact, implementation order, risk mitigation, testing strategy, documentation impact
3. Return summary (≤10 lines) — main conversation presents to user at **GATE**
4. After user approval, post spec summary + file path as Linear comment (shorter than a full implementation comment)

**Key principle**: The spec surfaces decisions for async review. Every architectural choice must show 2+ alternatives with tradeoffs. Past knowledge layer findings (gotchas, failed approaches) are risk mitigation — surface them explicitly in the Risk Mitigation table.
