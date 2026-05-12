# Decision Debate — Reference

Detailed templates, prompts, and examples for the decision-debate skill.

---

## Step 1: Frame the Decision

Clearly state:
- **Context**: What problem are we solving?
- **Approaches**: What are the options? (2-4 max)
- **Criteria**: What matters? (performance, maintainability, complexity, etc.)

Example:
```markdown
**Context:** Need to fix Rich Live table flicker in CLI benchmark harness

**Approaches:**
- Approach A: Use `auto_refresh=False` with manual refresh control
- Approach B: Use `screen=True` for full terminal control

**Criteria:** Reliability, code complexity, cross-platform compatibility
```

## Step 2: Dispatch Advocate Agents (Parallel)

Launch advocate agents simultaneously — one per approach:

```
Task: "Advocate for [Approach A]" (Explore agent)
Prompt:
You are advocating for [Approach A] in a technical debate.

**Context:** [problem description]
**Your position:** [Approach A description]

Your task:
1. Search the codebase for relevant patterns, existing implementations, or similar problems solved
2. Find evidence supporting this approach (code examples, documentation, test patterns)
3. Identify 3-5 key advantages with concrete codebase references
4. Acknowledge 1-2 weaknesses honestly (builds credibility)
5. Propose how to mitigate the weaknesses

Return a structured argument:
- **Position Summary** (2-3 sentences)
- **Key Advantages** (with file:line references)
- **Evidence from Codebase** (specific examples)
- **Acknowledged Weaknesses** (honest assessment)
- **Mitigation Strategies**
- **Recommendation Confidence** (high/medium/low)
```

## Step 3: Dispatch Evaluator Agent (After advocates complete)

```
Task: "Staff engineer final recommendation" (Plan agent)
Prompt:
You are a staff engineer making a final recommendation.

**Context:** [problem description]
**Approaches debated:**
- Approach A: [description]
- Approach B: [description]

**Advocate A's argument:**
[paste full argument from Step 2]

**Advocate B's argument:**
[paste full argument from Step 2]

Your task:
1. Evaluate both arguments for:
   - Strength of evidence (codebase references)
   - Completeness of analysis
   - Validity of trade-off assessment
   - Practical implementability
2. Identify any blind spots in either argument
3. Consider additional factors neither mentioned
4. Make a final recommendation with clear reasoning

Return:
- **Argument Analysis** (which advocate made stronger case and why)
- **Blind Spots Identified** (what both missed)
- **Additional Considerations**
- **Final Recommendation** (Approach A/B/hybrid)
- **Implementation Guidance** (how to proceed)
- **Risk Mitigation** (what to watch for)
```

## Step 4: Present to User

Summarize the debate:

```markdown
## Decision Debate Summary

### The Question
[problem context]

### Advocate for Approach A
[condensed argument - 3-5 bullets]

### Advocate for Approach B
[condensed argument - 3-5 bullets]

### Staff Engineer Verdict
**Recommendation:** [Approach X]
**Reasoning:** [2-3 sentences]
**Key factors:**
- [factor 1]
- [factor 2]
- [factor 3]

### Implementation Next Steps
[if user agrees with recommendation]
```

## Agent Dispatch Quick Reference

```typescript
// Step 2: Parallel advocates
Task("Advocate for approach A", subagent_type: "Explore")
Task("Advocate for approach B", subagent_type: "Explore")
// Both run simultaneously

// Step 3: Evaluator (after advocates complete)
Task("Staff engineer evaluation", subagent_type: "Plan")
```

## Full Example

**User says:** "Should we use Redis or in-memory cache for session storage?"

**Claude dispatches:**

1. **Advocate for Redis** (Explore agent)
   - Searches for existing Redis patterns
   - Finds distributed cache examples
   - Returns structured argument

2. **Advocate for In-Memory** (Explore agent)
   - Searches for existing cache implementations
   - Finds performance benchmarks
   - Returns structured argument

3. **Staff Engineer** (Plan agent)
   - Receives both arguments
   - Evaluates against project constraints
   - Returns final recommendation

**Claude presents:** Summary with clear recommendation and reasoning

## Integration with Brainstorming

When using `superpowers:brainstorming` and reaching "Exploring approaches" phase:

1. If approaches are clearly different (e.g., different architectures), offer:
   > "I've identified 2 distinct approaches. Would you like me to run a decision debate to evaluate them thoroughly?"

2. If user agrees, invoke this skill
3. Return to brainstorming with clear recommendation

## Variations

### Quick Debate (2 roles)
For simpler decisions, skip evaluator — just run advocates and summarize yourself:
```
Task("Advocate for A")
Task("Advocate for B")
// Claude synthesizes and recommends
```

### Deep Debate (4+ roles)
For complex decisions, add specialized roles:
```
Task("Advocate for A")
Task("Advocate for B")
Task("Security reviewer")      // Evaluates security implications
Task("Performance analyst")    // Evaluates performance trade-offs
Task("Staff engineer verdict") // Final synthesis
```

### Devil's Advocate
When team is leaning toward one approach, strengthen counter-argument:
```
Task("Devil's advocate against [preferred approach]")
// Specifically argue against the favored option
// Forces consideration of alternatives
```
