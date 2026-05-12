# Estimate Inference Reference

## Why Inference

Linear MCP `get_team` does not return estimate settings (scale type, allowed values). To provide valid estimates when creating issues, we infer the team's estimate scale from existing issues.

## Inference Procedure

**When**: Before any issue creation (decompose or meeting-notes flow), once per team per session.

**How**:

1. `list_issues` for the target team (limit: 10, most recent)
2. Collect issues that have `estimate` field (skip those without)
3. Determine scale from the `estimate.name` values:

| `name` values seen | Scale | Allowed values |
|---|---|---|
| XS, S, M, L, XL | T-shirt | 1 (XS), 2 (S), 3 (M), 5 (L), 8 (XL) |
| 1, 2, 3, 5, 8, 13, 21 | Fibonacci | 1, 2, 3, 5, 8, 13, 21 |
| 1, 2, 3, 4, 5 | Linear | 1, 2, 3, 4, 5 |
| 1, 2, 4, 8, 16, 32 | Exponential | 1, 2, 4, 8, 16, 32 |
| No estimates found | Unknown | Ask user |

4. Cache the result — no need to re-infer for same team in same session.

**Shortcut**: If `estimate.name` contains any letter (S, M, L, XS, XL) → T-shirt. Otherwise match value set against known scales.

## Estimate Assignment Guidelines

Map scope analysis (from code exploration) to the team's scale:

| Scope Signal | T-shirt | Fibonacci | Linear |
|---|---|---|---|
| 1-2 files, config/copy change, no logic | XS (1) | 1 | 1 |
| 1-3 files, single domain, clear approach | S (2) | 2 | 2 |
| 3-5 files, moderate complexity, one domain | M (3) | 3 | 3 |
| 5-8 files, cross-component, some risk | L (5) | 5 | 4 |
| 8+ files, cross-domain, schema/arch change | XL (8) | 8 | 5 |
| 15+ files, multiple workstreams → should decompose | — | 13+ | — |

**Adjustment factors** (bump up/down 1 level):
- **Up**: unfamiliar area, no tests to lean on, migration involved, external API dependency
- **Down**: well-tested area, clear precedent in codebase, mostly boilerplate

## Presentation Format

When presenting estimates to user (in GATE step), show both the value and scale name:

```
Estimate: M (3) — 3-5 files, single domain, moderate complexity
```

For decompose flow, include estimates in the proposed breakdown:

```
1. 「[title]」 — est: M (3) — [scope rationale]
2. 「[title]」 — est: S (2) — [scope rationale]
```

## Rules

- **Never guess scale** — always infer from data or ask user
- **Estimate is advisory** — user has final say at GATE
- **16+ in T-shirt/Fibonacci means decompose** — suggest splitting before estimating
- **`save_issue` takes `estimate` as number** — pass the `value`, not the `name`
