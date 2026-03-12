# Video Recording & Media Publishing — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add screen recording (WebM) + GIF generation + media-enriched reports to the e2e-pipeline, then enable publishing to PR/Slack/Linear with embedded visuals.

**Architecture:** Agent layer handles `record start/stop` (conditional). Skill layer handles ffmpeg GIF post-processing and report templating. Phase 2 adds a GitHub upload utility and extends existing `--pr`/`--issue` publishing paths.

**Tech Stack:** agent-browser `record` command (WebM), ffmpeg (GIF), gh CLI (PR upload), Slack MCP, Linear MCP.

---

## Phase 1: Local Recording + GIF + Report Integration

### Task 1: Document `record` command in references

**Files:**
- Modify: `references/commands.md:62-72` (Tracing & Health section)

**Step 1: Add record commands to the reference**

Insert a new `## Recording` section before `## Semantic Locators` (line 74):

```markdown
## Recording

```bash
agent-browser record start "<abs-path.webm>"        # Start viewport recording (WebM)
agent-browser record stop                            # Stop recording and save file
```

**Rules:**
- Start AFTER `open` (browser must be active)
- Stop BEFORE `close` (or video file is truncated)
- Stop BEFORE `trace stop` (recording captures the trace-stop moment)
- Path must be absolute (same as screenshots/traces)
- Output format: WebM (VP8/VP9 codec)
```

**Step 2: Verify the commands exist**

Run:
```bash
agent-browser record --help
```
Expected: Help text showing `start` and `stop` subcommands.

**Step 3: Commit**

```bash
git add references/commands.md
git commit -m "docs: add record start/stop to CLI reference"
```

---

### Task 2: Add recording support to e2e-test-runner agent

**Files:**
- Modify: `agents/e2e-test-runner.md`

**Step 1: Add `record` to Input Contract table (after line 57)**

Add this row to the Input Contract table:

```markdown
| `record` | No | When `true`, record browser viewport to `{{report_dir}}/full.webm` (default: `false`) |
```

**Step 2: Add recording start to Phase 1 Setup (after line 127, after trace start)**

Insert after the `### 1e. Start Tracing` section, before `---`:

```markdown
### 1f. Start Recording (conditional)

If `record` is `true`:

```bash
agent-browser record start "{{report_dir}}/full.webm"
```

Start recording AFTER trace start. The trace captures internal data; the recording captures the visual viewport.
```

**Step 3: Force per-step screenshots**

Modify section `### 2i. Screenshot` (currently line 248-260). Replace the conditional:

```markdown
### 2i. Screenshot

Capture a screenshot for EVERY step (not just failures). This enables GIF generation downstream.

```bash
agent-browser screenshot --annotate "{{report_dir}}/step-{{step_number}}-{{id}}.png"
```

If `--annotate` fails, fall back to:

```bash
agent-browser screenshot "{{report_dir}}/step-{{step_number}}-{{id}}.png"
```

**Naming**: Use zero-padded step number prefix (e.g., `step-01-navigate.png`, `step-02-fill-email.png`) to ensure correct sort order for GIF generation.

On failure, ALSO capture the failure-specific screenshot:

```bash
agent-browser screenshot "{{report_dir}}/FAIL-{{id}}.png"
```
```

**Step 4: Add recording stop to Phase 3 Report (before trace stop)**

Modify section `### 3a. Stop Trace` (line 292). Insert recording stop BEFORE trace stop:

```markdown
### 3a. Stop Recording & Trace

If `record` is `true`:

```bash
agent-browser record stop
```

Then stop the trace:

```bash
agent-browser trace stop "{{report_dir}}/trace.zip"
```

**Order matters**: record stop → trace stop → (do NOT close browser).
```

**Step 5: Update Report template**

In section `### 3c. Write Report` (line 304), add to the Artifacts section of the report template:

```markdown
## Artifacts
- Trace: {{report_dir}}/trace.zip
- Recording: {{report_dir}}/full.webm   ← (only if record was true)
- Screenshots: {{report_dir}}/step-*.png, FAIL-*.png
```

**Step 6: Update Summary output**

In section `### 3d. Return Structured Summary` (line 352), add:

```markdown
- recording_path: {{report_dir}}/full.webm    ← (only if record was true, else omit)
```

**Step 7: Commit**

```bash
git add agents/e2e-test-runner.md
git commit -m "feat(agent): add conditional recording + per-step screenshots to test-runner"
```

---

### Task 3: Add `--video` flag to e2e-test skill

**Files:**
- Modify: `skills/e2e-test/SKILL.md`

**Step 1: Add --video flag to invocation (line 13)**

Update the invocation line:

```markdown
/e2e-test [flow-name|--tag tag|--all] [--mapping name] [--all-sites] [--suite name] [--pr NUMBER] [--issue ISSUE-ID] [--video]
```

Add to the args table:

```markdown
| `--video` | Enable screen recording + GIF generation (auto-enabled when `--pr` is used) |
```

**Step 2: Update agent dispatch (Phase 1, line 99-120)**

In the "Prepare Agent Input" table, add:

```markdown
| `record` | `true` when `--video` or `--pr` is present, otherwise `false` |
```

Update the dispatch template:

```markdown
Agent(subagent_type="e2e-test-runner"):
  "Execute E2E flow:
   flow_path: <path>  mapping_path: <path>  auth_profile: <path>
   base_url: <url>  app: <name>  report_dir: <path>  headed: true
   record: true              # only when --video or --pr
   suite_context: true"      # only for --all-sites / --suite
```

**Step 3: Add GIF post-processing (new section after Phase 1, before Phase 2)**

Insert a new section `### Phase 1.5 — Media Post-Processing` between Phase 1 (Dispatch) and Phase 2 (Present Results):

```markdown
### Phase 1.5 — Media Post-Processing

After agent returns, if `record` was `true`:

**Generate steps GIF** from per-step screenshots:

```bash
ffmpeg -framerate 1 -pattern_type glob -i "$REPORT_DIR/step-*.png" \
  -vf "scale=800:-1:flags=lanczos" -loop 0 -y "$REPORT_DIR/steps.gif"
```

- Framerate 1 = each screenshot holds 1 second
- Width 800px, height auto-scaled with lanczos filter
- `-loop 0` = infinite loop
- If ffmpeg fails (no screenshots, missing binary), warn but continue — GIF is optional

**Verify**: Check file exists and size > 0.
```

**Step 4: Update report presentation (Phase 2)**

In Phase 2 — Present Results (line 128), update the single-result format:

```markdown
**Single:** `Test complete: N/M PASS (X console errors, Y API failures) Report: <path> Browser still open.`

If recording was enabled, append:
- `Recording: <path>/full.webm`
- `Steps GIF: <path>/steps.gif`
```

**Step 5: Update PR comment section**

In the PR comment section (line 145), update:

```markdown
**PR comment (if --pr):** Write `$REPORT_DIR/pr-summary.md` with:
- Pass/fail summary table
- Steps GIF reference (local path for Phase 1; URL for Phase 2)
- Key findings from trace analysis
- Link to full report

Then: `gh pr comment <PR> --body-file $REPORT_DIR/pr-summary.md`
```

**Step 6: Commit**

```bash
git add skills/e2e-test/SKILL.md
git commit -m "feat(skill): add --video flag and GIF post-processing to e2e-test"
```

---

### Task 4: Add default recording to e2e-walkthrough skill

**Files:**
- Modify: `skills/e2e-walkthrough/SKILL.md`

**Step 1: Update invocation (line 22)**

```markdown
/e2e-walkthrough [context] [--mode guided|step|auto] [--sites name1,name2] [--pr N] [--issue ID] [--no-video]
```

Add to entry points table:

```markdown
| `--no-video` | Skip screen recording (default: recording ON) |
```

**Step 2: Add recording start to Phase 3 — Execute & Monitor (line 151)**

Update the summary line for Phase 3:

```markdown
**Summary**: Open browser → verify auth → start trace → **start recording** → execute steps in chosen interaction mode → track mapping discrepancies.
```

Add after trace start, before step execution:

```markdown
**Start recording** (unless `--no-video`):

```bash
agent-browser record start "$REPORT_DIR/full.webm"
```
```

**Step 3: Update Phase 4 — Output & Learn (line 165)**

Update the strict-order list. Insert recording stop as item 0.5 (before trace stop):

```markdown
1. **Stop recording** (if recording): `agent-browser record stop`
2. **Stop trace**: `agent-browser trace stop "$REPORT_DIR/trace.zip"`
3. **Trace analysis**: Dispatch `e2e-trace-analyzer` subagent with `trace_path` + `report_dir`
4. **Report**: Write `$REPORT_DIR/report.md` with summary, step results, health log, media links
5. **GIF generation** (if recording):
   ```bash
   ffmpeg -framerate 1 -pattern_type glob -i "$REPORT_DIR/step-*.png" \
     -vf "scale=800:-1:flags=lanczos" -loop 0 -y "$REPORT_DIR/steps.gif"
   ```
6. **Flow YAML auto-generation (MANDATORY)**: Always auto-generate
7. **PR/Issue posting**: `--pr` → `gh pr comment`, `--issue` → Linear MCP
8. **Mapping self-repair**: Present discrepancy list, human approves
9. **Browser handoff (BLOCKING: flow YAML must be written first)**
```

**Step 4: Commit**

```bash
git add skills/e2e-walkthrough/SKILL.md
git commit -m "feat(skill): default recording ON for walkthrough, add --no-video"
```

---

### Task 5: Pass flags through e2e-dispatch

**Files:**
- Modify: `skills/e2e-dispatch/SKILL.md`

**Step 1: Update dispatch routing**

In `### --test` section (line 78), update:

```markdown
### --test
Invoke `Skill: "e2e-test"` with the original arguments (flow name, --tag, --suite, --all, --pr, --issue, **--video**).
```

In `### --walk` section (line 90), update:

```markdown
### --walk
Invoke `Skill: "e2e-walkthrough"` with mapping name and any --mode, --smoke, --sites, --pr, --issue, **--no-video** arguments.
```

**Step 2: Update Quick Reference table (line 124)**

Add rows:

```markdown
| Record a test run | `/e2e-dispatch --test login-flow --video` |
| Walkthrough no video | `/e2e-dispatch --walk admin-panel --no-video` |
```

**Step 3: Commit**

```bash
git add skills/e2e-dispatch/SKILL.md
git commit -m "feat(skill): pass --video/--no-video through dispatch"
```

---

### Task 6: Update report template with media section

**Files:**
- Modify: `agents/e2e-test-runner.md` (report template in Phase 3)

**Step 1: Update the report.md template in section 3c (line 304)**

Replace the current report template with:

```markdown
# E2E Test Report: {{flow_name}}

**Date**: {{ISO date}}
**Flow**: {{flow_path}}
**Mapping**: {{mapping_path}}
**Base URL**: {{base_url}}

## Summary

| Metric | Count |
|--------|-------|
| Total Steps | N |
| Passed | N |
| Failed | N |
| Skipped | N |
| Console Errors | N |
| API Failures | N |

## Evidence

| Artifact | Link |
|----------|------|
| Steps GIF | [steps.gif](./steps.gif) |
| Full recording | [full.webm](./full.webm) |
| Trace (interactive) | [trace.zip](./trace.zip) |

_(Recording/GIF rows only if `record` was true)_

## Step Results

### [PASS] step-id: action description
- Expectations: 3/3 passed
- Screenshot: [step-01-step-id.png](./step-01-step-id.png)

### [FAIL] step-id: action description
- **Error**: reason
- Expectations: 1/3 passed
  - PASS: "element visible on page"
  - FAIL: "url contains /expected"
  - PASS: "dialog not visible"
- Screenshot: [FAIL-step-id.png](./FAIL-step-id.png)
- Debug Snapshot: FAIL-step-id-snapshot.txt

### [SKIP] step-id: action description (optional)
- Reason: Element not found

## Health Issues
- N console errors (after noise filter)
- N API failures (4xx/5xx)
```

**Step 2: Commit**

```bash
git add agents/e2e-test-runner.md
git commit -m "feat(agent): media-enriched report template"
```

---

## Phase 2: Remote Publishing

### Task 7: GitHub image upload utility

**Files:**
- Create: `references/media-upload.md`

**Step 1: Document the upload method**

```markdown
# Media Upload Reference

## GitHub Image Upload (for PR/issue embedding)

Upload an image or GIF to GitHub and get a permanent URL:

```bash
# Create a temporary issue with the image, extract the URL, then close
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
UPLOAD_URL=$(gh issue create \
  --title "tmp-upload" \
  --body "![media]($(gh api --method POST \
    repos/$REPO/issues/1/comments \
    -F "body=uploading" | jq -r '.id'))" \
  2>&1 | grep -o 'https://.*')
```

**Simpler approach** — use `gh` to upload via issue comment body:

```bash
# Upload file and extract GitHub-hosted URL
upload_to_github() {
  local file="$1"
  local repo=$(gh repo view --json nameWithOwner -q .nameWithOwner)
  local ext="${file##*.}"
  local mime="image/gif"
  [[ "$ext" == "png" ]] && mime="image/png"
  [[ "$ext" == "webm" ]] && mime="video/webm"

  # gh api supports file upload via asset endpoint on releases
  # For images in PR comments, use the drag-drop URL format:
  local url=$(gh api graphql -f query='
    mutation($file: Upload!) {
      createIssueComment(input: {
        subjectId: "'$(gh api repos/$repo -q .node_id)'"
        body: "upload"
      }) { id }
    }' 2>/dev/null)

  echo "$url"
}
```

**Practical approach for PR comments:**

GitHub renders image markdown in PR comments. The simplest method:
1. Open a draft issue
2. Use the issue body to host the image (GitHub auto-uploads)
3. Extract the `user-images.githubusercontent.com` URL
4. Close the draft issue
5. Use the URL in PR comments (URLs persist after issue deletion)

**Fallback**: If upload fails, include the local path in the comment with a note: "Screenshots available in the test report directory."
```

**Step 2: Commit**

```bash
git add references/media-upload.md
git commit -m "docs: add media upload reference for GitHub image hosting"
```

---

### Task 8: Media-enriched PR comments in e2e-test

**Files:**
- Modify: `skills/e2e-test/SKILL.md`

**Step 1: Update PR comment section (Phase 2 — Present Results)**

Replace the current `--pr` handling with:

```markdown
**PR comment (if --pr):**

1. **Upload media** (if recording was enabled):
   - Upload `$REPORT_DIR/steps.gif` to GitHub → get `GIF_URL`
   - Upload key failure screenshots (`FAIL-*.png`) → get URLs
   - If upload fails, fall back to text-only summary

2. **Write PR summary** `$REPORT_DIR/pr-summary.md`:

```markdown
## E2E Test: {{flow_name}}

**Result**: {{passed}}/{{total}} PASS | {{failed}} FAIL | {{skipped}} SKIP

![Steps]({{GIF_URL}})

### Failures
{{#each failures}}
**{{id}}**: {{error}}
![]({{FAIL_SCREENSHOT_URL}})
{{/each}}

### Health
- Console errors: {{console_errors}}
- API failures: {{api_failures}}

<details>
<summary>Full report</summary>

{{report.md contents}}

</details>
```

3. **Post**: `gh pr comment {{PR}} --body-file $REPORT_DIR/pr-summary.md`
```

**Step 2: Commit**

```bash
git add skills/e2e-test/SKILL.md
git commit -m "feat(skill): media-enriched PR comments for e2e-test"
```

---

### Task 9: Media-enriched PR/issue comments in e2e-walkthrough

**Files:**
- Modify: `skills/e2e-walkthrough/SKILL.md`

**Step 1: Update Phase 4 PR/Issue posting section**

Update item 7 (PR/Issue posting):

```markdown
7. **PR/Issue posting** (if `--pr` or `--issue`):
   - Upload `$REPORT_DIR/steps.gif` + failure screenshots to GitHub
   - Write summary with embedded GIF and failure images
   - `--pr` → `gh pr comment {{PR}} --body-file $REPORT_DIR/pr-summary.md`
   - `--issue` → Post via Linear MCP with summary text and GIF URL
   - Format matches e2e-test PR summary (GIF header, failure screenshots, health data, collapsible full report)
```

**Step 2: Commit**

```bash
git add skills/e2e-walkthrough/SKILL.md
git commit -m "feat(skill): media-enriched PR/issue posting for walkthrough"
```

---

### Task 10: Slack and Linear media publishing

**Files:**
- Modify: `skills/e2e-test/SKILL.md`
- Modify: `skills/e2e-walkthrough/SKILL.md`

**Step 1: Add Slack publishing option to e2e-test**

Add `--slack <channel>` flag to invocation:

```markdown
| `--slack <channel>` | Post summary + GIF to Slack channel after execution |
```

Add Slack posting logic after PR comment section:

```markdown
**Slack notification (if --slack):**

1. Upload GIF to GitHub (reuse URL if already uploaded for --pr)
2. Post via Slack MCP:
   ```
   mcp__claude_ai_Slack__slack_send_message:
     channel: <channel>
     text: "E2E Test: {{flow_name}} — {{passed}}/{{total}} PASS\n{{GIF_URL}}"
   ```
```

**Step 2: Add same to e2e-walkthrough**

Same pattern: `--slack <channel>` flag, post summary + GIF URL.

**Step 3: Add Linear attachment to both skills**

When `--issue` is used and media exists:

```markdown
**Linear attachment (if --issue and recording):**
1. Upload GIF to GitHub → get URL
2. Create Linear attachment via MCP:
   ```
   mcp__claude_ai_Linear__create_attachment:
     issueId: <resolved-issue-id>
     url: <GIF_URL>
     title: "E2E walkthrough recording"
   ```
3. Add comment with summary text
```

**Step 4: Commit**

```bash
git add skills/e2e-test/SKILL.md skills/e2e-walkthrough/SKILL.md
git commit -m "feat(skill): Slack and Linear media publishing"
```

---

### Task 11: Update README and CHANGELOG

**Files:**
- Modify: `README.md` (Recording & Evidence section)
- Modify: `CHANGELOG.md`

**Step 1: Update README recording section**

Replace the "Video recording" subsection with updated capabilities:

```markdown
### Video recording

The pipeline records browser viewport video (WebM) and generates step-by-step GIFs:

- **Walkthroughs** record by default (`--no-video` to skip)
- **Tests** record when `--video` or `--pr` is passed
- **GIF** auto-generated from per-step screenshots (800px, 1fps, looping)
- **PR comments** embed the GIF inline with pass/fail summary
- **Slack/Linear** receive GIF + summary via `--slack` / `--issue`

Output per run:
| File | Purpose |
|------|---------|
| `full.webm` | Complete viewport recording for debugging |
| `steps.gif` | Step overview for communication |
| `trace.zip` | Interactive replay: `npx playwright show-trace trace.zip` |
| `step-*.png` | Individual step screenshots |
```

**Step 2: Update CHANGELOG**

Add version 1.2.0 entry.

**Step 3: Update plugin.json version to 1.2.0**

**Step 4: Commit**

```bash
git add README.md CHANGELOG.md .claude-plugin/plugin.json
git commit -m "docs: update README and CHANGELOG for video recording feature"
```

---

## Execution Order Summary

| Task | Phase | Description | Depends On |
|------|-------|-------------|------------|
| 1 | 1 | Document `record` in references | — |
| 2 | 1 | Test-runner agent: recording + per-step screenshots | Task 1 |
| 3 | 1 | e2e-test skill: `--video` + GIF | Task 2 |
| 4 | 1 | e2e-walkthrough skill: default recording | Task 2 |
| 5 | 1 | e2e-dispatch: flag passthrough | Task 3, 4 |
| 6 | 1 | Report template with media | Task 2 |
| 7 | 2 | GitHub upload utility | — |
| 8 | 2 | e2e-test: PR media publishing | Task 3, 7 |
| 9 | 2 | e2e-walkthrough: PR/issue media publishing | Task 4, 7 |
| 10 | 2 | Slack + Linear media publishing | Task 7 |
| 11 | 2 | README + CHANGELOG + version bump | Task 8, 9, 10 |
