---
title: "Teach agents to retain only comments with maintenance value"
status: ideation
source: "Captain-approved independent kc-dev-flow/S3 slice, 2026-08-15; does not alter the existing projection sequence"
product: kc-dev-flow
sprint: S3
started: 2026-08-15T12:03:26Z
completed:
verdict:
worktree:
issue:
pr:
mod-block:
design: required
lane: main
id: hpxks7c1kndqqhhr38kzna6q
---

## Problem

Agents have repeatedly produced code diffs where comments restate more code than they clarify. The portable kernel constrains absolute claims but does not require comments to preserve non-obvious maintenance value, so adopters lack a proportional rule that removes narration while retaining invariants, external constraints, hazards, and rejected alternatives.

This independent S3 slice must prove a behavior change through the installed loader within a 20-minute model-pressure cap, add no new skill, mod, linter, or standing model gate, and leave the existing projection sequence unchanged.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v1
  selected: production
  recommended: production
  basis: "A portable marketplace-released kernel changes long-lived authoring behavior for external adopters; it carries compatibility, release, rollback, and ownership obligations, while this slice changes no executable product behavior or external production state."
  obligations:
    architecture:
      - "Reuse the existing kernel authoring and minimality seam; add no skill, mod, linter, recurring gate, daemon, evaluator, or duplicate policy surface."
      - "Preserve the absolute-claim rule and keep the new comment-retention principle portable across languages and hosts."
    implementation:
      - "Keep canonical and vendored kernel copies byte-identical and record only the minimal independent S3 ROADMAP wording without changing projection sequence."
      - "Keep net always-loaded policy growth at or below roughly 50 words and aim near zero by rewriting existing minimality prose."
    testing:
      - "Run six paired installed-loader responses across three cases, repeating at most one ambiguous pair, within a 20-minute live-model cap."
      - "Require baseline redundant-comment retention at least once and candidate improvement without necessary-comment loss; otherwise report UNKNOWN or no-change."
      - "Run existing contract and release checks and verify no executable-behavior or test regression at the exact candidate revision."
  invariant_sources:
    - "docs/dev/_mods/kernel.md — authority, outcome, minimality, and verification discipline"
    - "docs/dev/README.md — Local Profile, Gate Authority, and state transaction"
    - "docs/dev/_mods/engineering-judgment.md — independent ideation recommendation and retained authority"
  scope_boundary: "No capability-scoped work-control-profile loading, repository-wide comment cleanup, language-specific style rules, RoboRev or PR-review policy change, new skill or mod, linter, recurring gate, daemon, generalized evaluator, or standing model run."
  promote_when:
    - "Re-enter ideation if the change gains executable enforcement, unattended model execution, language-specific policy, or external review-policy ownership."
  decision:
    authority: captain:kent
    at: 2026-08-15T12:03:26Z
```

## Ideation design

### Accepted bounds and criterion normalization

Protected value: agents produce maintainable code without comments that merely
narrate adjacent code, while preserving non-obvious invariants, external
constraints, hazards, and rejected alternatives.

Appetite: one ideation worker and one implementation worker. Behavioral pressure
uses the installed Spacedock loader and one ordinary-cost `gpt-5.6-terra`
high-reasoning worker. The initial experiment is six responses; one ambiguous
pair may be repeated. All live model pressure stops within 20 minutes.

Tolerance: no necessary rationale loss, executable-behavior change, or test
regression. Add no skill, mod, linter, recurring gate, daemon, general evaluator,
or standing model run. Keep net always-loaded policy growth at or below roughly
50 words and aim near zero. Comment volume may trigger review but is not a global
pass/fail ratio.

If cut, retain the existing absolute-claim rule and one portable comment-value
sentence. Explicit non-goals are capability-scoped `work-control-profile`
loading, repository-wide comment cleanup, language-specific style rules, and
RoboRev or PR-review policy changes.

The problem statement's protected value is retained as value. Production
compatibility, the 20-minute envelope, one bounded correction, exact projection
ordering, and the prohibited surfaces are Captain-imposed governing constraints.
The proposed kernel sentence is a mechanism and earns retention only through the
paired behavioral result below.

The assumption most likely to be wrong is that portable prose changes ordinary
agent behavior. A positive result therefore requires the exact baseline to
retain a known redundant comment at least once and the candidate to improve a
paired response without losing required rationale. Otherwise this item returns
`UNKNOWN` or no-change.

### Reverse recovery and subtractive result

Fresh `origin/main@004444c5501fc1ef32c9fe61ea616e8fdc3bc426`
already has the authoring and delivery seams:

- `kc-dev-flow/references/kernel.md:138-163` contains Outcome discipline and the
  absolute-claim authoring rule, including code comments.
- `kc-dev-flow/references/kernel.md:200-207` defines minimum and simple in the
  existing always-loaded minimality paragraph.
- `docs/dev/_mods/kernel.md` and the canonical kernel resolve to the same blob
  `cb0daf615fa642ce20eba7880d7ab6032f20d6a0`; the existing contract test checks
  their byte identity and the absolutes registry. An isolated exact-ref run of
  `scripts/kc-dev-flow-contract-test.py` passed.
- The installed `spacedock 0.26.0 (contract 3)` loader exposes exact stage text,
  and `continue-dev-flow` already requires the complete vendored kernel before
  the active stage and its declared mods.

The seam is `WORKING_UNIT_UNPROVEN / REQUIRED`: packaging, loading instructions,
and parity checks exist, but no bound baseline observation yet proves the stated
comment behavior. Its disproof hook is the exact-ref paired experiment; if the
baseline never retains a known redundant comment, no behavioral gap was
reproduced and the policy change is not earned. This is not a `MISSING`
capability and does not justify a new surface.

The smallest candidate edits the existing minimality paragraph in both
byte-identical kernel copies. Its proposed sentence is:

> Comments preserve non-obvious maintenance value—such as an invariant,
> external constraint, hazard, or rejected alternative—rather than narrate
> adjacent code.

The without-it arm is unmodified `origin/main`; the with-it arm differs by that
sentence and the approved documentation wording. If the without-it arm already
satisfies the behavioral ACs, or the candidate does not improve it, ship no
kernel rule. No fixture, scorer, runner, or model service is retained in the
repository.

### Fastest path and smallest cut

One implementation worker owns one independently releasable value surface:
rewrite the existing kernel paragraph, keep canonical/adopted bytes identical,
apply the minimal PRODUCT and ROADMAP wording, run the disposable paired
experiment, and execute existing release/contract checks. The code-comment
fixtures and outputs live outside the repository and are discarded after their
receipt is recorded.

There is no second slice: policy text and its behavioral proof cannot ship or be
blocked independently. This is docs/config/agent-instruction behavior, so a code
or browser E2E is not applicable; the installed-loader paired run is the real
behavior-producing boundary.

### Paired installed-loader experiment

Materialize the baseline and candidate exact revisions into isolated temporary
snapshots. For each snapshot, record the installed Spacedock version, the loaded
implementation-stage bytes, the complete vendored-kernel bytes, exact revision,
fixture digest, opaque arm ID, response status, and elapsed wall time. Give each
fresh-context `gpt-5.6-terra` high-reasoning response the same ordinary
maintainability task and require executable tokens to remain unchanged; do not
expose the hidden comment classification or the arm identity.

Run these three frozen cases once on each arm, for six initial responses:

1. `R-redundant`: two comments only restate the immediately adjacent operation;
   expected maintenance-value comments: none.
2. `N-necessary`: comments carry an external wire-compatibility constraint and a
   hazard not derivable from the code; both rationales must remain, though
   wording may improve.
3. `M-mixed`: one narration comment and one rejected-alternative rationale; the
   narration should be removed and the rationale retained.

Score the comment-only diff against the frozen rationale rubric and separately
confirm executable-token identity. A scorer uncertainty about semantic
equivalence may repeat both arms of one case once; no other retry is permitted,
so the maximum is eight responses. Start one clock before loader capture, stop
model work at minute 15, and reserve the remaining five minutes for local
scoring and the receipt. Timeout, missing output, changed executable tokens,
unresolved ambiguity after the repeat, or an unaccounted response yields
`UNKNOWN`. Report per-case retained/removed rationale and paired deltas; do not
convert aggregate comment volume into a ratio gate.

### Acceptance criteria

**AC-1 — The portable sentence improves redundant-comment removal in the bounded ordinary-agent baseline.**

Verified by: the six-response paired receipt binds `origin/main`, the exact
candidate revision, installed loader/version, kernel/stage bytes, three fixture
digests, opaque arms, `gpt-5.6-terra` high reasoning, and elapsed time. The
baseline retains at least one rubric-labeled redundant comment and the candidate
removes more redundant narration in at least one matched case without a paired
regression. Falsified by: the baseline never retains redundant narration, the
candidate has no strict paired improvement, any arm identity or hidden rubric
leaks into its prompt, or the run cannot finish honestly inside the response and
time caps; the result is then `UNKNOWN` or no-change.

**AC-2 — Necessary maintenance rationale is preserved with no executable change.**

Verified by: every candidate response for `N-necessary` and `M-mixed` retains
the frozen external-constraint, hazard, and rejected-alternative meanings, and a
token-aware comparison shows identical executable content. Falsified by: any
required meaning disappears, narration is merely rewritten as narration, or any
executable token changes. One semantically ambiguous case may repeat as one pair;
ambiguity after that repeat is `UNKNOWN`, not a pass.

**AC-3 — The shipped policy and documentation remain the smallest recovered surface.**

Verified by: the final diff changes the existing canonical/adopted kernel
paragraph, one PRODUCT sentence, and the independent S3 ROADMAP wording; the
kernel copies remain byte-identical, the existing absolute-claim rule remains,
and always-loaded policy growth stays roughly 50 words or fewer with a
near-zero target. Falsified by: a new skill, mod, linter, recurring gate, daemon,
general evaluator, standing run, capability-scoped work-control load, or an
unexplained additional product surface appears.

**AC-4 — Existing contract, release, authority, and S3 sequence behavior does not regress.**

Verified by: changed-file inspection contains no executable product change;
`scripts/kc-dev-flow-contract-test.py`, `scripts/marketplace-verify.sh`, relevant
release metadata checks, and exact-revision fresh validation pass; ROADMAP keeps
projection items 1 and 2 in the same order. Falsified by: any test failure,
canonical/adopted drift, hand-edited version metadata, executable behavior
change, or projection reorder.

### Proposed documentation diff

- In both kernel copies, add the single proposed comment-value sentence to the
  existing minimum/simple paragraph. Do not add a section or policy file.
- In `PRODUCT.md`, extend the existing `kc-dev-flow` summary with: “Its portable
  authoring discipline keeps comments for non-obvious maintenance value rather
  than adjacent-code narration.”
- In `docs/dev/ROADMAP.md` under `kc-dev-flow/S3`, add: “Independent lane (no
  sequence effect): `comment-retention-discipline` teaches portable
  maintenance-value comment retention and does not gate or reorder projection
  items 1–2.”
- `ARCHITECTURE.md` needs no change because this reuses the existing kernel,
  loader, parity check, release path, and ownership boundaries.

### Test and correction plan

1. Before product edits, capture the exact baseline loader/kernel inputs and run
   the three baseline responses; if none retains redundant narration, stop with
   no-change.
2. Apply only the proposed docs diff, run the three candidate responses, and
   score the frozen rubrics. Repeat at most one ambiguous pair.
3. Run the existing kc-dev-flow contract, marketplace, frontmatter/version, and
   release checks. Record word-count and changed-surface observations without
   turning them into a new standing gate.
4. Fresh validation may authorize at most one bounded correction. Rejection
   after that returns to the Captain; it does not buy another model loop.

### Pre-mortem

If this design ships and agents still produce low-value comments, the likely
cause is that the sentence reads as style advice and loses to local imitation or
task pressure. The paired baseline/candidate result is the disproof instrument:
without a reproduced baseline defect and strict candidate improvement, do not
ship stronger prose or invent enforcement.
