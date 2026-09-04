# Skill scenario files

Forge Phase 2 reads `<target-plugin>/skill-scenarios/<skill-name>.scenarios.yaml`
before designing RED/GREEN scenarios by hand. Present → its scenarios run first,
by name, on the clean runner. Absent → Phase 2 falls back to hand design and the
Phase 4 report says `scenarios: hand-designed (no scenario file at <path>)`. The
file is an input, not a precondition.

Mirrors the existing `smoke-tests/<skill>.smoke.yaml` precedent: a list of
single-key mappings, one file per skill.

```yaml
schema: forge-skill-scenarios/v1
skill: <skill-name>
skill_path: <plugin>/skills/<skill-name>/SKILL.md
model: sonnet-4-6           # default pin; a scenario may override with its own model:
effort: low
green_preamble: "Before doing anything else, read {SKILL_PATH} in this checkout completely and follow it. Then:"
scenarios:
  - id: T1
    name: <short label>
    adversarial: <what the operator's ask opposes in the rule>   # required
    setup: |                                                     # required, "" if none
      mkdir -p {SCRATCH} && cat > {SCRATCH}/fixture.md <<'EOF'
      ...
      EOF
    prompt: |
      ... reference {SCRATCH} and {SKILL_PATH} as templates, never a literal path ...
    assert:                                                      # exactly one of assert:/judge:
      - file_matches: {path: "{SCRATCH}/ACTION.md", pattern: 'some regex'}
      - frontmatter_field: {path: "{SCRATCH}/ACTION.md", field: decision, equals: hold}
      - output_contains: "some phrase"
      - output_not_contains: "some phrase"
```

## Format rules — each closes something observed

- **`{SCRATCH}` is a template, never a literal path.** The runner substitutes a
  fresh per-run directory. A scenario's `setup:`/`prompt:` carrying a literal
  `/tmp/...` or `/var/folders/...` path is refused before any API call — that
  hardcoded path is what let two POC sessions read each other's fixture.
- **The token is injected by the runner, not stored in the file.** A stored
  token cannot be fresh, and freshness is what proves a transcript read
  belongs to this run.
- **`adversarial:` is required and must name the opposition.** A baseline the
  operator's ask does not oppose is a baseline that cannot fail — it measures
  nothing (a 2026-09-03 in-session trial answered 10/10 correctly this way).
- **`assert:` states what the rule requires, not "expected to fail".** RED and
  GREEN are scored against the identical assertion list; the RED/GREEN split
  is the only variable.
- **`judge:` is the exception, never the default.** Allowed only when a
  scenario carries no `assert:` (a criterion with no file or string
  signature). Evaluated by a model different from the runner model. Reported
  as `judged`, never `passed` — a judged scenario never counts toward a
  RED/GREEN claim without a human reading it. No scenario in this repo uses
  it yet; the refusal and label exist so the format doesn't silently drift
  toward "prose, graded by another model" as the default.

## How each assertion is evaluated

- **`file_matches` / `frontmatter_field`** — the epilogue `cat`s the named
  path inside a fixed `===FORGE-FILE-START/END===` marker; the runner reads
  it back from the tool-call output (cloud: paged `session message`; bare:
  the `stream-json` transcript) and matches host-side.
- **`output_contains` / `output_not_contains`** — checked against the run's
  **terminal result string only** (bare: `.result` of `--output-format json`;
  cloud: the `result` field of the `subtype: success` payload), never against
  tool output. Otherwise the epilogue's own `cat` would satisfy every
  `output_contains` trivially.
- Marker or token missing within budget ⇒ `outcome=error`, never `pass`.

## Enforcement point

These are refusals in `reference/skill-runner.py`, not
prose: it exits non-zero before any API call when a scenario omits
`adversarial:` or `setup:`, when it carries neither `assert:` nor `judge:` or
carries both, or when `setup:`/`prompt:` contains a literal absolute scratch
path. Without an enforcement point the rules are advice and the next scenario
reintroduces the hardcoded path.
