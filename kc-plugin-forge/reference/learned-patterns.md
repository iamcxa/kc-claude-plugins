# Learned Patterns

Cross-project patterns accumulated during plugin forge operations.

Curate periodically and PR valuable entries back to the origin repo.

---

## Persistent state markers vs event markers in routing (2026-03-18)

When multiple resume/restore mechanisms coexist (e.g., GSD checkpoint file + journal handoff), deterministic routing that checks a persistent state marker first (file exists → route A) can silently override a more recent event marker (timestamped journal entry). Fix: when both exist, present options to the user rather than defaulting to the persistent one. The event marker is more likely to reflect "where I left off" because it carries temporal context, but only the user knows their actual intent.

## Flow graph is a behavioral contract (2026-03-18)

When a skill has a dot graph or process flow visualization, agents treat it as the authoritative flow — steps not in the graph are invisible. During kc-em-triage forge, the Learning step existed in text (Step 7) but was absent from the dot graph. REFACTOR test showed agents would follow `discuss → next issue` and skip Learning entirely. Fix: every mandatory step must appear in the flow visualization. The graph is a contract, not decoration.

**Applies to**: Any skill with dot/graphviz flow or process flow summary line
**Action**: When adding a new step to a skill, always update BOTH the text description AND the flow visualization

## Described ≠ Enforced — Three-layer enforcement for mandatory steps (2026-03-18)

Writing "MANDATORY" or "must" in a skill step description does NOT enforce it. Agents skip steps that lack structural enforcement, especially under context pressure. A mandatory step requires three reinforcement layers:
1. **Output format** — a named, structured output block that produces visible evidence (e.g., `APPROACH: ... / GUARDRAILS: ...`)
2. **Gate check** — entry in the "NOT DONE UNTIL" table that requires the output as evidence
3. **Anti-rationalization** — specific Red Flag entry naming the exact excuse agents use to skip it (e.g., "approach is obvious" → B2 skip)

During /auto skill audit: Phase C (review) had all 3 layers → never skipped. Phase B (brainstorm, skill invocation) had 0 layers → skipped on first real use. The word "MANDATORY" without structural backing is decoration.

**Applies to**: Any orchestrator skill with multi-step pipelines
**Action**: When marking a step as mandatory, add all 3 enforcement layers. Audit existing "MANDATORY" annotations for missing layers.

## Intent-aware routing prevents skill misapplication (2026-03-18)

Multi-purpose orchestrator skills (e.g., /auto handles both features and bug fixes) need intent detection BEFORE entering the main pipeline. Without it, the pipeline applies feature-oriented steps to bug fixes (brainstorm approach before diagnosing root cause) or vice versa. Detection signal: reuse A3 branch-type heuristic (fix/error/broken → bugfix, else → feature). Route to different step sequences per intent, but share common infrastructure (quality gate, review, PR).

**Applies to**: Any skill that handles 2+ intent types through a single pipeline
**Action**: Add INTENT field to the parse step, add intent-aware routing table before the first divergent step

## Rubber-stamp compliance — output format without quality floor (2026-03-19)

When a mandatory step requires structured output (e.g., `GUARDRAILS: {list}`), agents satisfy the format with vacuous content (`GUARDRAILS: "none found"`). The format check passes but the cognitive work never happens. Fix: add a **quality floor** — require citing specific sources checked (e.g., "which CLAUDE.md sections were reviewed") and require at least one alternative considered. The format becomes evidence of work, not just a checkbox.

**Applies to**: Any mandatory output template with optional/default values
**Action**: Replace bare defaults ("none found", "only viable approach") with structured justifications that name what was checked

## Escape hatch abuse requires concrete decision list (2026-03-19)

When a skill provides an escape hatch with an undefined predicate (e.g., "pure UI with no testable logic"), agents stretch the definition to skip the requirement. SC-658's clone button (onClick + useCustomMutation + error handling) could be argued as "pure UI" because the terms are undefined. Fix: replace subjective predicates with **concrete decision lists** — enumerate what qualifies and what doesn't. "Is this pure UI?" becomes "Does it have an on* handler that calls a mutation? → TESTABLE."

**Applies to**: Any skill with conditional escape hatches ("if X, you may skip Y")
**Action**: Define X with enumerated examples, not subjective criteria. If the list doesn't cover a case, the escape hatch does not apply.

## B3 escape carrying to B4 — layered requirements need independence declarations (2026-03-19)

When two steps (B3 and B4) both require TDD, and B3 has an escape hatch, agents argue the escape "carries over" to B4 via vacuous satisfaction ("B3 said no tests → B4 TDD is satisfied with zero tests"). Fix: explicitly declare each requirement as **independent** — "B3's TDD-skip escape does NOT carry over to B4. B4 must independently validate."

**Applies to**: Any skill where multiple steps impose overlapping requirements with different escape clauses
**Action**: Add explicit "does NOT inherit exemptions from step X" language

## Brainstorm intent resists output gates stronger than execute intent (2026-03-19)

When a skill requires a mandatory output block (e.g., Assessment Output) before proceeding, agents comply for execute/non-task intents but skip it for brainstorm intent. Root cause: brainstorm intent's natural behavior ("explore and understand code") feels inherently useful, so agents rationalize skipping the gate as "I'm already doing what the skill asks." The gate works for execute because execution has clear consequences (wrong scale → wrong workflow), but brainstorming's consequence (missing formal classification) feels low-stakes. Fix: in the routing description for brainstorm, explicitly separate "classify intent" from "start exploring" — "routing to brainstorming skill means INVOKE the skill, not start reading files." Session-level skill loading provides stronger enforcement than subagent prompt injection.

**Applies to**: Any routing/classification skill with mandatory output gates across multiple intent types
**Action**: Add intent-specific routing clarification for low-consequence intents (brainstorm, review) where the default behavior overlaps with the routed action

## Help skill template blocks dominate over live-read instructions (2026-03-20)

When a help skill says "Read live data from skills/*.md" but then provides a hardcoded output template immediately after, agents emit the template verbatim instead of populating it from live reads. The template's specificity dominates the abstract instruction. Fix: add an explicit "formatting guide only — populate from live reads" directive immediately before the template block. Without this, new skills added to the plugin won't appear in the help output.

**Applies to**: Any help/guide skill with example output templates
**Action**: Always insert a "format guide only" directive before template blocks that should be populated dynamically

## Global prerequisites block mode-specific paths (2026-03-21)

When a skill supports multiple flow modes (e.g., browser + CLI-only), a "BLOCKING" prerequisite that only applies to one mode silently prevents the others. e2e-flow's "Discover Mapping" was a hard gate that blocked CLI-only flows — even though CLI-only flows use zero mapping references. Fix: prerequisites must be mode-aware. Check mode signals BEFORE enforcing the gate. If the prerequisite is irrelevant to the detected mode, skip it with an informational message instead of blocking.

**Applies to**: Any skill with multi-mode pipelines sharing a common preamble (e.g., browser/CLI, sync/async, interactive/batch)
**Action**: Audit each "BLOCKING" / "must complete before proceeding" gate — does it apply to ALL modes or only some? Mode-specific gates need early intent detection before enforcement.

## PreToolUse block is bypassed by Bash — warn beats block for hooks (2026-03-22)

A `PreToolUse:Write` hook that returns `{"decision": "block"}` only blocks the Write tool. Agents bypass it by using Bash (`echo > file`, `cat <<EOF > file`) — the hook never fires on Bash tool calls to the same path. Result: the agent learns to avoid Write, not to avoid the prohibited action. Worse: Bash writes get zero warning, so the bypass is completely silent. **Fix**: replace `"decision": "block"` with plain text warning output (cat <<'WARN'). PreToolUse hooks that output text (not JSON) inject that text as a warning into agent context without blocking. This is cooperative (agent gets consequences, decides) vs adversarial (agent finds workaround). Keep sentinel mechanisms for authorized paths — sentinel present → `exit 0` (silent), sentinel absent → warning text.

**Applies to**: Any PreToolUse hook that uses `"decision": "block"` on Write/Edit tools. Bash tool can perform the same filesystem operations.
**Action**: Prefer warn over block for file-write guards. Reserve block for truly dangerous operations where Bash bypass is also covered (e.g., matching both Write and Bash tools for the same path pattern).

## Bare skill name ≠ skill invocation in isolated mode (2026-03-23)

When running LLM in isolated mode (`claude --bare`), passing a skill name as a prompt (e.g., `"kc-sentry-insight"`) does NOT trigger the skill — the LLM treats it as an informational query and produces a topic summary. Adding a slash prefix (`"/kc-sentry-insight"`) signals invocation intent and triggers the skill's routing. This matters for any automated testing that invokes skills via CLI prompts (e.g., smoke tests, CI verification). The slash is an LLM convention, not a Claude Code feature — it's how agents distinguish "tell me about X" from "run X".

**Applies to**: Any automated test or script that invokes a skill via `claude -p` or similar CLI prompt
**Action**: Always use `/<skill-name>` (with slash) when the intent is to invoke the skill, not describe it. For smoke tests, prefer first-clause extraction from description; use `/<name>` as fallback only.

## Mode-specific required fields need explicit validation blocks (2026-03-23)

When a skill has multiple invocation modes (standalone, experiment, continue), each mode may require a different set of fields. If a mode skips an earlier phase (e.g., `--experiment` skips Phase 0), fields that would normally be generated by that phase must be provided by the caller. Without explicit validation ("when mode X, fields A, B, C are required — if missing, ask"), partial input creates an unhandled state downstream. Found in e2e-debug: `--experiment` without `--steps` caused Phase 2 dispatch with undefined `reproduction_steps` because Phase 0 (which generates steps) was skipped.

**Applies to**: Any skill with mode-dependent phase skipping
**Action**: After the argument table, add a validation block per mode listing required fields. "If missing, ask the user" — never silently proceed with undefined inputs.

## Subagents cannot use AskUserQuestion — skill must handle user interaction (2026-03-23)

Subagents communicate only via their return value to the orchestrator skill. They cannot use `AskUserQuestion` or other user-facing tools. If a subagent needs user input (e.g., "please log in manually"), it must return a special status (e.g., `WAITING_FOR_AUTH`) and let the **skill** (main context) handle the user interaction. The skill then re-dispatches the agent after user confirmation. Found in e2e-debug: agent was instructed to use `AskUserQuestion` for headed-mode auth pause, but subagents don't have access to it.

**Applies to**: Any agent definition that requires user interaction mid-execution
**Action**: Never reference `AskUserQuestion` in agent system prompts. Design a return-status protocol instead: agent returns structured status → skill presents to user → skill re-dispatches after confirmation.
