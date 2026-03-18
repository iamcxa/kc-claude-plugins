# Contributing to e2e-pipeline

Thanks for helping improve the E2E testing pipeline! This guide covers how to contribute documentation, patterns, and code.

## Ways to Contribute

| What | How | Effort |
|------|-----|--------|
| Report a doc gap | `/e2e-help --feedback "<description>"` or [open an issue](https://github.com/iamcxa/kc-claude-plugins/issues/new) | 1 min |
| Share a testing pattern | PR to `references/learned-patterns.md` | 5 min |
| Fix or improve a doc | PR to `docs/<file>.md` | 15 min |
| Add a new feature | PR with skill/agent changes + doc updates | 1+ hr |

## Reporting Issues

**Fastest**: If you have the plugin installed, run:

```
/e2e-help --feedback "description of what's missing or broken"
```

This classifies your feedback and creates a GitHub issue automatically.

**Manual**: [Open an issue](https://github.com/iamcxa/kc-claude-plugins/issues/new) with one of these labels:
- `documentation` — missing or unclear docs
- `enhancement` — feature request
- `bug` — something is broken

## Contributing Patterns

The pipeline accumulates testing patterns in `references/learned-patterns.md`. If you've discovered a useful pattern (selector strategy, timing workaround, framework-specific behavior), add it:

1. Fork the repo
2. Append your pattern to `references/learned-patterns.md`:
   ```markdown
   ### <Pattern Title> (YYYY-MM-DD)
   **Context**: When/where this applies
   **Pattern**: What to do
   **Why**: Why this works (or why the alternative doesn't)
   ```
3. Open a PR with the `patterns` label

Patterns are loaded by all skills at startup (Knowledge Bootstrap phase), so your contribution immediately benefits every user.

## Contributing Documentation

### Conventions

- **Practical over abstract** — lead with a YAML/code example, explain after
- **CTA at the end** — every doc ends with:
  ```markdown
  ---
  > **Found a better pattern?** [Open a PR](https://github.com/iamcxa/kc-claude-plugins/pulls) to share it.
  > **Docs unclear?** Use `/e2e-help --feedback "<description>"` to let us know.
  ```
- **Cross-reference** — add a "Related" section linking to sibling docs
- **Troubleshooting table** — for complex topics, use `| Issue | Cause | Fix |` format
- **Element names** — use `snake_case` for elements, `kebab-case` for pages (matching the pipeline convention)

### File locations

| Content type | Location |
|-------------|----------|
| User guides | `docs/<topic>.md` |
| Command reference | `docs/commands.md` |
| Testing patterns | `references/learned-patterns.md` |
| Agent-browser CLI | `references/commands.md` |
| Plugin conventions | `CLAUDE.md` |

### After writing docs

Run the doc-sync check to verify consistency:

```
/e2e-doc-sync --check
```

This catches missing cross-references, stale links, and README table gaps.

## Contributing Code

### Setup

```bash
# Clone the marketplace repo
git clone https://github.com/iamcxa/kc-claude-plugins.git
cd kc-claude-plugins/e2e-pipeline

# Install compiler dependencies
npm install

# Test with only this plugin loaded
ccp    # alias for: claude --plugin-dir "$PWD"
```

### Skill and Agent Changes

When modifying skills or agents, follow these rules from `CLAUDE.md`:

**Adding/changing action types** — trace the full chain:

| Layer | File | Must handle? |
|-------|------|-------------|
| Generator | `agents/e2e-flow-writer.md` | Can it produce the new type? |
| Verifier | `agents/e2e-flow-verifier.md` | Can it attempt execution? |
| Test runner | `agents/e2e-test-runner.md` | Can it execute at full fidelity? |
| Compiler | `bin/e2e-compile.js` | Does it handle or explicitly skip? |
| Skill | `skills/e2e-flow/SKILL.md` | Does the summary show the output? |
| Reference | `references/common-patterns.md` | Are patterns documented? |

**Removing a skill or agent:**
1. Delete the directory/file
2. `grep -rn "<name>" --include="*.md" --include="*.json" --include="*.sh"` across the plugin
3. Update every hit — replace with successor or remove
4. Update `skills/e2e-dispatch/SKILL.md` routing table

### Testing

- **Quick test**: `ccp` from plugin dir (loads only this plugin)
- **Full test**: `cc` from workspace root (loads all plugins)
- **Agent testing**: New agent `.md` files require a **fresh session** to be discoverable (agent registry is session-scoped)
- **Compiler tests**: `npm test` (471 tests across 10 files)

### Documentation Gate

Before submitting a PR with feature changes, run:

```
/e2e-doc-sync --check
```

If gaps are found, either:
- Run `/e2e-doc-sync --fix` to auto-generate doc updates
- Manually update the relevant docs

PRs with new features but no doc updates will be asked to add documentation.

### Commit Conventions

Semantic prefixes: `feat`, `fix`, `docs`, `chore`

```
feat: add --retry flag to e2e-test skill
docs: add retry section to commands.md
fix: handle timeout in cross-site session handoff
chore: bump version to 2.4.0
```

### PR Checklist

- [ ] Feature works with `ccp` (single plugin mode)
- [ ] `/e2e-doc-sync --check` reports no gaps (or gaps are acknowledged)
- [ ] Compiler tests pass (`npm test`) if compiler was modified
- [ ] `CLAUDE.md` counts are correct (skills, agents)
- [ ] `.claude-plugin/plugin.json` version bumped if user-facing change

## Architecture Overview

For understanding how the pipeline works before contributing, see [Architecture](docs/architecture.md).

```
skills/ (9) ── orchestrate in main context
    ↓ dispatch
agents/ (7) ── execute in subagent context (isolated)
    ↓ produce
docs/   (10) ── user-facing documentation
    ↓ inform
/e2e-help ── interactive guide (reads docs/ at runtime)
    ↓ feedback
issues ── track gaps → /e2e-doc-sync resolves
```

## Questions?

- `/e2e-help` — interactive guide to all pipeline features
- `/e2e-help --feedback "<question>"` — ask or report
- [Discussions](https://github.com/iamcxa/kc-claude-plugins/discussions) — open-ended questions
