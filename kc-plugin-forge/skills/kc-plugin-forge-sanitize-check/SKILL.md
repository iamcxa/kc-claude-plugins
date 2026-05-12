---
name: kc-plugin-forge-sanitize-check
description: Use before publishing a public plugin (especially before /kc-marketplace-sync) to grep for known leak patterns in the plugin's public reference files. Triggered by "/kc-plugin-forge sanitize-check <plugin>", "sanitize-check", "check leaks before publish", "prepublish scan". Read-only safety net — NOT a replacement for Early-stage Dreaming (which is the real privacy gate at capture time).
---

# Plugin Sanitize-Check

Prepublish backstop. Greps a plugin's public files (`reference/*.md`, `skills/**/*.md`, `agents/**/*.md`, `README.md`, `CLAUDE.md`, `docs/*.md`) for **known leak patterns**. If any hit, block publish with a per-finding report so user can decide: fix, allowlist, or override.

**Position in the knowledge ladder**: this skill is the safety net AFTER Early-stage Dreaming. Early-stage Dreaming is the primary defense (sanitize at capture time). Sanitize-check exists only because Dreaming is human-gated and humans miss things.

## When to invoke

| Trigger | Action |
|---------|--------|
| Before `/kc-marketplace-sync` for a public plugin | Run sanitize-check first; abort sync if findings exist and user does not override |
| Before opening a PR to a public plugin repo | Run sanitize-check on the changed files |
| After bulk Dreaming session | Sanity check that distilled rules don't still contain identifiers |
| Periodically (nightwatch) | Audit accumulated drift |

## Usage

```
/kc-plugin-forge sanitize-check <plugin-name>
/kc-plugin-forge sanitize-check <plugin-name> --strict   # treat WARN as block
/kc-plugin-forge sanitize-check --all                    # scan all kc-* plugins
```

## Detection rules

Three rule classes, all configurable in `~/.claude/kc-plugins-config/sanitize-rules.yaml` (created on first run with defaults).

### Class 1 — BLOCK (literal high-signal identifiers)

Strings that should NEVER appear in public files. Match = block publish.

Default seeds (user adds their own orgs):
- `DataRecce`
- `@recce/` (org-scoped npm package)
- `reccehq.com`
- `bw.tw`  (real domain)
- `pwd123` (known seed credential)
- `staff@bw.tw`

User override: edit `sanitize-rules.yaml` `block_literals:` list.

### Class 2 — WARN (heuristic patterns)

Regex patterns that are usually but not always identifiers. Match = warn, do not block.

Defaults (hardcoded — yaml has `disable_warn:` list to suppress):
- `[A-Z]{2,5}-\d{2,6}` (likely Linear/Jira ticket) — allow `DRC-XXXX`, `PROJ-NNN` templates
- `[a-z][-a-z0-9]+/[a-z][-a-z0-9]+#\d+` (likely GitHub PR ref)
- `` `[0-9a-f]{7,40}` `` (likely short SHA in markdown code-tick)
- `/Users/[^/]+/(Project|Code|Work)/` (likely local path)
- `[A-Za-z0-9._%+-]+@(?!example\.com|test\.com|seed\.[a-z]+)[A-Za-z0-9.-]+\.[A-Za-z]{2,}` (likely real email)
- `(feature|fix|chore)/[a-z]{2,5}-\d+` (likely ticket-prefixed branch)

### Class 3 — REJECT (production secret shapes)

Patterns that should never exist anywhere — log loudly and abort with non-zero exit.

Defaults:
- `AKIA[0-9A-Z]{16}` (AWS access key)
- `ghp_[A-Za-z0-9]{36}` (GitHub personal token)
- `sk-[A-Za-z0-9]{32,}` (OpenAI/Anthropic key shape)
- `-----BEGIN [A-Z ]+PRIVATE KEY-----`
- `ssh-rsa AAAA[0-9A-Za-z+/=]{100,}` (SSH private/public key body)

If REJECT fires, **also** flag for journal entry — production secret in plugin tree is a real incident.

## Flow

1. Load `~/.claude/kc-plugins-config/sanitize-rules.yaml` (create from defaults if missing). Print rule counts.

2. Resolve plugin root:
   - `$KC_WORKSPACE/kc-claude-plugins/<plugin>/` (public)
   - `$KC_WORKSPACE/claude-plugins-principle/<plugin>/` (private — still useful for catching secrets that shouldn't be anywhere)

3. Build file list — public-facing files only:
   ```
   <plugin>/reference/*.md
   <plugin>/skills/**/*.md
   <plugin>/agents/*.md
   <plugin>/hooks/**/*.md
   <plugin>/docs/*.md
   <plugin>/README.md
   <plugin>/CLAUDE.md
   ```
   Exclude: `.git/`, `.private/`, anything in `.gitignore`.

4. For each file, run all three rule classes (literal grep, regex grep). Collect findings.

5. Filter allowlist (from yaml `allowlist:`).

6. Report:

   ```
   ## Sanitize-Check Report — <plugin> @ <commit-sha>

   ❌ REJECT (1)
     - file.md:42  AKIA1234567890ABCDEF   ← AWS access key shape
       → STOP. Production secret in public tree. Run /kc-session-handoff and remediate before any further action.

   🚫 BLOCK (2)
     - learned-patterns.md:189  DataRecce        ← org name
     - learned-patterns.md:212  @recce/foo       ← internal package

   ⚠️  WARN (5)
     - skills/x/SKILL.md:30  DRC-3245            ← ticket shape
     - reference/y.md:11    /Users/kent/Project/recce  ← local path
     ... (3 more)

   Verdict: BLOCKED (1 REJECT + 2 BLOCK)
   ```

7. Decision tree:
   - REJECT > 0 → exit 2 (hard stop, no override)
   - BLOCK > 0 → exit 1 (block; user can add to allowlist or fix and re-run)
   - WARN > 0 → exit 0 with verdict CONDITIONAL PASS (no block unless `--strict`)
   - Clean → exit 0 with verdict PASS

## Output for `kc-marketplace-sync` integration

When invoked with `--ci` or `--exit-code-only`, suppress human-readable output and exit with class-based code. `kc-marketplace-sync` should run this skill with `--ci` and refuse to sync if exit code ≠ 0.

## Allowlist

`sanitize-rules.yaml`:

```yaml
block_literals:
  - DataRecce
  - "@recce/"
  - reccehq.com
allowlist:
  - "DRC-XXXX"
  - "DRC-NNNN"
  - "PROJ-101"
  - "<TICKET-A>"
  - "user@example.com"
disable_warn:
  # - real_email   # uncomment to disable a heuristic class
```

User edits this by hand; first run seeds defaults. Future enhancement: a `--add-allowlist <string>` flag.

## What this skill does NOT do

- ❌ It is NOT a router. It does not decide where to write captures.
- ❌ It does NOT modify files. Read-only — no autosanitize, no in-place edit, no commit.
- ❌ It does NOT replace Early-stage Dreaming. Privacy lives at capture time, not at publish time.
- ❌ It does NOT scan transcripts, journal, or anything outside the plugin tree.
- ❌ It does NOT detect contextual identifiers (paraphrased customer names, anonymized-but-identifiable case descriptions). That class remains a Dreaming-stage responsibility.

## Rules

- Read-only. Never edit, never commit, never delete.
- Output is the user's decision input — present findings, let user choose.
- Default to permissive on WARN (`--strict` is opt-in) — false positives erode trust.
- REJECT is non-negotiable — production secret class blocks unconditionally.
- Notify-only mode (`--report`) prints findings but always exits 0, for nightwatch integration.
