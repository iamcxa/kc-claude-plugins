---
title: Review the published-tag Science Officer runtime smoke
status: validation
source: Captain-approved issue #183 follow-up and v2.2.0 cycle-1 reset, 2026-08-11
product: kc-dev-flow
sprint: S1
design: required
id: jj5jbzp2tpyc7a6x78wnfqky
lane: main
started: 2026-08-10T22:03:08Z
worktree: .worktrees/spacedock-ensign-kc-dev-flow-published-tag-smoke-review
pr: ""
---

## Problem

The first containing-tag run at `kc-dev-flow-v2.2.0` earned retention by finding
installed-runtime evidence that no pre-release check had observed: Claude added
`verdict_note` to an adjudication object, and the intentionally strict consumer
rejected the extra field. The defect is a producer/consumer specification gap.
The packaged skill and smoke prompt enumerate fields but never say their objects
are closed.

The release-only placement is now wrong. Publication became the first full
observation of the host/report contract, so a preventable producer mismatch was
found only after the artifact was public. Without correction, later releases can
repeat that sequencing failure even though the smoke itself is valuable.

No new scope interview is needed for this reset: the captain's rejection and
decision answer the ideation questions directly. The cost of doing nothing is a
post-publication contract surprise; the protected core is pre-release dual-host
report proof plus post-release artifact identity; retries, schema relaxation,
provider matrices, and a second framework are happily excluded; and the
load-bearing assumption is that both existing marketplace installers can consume
a local candidate checkout.

## Review contract

Keep one smoke mechanism across two release triggers. Before a Release PR is
merged, the clean candidate must install and invoke through isolated Claude and
Codex state, and both reports must satisfy the exact closed schema. Preserve that
candidate receipt. After publication, rebind the exact tag, declared version, and
both installed plugin trees to the receipt without invoking either model, then
continue to local sync.

## End value

Publication is never the first observation of a host/report incompatibility. A
pre-release receipt proves both isolated installed hosts accepted the candidate's
closed compatibility record. A post-release receipt then proves that the exact
published tag's version and plugin bytes are the already-validated candidate,
while recording both candidate and published revisions.

## Fastest path, smallest cut, and rejected alternative

- **Fastest path:** teach the existing producer surfaces that the report objects
  are closed, then run the existing smoke before and after publication.
- **Smallest cut:** keep `scripts/kc-dev-flow-published-tag-smoke.py` as the only
  mechanism, split it into `candidate` and `published` modes, and pass one
  closed-schema JSON receipt between them. Extend only the existing contract test,
  packaged Science Officer skill, and root release instructions.
- **Taking the cheap path:** the one-script/four-existing-file repair satisfies
  the same ACs with no scope cut. The more thorough alternative is an authenticated
  Release-PR CI matrix plus hosted or signed receipt storage. It adds secrets,
  provider spend, workflow authority, and a second persistence concern without
  improving the accepted manual release-boundary proof.

## Smallest route and reverse-recovery audit

Audit target: fresh `origin/main` at published tag `kc-dev-flow-v2.2.0`, revision
`54913dda3e5e66841e043025bf646e0ad2493bc9`.

- **Release entry — `EXISTS_BROKEN`:** `CLAUDE.md:47-56` runs the only authenticated
  smoke after publication, so it cannot prevent publication from being the first
  report-contract observation. Falsifier: a containing-tag provider mismatch is
  seen only after the tag exists; v2.2.0 supplied that observation.
- **Producer contract — `EXISTS_BROKEN`:**
  `kc-dev-flow/skills/science-officer-em/SKILL.md:51-91` enumerates the report but
  does not say root, envelope, judgment, and adjudication objects reject extra
  keys. Falsifier: the v2.2.0 producer emitted `verdict_note`.
- **Smoke prompt — `EXISTS_BROKEN`:**
  `scripts/kc-dev-flow-published-tag-smoke.py:296-302` asks for every field but
  does not say "exactly these keys and no extras." Falsifier: the same released
  host output.
- **Strict consumer — `WORKING`:**
  `scripts/kc-dev-flow-published-tag-smoke.py:53-188` rejects duplicate, missing,
  extra, invalid-enum, wrong-revision, and wrapper-mismatch data. The v2.2.0
  failure is its runtime proof. Relaxing it would delete the evidence that earned
  retention.
- **Host install/invocation — `WORKING`:** the script already isolates and
  installs both hosts at lines 305-442; prior v2.1.0 probes exercised both host
  kinds, and v2.2.0 reached the real Claude producer. Current `claude` and `codex`
  CLI help both explicitly accept a local path for `plugin marketplace add`, so
  the candidate mode needs no new installer. Disproof hook: the first RED/GREEN
  rehearsal fails to install the exact local candidate.
- **Candidate receipt handoff — `MISSING` within the existing mechanism:** two
  searches of `origin/main` found no candidate-receipt vocabulary, and argparse
  at script lines 454-488 exposes only a published tag or standalone report
  validation. Add the seam inside the existing script; do not add a new script.
- **Published identity proof — `WORKING_UNIT_UNPROVEN` against a candidate:** exact
  tag resolution, version comparison, and source/installed tree digests already
  exist at script lines 323-364 and 407-421. They are not yet compared to a
  pre-release receipt. Disproof hook: mutate receipt version or digest and observe
  published mode refuse it without a provider call.

Live branch protection requires only the existing `version parity
(plugin.json / marketplace.json / codex / README)` context. The existing parity
job already runs `scripts/kc-dev-flow-contract-test.py`; no provider workflow or
required-check identity change is justified.

## Design determination

`required` — this changes a release CLI and two closed data contracts.

```text
# On the clean Release PR head, before merge/publication
python3 scripts/kc-dev-flow-published-tag-smoke.py candidate --receipt "$RECEIPT"

# After the exact tag exists, before local sync
python3 scripts/kc-dev-flow-published-tag-smoke.py published \
  kc-dev-flow-vX.Y.Z --candidate-receipt "$RECEIPT"
```

`candidate` installs the current clean checkout into temporary Claude and Codex
homes, checks each installed version/tree against source, invokes both hosts with
the current auth path, applies the unchanged strict report validator, and writes
the receipt only after both pass. The closed receipt contains its schema,
candidate revision, declared version, tree SHA-256, and Claude/Codex
version/tree/report results.

`published` validates that receipt strictly, exact-clones the tag, records the tag
revision, installs the tag checkout into both isolated homes, and requires tag
version plus source and installed-tree digests to equal the candidate receipt. It
does not copy operator auth or invoke a model. Candidate and tag revisions are
recorded but need not be equal because merge mechanics can change commit identity
without changing plugin bytes.

The packaged skill and smoke prompt will state that root, envelope,
`engineering_judgment`, and every adjudication item are closed objects: emit
exactly the documented keys and no additional keys, including `verdict_note`.
`exact_object` remains strict.

## Acceptance criteria

**AC-1 — Host and report compatibility is proven before publication.**

Verified by: `scripts/kc-dev-flow-contract-test.py:64-159` failure-path tests and
one real pre-release candidate receipt proving the isolated host path at
`scripts/kc-dev-flow-published-tag-smoke.py:305-442` writes no passing receipt
until both installed hosts return one strictly accepted report.

Falsified by: either host is skipped, uses implicit plugin state, returns an
invalid record, or publication is the first dual-host result.

Baseline: v2.2.0 was published before the first complete host/report observation.

**AC-2 — Producer and consumer share one closed report schema.**

Verified by: `scripts/kc-dev-flow-contract-test.py:64-159` producer-guidance
assertions and a direct `verdict_note` negative fixture, the unchanged strict
consumer at `scripts/kc-dev-flow-published-tag-smoke.py:53-188`, and closed
producer guidance at `kc-dev-flow/skills/science-officer-em/SKILL.md:51-91`.

Falsified by: an extra field is accepted, stripped, retried, or left permitted by
producer guidance.

**AC-3 — Publication only rebinds the validated artifact identity.**

Verified by: `scripts/kc-dev-flow-contract-test.py:64-159` receipt/tag/version/tree
mutation tests, the identity seams at
`scripts/kc-dev-flow-published-tag-smoke.py:323-451`, and the first containing-tag
receipt proving published mode exact-resolves the tag and matches its version,
source digest, and both installed trees without invoking either model.

Falsified by: a missing/non-exact tag, mismatched version or digest, unequal
installed tree, accepted extra receipt field, or any post-release host invocation.

**AC-4 — One mechanism spans exactly two release triggers.**

Verified by: the two ordered release commands in `CLAUDE.md:40-56`, both modes in
`scripts/kc-dev-flow-published-tag-smoke.py:454-488`, no new workflow or smoke
file in `git diff --name-only origin/main...HEAD`, and contract coverage remaining
in `.github/workflows/marketplace-parity.yml:28-57`.

Falsified by: a second smoke framework, per-PR model matrix, new
credential/persistence system, post-release report validation, or a relaxed
parser.

## Test plan

Use RED before GREEN inside the existing contract suite:

1. Add failing CLI/receipt tests for `candidate` and `published`, exact receipt
   fields, no receipt before both hosts pass, and candidate revision/version/tree
   capture.
2. Add failing orchestration tests proving candidate mode invokes both installed
   hosts and published mode invokes neither. Use faked command results; do not make
   provider calls in the deterministic suite.
3. Add failing mismatch fixtures for tag, version, source digest, either installed
   digest, extra receipt fields, and the observed report `verdict_note`.
4. Add failing text-contract assertions for closed-object guidance in the
   packaged skill and smoke prompt.
5. Implement the two modes and guidance, then run the contract suite, Python
   compilation, frontmatter, version parity, marketplace, state-prerequisite, link,
   and `git diff --check` gates.
6. In validation, run candidate mode once through real authenticated Claude and
   Codex before publication. After the next containing tag, run published mode
   with that receipt; do not terminalize on candidate evidence alone.

No new test framework is justified. A fifth implementation surface is allowed
only if a RED result proves that the installed CLI cannot consume the exact local
candidate, the receipt cannot bind version plus tree bytes across publication, or
the existing release instructions cannot carry the receipt. A preference for
automation, provider variation, or extra telemetry is not such evidence.

## Appetite and pre-mortem

Estimate one implementation worker and 60 minutes, with a declared tolerance of
30 minutes. Stop and re-cut at 90 minutes, on a fifth implementation surface, or
if the local installer/receipt premise fails; never compress validation to fit the
budget. The first implementation action re-fetches `origin/main` and starts from a
fresh isolated worktree rather than the stale release-batch branch.

No further spike is needed for ideation: current Claude and Codex help both state
that marketplace add accepts a local path, while the released script already
proves the other install, isolation, auth, tag, digest, and strict-consumer seams.
The first local-candidate RED/GREEN rehearsal remains the disproof hook.

If this ships exactly per spec and still fails, the most likely cause is the hidden
assumption that a Release PR candidate's version plus plugin-tree digest survives
publication unchanged even when its commit SHA does not.

## Out of scope

Retries, field stripping, schema relaxation, per-PR model calls, a model matrix,
new CI jobs or required contexts, signed/hosted receipt storage, a second smoke or
test framework, a new credential or installer abstraction, replacing marketplace
verification or post-release sync, manual version edits, general release-please
changes, post-release model invocation, and creating or merging a PR.

## Stage Report: ideation

- DONE: AC-1 reframes the accepted outcome so dual-host invocation and exact
  report validation are proven on the Release PR candidate before publication,
  reversing the v2.2.0 baseline.
- DONE: AC-2 preserves the strict consumer and closes the packaged skill and
  smoke-prompt producer contract, with the observed `verdict_note` as a direct
  negative fixture.
- DONE: AC-3 limits post-release work to exact tag/version/source/installed-tree
  identity against the candidate receipt and forbids model invocation there.
- DONE: AC-4 keeps one existing smoke script across `candidate` and `published`
  triggers and names the RED evidence required before adding any fifth surface.
- DONE: Recorded exclusions, the RED-first route, and a 60-minute estimate plus
  30-minute declared tolerance.
- DONE: Reverse recovery against `origin/main` at
  `54913dda3e5e66841e043025bf646e0ad2493bc9` found a sequencing/guidance seam,
  not a missing smoke abstraction; the strict parser remains `WORKING`.
- DONE: Exactly one fresh high-reasoning EM returned
  `proceed / high / multi_model:not_needed`. It supports a durable receipt as the
  evidence bridge, rejects commit-SHA equality as a merge-strategy assumption,
  and found no fifth implementation surface justified.

### Summary

Proceed with the one-mechanism/two-trigger reset. The candidate phase owns real
Claude/Codex report compatibility; the published phase owns artifact identity
only. Keep strict parsing, close the producer contract explicitly, and require a
RED falsifier before widening beyond the four existing files.

## Stage Report: implementation

- DONE: Captain-approved commit
  `24d91bb0af0b53fd0b18b882e79c538419115cb2` changes exactly four existing
  files: `CLAUDE.md`, the packaged Science Officer skill, the existing
  kc-dev-flow contract test, and the existing published-tag smoke script. Its
  diff is 664 insertions and 90 deletions; no fifth surface, workflow, version
  bump, publication, local sync, PR, or provider matrix was added.
- DONE: `candidate --receipt PATH` requires a clean checkout, installs that
  checkout through isolated Claude and Codex homes, invokes both hosts, applies
  the unchanged strict report consumer, and writes no receipt until both reports
  pass. `published TAG --candidate-receipt PATH` invokes neither model and
  rebinds the exact tag, declared version, source tree, and both fresh installed
  trees to the candidate identity.
- DONE: The durable receipt is the minimum closed bridge: `schema`,
  `candidate_revision`, `version`, one `tree_sha256`, and one closed `reports`
  object containing Claude/Codex `PASS`. Per-host version/digest copies were
  removed. One `package_identity` seam and one `install_verified_plugin` seam
  now own the shared source and installation checks without hiding the explicit
  candidate-only model invocations.
- DONE: The packaged skill and smoke prompt state that the root, envelope,
  `engineering_judgment`, and every adjudication item are closed objects with
  exactly the documented keys and no extras, including `verdict_note`.
  `exact_object` remains strict and unchanged.
- DONE: RED evidence was observed before each behavior was implemented:
  producer guidance failed on `missing boundary: closed objects`; the mode seam
  reported missing candidate/published/receipt callables; candidate orchestration
  reported `invocations=[]; receipt=None`; strict receipt loading rejected the
  valid fixture as `not implemented`; published identity cases all reported
  `published mode is not implemented`; both CLI modes exited argparse 2; and the
  release-order assertion reported missing candidate-before-published commands.
  The subtractive reset then failed against the superseded receipt while both
  fake hosts had completed, printing its duplicated root/Claude/Codex identity.
- DONE: GREEN contract coverage uses fake command results and makes no provider
  call. It proves both candidate hosts run, an invalid Codex report leaves no
  receipt, root and `reports` receipt objects are closed, and published mode has
  no model invocation across the named tag, version, source-tree, Claude-tree,
  and Codex-tree falsifiers. The observed adjudication `verdict_note` regression
  remains direct; redundant root/envelope/judgment copies were removed because
  the existing `exact_object` paths already enforce them.
- DONE: Old-behavior fixture audit found no quiet narrowing: malformed,
  incomplete, misplaced, duplicate, invalid-enum, wrapper-mismatch, and
  wrong-revision scenarios retain their prior intent. The new adjudication extra
  fixture extends that population; no existing setup was repurposed.
- DONE: Fresh stage-exit evidence passes: kc-dev-flow contract; Python compile;
  40/40 skill frontmatters; version parity at 2.2.0; marketplace L0/L1/L2 for all
  seven plugins; state-prerequisite; 35/35 audit-link cases; and
  `git diff --check`. The exact marketplace-parity CI command body completed in
  25.96 seconds against its 300-second timeout, and a fresh isolated Codex
  local-path install resolved kc-dev-flow 2.2.0. The real authenticated candidate
  run remains clean committed-head validation evidence, not a deterministic test.

### Summary

Runtime compatibility now moves before publication while post-publication work
is identity-only. The final subtractive shape is 139 insertions smaller than the
rejected first packet (803 to 664), removes duplicated receipt identity and
shared installation logic, and preserves every named AC and falsifier.

The prior implementation and validation reports below are retained as historical
cycle-1 evidence. They do not satisfy the revised ACs.

## Stage Report: validation

- DONE: Exact clean head `24d91bb0...` ran real isolated authenticated Claude
  and Codex candidate mode; both strict reports passed and the closed receipt was
  written only afterward.
- FAILED: AC-3's first-containing-tag published proof is unavailable because no
  tag contains exact head; deterministic published mode rejects all named
  identity mutations and records zero model invocations.
- DONE: Fresh exact-head EM and evidence block maps all four changed files to
  ACs with zero unmapped files and made no deliverable edits.

### TL;DR

Exact-head candidate validation passes at
`24d91bb0af0b53fd0b18b882e79c538419115cb2`: real authenticated isolated
Claude and Codex installs both returned strictly accepted reports, and the
closed receipt records version `2.2.0` plus tree
`be81769f994b031e92d543fdad46c2b02af33688c1a24eda32cbd6bd19461e37`.
The four-file implementation has no supported Material finding. Do not
terminalize or make a release-complete claim: no tag contains this commit, and
the future version-bumped Release PR head needs its own fresh candidate receipt
before the resulting tag can run real `published` identity closeout.

### Per-AC verdicts

- **AC-1 PASS at exact implementation head** — a clean real invocation of
  `scripts/kc-dev-flow-published-tag-smoke.py candidate` installed the current
  tree through isolated Claude and Codex state, invoked both authenticated
  hosts, strictly accepted both reports, and wrote the five-key receipt only
  afterward. A direct invalid-Codex case invoked both hosts and left no receipt;
  dirty-checkout and pre-existing-receipt probes both refused before model work.
  This verdict would flip if either host could be skipped, an invalid report
  left a receipt, or the eventual Release PR candidate did not repeat the proof.
- **AC-2 PASS** — the exact packaged skill and smoke prompt close the root,
  envelope, `engineering_judgment`, and adjudication objects; the unchanged
  `exact_object` consumer rejected `verdict_note`. Weakening that guard in a
  disposable detached copy made the contract suite fail on the same extra
  field. This verdict would flip if an extra field exited zero or the producer
  guidance again permitted it.
- **AC-3 NOT DONE at the release boundary** — deterministic published-mode
  checks reject extra/duplicate receipt fields and mutations to schema,
  revision, version, digest, tag, source tree, Claude tree, and Codex tree; the
  valid simulation records `host_invocations=[]`. A real auth-free Codex local
  install also resolved version `2.2.0` and the exact candidate digest, closing
  the independent reviewer's only plausible Material liveness concern. The
  required first-containing-tag execution is impossible today because refreshed
  tags contain no `24d91bb0...`; this verdict becomes PASS only when a fresh
  Release PR candidate receipt and its exact resulting tag complete the real
  `published` command without model invocation.
- **AC-4 PASS** — `git diff-tree` reports exactly four modified existing files,
  `664` insertions and `90` deletions: `CLAUDE.md` maps to AC-4, the packaged
  Science Officer skill maps to AC-2, and the existing contract test and
  existing smoke script map to AC-1 through AC-4. There are zero unmapped files,
  no workflow/version/publication/local-sync/PR/fifth surface, and the release
  instructions order candidate before published before local sync. This verdict
  would flip on a fifth file, second smoke mechanism, parser relaxation, or
  reordered trigger.

### Evidence block

`Lenses:` PASS at candidate scope — Read exact
`24d91bb0af0b53fd0b18b882e79c538419115cb2` over
`54913dda3e5e66841e043025bf646e0ad2493bc9` in `CLAUDE.md`,
`kc-dev-flow/skills/science-officer-em/SKILL.md`,
`scripts/kc-dev-flow-contract-test.py`, and
`scripts/kc-dev-flow-published-tag-smoke.py`. Correctness fired (0 supported
Material, 3 Advisory residuals), silent-failure fired (0 Material; all named
invalid inputs refused), type-design fired (0 findings; receipt/report objects
are closed), security fired (0 findings after the auth-free Codex install
falsified the only plausible concern), resource-lifecycle fired (0 findings;
temporary homes/checkouts are bounded), and manifest/back-compat fired (0
Material; both installed candidate hosts resolved the packaged skill). Security,
type, lifecycle, and manifest verdicts would fail on auth leakage, an accepted
identity extension, leaked persistent state, or an installed-host mismatch;
correctness/silent-failure would fail on any named mutation exiting zero.

`Diff coverage:` PASS — Coverage.py plus diff-cover read the executable delta
from `54913dda3...` to exact head `24d91bb0...` in the two changed Python files:
the contract test is `100%`, the smoke is `86.2%`, and total changed-line
coverage is `93%` (`243` lines, `16` missing). This field would fail below the
`85%` executable ratchet; Markdown behavior is covered by the real installed
invoke rather than line coverage.

`Adversarial:` PASS — The focused exact-head harness rejected
`verdict_note`; receipt root/report extras, duplicate key, wrong schema,
revision, version, digest, and report state; and published tag/version/source/
Claude-tree/Codex-tree mutations while keeping published host invocations empty.
A disposable `24d91bb0...` copy with `exact_object` weakened went RED on
`extra verdict_note`. This field would fail if that claim-breaking edit stayed
green or any identity mutation invoked a model or exited zero.

`Cross-model:` PASS — After `agy` Opus, Gemini Pro, and Sonnet attempts each
returned an observed timeout, fresh safe-mode Claude Opus 5 session
`c73ae360-547d-4170-8080-1a2247933ed3` read the exact current/base copies of all
four paths with only Read/Grep/Glob and no hooks, plugins, MCP, Bash, or writes.
It returned `proceed / medium-high`, one plausible Material and six Advisories;
the Material Codex-auth concern was then falsified through the exact auth-free
install helper (`PASS`, no `auth.json`, matching version and digest). This field
would fail on a supported file-cited Material defect or a reviewer bound to the
wrong revision.

`E2E:` FAIL — Read and ran exact-head
`scripts/kc-dev-flow-published-tag-smoke.py`: the real candidate half passed
both authenticated installed hosts and emitted the closed receipt, but refreshed
Git tags contain no `24d91bb0...`, so the real published half cannot run. This
field would pass only after a clean version-bumped Release PR head repeats
candidate and its resulting exact tag passes published identity binding with no
model invocation; either host/report failure, identity mismatch, or post-release
model call would fail it.

`Origin re-observation:` FAIL — Reported scenario: a published kc-dev-flow tag
is the already-validated Release PR candidate and published mode invokes no
model | Originating runtime kind: authenticated installed Claude/Codex CLIs plus
published-tag installers | Re-observation artifact/revision: candidate-only
receipt for `24d91bb0af0b53fd0b18b882e79c538419115cb2`; no containing tag exists |
Equivalent-runtime rationale: the candidate run matches the actor, instrument,
local install, auth, prompt, and strict report path, but cannot match the future
Release PR version/tree or exact tag delivery path | Falsifier kind:
existence-disproof | Result: no containing tag exists, so publication identity
remains unobserved and this field stays not-done.

### Engineering judgment

- `question:` Does exact commit `24d91bb0...` provide the smallest valid
  pre-release dual-host proof and post-release identity-only mechanism without
  claiming the not-yet-existent release artifact?
- `revision:` `24d91bb0af0b53fd0b18b882e79c538419115cb2` over
  `54913dda3e5e66841e043025bf646e0ad2493bc9`.
- `evidence_synthesis:` Real candidate receipt, focused closed-schema and
  identity refusals, one RED guard mutation, auth-free Codex installation, 93%
  executable diff coverage, full repository gates, refreshed tags, and fresh
  cross-vendor exact-head review all agree on the implementation-head result.
- `adjudications:` AC-1, AC-2, and AC-4 pass. AC-3's deterministic boundary
  passes but its accepted real published-tag observation remains open. The
  Opus Material hypothesis is unsupported after the exact auth-free install
  passed; its remaining advisories do not justify a fifth implementation
  surface before the real tag falsifier.
- `risk_tradeoff:` proceed with the four-file mechanism rather than adding CI,
  credentials, or persistence. Preserve the release boundary: rerun candidate
  on the actual Release PR head because its version/tree will differ from this
  feature head, then use only that receipt for published closeout.
- `recommendation/route/confidence:` proceed to the release boundary while
  keeping this entity in validation / `proceed` / high on the implementation,
  low until published-runtime liveness is observed.
- `dissent:` The independent reviewer notes that the prompt itself can elicit
  the closed shape even if packaged-skill guidance were absent, and that two
  receipt-extra assertions can reject for a broad `extra=` reason. Static skill
  guidance checks plus the direct report mutation preserve the accepted
  boundary; retain these as Advisory residuals rather than expanding scope.
- `disproof_condition:` return to implementation if the actual Release PR
  candidate cannot produce both strict reports and a closed receipt, or if the
  resulting published tag fails version/source/installed-tree binding, accepts
  a receipt mutation, or invokes a model.
- `authority_boundary:` advisory only. Captain and release workflow retain PR,
  merge, version, tag, publication, local-sync, scope, and terminal state
  authority.

## Measurement

- Exact implementation scope: 4 existing files, `+664/-90`, 0 unmapped.
- Executable diff coverage: `93%` across 243 changed lines; smoke `86.2%`,
  contract `100%`.
- Real candidate artifact: schema `kc-dev-flow-candidate-smoke/v1`, revision
  `24d91bb0af0b53fd0b18b882e79c538419115cb2`, version `2.2.0`, tree
  `be81769f994b031e92d543fdad46c2b02af33688c1a24eda32cbd6bd19461e37`,
  reports `Claude=PASS`, `Codex=PASS`.
- Full-suite evidence: release metadata `32/32`, skill-frontmatter fixture
  `12/12`, live frontmatter `40/40`, plugin-release contract `11/11`, work
  context `23/23`, state prerequisite PASS, marketplace L0/L1/L2 PASS for all
  seven plugins, audit-link `35/35`, Python compile PASS, contract PASS, and
  `git diff --check` PASS.

## Historical Stage Report: implementation (cycle 1)

- DONE: Commit `c48a9e97f1614d80d8220ac4c80b4df993db09fb` adds the one
  release-closeout script, its direct report-contract fixtures, and the bounded
  root release instruction.
- DONE: Claude runs with plugin autoload disabled and must report exactly one
  explicit kc-dev-flow plugin at the expected path/version; Codex uses a clean
  temporary home that reuses only operator authentication.
- DONE: Both installed plugin trees digest-match the canonical exact-tag clone;
  the nested EM revision must equal the tag commit and every duplicated wrapper
  value must match.
- DONE: Direct fixtures reject malformed, incomplete, misplaced, duplicate,
  invalid-enum, wrapper-mismatch, and wrong-revision records before provider
  execution.
- DONE: Fresh stage-exit checks pass: kc-dev-flow contract, 40 skill
  frontmatters, version parity at 2.1.0, marketplace L0/L1/L2, state-prerequisite
  contract, Python compilation, and `git diff --check`.

### Summary

The implementation is the accepted release-only shape and is self-contained for
fresh validation. The next exact tag invocation remains a release-closeout step.

## Historical Stage Report: validation (cycle 1)

### TL;DR

Fresh Claude Opus high session `d4daa8b0-ea12-4c8f-9ccc-a086ae9a8edd`
reviewed exact head `c48a9e97f1614d80d8220ac4c80b4df993db09fb` over
`a024b254e236f521d8438d567ade36d779a52d11` and returned
`proceed / high / multi_model:not_needed`, with zero Material findings. This is
candidate-code validation; the first tag containing the command and its local
sync are still release-closeout evidence, so the task stays in `validation`.

### Per-AC verdicts

- **AC-1 PASS** — the requested canonical tag resolves to one commit and both
  installed trees must digest-match that checkout; a wrong revision/tree is
  fail-closed.
- **AC-2 PASS** — post-correction Claude isolation reported one explicit
  kc-dev-flow plugin at the expected path/version; Codex reuses only operator
  auth in a temporary home.
- **AC-3 PASS** — direct fixtures reject missing, extra, duplicate, misplaced,
  invalid-enum, mismatched-wrapper, and wrong-revision reports.
- **AC-4 PASS** — `CLAUDE.md` places the command after tag publication and
  before local sync and explicitly excludes per-PR gating.

### Evidence block

`Lenses:` Runtime/platform, contract/schema, correctness, auth isolation, and
delivery fired; all PASS with zero Material findings against exact head above.
No concurrency or persistent-resource surface exists: temporary directories and
subprocess failures are bounded and fail-closed. Would fail on an extra Claude
plugin, unequal installed tree, malformed record, or revision mismatch.

`Diff coverage:` coverage.py reports 39% aggregate for the full new script under
the repeatable local contract suite (99/239 statements; 100 branches, 10 partial).
The uncounted authenticated orchestration is covered by the prior dual-host
v2.1.0 invocation plus post-correction isolation/install probes and remains a
release-only exact-tag check, not a unit-test substitute.

`Adversarial:` PASS — malformed/incomplete/misplaced/duplicate/invalid-enum/
wrapper-mismatch/wrong-revision fixtures all fail; plugin-count and tree-digest
mismatches are explicit refusal paths. Would fail if any bad fixture exited 0.

`Cross-model:` not_needed — the exact-head EM found no contested, irreversible,
low-confidence, or unresolved call. No optional second model was requested.

`E2E:` PASS, bounded — the v2.1.0 exact-tag one-off invoked both clean-installed
hosts; post-correction probes on this commit observed `plugins_count=1` for
Claude and equal Claude/Codex installed trees. The first execution from a tag
that contains this command is intentionally deferred to release closeout.

`Origin re-observation:` PASS — Reported scenario: an exact published kc-dev-flow
tag installs and invokes through Claude and Codex | Originating runtime kind:
authenticated installed host CLIs | Re-observation artifact/revision: v2.1.0 tag
`a024b254e236f521d8438d567ade36d779a52d11` plus corrected wrapper commit
`c48a9e97f1614d80d8220ac4c80b4df993db09fb` | Equivalent-runtime rationale:
same host CLIs, canonical repository, tag resolver, plugin layouts, and operator
authentication; the correction probes isolate plugin state and bind tree bytes |
Falsifier kind: mutation | Result: both host invocations passed, one Claude plugin
was observed, and both installed trees matched the tag checkout.

### Engineering judgment

- `question:` Does the retained release-closeout smoke prove the accepted exact
  tag, dual-host, isolation, and report boundaries without excess mechanism?
- `revision:` `c48a9e97f1614d80d8220ac4c80b4df993db09fb` over
  `a024b254e236f521d8438d567ade36d779a52d11`.
- `adjudications:` the prior isolation, structural-parser, revision/tree-binding,
  and recovery-version findings are closed; no whole changed file or smoke
  mechanism is removable without losing an AC or falsifier.
- `risk_tradeoff:` retain one substantial authenticated release-only check to
  cover boundaries the cheaper marketplace and sync helpers do not observe;
  avoid the higher recurring cost of a per-PR model matrix.
- `recommendation/route/confidence:` proceed / proceed / high.
- `dissent:` empty. `multi_model:` not_needed.
- `disproof_condition:` change route on an extra Claude plugin, unequal installed
  tree, accepted malformed/wrong-revision report, or unmapped changed file.
- `authority_boundary:` advisory only; Captain, Spacedock, GitHub checks, and
  release-please retain scope, state, PR, merge, tag, release, and sync authority.

### Exact-head PR rebind

Fresh PR-level Claude Opus high session
`53ca4a4a-e114-4a4b-9412-ae0fbb0c0e0a` rebound AC-1, AC-2, AC-3, and AC-4 to
`454507f7ba56ce79ca0414f1964af4e59126eea5`. The intervening delta changes no
smoke script, parser fixture, `CLAUDE.md` release placement, workflow file, or
host invocation surface; the new kernel rule preserves the pending smoke and
leaves its keep-or-remove decision captain-owned. Hosted CI is green at that
exact head. Verdict remains `proceed / high`, with zero Material findings; the
first containing-tag invocation remains release-closeout evidence.

## Exact-head candidate validation — `76614da671eaf29e9bed2147aae4e4f9f390af84`

Fresh Claude Opus high session `317c8a98-df85-4baa-8a48-c780d51e55b9`
returned `proceed / high`, AC 4/4 at candidate scope, zero Material findings,
and `multi_model: not_needed`. The same session corrected its output envelope
without changing evidence or verdict.

- `Lenses:` release placement, installed-tree binding, host isolation, report
  schema, and delivery sequencing pass.
- `Diff coverage:` all smoke paths map to AC-1 through AC-4; the subtractive
  correction changes no host invocation or release placement.
- `Adversarial:` malformed, duplicate, mismatched, and wrong-revision records
  fail; installed-tree and plugin-count mismatches remain refusal paths.
- `Cross-model:` not_needed — no contested, irreversible, low-confidence, or
  unresolved call remains.
- `E2E:` bounded PASS — prior v2.1.0 same-kind Claude/Codex host probes plus
  current exact-head contract, tree-digest, and isolation instruments.
- `Origin re-observation:` bounded PASS — Reported scenario: exact published
  kc-dev-flow tag installs and invokes through Claude and Codex | Originating
  runtime kind: authenticated installed host CLIs | Re-observation
  artifact/revision: v2.1.0 host probes plus candidate
  `76614da671eaf29e9bed2147aae4e4f9f390af84` | Equivalent-runtime rationale:
  same host CLIs, tag resolver, plugin layouts, operator authentication, and
  report contract | Falsifier kind: mutation | Result: prior host probes and
  current refusal instruments pass; the first containing-tag run remains open.

The sequencing boundary is intentional: release-please must create the first tag
that contains this command before its closeout smoke can run. Do not terminalize
this task until that tag records a keep-or-remove disposition.

### Feedback Cycles

- Cycle 1: REJECTED — `kc-dev-flow-v2.2.0` release-closeout smoke; keep one smoke mechanism across two triggers because it caught a producer/consumer closed-schema mismatch absent from pre-release checks; surface 1 mechanism vs estimate 1 mechanism (0%); AC narrowed: pre-release owns host/report validation, while post-release owns tag/version/tree identity
