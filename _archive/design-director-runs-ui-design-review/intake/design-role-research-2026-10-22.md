# Design review role research, 2026-10-22

Read-only research dispatched by FO (general-purpose, sonnet). Condensed by FO; "search summary" marks claims the researcher did not read in the primary source.

1. Shipped design skills are persona plus checklist, with no duty after the finding: Anthropic frontend-design ("Approach this as the design lead at a design studio…"), https://raw.githubusercontent.com/anthropics/skills/main/skills/frontend-design/SKILL.md; Vercel web-design-guidelines ("Review files for compliance with Web Interface Guidelines"), https://raw.githubusercontent.com/vercel-labs/agent-skills/main/skills/web-design-guidelines/SKILL.md.
2. Local gstack skills (~/.claude/skills/plan-design-review, design-review, design-consultation) use "senior product designer" framing; two say "The user decides"; design-review fixes its own findings, so it has no author/reviewer split.
3. In human critique the critic has no final say: "The only way the design can change is if the design owner does it" (https://articles.centercentre.com/?p=173). No source found on who wins when a design director and designer disagree.
4. Nielsen's severity scale ties low severity to inaction (1: "need not be fixed unless extra time is available") and warns "severity ratings from a single evaluator are too unreliable to be trusted" (https://www.nngroup.com/articles/how-to-rate-the-severity-of-usability-problems/). No study found measuring how often low-severity findings are dropped.
5. Design review (during design) and design QA (on the built result) are two stages (https://product.hubspot.com/blog/avoid-design-debt-with-better-design-qa); whether one person or agent should do both is not shown.
6. LLM critique from static screenshots is thin and mixed: UICrit (https://arxiv.org/abs/2407.08850) says LLMs "do not yet match" human evaluators; a GPT-4 Figma study (https://arxiv.org/abs/2403.13139) reports feedback getting less useful over iterations; a GPT-4o heuristic study (https://arxiv.org/abs/2506.16345, search summary) reports 21.2% of expert-found issues.
7. No published evidence that persona or role wording changes which issues a reviewer notices; studies measure answer accuracy (https://arxiv.org/abs/2512.05858: expert personas did not significantly improve accuracy; arXiv 2603.18507, search summary). The in-house 2026-08-21 role test (Chief of Staff framing found an unclaimed decision the engineering roles did not) is not contradicted and not backed.
8. kc-dev-flow-2 chief-engineer and engineering-reviewer are worded by duty and hold no gate; design-review.md is a dimension list plus MAJOR/MINOR.

Three duty wordings offered by the researcher:
- A. Owns coherence with the host product: name every departure from the host's components and who decides it. Attends to the 37 of 70 "host component" declines; misses states, flow, size, running-app problems.
- B. Owns the open design decisions (Chief of Staff framing): every finding is settled by a named fix or criterion, or becomes a decision with an owner; no decline closes without its reason checked against the picture. The only wording that touches the measured loss point; may attend less to new visual problems.
- C. Owns the user's first minute in two passes: pictures now, built screen later, with what only the running screen can settle handed to the later pass. Matches the two-stage practice; needs a separate severity rule.
The researcher would not claim any wording changes what the reviewer sees without a replay on the 10 already-raised findings.
