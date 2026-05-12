---
name: decision-debate
description: "Use when presenting 2+ technical approaches, listing pros/cons, evaluating architecture or technology trade-offs, or when the user asks 'which should I choose'."
---

# Decision Debate - Structured Approach Evaluation

## Overview

Structured debate for technical decisions — eliminates confirmation bias and surfaces blind spots.

**Announce:** "I'm using the decision-debate skill to evaluate these approaches."

**Setup:**
- `Read → ${CLAUDE_PLUGIN_ROOT}/reference/decision-debate-reference.md`
- `Read → ${CLAUDE_PLUGIN_ROOT}/reference/learned-patterns.md` (Debate Patterns section — public, curated)
- `Read → ~/.claude/kc-plugins-config/learned-patterns-local/kc-team-ops.md` (Debate Patterns section — local, raw; optional/may not exist yet)

## Step 0: Triage

Before starting a debate, assess whether one is warranted.

| Signal | Action |
|--------|--------|
| Single clear criterion decides it (e.g., "does it re-render?") | Answer directly — no debate |
| Well-known pattern with consensus best practice | Answer directly, cite the pattern |
| User asks "which should I use" on a trivial choice | Answer directly — debate is overkill |
| User's tool/framework has an opinionated default (e.g., RHF → uncontrolled) | Answer directly, explain the default + edge cases |
| Genuine trade-offs with 2+ weighted criteria | → Step 1 (debate) |
| Architectural decision with long-term consequences | → Step 1 (debate) |
| User says "stress-test", "challenge", "devil's advocate" | → Step 1 with Devil's Advocate variant |

**Rule:** If you can answer confidently in <5 sentences with no trade-off tension, skip the debate. The skill exists for decisions where reasonable engineers disagree, not for knowledge questions.

## Step 1: Frame

State clearly before proceeding:

- **Context**: What problem are we solving?
- **Approaches**: 2-4 options (if user provides only 1, generate the strongest alternative)
- **Criteria**: What matters?

**GATE:** All three elements confirmed before Step 2. Missing criteria or alternatives → ask the user, do not infer.

### Variant Selection

| Variant | Trigger | Process |
|---------|---------|---------|
| **Quick Debate** | 2 approaches, ≤3 criteria, reversible decision | 2 advocates, Main synthesizes (no evaluator) |
| **Standard** | 2-3 approaches, multiple criteria, moderate impact | 2-3 advocates + Staff Engineer evaluator |
| **Deep Debate** | 3+ approaches OR security/perf/compliance implications | Advocates + specialist reviewers + evaluator |
| **Devil's Advocate** | User leans one way ("I'm going with X, but...") | 1 strong contrarian + evaluator (see Devil's Advocate Rules below) |

State the chosen variant and why before dispatching.

### Devil's Advocate Rules

When Devil's Advocate variant is selected:

- **Conviction floor**: Contrarian MUST produce at least 2 arguments with explicit "If this is true, it changes the decision" framing. Going-through-the-motions contrarianism (all points framed as "minor concerns") fails the variant's purpose.
- **Evaluator must address each decision-changing argument individually** — cannot dismiss in aggregate ("valid but team has decided").
- **Evaluator sunk-cost ban**: MUST NOT use "the team already agreed", "the review already happened", or "switching cost of reversing direction" as evaluator reasoning. These are process artifacts, not technical evidence.
- **Strength disclosure**: Evaluator must state "The contrarian case is [weak / moderate / strong / overwhelming]" before giving recommendation.

## Step 2: Advocate (Parallel)

Dispatch one agent per approach — **simultaneously**.

**Agent type:** `feature-dev:code-explorer` or `Plan`. Do NOT use `Explore` (fast search ≠ analytical arguments).

Each advocate prompt MUST include:
1. "Make the **strongest possible case** for your assigned approach"
2. "Search codebase for specific evidence — file paths, code patterns, dependency counts"
3. "Acknowledge 2+ genuine weaknesses (not strawmen)"
4. "If no codebase evidence exists, explicitly state this and ground argument in what would need to change"

### Evidence Standard

Each advocate must return: Position Summary, Key Advantages (min 3 `file:line` citations — code observations, not name-drops), Acknowledged Weaknesses (min 2 genuine), Mitigation Strategies, Evidence Depth self-rating: `strong` (5+), `moderate` (3-4), `speculative` (≤2).

### Anti-Bias Rules

- **Equal conviction** regardless of user's stated preference
- **Same depth of instruction** for both advocates
- Zero codebase presence → flag as "speculative — no existing code supports it"

## Step 3: Evaluate (Sequential)

Dispatch **after** all advocates complete. Agent type: `Plan`.

The Staff Engineer evaluator MUST:

1. **Grade evidence depth** — Did advocates analyze code behavior or merely name-drop file paths?
2. **Check structural parity** — Did both sides receive equal analytical effort?
3. **Challenge the premise** — Is the framing correct? Is there a third option neither advocate considered? Is the question itself wrong?
4. **Score against criteria** — Rate each approach against each criterion from Step 1
5. **Produce recommendation** with confidence level (high/medium/low)

Return: Argument Analysis, Blind Spots, Premise Challenge, Criteria Scoring, Recommendation, Implementation Guidance.

## Step 4: Present

Summarize using the output template in the reference file. Include: variant used, each advocate's condensed argument with evidence depth, verdict with confidence + premise challenge, and next steps.

## Integration with Brainstorming

When `superpowers:brainstorming` reaches "Exploring approaches" with 2+ distinct approaches where reasonable engineers would disagree, offer to run a decision debate.

## Learning (D1)

After completing a debate, scan for hard signals:

| Signal | Source |
|--------|--------|
| Triage misjudged complexity (debated trivial / skipped genuine) | Triage table gap |
| Advocate produced speculative argument despite existing evidence | Evidence standard weakness |
| Evaluator used sunk-cost reasoning despite ban | Anti-bias gap |
| Same debate pattern seen 2+ times across projects | Recurring decision archetype |

Hard signals → check against LOCAL `~/.claude/kc-plugins-config/learned-patterns-local/kc-team-ops.md` Debate Patterns section → append if not covered. Notify user: "Appended to LOCAL kc-team-ops.md. Promote via `/kc-plugin-forge dreaming kc-team-ops` when generalizable." No hard signals → done. "Nothing novel" is valid — do not create filler entries.

**Do NOT write directly to** `${CLAUDE_PLUGIN_ROOT}/reference/learned-patterns.md` — that file is curated-only, entered via early-stage Dreaming.

## Reference

Full prompt templates and examples: [decision-debate-reference.md](${CLAUDE_PLUGIN_ROOT}/reference/decision-debate-reference.md)
