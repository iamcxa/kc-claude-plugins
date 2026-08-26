# Proportional Production delivery contract

This contract keeps one KC Dev Flow workflow, the POC, Pilot, and Production
profiles, and the workflow's superset state graph. It defines three interfaces:
a bounded Production recovery route, Captain-owned UAT at every profile's
verification exit, and explicitly authorized per-item auto-merge. The first
implementation slice changes only Production recovery; the other two interfaces
have separate implementation boundaries.

The implementation must preserve `kc-dev-flow-work-profile/v3` and compatible
v2/v3 full-route receipts. It must not add a workflow state, profile, CI job,
release action, or Spacedock engine dependency.

## Keep authority separate from evidence

| Decision or fact | Owner | Boundary |
|---|---|---|
| Profile, accepted scope, recovery eligibility, and recovery fallback | Captain | A worker may recommend; the committed work item records the decision. |
| Route resolution and stage dispatch | First Officer | The repository loader decides whether the committed receipt is valid; the First Officer does not infer missing fields. |
| Focused and full test results | Named deterministic checks | A green check supplies evidence, not scope, UAT, merge, or release authority. |
| Specialist or RoboRev findings | Named reviewer | Findings are advisory evidence; they cannot advance, merge, or release. |
| UAT approval | Captain | A delegated runner may exercise the candidate but cannot approve its own evidence. |
| Per-item merge authorization | Captain | Authorization covers one work item and delivery artifact under stated conditions; it is not repository-default authority. |
| Merge execution | Existing delivery provider | It acts only after the authorized conditions are green for one observed head/base pair. |
| Release authorization | Captain or declared release owner | UAT, merge authorization, and a successful merge do not authorize release. |

Missing, stale, contradictory, or malformed evidence is non-green. No provider,
worker, or profile label can manufacture an authority named in this table.

## Route a bounded Production recovery

### Extend v3 without replacing the full route

The ordinary Production receipt remains:

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: production
  route: [shape, build, verify]
```

An eligible recovery uses the same v3 receipt and selects the shorter route.
Angle-bracket values below are field types, not unresolved design decisions:

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: production
  route: [build, verify]
  recovery:
    failure_revision: <full-40-hex-git-object>
    failure_falsifier: <repository-owned command or observable scenario>
    shape_revision: <full-40-hex-git-object>
    shape_evidence: <repository-relative-path#heading>
    scope_heading: <unique-level-2-work-item-heading>
    scope_sha256: <sha256-of-that-section-body>
    scope_paths: [<repository-relative-prefix>, ...]
    full_without_it: <repository-owned full-suite command>
    review_risks: [none]
    fallback: full-production
    authority: <captain identity>
    authorized_at: <RFC3339 timestamp>
```

This is an additive v3 form, not a new receipt version. The loader accepts the
short route only for `selected: production` with every recovery field concrete.
It rejects v2 short routes, non-Production recovery blocks, placeholders,
non-full Git object IDs, a missing or mismatched scope digest, absolute or
escaping scope paths, an empty risk list, and `none` combined with another risk.
A full-route v2 or v3 receipt takes the existing path and needs no recovery
fields or migration.

`shape_revision` is the full Git object in the state authority that contains
`shape_evidence`; together they bind the previously accepted Production shape.
`failure_revision` is the code-repository Git object where
`failure_falsifier` observes the failure.
`scope_heading` names one level-2 section in the work item, and `scope_sha256`
binds the exact UTF-8 bytes after that heading through the next level-1 or
level-2 heading. `scope_paths` is the complete allowed implementation boundary.
`full_without_it` names the existing full suite that must expose the missing
fix. The loader hash-binds the exact work-item bytes as it does for every
selected route. The closed risk names are `behavior`, `contract-schema`,
`state-concurrency`, `security-privacy`, `runtime-platform`, and `delivery`;
`none` must be the sole list member.

### Use the superset graph without an ideation dispatch

Spacedock's existing backlog gate advances to `ideation` because that state is
next in the shared graph. For a valid recovery receipt, the loader returns an
additive `skip_to_workflow_stage: implementation` result and loads no stage
contract. The First Officer re-reads the committed item, applies the existing
status transition to `implementation`, and invokes the loader again. No
ideation worker, briefing, stage report, or synthetic gate is created.

At `implementation`, the loader returns Production `build`; at `validation`, it
returns Production `verify`. Ordinary Production still loads `shape`, `build`,
and `verify`. The POC and Pilot mappings do not change. Tests must exercise the
real Spacedock transition so the skip is not inferred from loader prose alone.

### Fail closed when the premise changes

The recovery route is eligible only while all of these remain true:

- the failure still reproduces at `failure_revision` with the named falsifier;
- the accepted Production shape exists at `shape_revision` and still covers the
  same journey, lifecycle, compatibility, and authority boundary;
- the exact body of `scope_heading` still matches `scope_sha256`;
- every changed path is equal to or below one `scope_paths` prefix;
- no new dependency, public contract, migration, permission, data boundary,
  irreversible action, operational owner, or accepted claim enters the work;
- `full_without_it` resolves to a repository-owned command that can run on a
  fresh checkout; and
- the risk list still describes the implementation.

The loader refuses malformed static evidence. The First Officer and stage owner
recheck the behavioral and diff conditions before the skip, at implementation
exit, and before validation verdict. Any false or uncertain condition produces
`RECOVERY_FULL_ROUTE_REQUIRED`; under the receipt's `fallback: full-production`,
the authorized work-item writer records the invalidation and restores
`route: [shape, build, verify]`, then returns the item to `ideation` through the
existing state owner before any further stage dispatch. Scope expansion still
returns to the Captain; the fallback does not approve a larger scope.

A changed work-item body invalidates prior loader output. A changed candidate
invalidates implementation-exit and validation evidence. A changed merge base
invalidates delivery evidence. These invalidations do not change the selected
Production profile or grant a schema migration.

### Make evidence proportional and falsifiable

Build owns focused red-green evidence for the named failure and relevant seam.
It does not pay for the full negative control. Validation owns two fresh
observations:

1. run the accepted full suite on the exact candidate and require green; and
2. in a fresh isolated checkout, reverse only the implementation delta while
   retaining the candidate's tests and other proof changes, record the reverse
   patch digest and resulting tree identity, run `full_without_it` once, and
   require the named failure to return.

The second observation is the single fresh full without-it. A command that does
not fail, fails for an unrelated reason, cannot isolate the recovery diff, or
depends on unrecorded machine state supplies no proof. A candidate change after
either observation requires fresh affected evidence; validation does not reuse
the build worker's red run as the full without-it.

For a recovery receipt with `review_risks: [none]`, the Production label alone
does not activate the RoboRev implementation-exit observation. Any named risk
activates the existing typed review observation when its repository
precondition is met; unavailable review remains honest evidence and never
replaces deterministic validation. Verification may select a named specialist
only for a risk that actually fired.

### Observe the route in order

1. **OBSERVED:** `profile-contract-loader.test.py` at base `5707a6f` passes and
   loads the current item at `ideation` as Production `shape`, with next state
   `implementation`.
2. **DESIGNED:** `choose-work-profile` presents recovery only after the Captain
   keeps Production and the complete recovery fields can be recorded.
3. **DESIGNED:** the loader validates the short v3 receipt at `ideation`, emits
   the skip result, and loads no ideation contract.
4. **DESIGNED:** the First Officer re-reads the same committed work item, moves
   it to `implementation`, and re-invokes the loader.
5. **DESIGNED:** build reproduces the named failure, changes only allowed paths,
   and records focused red-green evidence. Interruption leaves the item in
   `implementation`; restart revalidates the receipt and diff before work.
6. **DESIGNED:** risk-selected implementation review runs at most through the
   existing typed observation. Timeout or unavailability is recorded and
   carried into validation.
7. **DESIGNED:** validation runs the exact-candidate suite and one fresh full
   without-it. Failure returns to one repair owner; a changed premise returns to
   full Production shape.
8. **DESIGNED:** Production verify retains exact-revision rollout, rollback,
   ownership, Captain release authority, and terminal merge-guard boundaries.

Observable changes are limited to accepted v3 receipt grammar, loader output for
the recovery skip, route selection, implementation-review activation, and the
required validation evidence. Stored Spacedock gate records and the workflow
state graph do not change.

## End every profile with Captain-owned UAT

This interface belongs to `profile-uat-boundary`, not to the recovery slice.

Each profile's verification stage ends with one UAT decision recorded by the
Captain. POC uses it to accept the experiment conclusion, Pilot uses it to
accept the bounded user journey, and Production uses it to accept the operated
journey. The verification worker may prepare evidence but may not record the
approval.

UAT has two evidence modes:

- **attended:** the Captain operates the named journey against the candidate;
- **delegated exact-candidate E2E:** a delegated runner executes the named
  end-to-end scenario against the bound candidate and returns the artifact for
  the Captain's decision.

Both modes bind work-item ID, candidate head, merge-target base, scenario,
environment identity, evidence artifact digest, actor, timestamp, and decision.
Delegation transfers execution only. The Captain remains the approving actor,
and a runner cannot approve evidence it produced.

A changed head, merge-target base, accepted scenario, material environment, or
evidence artifact invalidates UAT. Provider check refreshes and prose edits that
do not alter those bound values do not. A rejection or missing Captain decision
keeps verification non-green. UAT approval grants neither merge nor release.

## Merge only an explicitly authorized work item

This interface belongs to `work-item-auto-merge`, not to the recovery slice.
Manual merge remains the default for all receipts and is required for the
recovery slice itself.

Advance auto-merge authorization binds one work-item ID, one delivery artifact,
one target branch, the accepted scope, the required evidence set, the Captain
identity, and a timestamp. It authorizes the existing delivery provider to
merge a later exact head/base pair when, in one fresh pre-merge observation:

- Captain-owned UAT is green for that head/base pair;
- every required CI check is terminal and green;
- provider feedback is fully dispositioned with no blocking thread;
- the artifact is open, mergeable, and points to the authorized target;
- head and base still equal the values used by those checks; and
- no scope, profile, delivery artifact, target, or authorization condition has
  changed.

A new head or base clears collected evidence and causes re-evaluation; it does
not create a second merge decision while the item remains inside the authorized
scope and artifact. Scope, profile, artifact, target, or condition drift cancels
auto-merge authority and returns to the Captain. Unknown, pending, skipped, or
stale evidence is non-green. The provider must re-read head and base immediately
before its merge call and fail closed on movement.

The authorization is per item, never a repository default. It cannot mark a
Draft ready, expand scope, accept red evidence, bypass branch protection,
publish, deploy, migrate data, or release. A merge completes delivery only;
manual release authority remains separate.

## Limit the recovery implementation boundary

The delivery base is `5707a6f`. The slice changes only the recovery route and
its package/adopter parity, tests, and current contract documentation. It does
not implement UAT or auto-merge.

| Path | Lines now | Estimated lines after | Obligation |
|---|---:|---:|---|
| `kc-dev-flow/scripts/profile-contract-loader.py` | 332 | 430 | Validate additive v3 recovery and emit the ideation skip. |
| `docs/dev/_mods/profile-contract-loader.py` | 332 | 430 | Keep the adopter's vendored loader byte-identical. |
| `kc-dev-flow/scripts/profile-contract-loader.test.py` | 1237 | 1470 | Prove legacy, eligible, malformed, stale, and drift refusal cases. |
| `kc-dev-flow/scripts/profile-spacedock-route.test.py` | 333 | 430 | Exercise the real superset-graph skip and terminal route. |
| `scripts/kc-dev-flow-contract-test.py` | 903 | 980 | Guard route grammar, typed review selection, and vendor parity. |
| `scripts/kc-dev-flow-minimal-stack-ablation.test.py` | 312 | 360 | Mutate away one recovery guard and require rejection. |
| `kc-dev-flow/references/kernel.md` | 184 | 205 | State the full default and eligible short route. |
| `docs/dev/_mods/kernel.md` | 184 | 205 | Keep the adopter's vendored kernel byte-identical. |
| `kc-dev-flow/references/profiles/production/build.md` | 72 | 88 | Bind focused proof, scope recheck, and risk-triggered observation. |
| `docs/dev/_mods/profiles/production/build.md` | 72 | 88 | Keep the adopter's Production build contract byte-identical. |
| `kc-dev-flow/references/profiles/production/verify.md` | 65 | 88 | Own the fresh candidate and one full without-it evidence. |
| `docs/dev/_mods/profiles/production/verify.md` | 65 | 88 | Keep the adopter's Production verify contract byte-identical. |
| `kc-dev-flow/skills/choose-work-profile/SKILL.md` | 104 | 140 | Ask one coupled Production-route decision and emit the receipt. |
| `kc-dev-flow/skills/continue-dev-flow/SKILL.md` | 147 | 200 | Apply the skip and recheck invalidation without dispatching shape. |
| `kc-dev-flow/README.md` | 159 | 185 | Describe the full default and explicit recovery variant. |
| `kc-dev-flow/MIGRATION.md` | 198 | 225 | State that old receipts need no migration and mixed versions fail closed. |

The implementation stops and reports when the diff against `5707a6f` reaches
17 changed files, 901 changed lines, or 281 changed lines in
`profile-contract-loader.test.py`. It also stops immediately if correctness
requires a receipt schema version change, a new executable or persistent
ledger, a Spacedock engine change, a new CI job, or edits to either later S5
interface. These are stop conditions, not budgets.

Rollback is one feature-commit revert plus restoration of the byte-identical
adopter copies. Because legacy full routes remain accepted and no stored record
is migrated, rollback requires no receipt rewrite. Any recovery item active at
rollback is mechanically restored to the full Production route before the older
loader is used.

## Prove the recovery slice

- Unit fixtures show unchanged v2/v3 Production receipts still load
  `shape -> build -> verify` and an eligible v3 receipt loads only
  `build -> verify`.
- Refusal fixtures cover every missing field, malformed Git object, unsafe path,
  invalid risk list, v2 short route, non-Production recovery, and short route at
  an unsupported state.
- The live Spacedock fixture observes backlog landing at `ideation`, the loader's
  skip result, no ideation dispatch artifact, implementation and validation
  loads, and terminalization through the existing merge guard.
- A scope-drift fixture changes one path outside `scope_paths` and requires
  `RECOVERY_FULL_ROUTE_REQUIRED` before validation.
- A review fixture proves `[none]` performs no RoboRev activation and a named
  accepted risk activates the existing typed observation without making it a
  gate.
- A fresh-checkout fixture proves the declared full suite is green with the
  candidate and fails for the named reason when only the recovery diff is
  removed while its tests remain. Mutating away that check must make the
  ablation suite fail.
- The existing contract, route, package-parity, and repository gates remain
  green. CI uses the existing release-gate job; measured incremental CI cost is
  not yet available and no cost number is claimed.

Delivery is one Captain-reviewed PR to `main`. The PR remains manual merge for
this slice, and release remains separately authorized.

## Recover the existing mechanism before adding one

```yaml
reverse_recovery:
  trigger: add an eligible Production route and change its review activation
  boundary: work-profile receipt through loader, dispatch, build, and verify in kc-dev-flow at 5707a6f
  layers:
    - surface: full Production receipt and loader route
      location: kc-dev-flow/scripts/profile-contract-loader.py:13-19,67-130,213-260
      completeness: WORKING
      need: REQUIRED
      evidence: profile-contract-loader.test.py passed and the live item loaded Production shape then implementation
      disproof_hook: python3 kc-dev-flow/scripts/profile-contract-loader.test.py
    - surface: Production recovery receipt and short route
      location: MISSING
      completeness: MISSING
      need: REQUIRED
      evidence: git-grep for short-route and recovery fields plus structural inspection of ROUTES and receipt validation found only the fixed full route
      disproof_hook: git grep -n -E '\[build, verify\]|production_recovery|recovery_route' -- kc-dev-flow
    - surface: implementation-exit review selection
      location: kc-dev-flow/references/profiles/production/build.md:55-72
      completeness: EXISTS_BROKEN
      need: REQUIRED
      evidence: the typed RoboRev observation works but currently activates from the Production build contract without recovery-risk discrimination
      disproof_hook: python3 scripts/kc-dev-flow-contract-test.py
    - surface: one fresh full without-it at Production verify
      location: MISSING
      completeness: MISSING
      need: REQUIRED
      evidence: git-grep and a bounded read of Production verify found exact-candidate checks but no recovery-diff negative control
      disproof_hook: rg -n -i 'without.it|full.*falsif' kc-dev-flow/references/profiles/production scripts
  decision: recover
```

The two missing layers extend the existing loader, contracts, and test harness;
they do not justify a second router, receipt store, review framework, or engine
feature.

## Keep this retained document stable

This design follows retained-document Rules 1-3 and 6-8: it states durable
obligations in present-tense normative form, keeps delivery status in the work
item, names executable checks for material claims, uses no mutable deployment or
version snapshot, and adds no diagram that needs a renderer.

The per-section overlap check used two strategies: concept search across
`kc-dev-flow`, `docs/dev/_mods`, `docs/dev/ROADMAP.md`, and existing specs; then
structural reads of the loader, kernel, Production contracts, continuation
skill, migration guide, validation runbook, and PR-merge mod. The boundary was
this repository at `5707a6f`; external adopter-specific controls were not read.

- **Recovery route:** README, kernel, chooser, continuation, loader, and
  migration currently own the live full-route claim. This spec owns the new
  eligibility rationale and invalidation contract; implementation replaces the
  affected live claims rather than leaving duplicate variants.
- **UAT:** the roadmap owns scheduling and profile verification contracts own
  current profile-specific exits. This spec owns the shared authority and
  invalidation interface until the later UAT item places concise runtime rules
  in those contracts.
- **Auto-merge:** the roadmap says it is scheduled, while `pr-merge.md` owns the
  current manual provider ceremony. This spec owns the conditional per-item
  authority interface; the later item must modify the provider's live claim
  rather than copying it into a second runbook.

Self-review found no `TBD`, `TODO`, bracket placeholder outside the illustrative
receipt, status promise, second tracker, or mutable current-version claim. The
defaults are explicit: full Production route, risk review only when named,
Captain-owned UAT, manual merge, and manual release. The recovery slice neither
implements nor implies the two later interfaces.
