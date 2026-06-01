# EM Plan Review — Lens Rubric

Full rubric for `kc-em-plan-review`. The SKILL.md carries a compact checklist; this file is the depth. **Source of truth for the lenses is the user's current `~/.claude/CLAUDE.md`** (Conviction Calibration, Escalation Mantra, E2E-First Acceptance) — re-read it; this file operationalizes those into review probes. For triage-depth routing (how deep to triage a single issue) see `strategic-lens.md` — different purpose, complementary.

## The prime directive

A review's value is not "did it list correct risks" — it is "did it change the outcome." Advice transfers the work of deciding + verifying back onto the busiest person. Aim to **remove** uncertainty, not add homework:

- Convert the load-bearing assumption from inherited → verified (see P2). Disclosing a risk and stopping is analysis, not engineering — go verify the keystone.
- Collapse to the **one** blocking decision; mark the rest "post-event / non-blocking."
- Ship every suggestion with a **reversible default** + escape hatch ("Default: X. If you've already done Y, ignore this.").
- Attach **owner + deadline** to each risk — free-floating risk is just anxiety.
- Hand over a **go/no-go checklist** the team can run without you in the loop.

## Lenses (probes)

### 1. Idiot Index / Loss Function Audit
- What does the user actually see/experience? Is the **visible payload** prioritized, or buried in "polish / non-blocking" while invisible plumbing is "Urgent"?
- Ratio of ceremonial work (enforcement that's deliberately not enforced, scaffolding) to user-visible progress.
- **Sequence by what's on stage.** For a demo, order by what's in front of the audience.

### 2. Bad-news-early (Escalation Mantra)
- Is the **riskiest, least-controlled** thing (3rd-party behavior, unverified integration, new-user path) validated FIRST or LAST? If last → pull it to a day-0 throwaway spike.
- Buffer between the last milestone and the hard deadline? Zero buffer is a hope, not a plan.
- Bus-factor: everything on one person over a weekend? Who signs off, and when?
- Is there an explicit go/no-go checkpoint, or does it just "land on the day"?

### 3. E2E-first acceptance
- Is "done" defined as a **human end-to-end loop** (real device, real data, real network), or just unit ACs?
- The real acceptance criterion is usually a human action the plan does not list. Name it, and make it a task.

### 4. break-point-probe (unit-green ≠ runtime-verified)
- Which findings are verified at the **runtime path** vs only at unit-test level?
- Agent/CI goes green on the exact path where the real integration can still silently break — flag that gap.

### 5. Conviction-calibration
- Named "MVP / spike" but the foundation is quietly a platform (new domain, enforcement, migrations)? Name the gap between stated appetite and actual surface area.
- Absolutist language ("must", "一定") without a loss-function audit.

## Output structure
1. **One-line verdict** up front.
2. **Successful designs** — genuine and specific, not filler praise.
3. **Likely failure points** — ranked 🔴🟠🟡 by impact on the goal. Each: trigger evidence → why it bites → fix.
4. **Concrete actionable recommendations** — time-phased (now / before-build / pre-ship), each with a default.

## Severity calibration
- 🔴 = blocks the goal / silent-fail on the main path. 🟠 = real risk with a workaround. 🟡 = judgment call.
- **Don't cry wolf.** Overstating burns your one escalation. If P2 verification lowers a risk, downgrade it openly and say why.
- Distinguish **load-bearing details** (authz, tenant scoping, credit/billing state, migrations, new-user empty states, idempotency) from cosmetic ones. "Post-completion is just details" is false — the expensive bugs live in the details.
