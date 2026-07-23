# Shadow review receipt — Shape Projection

## Shape Output

### Problem

The current interactive review produces transient orchestration output. A fresh agent cannot validate which exact head, lanes, findings, evidence, or usage produced the result without re-reading the full workflow and repeating work.

### Appetite

Three working days. This child is the first of three sequential PRs and must remain behaviorally shadow-only.

### Scope In

- A local exact-head run identity and versioned append-only event envelope.
- Validation, replay projection, inspect/show output, and evidence-pointer rehydration.
- Provider-neutral task, result, finding-candidate, and usage-provenance contracts.
- Read-only quarantine for invalid or unsupported state.
- One post-classification shadow integration seam in the existing interactive review.
- Deterministic fixtures plus a paired-run corpus and baseline report.
- Documentation for the shadow commands, state location, provenance, and rollback boundary.

### Scope Out

- Behavioral authority over verdict, confirmation, review body, comments, event selection, or GitHub posting.
- A second review dispatch, prompt or reviewer-intelligence rewrite, resume, garbage collection, remote idempotency, or daemon mutation.
- Required-coverage enforcement, an approval eligibility change, or a token-improvement claim.
- Full diff, prompt, evidence excerpt, or raw provider-output persistence.

### Done Criteria

| ID | Assertion | Type |
|---|---|---|
| DC-1 | A validated receipt binds full repository identity, PR number, base and head SHA, schema and configuration hashes, run identity, lane terminal states, coverage, normalized findings, evidence pointers, and typed usage provenance. | cli |
| DC-2 | Canonical event hashing, duplicate-event no-op behavior, deterministic replay, additive supported-v1 fields, and read-only quarantine are covered by deterministic fixtures. | cli |
| DC-3 | Evidence pointers rehydrate only against the exact source hash, while durable state contains no full diff, prompt, evidence excerpt, or raw provider output. | cli |
| DC-4 | ReviewTask, LaneResult, candidate, finding, and usage envelopes remain provider-neutral; unavailable usage remains null and cannot satisfy an efficiency comparison. | cli |
| DC-5 | Shadow integration dispatches no additional review and leaves legacy verdict, confirmation, review body, inline comments, event selection, and GitHub mutation behavior unchanged. | cli |
| DC-6 | A paired-run corpus reports recall, lane accounting, parity, stability, and usage provenance without claiming token improvement from unavailable or incomparable measurements. | cli |

### Assumptions

- Bash and `jq` are sufficient for the local runtime and are already consistent with plugin scripts.
- The stable observation seam is after finding classification and before the confirmation/posting gate; plan research must revalidate the exact insertion point.
- Existing shell tests can be extended without adding a repository-level package manager.
- PR1 can fail open to the unchanged legacy review when shadow-state creation or validation fails.

### Risks

- A shadow hook placed before final classification may capture a different result than the user sees.
- Persisting convenient excerpts would silently expand the sensitive state surface.
- Treating missing usage as zero could create a false efficiency claim.
- A fixture-only parity check could miss changes in the generated GitHub payload.

### Hand-off to Design

- Inherit parent decisions D1-D4 and D7.
- Add no child contract decisions.
- Preserve legacy behavioral authority and external-output parity.
