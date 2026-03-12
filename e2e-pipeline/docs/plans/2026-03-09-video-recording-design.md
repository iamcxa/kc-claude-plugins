# Video Recording & Media Publishing — Design

## Goal

Add screen recording and media publishing to the e2e-pipeline so every test run and walkthrough produces visual evidence (video + GIF + screenshots) that can be embedded in PR comments, Slack messages, and Linear issues.

## Recording Strategy

| Skill | Default | Override |
|-------|---------|----------|
| `/e2e-walkthrough` | Record on | `--no-video` to skip |
| `/e2e-test` | Record off | `--video` or `--pr` to enable |
| `/e2e-map` | No recording | N/A |

## Output Artifacts

Every recording-enabled run produces:

```
e2e-reports/<timestamp>/
├── report.md          # Integrated report with media links
├── full.webm          # Full browser viewport recording (debug)
├── steps.gif          # Key steps GIF (communication)
├── trace.zip          # Playwright trace (interactive replay)
├── step-1.png         # Per-step screenshots
├── step-2.png
└── ...
```

### Three Layers of Evidence

| Artifact | Audience | Format | Size |
|----------|----------|--------|------|
| full.webm | Developers | WebM (VP8/VP9) | Large |
| steps.gif | PM, designers, reviewers | GIF (800px wide) | Small |
| trace.zip | Developers | Playwright trace | Medium |

## Technical Approach

### Video Recording

Use existing `agent-browser record start/stop`:

```bash
agent-browser record start "$REPORT_DIR/full.webm"
# ... run test steps ...
agent-browser record stop
```

Integrated at the agent level (e2e-test-runner, walkthrough flow). The skill passes a `record: true/false` flag to the agent.

### GIF Generation

After all steps complete, the skill (not the agent) runs ffmpeg to stitch per-step PNGs into a GIF:

```bash
ffmpeg -framerate 1 -pattern_type glob -i '$REPORT_DIR/step-*.png' \
  -vf "scale=800:-1" -loop 0 "$REPORT_DIR/steps.gif"
```

Each frame holds ~1 second. Width fixed at 800px, height auto-scaled.

Prerequisite: per-step screenshots must be captured for ALL steps (not just failures). This requires a change to the test-runner agent.

### Report Format

```markdown
## Test Report: login-flow
**Result**: 7/7 PASS | **Duration**: 12s

### Evidence
- Full trace: [trace.zip](./trace.zip) (interactive replay)
- Steps overview: [steps.gif](./steps.gif)
- Screenshots: [step-1](./step-1.png) | [step-2](./step-2.png) | ...

### Steps
| # | Step | Result | Screenshot |
|---|------|--------|------------|
| 1 | Navigate to /login | PASS | ![](./step-1.png) |
| 2 | Fill email | PASS | ![](./step-2.png) |
```

## Two-Phase Rollout

### Phase 1 — Local Report Integration

Scope: recording + GIF + updated report format. All artifacts stay local in `e2e-reports/`.

Changes:
- `agents/e2e-test-runner.md` — add `record start/stop` (conditional on `record` flag); force per-step screenshots (not just on failure)
- `skills/e2e-test/SKILL.md` — add `--video` flag; run ffmpeg for GIF post-run; update report template
- `skills/e2e-walkthrough/SKILL.md` — default `record: true`; add `--no-video` flag; run ffmpeg for GIF post-run
- `skills/e2e-dispatch/SKILL.md` — pass `--video` / `--no-video` flags through
- `references/commands.md` — document `record start/stop`

### Phase 2 — Remote Publishing

Scope: upload media to GitHub, embed in PR/Slack/Linear.

Upload strategy: upload GIF + key screenshots to GitHub via issue attachment (produces `user-images.githubusercontent.com` URL). Replace local paths in report with remote URLs before posting.

Channels:
- **PR comment**: `gh pr comment` with markdown containing embedded GIF + summary
- **Slack**: Slack MCP `slack_send_message` with GIF URL + summary text
- **Linear**: Linear MCP attachment API upload + comment

Changes:
- `skills/e2e-test/SKILL.md` — media upload logic when `--pr` flag present; URL replacement in report
- `skills/e2e-walkthrough/SKILL.md` — same for `--pr`, `--issue` flags
- New utility: GitHub image upload helper (bash function or script)
- Slack/Linear integration: extend existing `--pr` / `--issue` post logic with media

## Dependencies

- `agent-browser` — `record start/stop` (already available)
- `ffmpeg` — GIF generation (already installed at `/opt/homebrew/bin/ffmpeg`)
- `gh` CLI — PR comment + image upload (already available)
- Slack MCP — message posting (already configured)
- Linear MCP — attachment upload (already configured)

## Non-Goals

- Desktop/system screen recording (browser viewport only)
- MP4 output (WebM sufficient for debug; GIF for communication)
- Video editing or trimming (full recording as-is)
- Recording during `/e2e-map` (mapping is exploration, not demonstration)
