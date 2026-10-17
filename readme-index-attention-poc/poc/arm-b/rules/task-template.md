## Task Template

```markdown
---
id: <task-id>
title: <bounded outcome>
status: backlog
variant: kc-dev-flow-2
profile: <selected-profile>
merge: pr
worktree:
pr:
---

<Why this outcome matters.>

## Scope

<Approved scope, non-goals, budget and stop condition.>

## Acceptance criteria

**AC-1**: <Observable outcome.>
Verified by: <Reproducible evidence and its limits.>
```

Optional frontmatter, absent until used: `journey`, `journey-release` and
`journey-story`, set by FO at Release review (see `backlog`). A placeholder comment would sit beside the real values once
`status --set` filled them, so the template carries none.
