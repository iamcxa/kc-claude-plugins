---
name: work-control-profile
description: "Optional portable controls for keeping work-context, delivery, landing, resource, and review claims evidence-bound"
version: 0.1.0
---

# Work Control Profile

This is an optional companion to a repository's work-context contract. The
work-context contract names where project context and work-item truth live.
This profile names controls that can prove selected workflow claims remain
truthful at repository-defined enforcement points.

Adopting this file activates nothing by itself. A repository declares only the
capabilities it needs, supplies its own provider adapter, and names the local
authority and enforcement points. The profile does not prescribe GitHub,
Markdown tasks, a CI vendor, paid models, or auto-merge.

## Declaration

Declare each adopted capability in the repository's workflow binding:

```yaml
work_controls:
  <capability>:
    mode: observe | required
    adapter: <repository-owned command or provider binding>
    authority: <who may accept failure, expand scope, or spend more>
    enforcement:
      - <named local boundary>
```

`observe` records receipts and non-passes without blocking the boundary.
`required` makes every outcome except `PASS` fail closed at every declared
enforcement point. Omitting a capability is valid and different from declaring
it `observe`.

## Evidence envelope

Every attempt emits or records this logical envelope:

```yaml
capability: <capability id>
mode: observe | required
adapter: <provider binding>
authority: <named authority>
input:
  ref: <stable artifact or work-item reference>
  revision: <exact revision when the provider supports one>
outcome: PASS | FAIL | UNKNOWN | UNAVAILABLE
evidence:
  - <provider-native evidence reference>
```

The four outcomes are closed:

- `PASS` — the adapter evaluated the declared input and produced evidence that
  satisfies the capability's acceptance rule.
- `FAIL` — the adapter evaluated the input and found a contract violation.
- `UNKNOWN` — required input, provider state, or exact revision could not be
  established. Absence of proof is not a pass.
- `UNAVAILABLE` — the declared provider or capability is known not to be
  available for this attempt. Silence is not a pass.

Evidence remains bound to the recorded input. A changed task, delivery head,
landing message, resource envelope, or review head invalidates the old
receipt. Provider-native evidence is preferred; a prose claim written by the
actor being checked does not independently close a required control.

## Capabilities

### `bound_field_validation`

Use when work-item fields drive provider queries, routing, iteration views, or
other derived claims.

The adapter must:

1. validate every controlled field's requiredness, scalar shape, and allowed
   registry value on a new or changed work item;
2. reject duplicate or malformed controlled fields rather than guessing how a
   general YAML parser would normalize them;
3. authenticate the provider's live population root and exact revision, then
   audit that complete population while excluding the adopter's declared
   archive locations;
4. report field validity separately from migration completeness;
5. report whether each derived filter or view is authoritative, and why.

Mechanical coverage can prove a field present on every live item. It cannot
prove that a blank optional field means "intentionally unassigned" rather than
"not migrated." That semantic completeness needs an explicit declaration from
the repository's migration authority, and invalid live fields still defeat the
declaration.

Acceptance is a `PASS` receipt for the exact changed item at capture or
transition. A view may be called authoritative only when the population audit
sets that view's authority flag to true. Invalid data is `FAIL`; missing or
unreadable registry/state input, an unauthenticated population root, or a
population that cannot be bound to one revision is `UNKNOWN`.

### `delivery_reconciliation`

Use when a hosted delivery artifact can complete one or more work items.

The adapter binds the exact delivered revision to stable work-item references,
rejects ambiguous coverage, observes the provider's landed state, and applies
each legal transition idempotently. A merged artifact without proven coverage
or a provider outage is a non-pass.

### `landing_metadata_preview`

Use when a final title, message, manifest, tag, or other landing-time metadata
can change the released result after ordinary branch validation.

The adapter evaluates the exact proposed landing metadata and revision through
the release consumer, or a version-pinned faithful parser. A different landed
message invalidates the receipt.

### `resource_envelope`

Use before bounded paid, time-limited, rate-limited, or retry-heavy work.

The adapter records approved units, known and unknown usage, remaining
authority, and a conservative completion floor before the first expensive
action and at every round boundary. Insufficient authority stops before the
next action; a retry needs a fresh envelope.

### `review_convergence`

Use when review and repair repeat until a landing decision.

The adapter binds each round to the exact delivery revision, gives findings
stable identities, distinguishes closed, residual, new, and repeated findings,
caps rounds, and records typed preferred-reviewer failure before a declared
fallback. Reviewer silence, timeout, or setup failure is never a clean verdict.

## Adoption sequence

1. Run a reverse-recovery audit and name the existing abstraction and broken
   seam. Do not create a parallel workflow for an abstraction that already
   exists.
2. Declare one capability and one enforcement point.
3. Build the smallest repository adapter that can emit the evidence envelope.
4. Start in `observe` if the population or provider baseline is unknown.
5. Promote to `required` only after the repository can demonstrate the
   enforcement point fails on `FAIL`, `UNKNOWN`, and `UNAVAILABLE`.
6. Add another capability only when its own risk justifies the adoption cost.

Combining all five capabilities into one verdict or rollout is not conformant:
each capability must remain independently adoptable, observable, and
enforceable.
