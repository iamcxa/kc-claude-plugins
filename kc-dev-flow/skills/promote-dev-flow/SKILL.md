---
name: promote-dev-flow
description: Use when sanitized field evidence from a kc-dev-flow adopter reaches the plugin source, especially when deciding whether a finding is a portable rule gap, an enforcement gap, a local instance, or a duplicate.
---

# Promote Dev Flow

Perform source-side intake without treating detection as authority. The output is a
reviewable proposal; classification and recurrence do not create work.

## Intake

1. Work from the canonical `kc-dev-flow` source checkout, not an installed cache.
   Recheck the merge target, dirty state, and source work-item authority.
2. Require one or more sanitized `kc-dev-flow-improvement-handoff/v1` files for
   exactly one failure shape. Its producer contract is
   `kc-dev-flow/skills/continue-dev-flow/SKILL.md`.
   Accept a captain-approved file attachment or copied path; never fetch an adopter
   repository or infer upload authority. Run:

   ```bash
   python3 kc-dev-flow/scripts/improvement-intake.py \
     --handoff <first.json> [--handoff <next.json> ...]
   ```

   Treat `captain-review-only` as the authority result. A classification conflict is
   a prompt for source judgment, never a majority vote.
3. Search the current merge target, kernel, policy mods, skills, enforcement scripts,
   and open or closed source work items when that provider is available. Match the
   proposal fingerprint and the failure shape; keyword overlap alone is a sample.
   Treat an observation ID collision with different evidence as a malformed
   handoff, not as duplication or recurrence.
4. Treat `failure_shape` as an adopter-coined label, not a verified merge key.
   Compare evidence before aggregation. For synonymous labels, retain the originals,
   prepare sanitized working copies with one source-chosen canonical label, and
   rerun intake; for one overloaded label covering distinct failures, use separate
   invocations. This normalization is proposal preparation, not policy authority.
   Passing validation is necessary but not proof that all adopter identity was
   removed; re-audit bare domains, company names, relative paths, and unlabeled data.

## Classify Placement

Use `kc-dev-flow/references/reverse-recovery-audit.md`, then choose one
disposition:

| Disposition | Meaning | Destination |
|---|---|---|
| `rule-gap` | A portable semantic obligation is absent. | Kernel proposal. |
| `enforcement-gap` | The rule exists but repeated violations lack a control. | Named plugin or adopter enforcement point; no duplicate clause. |
| `local-instance` | The rule is portable but the topology or mechanism is not. | Return to adopter authority. |
| `duplicate/no-change` | Existing work covers it, or the rule worked as designed. | Merge observations or retain evidence only. |

Record observations, recurrence, expected value, cost, disproof hook, duplicate
search, disposition, target, and the result that would reverse the classification.
The source maintainer decides placement; adopter hints are evidence, not verdicts.

## Captain Gate

Present at most one narrow proposal. **Do not create, schedule, edit, post, or merge**
because intake qualified. Do not pause adopter product work.

After explicit admission:

- `rule-gap`: edit the canonical kernel, propagate accepted vendored copies
  byte-for-byte, classify absolutes, and run the package contract.
- `enforcement-gap`: build the smallest fail-closed mechanism test-first at the
  named surface; do not add kernel wording.
- `local-instance`: return the proposal to the adopter's existing authority.
- `duplicate/no-change`: append distinct evidence only through the authorized
  source work item; do not reset or inflate recurrence.

## Quick Reference

| Signal | Stop condition |
|---|---|
| Unsafe or adopter-specific text | Reject the handoff. |
| Conflicting hints | Require source judgment. |
| Recurrence/source counts | Adopter-reported transport counts; not source-verified. |
| No task authority | Proposal only. |
| Existing rule, repeated escape | Investigate enforcement, not prose. |

## Common Mistakes and Red Flags

- Calling the compatibility label `reusable-kernel` a confirmed kernel placement.
- Counting retries or duplicate observation IDs as recurrence.
- Using one grep as proof that no rule or enforcement point exists.
- Editing both a rule and a mechanism before deciding which gap exists.
- Posting an issue because the proposal renderer returned green.

Any of these returns intake to evidence and classification.
