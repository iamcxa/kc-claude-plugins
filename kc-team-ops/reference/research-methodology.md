# Research Methodology

## Source Priority (High → Low)

| Priority | Source | Confidence | When to Use |
|----------|--------|-----------|-------------|
| 1 | **Context7** (`resolve-library-id` → `query-docs`) | HIGH | Library APIs, features, configurations, versions |
| 2 | **WebFetch** (official docs/README) | HIGH-MEDIUM | Official docs not in Context7, changelogs |
| 3 | **WebSearch** (community) | Needs verification | Ecosystem discovery, community patterns, pitfalls |

## Context7 Flow

```
resolve-library-id(libraryName)
  → query-docs(resolvedId, specific query)
```

Always try Context7 first. If the library isn't indexed, fall back to WebFetch.

## Verification Protocol

For each finding from WebSearch:
1. Can verify with Context7? → HIGH confidence
2. Can verify with official docs (WebFetch)? → MEDIUM confidence
3. Multiple independent sources agree? → Increase one level
4. None of above → Remains LOW, flag for validation

## Research Discipline

- **Verify before asserting** — don't state library capabilities without checking current docs
- **Date knowledge** — "As of my training" is a warning flag, always verify
- **Prefer current sources** — Context7 and official docs trump training data
- **Flag uncertainty** — LOW confidence when only training data supports a claim
- **Negative claims need evidence** — "X doesn't support Y" requires official docs confirmation

## Anti-Patterns

- ❌ Stating version numbers from memory without verification
- ❌ "I believe X supports Y" without source
- ❌ Padding findings to look comprehensive
- ❌ Single-source critical claims
- ❌ Exploring tangential topics beyond the research questions
