# E2E Verification — PR Integration Detection

Reference for kc-pr-create Step 1.5. Loaded on demand when analyzing PR diff.

## Layer Classification

Project-agnostic heuristics for detecting integration changes in a PR diff.

| Layer | Default patterns |
|-------|-----------------|
| Backend | `api/**`, `server/**`, `routes/**`, `services/**`, `middleware/**`, `lib/**`, `schema/**` |
| Frontend | `components/**`, `pages/**`, `app/**`, `views/**`, `screens/**`, `hooks/**`, `ui/**` |
| Shared | `types/**`, `interfaces/**`, `contracts/**`, `shared/**` |
| Infra (ignore) | `.github/**`, `docker/**`, `*.md`, `*.test.*`, `*.spec.*`, `__tests__/**` |

**Project override**: If the project has `.claude/e2e/config.yaml` with a `layers:` section, use those patterns instead of defaults.

## Detection Logic

1. `git diff --name-only <base>...HEAD` to collect changed file paths
2. Classify each file into a layer (first match wins; unclassified → ignore)
3. **Integration detected** if changes span 2+ layers (Backend + Frontend, Backend + Shared, etc.)
4. **Shared-only** does not trigger (shared changes without a consuming layer are not integration)
5. Single-layer only → skip suggestion

## Existing Flow Match

After detection, check for reusable verification flows:

1. `ls .claude/e2e/flows/*.yaml 2>/dev/null` — if directory doesn't exist, skip entirely
2. Scan flow files for `tags:` containing `verification`
3. Cross-reference: do the flow's step pages/actions overlap with the changed files' domains?
4. **Match found** → suggest: `/e2e-test <flow-name> --video`
5. **No match** → suggest: `/e2e-walkthrough --verify`

## Suggestion Format

```
⚡ This PR modifies frontend-backend integration:
  - Backend: <file1>, <file2>
  - Frontend: <file3>, <file4>

E2E verification creates a repeatable flow proving the feature works.
  1. /e2e-walkthrough --verify — interactive verification (generates reusable flow)
  2. /e2e-test <existing-flow> --video — replay existing flow with recording
  3. Skip — proceed to PR creation
```

Option 2 only shown when a matching verification flow exists.

## Notes

- This is a **soft suggestion**, not a gate. User can always skip.
- The e2e-pipeline plugin is a runtime dependency — if not installed, the mappings directory won't exist and the check skips silently.
- After e2e completion, the user returns to kc-pr-create Step 2 (Title).
