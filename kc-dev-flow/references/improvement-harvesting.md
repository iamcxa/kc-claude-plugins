# Explicit Improvement Harvesting

Load this reference only after `continue-dev-flow` resolves the product route and
the current invocation explicitly asks to harvest unseen debrief evidence or
prepare a dev-flow improvement. After the procedure, resume the already-resolved
product route.

## Consume debrief evidence once

Resolve one authoritative `_debriefs/` home through execution-state authority.
If no debrief home is bound, treat that as no unseen debrief: perform no analysis,
write no improvement state, and continue to product routing. If multiple
candidates remain, stop with `UNKNOWN`, name the ambiguity, and require
adoption/refit before continuing. When one home resolves, read its sibling
`_improvements/state.yaml` when present; absence means there is no cursor yet.
This file is derived coordination state with the following minimum shape:

```yaml
schema: kc-dev-flow-improvements/v1
newest_processed_debrief: <immutable debrief name or none>
last_run:
  consumed: [<debrief names>]
  skipped_superseded: [<older unseen debrief names>]
  disposition: none | repository-local | reusable-kernel
  candidate: <work-item or handoff reference, or none>
```

1. Consider only immutable debriefs newer than `newest_processed_debrief`. If
   there is no cursor, take at most the most recent three in the authority's
   stable order. When more than three are unseen, record the older names under
   `skipped_superseded`; this bounded scan deliberately retires them instead of
   queueing them for a later launch. If there is no unseen debrief, perform no
   analysis and do not rediscover or re-propose an older issue.
2. From the consumed set, classify at most one narrow candidate as
   **repository-local** or **reusable kernel**. Its reviewable record names the
   observations, expected value, cost, disproof hook, duplicate search, and
   disposition.
3. Advance `newest_processed_debrief` to the newest consumed record even when no
   candidate is proposed. Record the consumed names and disposition. This
   prevents the next launch from treating the same evidence as new.
4. Use the execution-state authority's existing single-writer transaction or
   compare-and-swap for the cursor update. Inside the same transaction that
   writes the new state, resolve the debrief home again and verify the locator is
   unchanged, then re-read and compare the live cursor. A home or cursor mismatch
   aborts the write and recomputes from live authority; if the authority provides
   neither atomic comparison nor exclusive ownership, report `UNKNOWN`, skip the improvement write, and continue to product routing. The cursor and any handoff
   are one write unit: if the authority cannot safely write both, write neither.
5. Route a repository-local candidate to the existing work-item authority. A
   reusable kernel candidate becomes a sanitized handoff to the installed
   dev-flow source. Detection does not create or schedule a task, grant sprint
   membership, merge anything, or pause product work.

`reusable-kernel` remains the schema-v1 **compatibility transport label**. It
means "send to the canonical source for placement judgment," not "the adopter
proved a new kernel clause is needed." The source-side procedure is
`promote-dev-flow`.

The referenced handoff uses this exact top-level shape:

```json
{
  "schema": "kc-dev-flow-improvement-handoff/v1",
  "source_policy_revision": "<kc-dev-flow-vX.Y.Z or 40-64 char Git revision>",
  "failure_shape": "stable-lowercase-identifier",
  "finding_kind_hint": "unknown",
  "landing_target_hint": "unknown",
  "existing_rule": "rule locator or none",
  "summary": "sanitized bounded summary",
  "expected_value": "bounded value",
  "cost": "bounded cost",
  "disproof_hook": "result that would reverse the candidate",
  "duplicate_search": ["bounded search record"],
  "observations": [{"id": "src-<12 lowercase hex>-<16 lowercase hex>", "evidence": "bounded evidence", "impact": "bounded impact"}]
}
```

Allowed finding hints are `rule-gap`, `enforcement-gap`, `local-instance`,
`duplicate/no-change`, and `unknown`. Allowed landing hints are `kernel`,
`plugin-enforcement`, `adopter-local`, `no-change`, and `unknown`.
The failure shape is an adopter-coined label for source reconciliation, not a
verified cross-adopter merge key.

Carry every distinct occurrence of the one failure shape in `observations`; a
retry keeps the same ID. On the first reusable-source candidate, generate 128
cryptographically random bits as `source_namespace_key`. Store its 32 lowercase
hex characters and the derived 12-hex `source_namespace` only in durable
pseudonymous state at `_improvements/.private/source-identity.json`; neither field
belongs in `_improvements/state.yaml`. Before writing, require ignore proof from
the repository's bound version-control authority. For Git this means the exact
path passes `git check-ignore -q`; for another provider use its equivalent. If
ignore or private durable backup cannot be proven, report `UNKNOWN`, produce no
reusable-source handoff, and continue product routing. Never regenerate, rotate,
publish, or commit this identity file. If it is lost, report that recurrence
restarts under a new namespace instead of claiming continuity.
This private identity is durable pseudonymous state, not derived coordination state.

Compute `source_namespace` as the first 12 lowercase hex characters of SHA-256
over the key bytes. Never derive either value from repository identity and never
place the key in a handoff.

Form each ID as `src-<source_namespace>-<occurrence digest>`. The occurrence
digest is the first 16 lowercase hex characters of HMAC-SHA-256, keyed by the
16 bytes decoded from the stored lowercase hex key. Encode the message as UTF-8
bytes of `json.dumps(payload, separators=(',', ':'), ensure_ascii=False)`, where
`payload` is `[failure_shape, immutable_debrief_name,
zero_based_occurrence_index]` and the index counts occurrences within that one
debrief in the authority's stable order. This keeps retries stable without
exposing adopter identity or making debrief names dictionary-testable.
Every observation in one handoff must use the same namespace. An ID collision
with different evidence is malformed input, not recurrence.

Write reusable-source handoff batches under
`_improvements/handoffs/<failure-shape>/<source-namespace>-<sequence>.json`, with
a zero-padded sequence beginning at `0001`. Set `last_run.candidate` to the batch
updated or created in the same single-writer or compare-and-swap transaction that
advances the cursor. A repository-local candidate continues to reference its
existing work item.

Inside the transaction, re-read the latest batch for this failure shape and
namespace. Require the same schema, failure shape, and source namespace. Merge
existing observations by ID and union duplicate-search entries only when the
result remains at most 50 observations and 20 searches. Identical IDs with
identical evidence and impact collapse; conflicting IDs abort as malformed. If
either cap would be exceeded, or no same-namespace batch exists, roll over to the
next sequence with only the new bounded candidate; never truncate, overwrite, or
mix namespaces. First-write-wins for summary, expected value, cost, disproof hook,
existing rule, hints, and source policy revision within each batch; that revision
records the earliest observation in that batch. A materially different proposal
requires source-side judgment, not a silent scalar update. The batch and cursor
advance commit together or neither is written. Remove adopter names, URLs,
hosts, email addresses, absolute paths, credentials, selectors, and customer
data. Hints are not source verdicts. The handoff itself does not create source
work.

Merge rule summary: merge its existing observations by ID only within one bounded,
same-namespace batch; otherwise create the next batch.
Overflow rule: roll over to the next sequence without truncation.

The version-1 validator accepts a release tag shaped `kc-dev-flow-vX.Y.Z` or a
40-64 character lowercase Git revision, a lowercase failure-shape identifier of
3-128 characters, observation IDs with exactly 12 namespace hex plus 16
occurrence hex characters, one failure shape and one source namespace per file,
1-20 duplicate-search entries, and 1-50 observations. Bounds are: existing rule
4-160 characters; summary 12-200; expected value and disproof hook 12-300; cost
8-240; each search entry 3-160; evidence and impact 12-300. Produce one handoff
for one failure shape; do not combine unrelated candidates to fill the bounds.

Before the handoff leaves the repository, run:

```bash
python3 <kc-dev-flow package root>/scripts/improvement-intake.py --handoff <path>
```

A non-zero exit means the file is not sendable. Delivery requires a
captain-approved file attachment or copied path; validation grants no permission
to post, upload, or create source work.
