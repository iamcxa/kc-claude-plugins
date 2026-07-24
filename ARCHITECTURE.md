# Architecture Contracts

This document records durable architecture decisions for repository capabilities. It is written for contributors implementing or reviewing changes that cross lifecycle, provider, persistence, or remote-mutation boundaries.

## Repository layout

The repo is a monorepo of six independent Claude Code plugins at top level
(`e2e-pipeline/`, `kc-plugin-forge/`, `kc-nightwatch/`, `kc-hyperfocus/`,
`kc-team-ops/`, `kc-pr-flow/`), each with its own `skills/` directory; five
of the six also ship `agents/` (all but `kc-plugin-forge`), and (where
applicable) `hooks/` directories, plus a repo-level `scripts/` directory and
`.claude-plugin/marketplace.json` manifest. `docs/dev/` holds the lean
ship-flow-style task workflow (split-root state under
`docs/dev/.spacedock-state`) that governs how repo changes are proposed,
built, and verified.

## Marketplace publish flow

`.claude-plugin/marketplace.json` is the published catalog; each plugin
entry names its `source` path, `description`, `version`, and `keywords`.
`scripts/marketplace-verify.sh` validates marketplace schema plus plugin
installability (and optionally skill execution, `--smoke`) in an isolated
temp `HOME`. `scripts/post-install-smoke.sh` runs the full post-install
lifecycle (marketplace add → plugin install → MCP deps → smoke test) per
plugin. `.github/workflows/marketplace-parity.yml` runs on every PR (no
`paths:` filter, so it stays a valid required check) and enforces version
parity plus skill-frontmatter well-formedness before merge.

## Hooks and scripts surfaces

Four plugins ship a `hooks/hooks.json`: `e2e-pipeline`, `kc-plugin-forge`,
`kc-hyperfocus`, `kc-pr-flow`. `kc-nightwatch` and `kc-team-ops` currently
ship no hooks. `.githooks/pre-commit` is an opt-in local pre-commit hook
(`git config core.hooksPath .githooks`) that runs `e2e-pipeline`'s biome
lint + tests only when `e2e-pipeline/` files are staged. Repo-level
`scripts/` holds cross-plugin checks run in CI: `marketplace-verify.sh`,
`post-install-smoke.sh`, `release-metadata.test.sh`,
`release-please-config-check.sh`, `skill-frontmatter-lint.sh` (+ its
test), `version-parity-check.sh`.

## Versioning scheme

Each plugin is an independent release-please component
(`release-please-config.json`, manifest mode, `tag-separator: "-"`,
`include-component-in-tag: true`) tracked in
`.release-please-manifest.json`. On push to `main`,
`.github/workflows/release-please.yml` maintains a Release PR that bumps
the changed plugin(s) across `<plugin>/.claude-plugin/plugin.json`,
`<plugin>/.codex-plugin/plugin.json` (only `e2e-pipeline`, `kc-plugin-forge`,
`kc-pr-flow` ship a Codex manifest), and the matching `marketplace.json`
array entry; merge cuts a `<plugin>-vX.Y.Z` tag, GitHub Release, and
per-plugin `CHANGELOG.md`. `scripts/version-parity-check.sh` is the
machine-enforced backstop asserting all tracked version sources agree.

## kc-pr-flow: Agent-native review runtime

### Context

The legacy review flow coordinates model lanes and GitHub posting through procedural instructions. The target runtime adds a local typed state layer that agents can validate, replay, inspect, and resume without giving that layer behavioral authority before evidence gates pass.

The state root is configurable and defaults to the platform state directory under `kc-pr-flow`. The runtime remains local Bash plus `jq`, with a Python 3.8+ helper for fail-closed safe I/O, duplicate-key detection, jq-safe integers, and real UTC calendar validation. No network service or database is required.

### Decision record

| ID | Decision |
|---|---|
| D1 | A stable exact-head review key groups unique runs. Compatible interruption resumes the same run; reruns and head or configuration changes create typed successors. |
| D2 | Versioned append-only JSONL events are authoritative for typed run records. The v1 envelope and payloads are closed; same-major extension is limited to typed hash-only metadata with no replay authority. Replayed projections are caches. A closed derived interactive decision may govern coverage, event precedence, and confirmation input, but never posting. |
| D3 | Provider observations remain candidates. Merged findings use exact-head, source-location, evidence-hash, category, and constrained-claim identity. Durable evidence stores typed pointers and hashes, not excerpts. |
| D4 | Core lifecycle contracts are provider-neutral. Adapters cannot own lifecycle, verdict, authorization, or posting. Usage provenance is reported, estimated, or unavailable; missing values remain null. |
| D5 | Requiredness is capability-based. Every required capability needs typed terminal evidence. Remaining gaps forbid approval but cannot dilute confirmed blockers. |
| D6 | Authorization binds repository, PR, exact head, effective event, policy, and payload hash. Pending intent is durable before mutation, and deterministic remote identity is reconciled before retry. |
| D7 | Unsupported majors, unknown event types, missing required fields, and hash failures are excluded from accepted state. Rejected append input creates metadata-only quarantine containing reason, input hash, byte count, and timestamp, never the rejected bytes. Invalid state cannot reduce, resume, authorize, mutate, migrate, or be garbage-collected automatically. |

### Authority boundaries

| Concern | Authority |
|---|---|
| Typed run history | Valid append-only events |
| Rebuilt receipt and CLI display | Replay projection; never an independent source of truth |
| Coverage, approval eligibility, and event precedence in typed mode | A closed `InteractiveCollationDecision/v1` is primary authority; invalid decision production may preserve REQUEST_CHANGES only through independently confirmed exact-identity `confirmed-blocker-evidence/v1`, and inconsistency fails closed |
| Human confirmation and remote posting | Existing interactive review flow; the runtime cannot bypass or execute either |
| Required coverage | Capability terminal states plus explicit evidence-bound fallback |
| Remote mutation | GitHub review identity, reconciled to a deterministic local intent |
| Provider-specific invocation | Adapter only; it cannot mutate core lifecycle state directly |

### Interactive components and data flow

```mermaid
flowchart LR
    Start[Fresh invocation] --> Switch{Typed gate exactly on?}
    Switch -->|no| Legacy[Legacy collation]
    Switch -->|yes| Lanes[Provider-neutral capability work]
    Lanes --> Log[Terminal typed exact-head receipt]
    Log --> Replay[Safe snapshot, validate, replay, verify evidence]
    Replay --> Decision[Closed interactive decision]
    Decision --> Confirm[Existing human confirmation]
    Legacy --> Confirm
    Log --> Pair[Sanitized paired corpus]
    Pair --> Gates[Ordered G1-G5 promotion report]
    Confirm --> Post[Existing posting path]
    Decision -. no posting authority .-> Post
```

The typed gate is sampled once before dispatch. With the gate unset, off, or unknown, one fresh invocation follows the legacy path. With the gate exactly on, the runtime may derive interactive authority only from one complete terminal receipt whose repository, PR, base, head, configuration, review key, and run identity match the caller's fresh inputs. Typed failure stays typed for that invocation and yields an explicit non-approval decision; it cannot fall through to legacy behavior after dispatch.

Accepted state is fail-closed and uses owned reservations, private rebuild plus atomic rename, immutable run identity, contiguous sequence, and content-addressed metadata-only quarantine. Python 3.8+ safe I/O opens a no-follow regular-file descriptor, proves stable file identity around a bounded descriptor read, and publishes a private mode-0600 snapshot before every runtime consumer parses file input. Missing Python or `O_NOFOLLOW`, unsafe types, path races, concurrent mutation, oversize input, invalid JSON members, unsafe integers, or impossible UTC dates fail before accepted-state mutation. The separate shadow observer remains fail open because it has no behavioral authority.

### Run and event identity

The review key hashes full repository identity, PR number, base SHA, head SHA, and effective configuration hash. Each fresh execution receives a unique run ID. Event IDs are deterministic over run, sequence, type, and canonical payload hash; appending the same event ID is a no-op.

Breaking event semantics require a new schema major. Within v1 the only optional top-level addition is a closed `extensions` array of namespace, key, value SHA-256, and byte count. Extensions participate in record integrity but never replay or review authority. Rejected bytes are deliberately unavailable; quarantine exposes only bounded metadata.

### Finding and evidence identity

Each provider lane emits candidate observations. The collator may merge candidates only when their constrained merge key agrees. Uncertain matches stay separate so cross-model disagreement remains visible.

Evidence pointers identify a review key, base and head, source kind, exact repository object, relative location, side, locator, and content hash. `LEFT` binds to the base object; `RIGHT` and `FILE` bind to the reviewed head. Candidate, merge, and finding identities include the evidence content hash. Rehydration must verify that hash before the evidence can support a finding or authorization decision.

### Coverage and failure policy

Capabilities, not provider names, define required coverage. A required transient failure receives one retry and then a typed manual fallback opportunity. If required coverage remains incomplete, the run has an explicit comment ceiling and is not approval-eligible. Confirmed blockers may still produce a request for changes.

Optional provider failures remain recorded evidence and do not independently block completion.

`InteractiveCollationDecision/v1` is a closed replay-derived projection. It contains capability terminal records, required-gap and confirmed-blocker references, approval eligibility, effective event, and typed confirmation input. Confirmed blockers take precedence over coverage gaps; otherwise incomplete required coverage selects COMMENT, and only complete blocker-free coverage is approval-eligible. Terminal rehydration verifies exact identity and evidence and returns this projection in memory without append, recovery, resume, retention, authorization, model, network, or GitHub behavior.

The benchmark reports G1 valid bound inputs, G2 required capability coverage, G3 external behavior parity, G4 zero lost expected must-fix findings, and G5 efficiency in that order. G5 passes only through complete same-provider/scope reported usage with median token reduction of at least 20%, or a receipt-bound fresh local terminal-collation measurement with median cost no greater than 60% of a designed full review rerun and zero model or remote calls. Branch B uses a corpus-owned `local-measurement-binding/v1`: it binds raw terminal, decision, and `full-review-rerun-control/v1` hashes plus both `canonical-artifact-bytes/v1` unit values. The producer executes rehydration only; it never labels replay output as the full-rerun control.

### Authorization and posting

Authorization is exact-head and exact-payload. The runtime persists a restrictive pending payload and deterministic idempotency key before GitHub mutation. A timeout or ambiguous connection result must be reconciled against the remote marker or review identity before any retry.

The daemon is default-deny. It requires explicit preauthorization plus current typed state, exact-head, coverage, and idempotency gates. It cannot issue an approval in the initial runtime.

### Retention and recovery

Terminal receipts are retained for 30 days. Failed pending payloads are retained for 24 hours. Active or remotely uncertain runs are never garbage-collected. Garbage collection is dry-run by default and requires an explicit apply action.

These are target-runtime rules, not shadow capabilities. Increment 2.3 owns crash-safe lock recovery and PID-reuse handling, predecessor-lineage verification, append/compaction performance, resume, retention/garbage collection, once-only posting, remote reconciliation, and daemon mutation. The shadow runtime must fail closed or remain diagnostic rather than approximate those behaviors.

### Increment boundaries

- Shadow receipt: closed `ShadowObservation/v1`, D1-D4 and D7 schemas, fail-closed safe ingestion, complete replay, evidence rehydration, and authority-bound baseline collection. No behavioral authority.
- Typed interactive lifecycle: D5 enforcement, typed collator authority, exact-head rehydration, and a legacy fallback switch.
- Safe resume and once-only post: remaining D1 retention behavior and D6 authorization, pending payload, remote reconciliation, and guarded daemon integration.

Every increment must be independently reversible. Rollback must retain evidence required to reconcile an uncertain remote mutation.
