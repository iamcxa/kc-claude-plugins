# Recording & Evidence

## Artifacts per run

| Artifact | Format | When |
|----------|--------|------|
| Accessibility snapshots | Text (a11y tree) | Every step |
| Screenshots | PNG | Every step (when recording) or on failure |
| Annotated screenshots | PNG with labeled elements | On demand (`--annotate`) |
| Video recording | WebM | Walkthroughs (default) or tests (`--video`) |
| MP4 video | MP4 (1.5x speed) | Auto-converted from WebM for sharing |
| Steps GIF | GIF (800px, 1fps loop) | Auto-generated from per-step screenshots |
| Network trace | JSONL HAR (trace.zip) | Per walkthrough/test run |
| Console log | JSONL (trace.zip) | Per walkthrough/test run |
| Trace analysis report | Markdown | After each trace |
| Test report | Markdown | After each test run |
| Flow YAML | YAML | Auto-generated after walkthrough |
| Metrics JSON | JSON | When `--metrics-output` is used |

## Recording defaults

| Skill | Video Default | Override |
|-------|--------------|----------|
| `/e2e-walkthrough` | ON | `--no-video` |
| `/e2e-test` | OFF | `--video` or `--pr` |
| `/e2e-map` | No recording | — |

## Output files per run

| File | Purpose |
|------|---------|
| `full.webm` | Complete viewport recording for debugging |
| `test-run.mp4` / `walkthrough.mp4` | 1.5x speed MP4 for sharing (auto-converted from WebM) |
| `steps.gif` | Step overview for communication (PR comments, Slack) |
| `step-*.png` | Individual step screenshots |
| `trace.zip` | Interactive replay with network waterfall and DOM snapshots |

> Large binary artifacts (`*.webm`, `*.mp4`, `trace.zip`) are automatically added to the project's `.gitignore` on first run to prevent accidental commits.

Replay a trace interactively:

```bash
npx playwright show-trace trace.zip
```

---

## PR Review with E2E Evidence

### Proving a bug fix works

A PR claims to fix a frontend bug. Use the pipeline to produce evidence:

```
/e2e-walkthrough --pr 940
```

The skill reads the PR diff, identifies which UI pages are affected, and proposes a walkthrough targeting the fix. Walk through the repaired flow — the output includes:

- Step-by-step screenshots
- Console error / API failure counts (via trace analysis)
- Auto-generated flow YAML capturing the working state

Then post the results as a PR comment:

```
/e2e-test <generated-flow> --pr 940
```

The test summary (pass/fail, step count, health data) is posted directly to the PR as a comment, giving reviewers concrete proof.

### Proving a feature matches requirements

A PR implements a feature from a spec or flowchart. You need to verify the implementation matches the expected flow:

```
/e2e-walkthrough --pr 940 --issue DRC-2779
```

The skill reads both the PR diff and the issue description (from Linear/GitHub), then proposes a walkthrough plan covering the feature's expected flow. Walk through it step by step:

1. The walkthrough plan maps issue requirements → UI pages → expected elements
2. Each step verifies elements exist, interactions work, and navigation is correct
3. Trace analysis catches API errors or console warnings hidden from the UI
4. A flow YAML is auto-generated, becoming a **regression test** for this feature

Post results:

```
/e2e-test <generated-flow> --pr 940 --issue DRC-2779
```

The PR comment includes the issue context, making the review self-documenting.
