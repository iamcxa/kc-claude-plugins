# kc-nightwatch

Autonomous nightly plugin improvement pipeline for Claude Code plugins.

## Daily Workflow

```
First setup   /kc-nightwatch-config             Configure schedule + Slack channel
    │
    ▼
3:00 AM       /kc-nightwatch (cron)             Create branches + PRs + Slack report
    │
    ▼
Morning       Slack morning report              See what changed at a glance
    │
    ▼
              /kc-nightwatch-report             View detailed status and trends
    │
    ▼
              /kc-nightwatch-report --review    Accept / defer / reject one by one
```

## Nightly Pipeline Flow

```
                         ┌─────────────────────┐
                         │   /kc-nightwatch     │
                         │  (cron or manual)    │
                         └──────────┬───────────┘
                                    │
                    ┌───────────────▼───────────────┐
                    │  Phase 0: Preflight            │
                    │                                │
                    │  Load config:                  │
                    │    nightwatch-targets.yaml      │
                    │    safety.yaml                  │
                    │    nightwatch-improvement-log   │
                    │                                │
                    │  Verify plugin paths            │
                    │                                │
                    │  Skip guards (per plugin):     │
                    │    dirty repo? → skip           │
                    │    recent commit? → skip        │
                    │    (--dry-run bypasses both)    │
                    └───────────────┬────────────────┘
                                    │
                         ┌──────────▼──────────┐
                         │ Active plugins = 0? │
                         └──┬──────────────┬───┘
                        yes │              │ no
                            ▼              ▼
                   ┌──────────────┐  ┌──────────────────────────┐
                   │ Silent night │  │ Phase 1: Forge Validation │
                   │ (log only)   │  │ (per plugin, parallel)    │
                   └──────┬───────┘  │                           │
                          │          │ forge validate-only        │
                          │          │   PASS → Phase 2           │
                          │          │   FAIL → branch → auto-fix │
                          │          │     max 3 files, edit-only │
                          │          │     re-validate → commit   │
                          │          └────────────┬──────────────┘
                          │                       │
                          │          ┌────────────▼──────────────┐
                          │          │ Phase 2: Signal Harvest    │
                          │          │ (per plugin, parallel)     │
                          │          │                            │
                          │          │ Dispatch agents by source: │
                          │          │   signal-harvester:        │
                          │          │     journal, episodic,     │
                          │          │     MEMORY.md              │
                          │          │   sentry-scanner:          │
                          │          │     Sentry project errors  │
                          │          │   e2e-scanner:             │
                          │          │     E2E reports + mappings │
                          │          │   git-scanner:             │
                          │          │     churn + staleness      │
                          │          │   → merge + dedup signals  │
                          │          └────────────┬──────────────┘
                          │                       │
                          │          ┌────────────▼──────────────┐
                          │          │ Phase 3: Gap Analysis      │
                          │          │                            │
                          │          │ Filter: high + medium only │
                          │          │ Cooldown: 7d dedup         │
                          │          │ Classify:                  │
                          │          │   quick-fix ← no logic Δ   │
                          │          │   proposal  ← logic Δ      │
                          │          │   linear-issue ← investigate│
                          │          │   alert ← notify only      │
                          │          │   e2e-flow ← coverage gap  │
                          │          │ Cap: max 3 per target      │
                          │          └────────────┬──────────────┘
                          │                       │
                          │          ┌────────────▼──────────────┐
                          │          │ Phase 4: Execute           │
                          │          │                            │
                          │          │ quick-fix:                 │
                          │          │   branch → edit → forge    │
                          │          │   re-validate → commit     │
                          │          │                            │
                          │          │ proposal:                  │
                          │          │   branch → PROPOSAL.md     │
                          │          │   → commit (no code edits) │
                          │          └────────────┬──────────────┘
                          │                       │
                          ├───────────────────────┘
                          │
             ┌────────────▼────────────────────┐
             │  Phase 5: Output                 │
             │                                  │
             │  PR routing:                     │
             │    has remote → gh pr create     │
             │    no remote  → local branch     │
             │                                  │
             │  Update nightwatch-improvement-log│
             │  Slack morning report → channel  │
             │  (silent night = skip reasons)   │
             └─────────────────────────────────┘
```

## Morning Review Flow

```
             ┌──────────────────────────────┐
             │ /kc-nightwatch-report         │
             │ (status mode — default)       │
             │                               │
             │ Show: last run, recent fixes, │
             │ proposals, signal trends      │
             └──────────────┬───────────────┘
                            │
             ┌──────────────▼───────────────┐
             │ /kc-nightwatch-report --review│
             │                               │
             │ Discover branches across      │
             │ all repos (proposals + fixes) │
             └──────────────┬───────────────┘
                            │
                   ┌────────▼────────┐
                   │  Per branch:    │
                   │                 │
                   │  Show diff/     │
                   │  PROPOSAL.md    │
                   │       │         │
                   │  ┌────▼────┐    │
                   │  │ Decision │   │
                   │  └─┬──┬──┬─┘   │
                   │    │  │  │     │
                   │    A  D  R     │
                   └────┼──┼──┼─────┘
                        │  │  │
          ┌─────────────┘  │  └──────────────┐
          ▼                ▼                  ▼
   ┌────────────┐  ┌─────────────┐  ┌──────────────┐
   │ Accept/    │  │ Defer       │  │ Reject       │
   │ Merge      │  │ (keep       │  │ (delete      │
   │            │  │  branch)    │  │  branch,     │
   │ merge to   │  │             │  │  close PR)   │
   │ main,      │  │ next review │  │              │
   │ delete     │  │ cycle       │  │              │
   │ branch,    │  │             │  │              │
   │ close PR   │  │             │  │              │
   └────────────┘  └─────────────┘  └──────────────┘
```

## Prerequisites

Required:
- None — kc-nightwatch works standalone with graceful degradation

Optional (enhances capabilities):
- **kc-plugin-forge** — enables Phase 1 forge validation (skipped if not loaded)
- **private-journal MCP** — enables journal-based signal discovery
- **episodic-memory MCP** — enables cross-session pattern detection
- **Sentry MCP** (claude.ai) — enables production error scanning
- **Linear MCP** (claude.ai) — enables Linear issue creation
- **Slack MCP** (claude.ai) — enables Slack morning reports

## Usage

### Manual Run

```
/kc-nightwatch
```

### Self-Repair (validate config + collect feedback)

```
/kc-nightwatch --self-repair
```

Validates config (Linear team/project names, Sentry access), collects feedback from own PRs/issues, and runs forge on itself. Runs automatically before the regular pipeline in cron mode.

### Dry Run (bypass skip guards)

```
/kc-nightwatch --dry-run
```

Bypasses `skip_if_dirty` and `skip_if_recent_human_commit` guards. Combinable with `--self-repair`. Use during active development or for testing.

### View Last Results

```
/kc-nightwatch-report
```

### Review Proposals

```
/kc-nightwatch-report --review
```

Interactive review of pending proposal and fix branches — accept, defer, or reject each one.

### Setup & Configuration

```
/kc-nightwatch-config              # overview — show current status
/kc-nightwatch-config schedule     # install/change/remove cron
/kc-nightwatch-config channel      # set Slack notification channel
/kc-nightwatch-config plugins      # view/add monitored plugins
```

## Safety

All boundaries defined in `config/safety.yaml`:
- Auto-fix: edit-only, max 3 files per plugin
- Proposals: draft PR, requires PROPOSAL.md (no code edits)
- Skips plugins with uncommitted changes or recent human commits (bypassed with `--dry-run`)
- 7-day cooldown per signal to prevent re-proposals
- 30-minute max runtime

## Components

| Component | File | Purpose |
|-----------|------|---------|
| Orchestrator | `skills/kc-nightwatch/SKILL.md` | Phase 0-5 nightly pipeline |
| Report | `skills/kc-nightwatch-report/SKILL.md` | Status + interactive review |
| Config | `skills/kc-nightwatch-config/SKILL.md` | Schedule, Slack channel, plugin management |
| Signal Harvester | `agents/signal-harvester.md` | Search journal/memory for signals |
| Sentry Scanner | `agents/sentry-scanner.md` | Scan Sentry for error signals |
| E2E Scanner | `agents/e2e-scanner.md` | Scan E2E reports for failure trends |
| Git Scanner | `agents/git-scanner.md` | Analyze git churn + staleness |
| Targets | `~/.claude/kc-plugins-config/nightwatch-targets.yaml` | Monitoring targets + north stars |
| Safety | `config/safety.yaml` | All limits and constraints |
| Improvement Log | `~/.claude/kc-plugins-config/nightwatch-improvement-log.md` | Historical run records + cooldown |
| Cron Wrapper | `~/.claude/scripts/nightwatch-cron.sh` | Plugin loading for headless cron |
| Slack Config | `~/.claude/kc-plugins-config/channels.yaml` | `nightwatch` channel entry |
