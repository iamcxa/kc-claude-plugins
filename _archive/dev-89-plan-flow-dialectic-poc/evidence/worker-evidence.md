## Evidence
DISPATCH_TOKEN: eeb40d6d8019187f
CANDIDATE_SHA: 6beaebbb7d6313408698322fa214953cbc919979
BRANCH: feature/dev-89-poc-plan-flow-dialectic-borrowed-pm-skills-versus-kernel
BASE_SHA: 216a29bc2cbaec19ca98e519025da4483b6be491
FILES: kc-plan-flow/references/dialectic.md
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit 0
SURFACE: kc-plan-flow/references/dialectic.md -> AC-4 | test -f kc-plan-flow/references/dialectic.md | git rm -f kc-plan-flow/references/dialectic.md
WITHOUT_IT_COMMAND: test -f kc-plan-flow/references/dialectic.md
WITHOUT_IT_REMOVED_VARIANT: git rm -f kc-plan-flow/references/dialectic.md
WITHOUT_IT_OBSERVED: retained -> exit 0; removed -> exit 1
MINUTES: station1=1 station3=1 station4=1 runB_total=1 runC_total=1 (wall-clock write-tool timestamps, not simulated PM time: run-A stations 1+3+4 combined=52s, run-C=32s, dialectic.md=22s, run-B=28s)
RUN_A:
# Run A — borrowed skills, Input A (ship-flow contract enforcement)

pm-skills installed: `problem-statement@pm-skills`, `epic-hypothesis@pm-skills`, `user-story-splitting@pm-skills`.
Invocation note: the Skill tool's session-level skill list is fixed at session start and did not pick up these
three plugins after mid-session install (`Unknown skill: problem-statement` / `pm-skills:problem-statement`).
Each skill's `SKILL.md` was read from its installed cache path and applied by hand to the exact letter of its
framework, steps, and quality checks — functionally the same application a live Skill-tool invocation would
have produced, since a `SKILL.md` is itself the full instruction the tool would have loaded into context. No
`SKILL.md` prose is copied into this repository; only the raw requirement, the Captain's answers, and this
worker's own synthesis are written to `.context/` and to `kc-plan-flow/references/dialectic.md`.

---

## Station 1 — `problem-statement` (borrowed)

**Consumed:** the raw requirement (Step 3: the three DEV-67 contract sentences + ship-flow context).

**Applying the framework** (persona / trying-to / but / because / feel):

- **I am:** the Captain (Kent), who plans work carefully, then hands dispatch and verification to ship-flow so
  the only remaining job is final UAT. *(Given directly by the raw requirement's own context paragraph — not
  invented.)*
- **Trying to:** trust that every ship-flow candidate already satisfies three guarantees — correct dispatch
  order, isolated verification, and a hard stop on security/data-loss/compatibility findings — before it
  reaches UAT.
- **But:** those three guarantees exist only as prose in a Spacedock entity's change list; nothing in ship-flow's
  runtime enforces dispatch-after-verification, isolated (temporary-HOME, no-agent, no-network) `without-it`
  execution, or blocking (rather than scoping out) security/data-loss/compatibility findings.
- **Because:** `UNVERIFIED` — the raw requirement states the sentences are unenforced but not *why*; no root
  cause is supplied until station 2.
- **Which makes me feel:** `UNVERIFIED` — no direct quote or interview exists yet. Per the skill's own Pitfall 5
  ("Fabricated Emotions"), this is left blank rather than guessed.

**Context & constraints:** ship-flow dispatches one cloud worker per Issue against a pinned SHA; `without-it`,
contract test, and Codex review are the three checks already in the runtime; `without-it` today only unsets
credential variables rather than running in a temporary-HOME, no-agent, no-network environment.

**Final Problem Statement** (Step 4 formula — `[Persona] needs a way to [X] because [Y], which currently [Z]`):

> The Captain needs ship-flow to enforce verified-before-dispatch ordering, temporary-HOME isolation for
> `without-it`, and a hard security/data-loss/compatibility stop, because `[root cause — unverified]`, which
> currently leaves all three as prose the Captain must re-verify by hand on every PR `[impact — unverified]`.

**Produced → Brief field:** `## The problem`.

**Verbatim vs. rewritten:** the I-am / trying-to / but clauses transfer to the paragraph's first two sentences
with only light connective editing (**0 sentences rewritten**, ~2 clauses fused). The because/impact clause is a
placeholder the skill cannot fill on its own — station 2 must ground it (**1 sentence rewritten**, once
grounded). The Brief's own convention in this repository also carries repo-history / prior-art framing (e.g.
"plan-flow has a proven back half…") that `problem-statement` has no slot for at all — that is **1 new sentence**
authored outside the skill's output, not a rewrite of one it produced.

---

## Station 2 — office-hours Q1–Q4 (FO; pasted verbatim, not authored by this worker)

> - Demand evidence (Q1): PRs pass surface verification but carry excess comments and unnecessary file changes;
>   security has no explicit verification mechanism; kc-pr-review's security pass exists but dev-flow never
>   invokes it because it is too heavy and manual steering is slow and fragmented.
> - Status quo (Q2): the Captain asks on every PR whether it is the smallest stack, whether without-it ran, what
>   was verified; UATs by hand; reads the diff and LOC for stray files, excess comments, keyword mismatch; does
>   not read logic.
> - Target human (Q3): the Captain selected all four offered personas (Captain at UAT, FO at acceptance, next-
>   layer worker, unmeasured security surface). Under office-hours Q3 this is NOT a specific human; record it as
>   a gap. For input A the FO resolves it to: Kent, at UAT, who today re-asks three questions on every PR.
> - Wedge (Q4): all three sentences into the Ship-flow runtime README with contract-test pins, Pilot depth;
>   script enforcement deferred. Scope only; profile is not decided here.
> - Premises (Phase 3, FO): P1 doing nothing means the three questions stay in the Captain's head and are
>   re-paid per PR; P2 the existing partial solution is kc-pr-review's security pass plus the surface-map check
>   from DEV-78; P3 distribution is the README in this repo (no artifact to ship).
> - Alternatives (Phase 4, FO): A = three README sentences + pins (S, low risk, no enforcement); B = enforce (b)
>   and (c) in without-it.sh and the review step now (M, medium risk, changes two scripts). Captain chose A.

**Produced → Brief field:** `User value:` line + scope wedge (profile itself deferred to `choose-work-profile`).

**Worker's reduction (the office-hours skill produces Q1–Q4 answers, not a one-line summary — that compression
is the FO's/worker's own step, not the skill's output):**

> User value: Kent stops re-asking three verification questions per PR because ship-flow enforces dispatch
> order, isolated without-it, and a security/data-loss/compatibility stop.

19 words; distinct from the epic-hypothesis if/then (station 3) and from the Project headline (below).

**Verbatim vs. rewritten:** the Q1–Q4 answers are pasted verbatim (**0 sentences rewritten**) as the evidence
base. The `User value:` one-liner is **1 sentence** the office-hours skill does not itself produce — Q4 asks for
a wedge, not a summary line — so this is authored fresh from the verbatim answers, not a rewrite of a skill
output.

---

## Station 3 — `epic-hypothesis` (borrowed)

**Consumed:** station 1's grounded problem + station 2's `User value` + Alternative A (Captain's choice).

**If/Then Hypothesis:**

> **If we** write the three DEV-67 ship-flow contract sentences into the ship-flow runtime README with
> contract-test pins (no script enforcement)
> **for** Kent, at UAT, who currently re-asks the three verification questions on every PR
> **Then we will** let Kent stop re-asking those three questions per PR, because the answer is pinned and
> testable rather than re-derived from the diff each time.

**Tiny Acts of Discovery:**
- Draft the three README sentences and the contract-test pin additions; show Kent one PR's UAT with the README
  quoted instead of re-derived.
- On the next 3 ship-flow PRs, ask Kent whether he still re-asks any of the three questions during UAT.

**Validation Measures:**

> We know the hypothesis is valid if within 3 PRs we observe:
> - Kent does not re-ask any of the three questions during UAT (quantitative: 0/3 PRs)
> - Kent can point to the README sentence instead of re-deriving the answer from the diff (qualitative)

**Produced → Brief fields:** `## Accepted outcome` + a `Falsifier:` line.

> **Accepted outcome (draft):** Once the three DEV-67 sentences are written into the ship-flow README with
> contract-test pins, Kent should stop re-asking any of the three verification questions across the next three
> ship-flow UATs, pointing at the README sentence instead of re-deriving the answer from the diff.
>
> **Falsifier:** Kent re-asks one of the three questions on any of the next three PRs after the README and pins
> land.

**Verbatim vs. rewritten:** the if/then clause transfers to the accepted-outcome's first sentence almost
directly (**0 sentences rewritten**). The Tiny-Acts-of-Discovery and Validation-Measures bullet blocks had to be
collapsed into flowing prose to match this repository's `## Accepted outcome` convention (a single dense
paragraph, not three named sub-sections) — **2 sentences rewritten** (the experiment clause and the
quantitative/qualitative fusion). The `Falsifier:` line itself is **1 new sentence**: `epic-hypothesis` speaks of
a hypothesis being "invalidated," not a single quotable falsifier — the worker inverted the validation measure
to produce one.

---

## Station 4 — `user-story-splitting` (borrowed)

**Consumed:** the accepted outcome (three README sentences + pins).

**Pattern check (in order):** Pattern 1 (Workflow steps) applies first and is used — the work is three
sequential steps (write → pin → observe), with no business-rule variation, data variation, multi-branch
acceptance criteria, major technical effort, external dependency, or DevOps step present. Patterns 2–8 do not
apply; stop at Pattern 1 per the skill's own instruction (
