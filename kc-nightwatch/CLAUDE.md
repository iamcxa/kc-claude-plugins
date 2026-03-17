# kc-nightwatch

## Roadmap

See `reference/ROADMAP.md` for the v0.1→v1.0 evolution plan. Always read before starting nightwatch development work.

## Commit Convention

- `kc-nightwatch:` prefix — auto-generated commits during nightly runs (Phase 1 forge fixes, Phase 4 quick-fixes and proposals)
- Standard semantic prefixes (`feat`, `fix`, `docs`, `chore`) — human development of the plugin itself

## Safety Source of Truth

`config/safety.yaml` is the single source of truth for all limits and constraints. The orchestrator skill reads values from this file at Phase 0 — never hardcode limits in the skill.

When modifying safety values:
- Always update `safety.yaml`, not the skill
- Changes require human review (never auto-modified by nightwatch)
- Test changes with `--dry-run` before the next nightly cycle

## Self-Repair (v0.4+)

kc-nightwatch monitors itself via `--self-repair` mode:
- **Config auto-fix**: validates Linear team/project names, Sentry access, webhook connectivity
- **Feedback loop**: checks status of its own PRs and Linear issues to adjust future confidence
- **Own forge check**: runs forge validate-only on itself, creates PR for structural FAIL items

Circuit breaker: max 1 self-fix PR + 3 config fixes per run (from `safety.yaml`).

The `--self-repair` session runs BEFORE the regular pipeline in cron mode. It does NOT process other targets.

## File Ownership

| File | Maintained by | Rules |
|------|--------------|-------|
| `~/.claude/kc-plugins-config/nightwatch-improvement-log.md` | Orchestrator (auto) | Always writable regardless of `allowed_operations` |
| `~/.claude/kc-plugins-config/nightwatch-targets.yaml` | Human + config skill | Monitoring targets; use `/kc-nightwatch-config plugins` to manage |
| `config/safety.yaml` | Human only | Changes require review; test with `--dry-run` |
| `*/PROPOSAL.md` | Orchestrator (auto) | Created on proposal branches, reviewed via `--review` |
| `~/.claude/kc-plugins-config/nightwatch-self-repair.yaml` | Self-repair (auto) | Written each run by `--self-repair` session |
| `~/.claude/kc-plugins-config/nightwatch-feedback.yaml` | Self-repair (auto) | Feedback from PR/issue status; read by regular pipeline |

## Plugin Maintenance Workflow

### Adding a new target to monitoring

Use `/kc-nightwatch-config plugins` → [A]dd, or edit `~/.claude/kc-plugins-config/nightwatch-targets.yaml` directly.

Required fields: `type`, `path`, `repo`, `north_star`, `keywords`, `sources`, `actions`, `proxy_signals`.

Test with `/kc-nightwatch --dry-run` — new target should appear in Phase 0 active list.

### Updating north star or proxy signals

1. Edit `~/.claude/kc-plugins-config/nightwatch-targets.yaml`
2. Old signals in `improvement-log.md` retain their original proxy signal IDs — no migration needed
3. New harvester runs will use the updated keywords and signals

### After reviewing proposals (`--review`)

- **Accepted proposals**: PROPOSAL.md is merged to main. Create implementation todos separately (nightwatch does not implement proposals).
- **Rejected proposals**: branch + PROPOSAL.md deleted. The signal enters cooldown (7d) via improvement-log entry, preventing re-proposal.
- **Deferred proposals**: branch stays. Next nightly run skips the same signal via cooldown check.

### Debugging "why was plugin X skipped?"

1. Check `git diff --quiet HEAD` in the plugin's repo — non-zero = dirty (tracked changes)
2. Check `git log -1 --format="%aI"` — within 2h = recent commit
3. Use `--dry-run` to bypass both guards for testing

### Debugging "why was signal Y not acted on?"

1. Check `~/.claude/kc-plugins-config/nightwatch-improvement-log.md` — signal may be in cooldown (processed within 7 days)
2. Check confidence — `low` signals are dropped in Phase 3
3. Check per-plugin cap — max 3 signals per plugin per run

## Slack Configuration

Nightwatch reads `nightwatch` channel from `~/.claude/kc-plugins-config/channels.yaml`. If channel is archived or missing, Slack is skipped silently (improvement-log still updated).

## Branch Naming Convention

```
kc-nightwatch/{YYYY-MM-DD}-{plugin-name}-forge-fix     Phase 1 forge auto-fix
kc-nightwatch/{YYYY-MM-DD}-{plugin-name}-fixes          Phase 4 quick-fixes
kc-nightwatch/{YYYY-MM-DD}-{plugin-name}-proposal       Phase 4 proposals
kc-nightwatch/{YYYY-MM-DD}-{target-name}-e2e-flow       Phase 4 e2e-flow generation
```

All branches are created from and merged back to `main`. One branch per target per type per run.
