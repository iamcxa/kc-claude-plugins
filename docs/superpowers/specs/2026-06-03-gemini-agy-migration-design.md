# Design: Migrate `/gemini` skill from `gemini` CLI to `agy` (Antigravity CLI)

- **Date**: 2026-06-03
- **Status**: Approved (brainstorming) → pending implementation plan
- **Scope**: `kc-team-ops/skills/gemini/SKILL.md` (+ its `reference/gemini-reference.md`) ONLY

## Context & Why

Google is discontinuing Gemini CLI for consumer tiers on **2026-06-18** (official:
[Transitioning Gemini CLI to Antigravity CLI](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/)).
The author is on **AI Pro (consumer)**, so `gemini` stops serving requests on that date.
The `/gemini` skill is entirely built on the `gemini` binary and would die.

The replacement is the Antigravity CLI (`agy`). It is **NOT a drop-in** — Google's own
announcement says "no 1:1 feature parity right out of the gate". This migration replaces the
binary AND rewrites the call/parse layer accordingly.

## Ground-Truth Discipline (load-bearing)

Three sources about `agy`'s CLI surface were checked and **all proved unreliable**:

- **Third-party migration blogs** — contradict each other on the binary name (agy/av/antigravity)
  and hallucinate flags (e.g. `--output-format`, which does not exist).
- **Official docs** (`antigravity.google/docs/cli-*`) — JavaScript-rendered; fetch returns title only.
- **agy self-report** (asked `agy` headless about its own usage) — hallucinated nearly every flag
  (`--non-interactive`, `--json`, `--model`, `--read-only`, `--resume`), same failure mode as the blogs.

**The only authoritative source is `agy --help`.** Every flag in this design was verified there on
`agy 1.0.4`. Implementation MUST re-verify against the installed `agy --help`, never against docs,
blogs, or model self-report.

### Verified `agy` surface (from `agy --help`, v1.0.4)

| Capability | `agy` flag | Note |
|---|---|---|
| Single headless prompt | `-p` / `--print` / `--prompt` | stdout = response (plain text) |
| Print timeout | `--print-timeout <dur>` | default 5m |
| Continue most recent conversation | `-c` / `--continue` | no id needed |
| Resume specific conversation | `--conversation <ID>` | |
| Sandbox (terminal restrictions) | `--sandbox` | semantics NOT yet tested |
| Auto-approve ALL tools (DANGER) | `--dangerously-skip-permissions` | the YOLO flag — never use |
| Structured/JSON output | — | **does not exist** |
| Model selection (headless) | — | **no flag**; model chosen via interactive `/model` |

Empirically observed: a tool-free "analysis only" prompt returns in seconds (exit 0); a prompt that
induces tool use hangs headlessly (no TTY to grant permission) until timeout.

## Decisions (approved)

1. **No fallback.** Replace `gemini` outright; remove all `gemini` paths. Rationale: effective user
   base is one (the author), who wants `agy` fast. `git` history + the still-installed `gemini`
   binary are the only rollback needed before 6/18. (Rejected: agy-first-with-gemini-fallback —
   YAGNI for a single user.)
2. **Keep the skill name `gemini`** and triggers ("gemini review/challenge/ask gemini"). Muscle
   memory + agy still typically runs a gemini-family model. Only SKILL.md *prose* changes to `agy`.
3. **Rename the gate token** `GEMINI_GATE` → `MODEL_GATE` (agy may run non-gemini models:
   Claude/GPT-OSS). The PASS/FAIL sentinel mechanism is unchanged.
4. **Model-agnostic.** The skill does NOT pin a model. Whatever `agy`'s `/model` setting is, that is
   what runs. (Original request to default to gemini-3.5-flash was dropped — respect agy's own setting.)

## Design

### §1 Binary detection (replaces Step 0)
- `command -v agy`; if absent → stop with install guidance (`https://antigravity.google`, `agy update`).
- **Remove** the gemini multi-signal auth probe (`~/.gemini/oauth_creds.json`, `GEMINI_API_KEY`, …).
  `agy` uses cached OAuth and ran without extra setup in testing; treat "agy on PATH" as usable and
  let agy self-guide first-run login.

### §2 Call layer (replaces `run_gemini` + `gemini_field`)
- New `run_agy()`: `agy -p "$prompt" --print-timeout <N>s 2>"$TMPERR"`. **stdout IS the response.**
- **Delete** `gemini_field` (the jq/python JSON parser), `-o json`, and the `-m` model-override section.
  No parsing — the response is the raw stdout text.

### §3 Read-only / anti-hang (replaces `--approval-mode plan`), three layers
1. **Never** pass `--dangerously-skip-permissions` (mirrors the original "never -y/--yolo" rule).
   agy's default is "stop and ask before using a tool", so it will not silently write files.
2. Prefix every prompt with `Analysis only; do not call or use any tools; do not edit files.`
   (Empirically prevents the headless hang; matches the analytical nature of all three modes.)
3. `--print-timeout` + the Bash tool `timeout` as a backstop: if the model still attempts a tool and
   stalls, the timeout kills it and the skill reports `agy stalled — possibly waiting on tool approval`.
- `--sandbox` is left OUT for now (behavior untested; revisit only after verifying it does not break
  reading the piped prompt).

### §4 The three modes
- **Review (2A) / Challenge (2B)**: the diff-inlined prompt + `MODEL_GATE=PASS/FAIL` sentinel is
  unchanged; gate parsing is unchanged (the sentinel is a plain text line, never needed JSON).
- **Consult (2C)**: session-id display is removed; follow-up uses `agy --continue` (resume most
  recent). The `-p` + `--continue` combination is **unverified** — mark it best-effort, do not promise it.

### §5 Lost features (agy print mode does not provide them)
- Remove the `Tokens: <N>` line (no token stats in print mode).
- Remove the `Session: <id>` line (no conversation id in print output).
- **Keep** the gstack hooks (binary-agnostic; they no-op without gstack as before).

## Out of scope (explicitly deferred)
The other four `gemini`-bin call sites are NOT touched in this change:
`kc-pr-flow/scripts/cross-model.sh` (`cross_model_tool_available gemini`),
`kc-pr-flow/skills/kc-pr-review/SKILL.md` §5.6a, `cross-model.test.sh`, and the kc-pr-flow CLAUDE.md
prose. The Gemini-arbitration path is additive, non-blocking, and fail-open, so after 6/18 it simply
goes silent (no broken review). It will be migrated in a follow-up using the pattern proven here.

## Risks / unverified
- `--continue` behavior in `-p` mode is unverified (consult follow-up is best-effort).
- `--sandbox` semantics are unverified (deliberately not used).
- agy headless model identity is opaque (print mode shows no model); we accept whatever `/model` is set to.

## Acceptance
- **Static**: `shellcheck` clean; the `MODEL_GATE` parsing logic unit-tested against mock stdout
  (PASS line present / FAIL line present / sentinel missing → heuristic + warning).
- **Dynamic**: ONE author-authorized live `/gemini review` end-to-end run confirming agy returns a
  review and the gate parses. (Automated agy headless verification is impractical: hang + quota cost.)
