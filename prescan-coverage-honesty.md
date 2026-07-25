---
title: Eleven pre-scans report nothing, so a skipped scan reads like a clean one
status: backlog
source: agent-native audit of the kc-pr-review kit, 2026-07-26; sprint slice 1 of 2, planned with a cross-vendor (agy) pass
started:
completed:
verdict:
worktree:
issue:
pr:
design:
id: 2tpagghhkaqzfkq4wvs7f1nh
---

Step 4.5 of `kc-pr-review` runs eleven mechanical pre-scans — `4.5a` CLAUDE.md rule
compliance, `4.5b` stale reference detection, `4.5c` dependency chain validation, `4.5d`
prompt consistency, `4.5e` runtime data shape, `4.5f` lint gate, `4.5g` non-code file scan,
`4.5h` dead export detection, `4.5i` helper rollout completeness, `4.5j` cross-file doc claim
verification, `4.5k` intra-doc rule-vs-example consistency (`skills/kc-pr-review/SKILL.md:468-728`).
Every one is a prose instruction to grep. None invokes a script, and none reports whether it
ran. **A review that ran a pre-scan and found nothing is indistinguishable from one that
skipped it.**

This is the repo's recurring defect class, not a new one: a guarantee stated in prose while
the enforcement point checks something weaker. Slice 1 of the daemon arc found a posting
validator that lived only in skill prose; the same round found a 56-assertion test group that
had never run in CI while appearing covered.

## The machinery already exists and is closed — this is wiring, not invention

The typed runtime's capability policy is closed and tested. Each capability is required or
optional and terminates in exactly one of `clean`, `findings`, `evidence_backed_na`,
`incomplete_required`, `incomplete_optional`; required gaps forbid approval and cap the event
at COMMENT (`reference/review-runtime.md:127`).

Not one pre-scan is modelled in it. Verified by grep: `4.5`, `prescan`, and `pre-scan` appear
**zero** times in `reference/review-runtime.md` and `scripts/review-runtime.sh`.

Two properties were verified against the implementation during planning, and both make this
cheaper than it looks:

- **Absence is already an error, not a silent pass.** `scripts/review-runtime.sh:2073` asserts
  `($p.review_config.capabilities - [$obligations[].capability]) | length == 0`, and `:1979`
  emits `capability_policy_config_mismatch` when it fails. So a capability declared in the
  config but never reported cannot vanish quietly — it invalidates the typed decision, which
  `SKILL.md:1256-1260` already routes to a `typed-runtime-invalid` gap and a COMMENT ceiling.
  A run that dies halfway through Step 4.5 therefore cannot reach APPROVE.
- **Conditional applicability needs no schema change.** A pre-scan that genuinely does not
  apply (the non-code file scan on a code-only diff) terminates `evidence_backed_na`, which is
  not counted in `capability_gap_refs` and therefore passes. The closed schema stays closed.

## Honest boundary — state it in the docs, do not overclaim

The terminal state is still authored by the same agent that ran (or skipped) the scan. This
slice converts a **silent skip** into a **visible gap**. It does not make a report of `clean`
trustworthy. It defends against omission, truncation, and budget-drift — the realistic
failure — not against an agent that fabricates a terminal. Script-produced evidence for the
mechanically decidable subset (`4.5f` lint, `4.5h` dead export, `4.5b` stale reference) is a
separate later slice; do not let the documentation here read as if it had already landed.

**Decide the evidence payload shape now even though this slice fills it agent-side.** The
cross-vendor pass made the case that a terminal carrying structured execution evidence (the
pattern searched, files inspected, matches found) is materially harder to fabricate coherently
than a bare `clean`. Adding that later would mean a second bump of a closed schema, so the
shape is an ideation decision here even if the values are agent-authored until the script tier
lands.

## Acceptance criteria

**AC-1 — A review that does not report a terminal for a required Step 4.5 pre-scan cannot reach APPROVE.**
Verified by: driving the decision projection with one pre-scan terminal withheld, asserting
`coverage == "incomplete"`, the capability named in `capability_gap_refs`, and
`effective_event == "COMMENT"`; and separately with the obligation omitted entirely, asserting
`capability_policy_config_mismatch`. Falsified by: APPROVE surviving either case.

**AC-2 — A pre-scan that does not apply to the diff passes without being a gap, and says why.**
Verified by: a not-applicable pre-scan terminating `evidence_backed_na` with its reason, the
decision still reaching `coverage == "complete"`. Falsified by: a not-applicable scan forced to
either block approval or masquerade as `clean`.

**AC-3 — The per-pre-scan terminals are visible to the human at the confirmation gate.**
Verified by: the rendered §6c output distinguishing ran-and-clean, not-applicable, and
not-run for each of the eleven. Falsified by: gate output from which a reader cannot tell
which scans actually executed.

## Out of scope

Script-produced evidence for any pre-scan (later slice). Any change to what the pre-scans
look for. The learned-pattern corpus (sprint slice 2). The daemon authorization arc
(`vf`, `x0`).

## Notes for the implementing session

Re-measure the suite baseline first — main has moved past the 920/0 recorded on 2026-07-26
(#60 and #61 landed since). Lint with CI's pinned ShellCheck v0.9.0, never the local build;
both parity commands are in `kc-pr-flow/CLAUDE.md`. Changes inside
`# typed-interactive-recipe:start/end` in `skills/kc-pr-review/SKILL.md` are extracted and
sourced by `review-shadow.test.sh`, so that prose is tested implementation.
