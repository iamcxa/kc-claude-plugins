---
id: 92h25gk5mcagj6wtqrz24nsa
title: "kc-dev-flow: no stage reads PR review feedback, so a PASSED verdict can ship unread reviewer findings"
status: validation
source: https://github.com/iamcxa/kc-claude-plugins/issues/213
product: kc-dev-flow
sprint: S2
started: 2026-08-12T01:51:59Z
completed:
verdict:
worktree: /Users/kent/conductor/workspaces/kc-claude-plugins/montpellier-v1/.worktrees/kc-dev-flow-pr-feedback-gate
issue: "213"
pr: "#220"
mod-block:
design: required
lane: main
---

## Problem

The kc-dev-flow contract declares no stage that reads a pull request's review
feedback, so a task can close `validation` with an EM verdict of `proceed`, be
recorded `verdict: PASSED`, and reach the `done` gate while unresolved review
threads — including ones describing a regression the change itself introduced —
have never been read by any seat. The reporter's account is that `validation`
declares its inputs as the ACs plus the implementation stage report, which does
not include the PR; `_mods/pr-merge.md` owns PR lifecycle but touches reviews
only in its PR-body approval guardrail and never queries review state; and the
`done` gate turns on CI observed green, which is silent about open review
threads. The reported downstream instance is `iamcxa/qnow` PR #1057, where two
bot reviewers independently raised a filter/pagination reset regression that a
full flow — fresh-context validator, EM verdict, cross-model gate, and a browser
drive — did not surface, and which the browser drive reportedly could not have
surfaced because the branch data set was too small to reach page 2.

## Proposed approach

Protect the captain-approved feedback-safety value with one GitHub-native
observation at the existing PR lifecycle seam. At validation entry, before
Ready, immediately before merge, and before terminalization, resolve the
explicit repository and PR (or stack layer), pin `headRefOid`, paginate GraphQL
`reviewThreads`, and separately paginate REST PR-level reviews. Normalize
external reviewer items (bots included) into a sorted transient set.
Conversation-tab comments remain outside this slice. Startup and idle polling
are not required because they authorize no safety boundary.

The observer records only one compact `PR feedback:` record in the existing
validation report. It binds repository, PR number or stack-layer identity,
exact head, fingerprint scheme `github-pr-feedback/v1`, the population
fingerprint, and one disposition per normalized item ID. The canonical v1 input
sorts by kind then stable GitHub ID and covers each item's author, review state
or thread resolution state, commit ID when present, and a SHA-256 of every
mutable body/comment. Each `rejected-with-reason` includes its reason; each
`fixed` includes the fix revision and verification-evidence reference; each
`out-of-scope-and-filed` includes the filed work-item reference. The fingerprint
is necessary because GitHub review bodies and inline comments are mutable;
ID-only reuse can silently accept changed feedback. This extends the existing
stage report rather than creating another ledger, resolver result schema, or
provider framework.

Observation and repair stay separate. If
`kc-pr-flow:kc-pr-review-resolve` is installed, it may accelerate technical
triage. If it is absent or unavailable, do not install or simulate it: route the
complete normalized set to the ordinary implementation worker, return to fresh
validation after any code change, and keep Ready/merge blocked until a new
exact-head observation matches complete dispositions and their evidence. API,
repository/PR identity, parsing, pagination, head, fingerprint, disposition
reason, or filed-reference uncertainty is `UNKNOWN`, never clean.

Add `--assignee "@me"` to the one active canonical Draft `gh pr create`
command. The authenticated creator remains the author; the assignee becomes the
default owner for follow-through.

Fastest path: recut Draft PR #214 from fresh `origin/main` `281bd7f6` and repair
the existing `docs/dev/_mods/pr-merge.md` lifecycle seam. Retain the generic
provider-feedback invariant in the packaged kernel and its byte-identical
vendored copy, and bind validation/done in `docs/dev/README.md`. Delete the
special kc-pr-review-resolve integration change and the standalone plan; use the
existing contract-test files for RED/GREEN and known-mutant coverage.

Riskiest-assumption result: separation is viable, but a restartable gate cannot
safely use only item IDs. A live read-only probe of merged
`iamcxa/qnow#1057` at `ca1d613c` found two external non-empty PR-level reviews
and three raw external threads, all three resolved at that final head, while
`reviewDecision` remained empty. A positive live probe of open
`iamcxa/qnow#1124` at `ebddb0ab` found two unresolved external threads and one
external non-empty PR-level review, with complete first pages and
`reviewDecision` still empty. GitHub also exposes review-body and review-comment
update operations. Therefore one versioned observation fingerprint is the
minimum restart fact, but another durable feedback ledger and a resolver-side
integration mode are not necessary.

Pre-mortem: the accepted design ships but an edit, deletion, resolution change,
or new review lands after validation and before Ready. The failure would be
stale disposition reuse; the pre-Ready, pre-merge, and pre-terminal
identity/head/fingerprint re-observations must invalidate that report and
preserve Draft or pending state.

## Design determination

`design: required` — two independently violable value surfaces under the
captain-approved one-small-S2 scope exception: (1) fail-closed GitHub feedback
safety and (2) default creator ownership through self-assignment. The first
repairs the existing GitHub delivery seam: the dev-flow observer owns complete
GitHub reads, normalization, exact-head binding, and the delivery barrier; the
selected repair worker owns technical disposition; `kc-pr-review-resolve` is an
optional accelerator with no required integration contract. The second is one
flag in the already-canonical Draft creation unit. One implementation worker is
sufficient; these share the same delivery-policy files and together stay within
the captain's explicit appetite.

Reverse-recovery audit against `origin/main` `281bd7f6`:

| Surface | Completeness / need | Subtractive result and disproof hook |
|---|---|---|
| `docs/dev/_mods/pr-merge.md` PR lifecycle | `EXISTS_BROKEN` / `REQUIRED` by the validation-entry, Ready, merge, and terminalization consumers | Retain and repair: without provider observation, the qnow probes are invisible and AC1 fails. Disproof: a fresh grep/API walk finds an existing complete review read before every delivery boundary. |
| `docs/dev/README.md` validation and done stages | `EXISTS_BROKEN` / `REQUIRED` by stage actors | Retain and bind the observer result: without a declared input/disposition, AC2 fails. Disproof: current stage text already requires exact-head external feedback disposition. |
| packaged kernel plus vendored copy | `EXISTS_BROKEN` / `REQUIRED` by adopters and the local workflow | Retain one generic feedback-reentry invariant; byte identity is already enforced. Disproof: current kernel already makes late provider feedback invalidate validation. |
| `kc-pr-review-resolve` integration change from #214 | `WORKING_UNIT_UNPROVEN` / `NO_OBSERVED_CONSUMER` inside this slice; external consumers are out of scope | Remove from the recut: fallback route satisfies AC2 without changing the skill. Disproof: a fixture with the skill absent cannot reach the ordinary worker or cannot produce complete dispositions. |
| standalone plan or new feedback ledger | `MISSING` / `NO_OBSERVED_CONSUMER` inside repo workflow and delivery boundaries | Do not add: the entity and existing validation report own the decision and restart fact. Disproof: a restart cannot distinguish edited/new feedback using the compact fingerprint. |
| canonical Draft creation command | `EXISTS_BROKEN` / `REQUIRED` by PR creation | Repair in place with `--assignee "@me"`. Disproof: installed `gh pr create` lacks `--assignee` support or another active create path exists. |

Kernel subtraction result: the independently maintained surfaces are the
existing provider observer/barrier and the existing validation report. Removing
either fails a named AC; the optional resolver change, new ledger, and plan do
not. No new product runtime, service, schema file, or review framework advances.

## Acceptance criteria

**AC1 — GitHub-native observation is complete, exact-head, and fail-closed**

For every delivered PR or stack layer, dev-flow reads the explicit GitHub
repository and current `headRefOid`, all GraphQL review-thread pages within the
declared bounded comment-page contract, and all REST PR-review pages. It
normalizes external unresolved threads plus external non-empty or
`CHANGES_REQUESTED` PR-level reviews; any top-level or nested page reporting
unread data, incomplete response, ambiguous identity, or head drift returns
`UNKNOWN` and blocks the boundary. **Verified by:** contract and known-mutant
checks establish that the declared provider data path rejects missing REST
reviews, unread GraphQL pages, nested-comment overflow, author-filter inversion,
API failure, and head drift. Read-only same-kind probes establish provider
behavior: merged `qnow#1057@ca1d613c` yields two external non-empty reviews plus
three raw but zero unresolved external threads; open
`qnow#1124@ebddb0ab` yields one external non-empty review plus two unresolved
external threads, with complete first pages. **Falsifier:** a contract mutant
survives, or a live response contradicts the declared population rule.

**AC2 — Unread or undispositioned feedback cannot cross Ready or merge**

At validation entry, before Ready, immediately before merge, and before
terminalization, repository, PR or layer identity, current head, fingerprint
scheme, and feedback fingerprint must match a validation report with one
evidence-bearing disposition for every normalized item. A rejected item requires
its recorded reason; a fixed item requires its fix revision and verification
evidence reference; an out-of-scope item requires its filed work-item reference.
With
`kc-pr-review-resolve` absent, the complete set routes to the ordinary
implementation worker and remains blocked; a code change invalidates prior
validation. **Verified by:** contract decision-table and ordering mutants prove
the policy represents blocking for actionable feedback, missing resolver,
ambiguous identity, missing disposition evidence, changed head, changed
fingerprint, and provider `UNKNOWN`; fresh exact-revision validation owns the
behavioral judgment that the workflow follows those instructions. **Falsifier:**
a mutant removes one refusal and still passes, or fresh validation observes a
Ready/merge/terminal path that ignores a non-pass case.

**AC3 — The authenticated Draft creator owns follow-through by default**

The single active canonical Draft creation unit includes
`--assignee "@me"`, while the released disabled command remains untouched.
**Verified by:** the focused portable-delivery contract test plus a mutant that
deletes only the assignee flag. **Falsifier:** the mutant still passes, or more
than one active PR-create command exists.

**AC4 — The recut adds no second review framework or durable feedback ledger**

The #214 replacement changes no `kc-pr-flow/**` file, adds no feedback-state
file, and uses the existing validation report for the compact restart fact.
**Verified by:** the exact `origin/main...HEAD` file map plus contract and
known-mutant checks that require the optional-skill-absent route to name the
ordinary worker and remain fail closed; fresh validation verifies that no hidden
resolver dependency exists. **Falsifier:** delivery correctness requires a
resolver-side integration mode or a separate persistent store.

## Test plan

1. RED on fresh `origin/main`: the focused contract test must reject both the
   absent GitHub feedback barrier and the canonical create command without
   `--assignee "@me"`.
2. GREEN with contract and mutation coverage: check canonical v1 population
   fields, pagination failure, identity/head/fingerprint invalidation, fallback
   routing, gate ordering, stack per-layer coverage, disposition evidence, and
   self-assignment. Each mutant must name the policy/data-path property it
   removes; these checks do not claim agent behavioral compliance.
3. Run `scripts/kc-dev-flow-contract-test.py` and
   `scripts/pr-merge-portable-delivery.test.py`, then the existing version
   parity, frontmatter, marketplace, and sanitize checks earned by the diff.
4. Re-run live read-only GitHub probes against pinned merged
   `qnow#1057@ca1d613c` (resolved-thread case) and open
   `qnow#1124@ebddb0ab` (positive unresolved-thread case), recording raw and
   normalized counts plus pagination completeness. If the open head drifts,
   record the probe stale and choose a newly pinned equivalent; do not silently
   reuse it. No product UI E2E applies because this is workflow-policy/config
   behavior; the provider probes are the same-kind observation boundary and
   perform no GitHub mutation.
5. Fresh-context validation reviews the final recut against the exact new
   `origin/main` base and confirms the old #214 resolver modification and plan
   document are absent.

## Measurement

- Primary feedback-safety measure: every declared non-pass case in the
  feedback-blocking decision table is represented as refusing
  Ready/merge/terminal mutation until the same-identity, same-head observation is
  completely dispositioned; fresh validation reports zero observed unsafe
  transitions.
- Primary ownership measure: deleting only `--assignee "@me"` makes the focused
  canonical-create contract test fail.
- Scope measure: one implementation worker, two captain-approved value surfaces
  in the same existing delivery-policy seam, no
  `kc-pr-flow/**` diff, no new state file, and no product/architecture document
  change. The workflow README, pr-merge mod, kernel copies, and two existing
  tests are the six-file expected family.
- Comparison baseline: current Draft #214 is 392 additions/deletions across
  eight files and is based on `a18ba78f`; the recut must be based on fresh
  `origin/main` and remove the resolver-side integration and standalone plan.

## Doc diff

- `docs/dev/README.md`: declare GitHub feedback observation as validation input,
  record the compact fingerprint/dispositions, document fallback routing, and
  make current feedback proof a done prerequisite.
- `kc-dev-flow/references/kernel.md` and byte-identical
  `docs/dev/_mods/kernel.md`: add one provider-neutral late-feedback re-entry
  invariant; keep GitHub commands and routing out of the kernel.
- `docs/dev/_mods/pr-merge.md`: document the GitHub-native observation,
  fail-closed boundaries, optional accelerator/fallback, and self-assigned
  canonical Draft command.
- No `PRODUCT.md` change: its kc-dev-flow outcome already promises adoption of
  repository delivery authority without duplicating truth. No `ARCHITECTURE.md`
  change: this slice repairs local workflow policy and deliberately adds no new
  durable component or ownership boundary.

## Out of scope

- Auto-merge, automatic Ready, or any new merge authority.
- Auto-installing or requiring `kc-pr-flow` / `kc-pr-review-resolve`.
- A second review framework, generalized provider adapter, database, state file,
  or durable feedback ledger.
- Conversation-tab issue comments, automatic replies, or automatic thread
  resolution.
- Retrofitting every adopter or changing GitHub repository protection rules.

## Stage Report: backlog

Verdict: core claim CONFIRMED; issue's supporting detail is wrong in three
places. Defect lane does NOT hold — main route through ideation required.
Scope: `origin/main` @ `abf69f5`, clean tree, tags refetched.

- DONE: Verify or refute, at file:line against fresh origin/main, the issue's core claim that no kc-dev-flow stage, gate, or vendored mod declares reading a PR's review feedback — and state which result would have refuted it.
  CONFIRMED. Census over `docs/dev/README.md` + `docs/dev/_mods/*.md`: `review
  comment`/`review thread`/`bot review`/`automated review`/`reviewDecision`/
  `CHANGES_REQUESTED`/`dispositioned` = 0; `reviewer` = 26 (issue said 21).
  Over all of `kc-dev-flow/**`: same 0s except `dispositioned` = 4, all in
  `kc-dev-flow/scripts/absolutes-check.py` (absolutes registry, unrelated).
  Across all nine release tags `kc-dev-flow-v1.0.0`..`v2.3.0`: 0 — verified from
  git tags, not the plugin cache (no kc-dev-flow in this machine's cache).
  Concept census by other wordings (`copilot`, `PR review`, `review state`,
  `unresolved`, `feedback`, `gh api`, `resolve`) over the same population: no
  hit means a PR's review feedback. `docs/dev/README.md:24` `feedback-to:` is
  spacedock gate routing, a homonym. Behavioral corroboration, not tokens: the
  only `gh` PR reads request `state` (`docs/dev/_mods/pr-merge.md:13`) and
  `body,headRefOid,mergedAt` (`:197`, `:309`) — `reviews`, `reviewDecision`,
  `reviewThreads` are never requested. REFUTED BY: any of those `--json` field
  lists naming a review field, or any stage/gate clause requiring a review read.
- DONE: (same item) — where the issue is wrong or overstated
  (a) "none of the `reviewer` hits mean a GitHub reviewer" is false:
  `docs/dev/_mods/pr-merge.md:61,:70` mean the PR's reader, and `:243-244`
  imposes a real duty ("A reviewer must explicitly acknowledge the exception
  before the PR becomes ready or merges; author approval is insufficient"), as
  does `:281` ("each layer's required checks and review are green"). The
  contract is not silent about GitHub reviewers — it is silent about reading
  their findings. (b) The quoted validation Inputs ("the ACs and the
  implementation stage report") exist at no file:line here; that wording is the
  downstream adopter's own README, not anything kc-dev-flow ships. (c)
  `_mods/pr-merge.md` is not a kc-dev-flow mod: frontmatter `version:
  0.12.2+kc.1 / upstream-version: 0.12.2` (`:1-5`), stock = spacedock 0.26.0
  `mods/pr-merge.md`; `:1-100` is stock (only `:57` adds `--draft`), `:101-357`
  is a local kc-dev-flow extension. Spacedock is not one of this repo's plugins.
- DONE: (same item) — where Inputs and the done gate are actually declared, and which an adopter reads
  SHIPPED: `kc-dev-flow/references/kernel.md:39-49` (validation `:47-48`, done
  `:49` — one line each, no Inputs list) and
  `kc-dev-flow/skills/continue-dev-flow/SKILL.md:193-204` (EM verdict per gate;
  exact-head CI/runtime as delivery evidence; terminalize when every AC has
  fresh validation). NOT SHIPPED: the detailed stage sections —
  `kc-dev-flow/skills/adopt-dev-flow/SKILL.md:44-54` has the adopter add
  `Policy mods:` to its OWN workflow README and vendor kernel.md byte-for-byte.
  So `docs/dev/README.md:282-321` (validation) and `:327-332` (done, "required
  checks green on its exact HEAD") are this repo's local instance only. An
  adopter reads `_mods/kernel.md` (byte-identical to the shipped reference —
  `diff` empty) + the shipped skills + its own README; it never reads
  `docs/dev/README.md`.
- DONE: Determine whether the proposed fix can reuse existing capability rather than add a mechanism: establish whether kc-pr-flow in THIS repo actually ships a review-resolution skill, name it at its path, and record what it does and does not do.
  YES: `kc-pr-flow/skills/kc-pr-review-resolve/SKILL.md` (kc-pr-flow 1.11.1).
  DOES: fetch both unresolved inline `reviewThreads` (GraphQL) and PR-level
  reviews (REST) (`:91-114`); reviewer/is_ai map (`:116-129`); validate every
  comment on technical merit, forbidding both auto-accept and auto-dismiss
  (`:135-157`); cross-AI dedup by (file, conceptual issue) that surfaces
  parallel agreement (`:161-196`) — the incident's exact shape; verdict
  persistence (`:198-243`); triage + confirmation GATE (`:245-278`); reply to
  every thread, resolve, then re-query and assert unresolved (`:348-392`);
  `auto_confirm: off|reply_only|preapproved` (`:10-22`).
  DOES NOT: produce a verdict any stage consumes; know the entity, stage, ACs,
  or `verdict:` field; gate on an EM/FO seat (it gates on the user); or fail
  closed — `reply_only`/`preapproved` skip its own gate (`:288-331`). Nothing in
  kc-dev-flow or docs/dev invokes it (`git grep kc-pr-flow` over both returns
  only ROADMAP sprint labels and an artifacts script). Reuse is nonetheless
  demonstrated in this repo: `docs/ship-flow/_mods/pr-merge.md:290-305` already
  dispatches it and gates CLEAN/BLOCKING/PROMPT_CAPTAIN with a 2-round cap — but
  in ship-flow's mod, not dev-flow's. Constraint on reuse:
  `kc-dev-flow/references/engineering-judgment.md:122-125` and
  `kc-dev-flow/README.md:38` disclaim prescribing a delivery provider or
  thread-reply format, so naming this skill in the shipped kernel cuts against a
  stated boundary; naming it in this repo's local README does not.
- DONE: Return the backlog routing determination: whether the defect lane's four conditions hold, naming the first that fails, or whether the main route through ideation is required.
  Main route through ideation. FIRST FAILURE is condition 1: the reported root
  cause has no file:line here (the quoted Inputs sentence is absent), and the
  real anchor is an omission spread across `kernel.md:47-49`,
  `continue-dev-flow/SKILL.md:193-204`, `docs/dev/README.md:287-290` and
  `:327-328`, and `runbooks/validation-evidence.md:8-16` — which of those is
  "the" root cause IS the placement decision. Condition 2 is partly available
  and I decline to score it clean: `scripts/kc-dev-flow-contract-test.py`
  already pins stage prose by substring (`:1106-1112`), so a fails-before/
  passes-after assertion is mechanically writable, but `docs/dev/README.md:144-147`
  and `adopt-dev-flow/SKILL.md:59` disqualify a text match as proof of
  behavior — it would prove the clause was written, not that a seat reads a
  review. Condition 3 fails: seams span `references/kernel.md` + its vendored
  copy (`adopt-dev-flow:53,:56` forbids editing the vendored file, so both
  move), `continue-dev-flow/SKILL.md`, `docs/dev/README.md`, and the
  spacedock-owned `_mods/pr-merge.md`. Condition 4 fails: portable-vs-local
  placement, whether the kernel may name a sibling plugin, what "unresolved"
  means without a GitHub-specific API, and post-gate review arrival — which the
  issue explicitly leaves undecided — are all open.
- SKIPPED: independent verification of the downstream incident (iamcxa/qnow PR #1057)
  Not reachable from this checkout; treated as report, per the assignment.

### Could not determine

Whether `main` requires an approving review: `gh api .../branches/main/protection`
returns 404 and `.../rulesets` returns `[]`. That reads as "unprotected", but a
404 can also be a token-permission artifact and I could not distinguish the two.
If unprotected, nothing outside the contract catches an unread review here.

### Summary

The issue's core claim survives: across `kc-dev-flow/**` at every released tag
and across this repo's adopted `docs/dev/**`, no stage, gate, or vendored mod
declares reading a PR's review feedback, and the mod that touches PRs never asks
GitHub for a review field. Three supporting details are wrong — the `reviewer`
hits do include GitHub reviewers with a real duty, the quoted validation
"Inputs" sentence exists nowhere in this repository, and `_mods/pr-merge.md`
belongs to spacedock rather than kc-dev-flow. The capability the issue points at
is real and already wired in a sibling workflow here, but the fix's placement
(portable kernel vs local README vs another project's mod) is undecided and is
itself the root-cause question, so this is not a defect-lane item.

## Stage Report: ideation

- DONE: Define a GitHub-native feedback observation and fail-closed repair fallback that works without kc-pr-review-resolve.
  The accepted direction binds `github-pr-feedback/v1` to repo/PR-or-layer/head, a canonical mutable-content fingerprint, and evidence-bearing dispositions; absent resolver routes to the ordinary worker and every incomplete read stays `UNKNOWN`.
- DONE: Add default self-assignment to the canonical Draft PR creation unit with a falsifiable contract test.
  The design adds `--assignee "@me"` to the sole active command; deleting only that flag is the named contract-test mutant, and installed `gh` help confirms support.
- DONE: Recut the existing #214 direction into the smallest S2 slice against fresh origin/main without adding a second review framework.
  Against `origin/main` `281bd7f6`, the proposed recut is six existing files and removes the `kc-pr-flow` change plus standalone plan from stale-base PR #214 (`40fdf84`, 392 additions/deletions across eight files).
- DONE: Run the reverse-recovery audit and kernel subtraction.
  Existing PR lifecycle and validation-report seams are `EXISTS_BROKEN/REQUIRED`; removing either fails AC1/AC2, while a resolver integration, separate ledger, plan, startup polling, and idle polling fail no named AC and are cut.
- DONE: Test the likely-wrong assumption with same-kind provider evidence.
  `qnow#1057@ca1d613c` yields two external non-empty reviews and three raw but zero unresolved external threads; positive `qnow#1124@ebddb0ab` yields one such review and two unresolved threads, with complete first pages and empty `reviewDecision` in both.
- DONE: Record `design: required`, end-state ACs with falsifiers, test scope, measurement, docs, and non-goals.
  `spacedock status --read ... --ac-scan` exits 0 for four bold AC headings; UI E2E is inapplicable to this policy/config slice, so live read-only GitHub probes preserve the provider observation boundary.
- FAILED: Advance the ideation gate.
  The one fresh-context EM returned `return/high`: the first draft under-specified fingerprint identity/evidence, miscounted two value surfaces as one, over-retained startup/idle, and overstated what contract tests prove; the body now incorporates all corrections, but this report does not rewrite that verdict.

### Engineering judgment

```yaml
route: return
confidence: high
multi_model: not_needed
recommendation: Re-evaluate the corrected two-surface, six-file recut in the next ideation cycle; keep the versioned compact report fact and remove resolver integration, standalone plan, startup, and idle observation.
dissent: The original proposal mislabeled assignee ownership as the same value surface and treated resolved qnow threads as normalized unresolved evidence.
disproof_condition: Proceed only after the artifact unambiguously binds the fingerprint and disposition evidence, counts both captain-approved surfaces, bounds tests to policy/data-path proof, and supplies a positive unresolved-thread provider observation.
authority_boundary: Captain retains the two-surface exception and merge policy; the gate retains advancement; FO retains mechanics; the optional resolver has no gate authority.
```

### Summary

The smallest credible design keeps GitHub observation and fail-closed delivery in dev-flow, persists only a versioned compact fact in the existing validation report, and uses the ordinary worker when the optional resolver is absent. The initial proposal was corrected after independent EM review, but the recorded advisory route remains `return`; a new ideation cycle must evaluate the corrected artifact rather than treating the correction as self-approval.

## Stage Report: ideation (cycle 2)

Verdict: `proceed` with high confidence; multi-model review `not_needed`.

- DONE: Re-read the corrected Design determination, Acceptance criteria, and Test plan without changing product files or broadening scope.
  Review bound the proposal to fresh `origin/main` `281bd7f6` and corrected artifact blob `59269267f89a11d51875b0acb512c1e5c9348b29` (SHA-256 `591e1401d45c73c93c0f6376c747eec8cf931d45e7e9adfcd5706fac258c6ac6`).
- DONE: Verify every prior EM return condition is now satisfied.
  The artifact now binds versioned mutable content and full PR/layer identity, requires evidence for all dispositions, counts two captain-approved surfaces, names only four boundaries, bounds test claims, and preserves the six-file/no-ledger/no-resolver-integration cut.
- DONE: Recheck the positive and resolved-thread provider evidence.
  `qnow#1057@ca1d613c` remains two external non-empty reviews plus three raw/zero unresolved threads; `qnow#1124@ebddb0ab` remains one external non-empty review plus two unresolved threads, with empty `reviewDecision` and complete pages.
- DONE: Commission exactly one new fresh-context Science Officer EM review.
  The new reviewer independently returned `proceed/high`; all five adjudications were supported, dissent was empty, and no additional reviewer was commissioned.
- DONE: Preserve the bounded correction-cycle scope.
  Only this entity changed; implementation remains six existing files with no startup/idle polling, `kc-pr-flow` change, second ledger, standalone plan, or added delivery authority.
- DONE: Re-run the ideation AC structure check.
  `spacedock status --workflow-dir docs/dev --read .../issue213.md --ac-scan` exits 0; removing a bold single-line AC heading would fail this check.

### Engineering judgment

```yaml
question: Whether corrected issue213 artifact 59269267 should advance under the captain-approved two-surface S2 exception.
revision: origin/main 281bd7f6; artifact blob 59269267f89a11d51875b0acb512c1e5c9348b29
adjudications: binding exactness, prior return conditions, iteration-size exception, live probes, and boundary/scope consistency are supported.
risk_tradeoff: Maintain one versioned fingerprint and four boundary observations; implementation drift remains for fresh exact-head validation.
recommendation: Proceed with the six-file slice exactly as written and re-pin origin plus the open probe at implementation entry.
route: proceed
confidence: high
dissent: ""
disproof_condition: Return or narrow if implementation needs a seventh file, resolver contract, second store, startup/idle polling, standalone plan, or lets a non-pass provider state cross a required boundary.
authority_boundary: Captain retains scope and exception authority; Gate Authority retains advancement; delivery owners retain Ready, merge, and terminalization mutations.
```

### Summary

The bounded correction resolves every prior return condition without expanding the design or file family. One new fresh-context EM recommends `proceed`; implementation should re-pin the moving provider evidence and build only the accepted six-file slice.

## Stage Report: implementation

Verdict: `DONE` at exact product commit
`107fb9546d560a421e187ae2f77e26cd056ee7a6`, based on `origin/main`
`281bd7f69db38089ca5f487b9da0596fe11c6c64`. The code branch was not pushed
and no GitHub state changed.

- DONE: Recut the existing #214 work without rewriting or moving its PR branch.
  The assigned branch `spacedock-ensign/issue213` starts at exact fresh
  `origin/main` `281bd7f6`; the existing local and remote
  `fix/kc-dev-flow-pr-feedback-gate` branch remains at `40fdf84`. The final
  merge-base diff contains exactly the approved six files, +477/-12: no
  `kc-pr-flow/**` change, standalone plan, feedback state file, or seventh
  product file.
- DONE: Close AC1 with a complete GitHub-native, exact-head, fail-closed
  observation contract.
  `_mods/pr-merge.md` binds `github-pr-feedback/v1` to explicit repository,
  PR/layer, head, stable normalized IDs, state, authors, commit IDs, exact body
  hashes, and deterministic canonical JSON. It paginates GraphQL thread pages
  and REST review pages, rejects nested-comment overflow, rereads the head, and
  maps every ambiguous, incomplete, drifting, malformed, or unread result to
  `UNKNOWN`. Focused mutants reject ambient repository reads, unread pages,
  author-filter inversions, head drift, mutable-content/state loss,
  non-canonical fingerprints, and top-layer-only coverage.
- DONE: Close AC2 with the four approved boundaries and evidence-bearing
  dispositions, without resolver coupling.
  Existing PRs observe at validation entry; every delivery re-observes before
  Ready, immediately before merge, and before terminalization. Initial Draft
  creation remains outside the loop when no PR exists. The compact existing
  validation-report record requires an exact fingerprint match and exactly one
  `fixed`, `rejected-with-reason`, or `out-of-scope-and-filed` disposition per
  item, including its required evidence. The optional resolver supplies no
  observation or gate authority; absence routes actionable work to the ordinary
  implementation worker and never means clean.
- DONE: Close AC3 in the sole active canonical Draft creation unit.
  Added only `--assignee "@me"` to the enabled body-file command. The released
  disabled inline-body example is byte-protected and unchanged. The focused
  `missing-self-assignment` mutant deletes only that flag and is rejected with
  `missing canonical Draft create`.
- DONE: Preserve AC4's existing authority surfaces and map every file to an AC.
  `docs/dev/_mods/pr-merge.md` owns AC1/AC2/AC3; `docs/dev/README.md` binds
  validation and done for AC2; the byte-identical packaged and vendored kernels
  carry the provider-neutral AC2 invariant; the two existing test files prove
  AC1/AC2/AC3 scope and fail-closed mutations. No second ledger, daemon,
  startup/idle observation, automatic reply, resolver integration, or added
  Ready/merge authority was introduced.
- DONE: Record RED before production edits and GREEN on the exact candidate.
  RED: `scripts/pr-merge-portable-delivery.test.py` exited 1 with
  `single-PR completion table drifted` and `missing canonical Draft create`;
  `scripts/kc-dev-flow-contract-test.py` exited 1 with
  `native-stack completion decision drifted`. GREEN at `107fb954`: both focused
  suites exit 0, the assignee and existing portable-delivery mutants report
  `REJECTED`, `git diff --check` passes, and the two kernels compare
  byte-identically.
- DONE: Re-run same-kind provider probes at the pinned examples.
  `iamcxa/qnow#1057@ca1d613c` remained head-stable with one complete thread page,
  one REST-review page, no nested overflow, three raw threads, zero normalized
  unresolved external threads, seven raw reviews, and two normalized external
  reviews. `iamcxa/qnow#1124@ebddb0ab` remained head-stable with complete first
  pages, no nested overflow, two raw/two normalized unresolved external threads,
  and one raw/one normalized external review. The documented GraphQL selection,
  including comment commit IDs, executed successfully.
- DONE: Run the proportional repository exits at the committed candidate.
  `scripts/version-parity-check.sh` passes all seven plugins;
  `scripts/skill-frontmatter-lint.sh` passes 40/40 skill directories;
  `scripts/marketplace-verify.sh` passes L0 parity, L1 schema, and all seven L2
  installs. The repo sanitize-check skill scanned the changed public
  `kc-dev-flow/references/kernel.md` and returned PASS with zero REJECT, BLOCK,
  or WARN findings.
- DONE: Apply the authoritative delivery-topology decision without changing
  GitHub state.
  Dependent green layers: no. Independent deliverable green slices at the
  accepted unit: no — the two separately falsifiable values intentionally share
  the same canonical Draft lifecycle command, completion table, and focused
  delivery contract under the captain-approved six-file exception. Numeric
  trigger: no (489 gross changed lines, six files). Required topology remains the
  one preserved Draft PR #214 named by the dispatch; this worker performed no
  push, Ready, merge, or PR edit.

### Summary

Exact commit `107fb9546d560a421e187ae2f77e26cd056ee7a6` implements the corrected
six-file PR-feedback gate and default self-assignment against exact
`origin/main` `281bd7f6`. Focused mutants, repository gates, sanitize-check, and
both live provider cases pass; the code worktree is clean and the candidate is
committed but unpushed for fresh validation.

## Stage Report: validation

Verdict: `PASS` at exact candidate
`107fb9546d560a421e187ae2f77e26cd056ee7a6`, based on
`281bd7f69db38089ca5f487b9da0596fe11c6c64`. No product file or GitHub state
was modified during validation.

- DONE: Validate AC1 against the exact policy and provider data path.
  The GitHub-native contract reads the explicit repository and PR/layer, binds
  start and end `headRefOid`, paginates all GraphQL thread pages and all REST
  review pages, fails closed on nested-comment overflow, and normalizes the
  accepted external thread/review populations including bots. The canonical
  `github-pr-feedback/v1` input includes stable kind/ID, authors, review or
  resolution state, commit IDs, and SHA-256 hashes for every mutable body or
  comment; malformed, incomplete, ambiguous, drifting, or failed reads become
  `UNKNOWN`.
- DONE: Validate AC2's dispositions, fallback, and all four delivery boundaries.
  The validation report binds identity, head, fingerprint, population, and one
  evidenced disposition per item. Missing fix evidence, rejection reason, filed
  reference, resolver, parse result, or provider proof cannot pass. The ordinary
  implementation worker remains the fallback, a code change invalidates the
  prior verdict, and observations occur at validation entry for an existing PR,
  before Ready, immediately before merge, and before terminalization. Existing
  startup/idle scans gain no independent polling surface; they invoke the same
  terminalization decision only when that boundary is reached.
- DONE: Validate AC3 self-assignment at the active canonical command.
  The enabled body-file command includes `--assignee "@me"`; installed `gh` help
  confirms that value self-assigns. The released inline-body command remains
  disabled and unchanged, and the focused flag-deletion mutant is rejected.
- DONE: Validate AC4 and the approved subtraction.
  The exact merge-base map is six modified existing files, +477/-12, with no
  added/deleted file, `kc-pr-flow/**` diff, ledger, resolver mode, daemon,
  standalone plan, PRODUCT/ARCHITECTURE change, or seventh product surface. The
  packaged and vendored kernels are byte-identical.
- DONE: Re-run adversarial and proportional exact-head exits.
  `scripts/kc-dev-flow-contract-test.py` passes with all 23 feedback mutants
  rejected; `scripts/pr-merge-portable-delivery.test.py` passes with all four
  portable mutants rejected. `git diff --check`, version parity for seven
  plugins, frontmatter lint for 40/40 skill directories, marketplace L0/L1 and
  all seven L2 installs pass. The changed public kernel has zero sanitize
  REJECT/BLOCK patterns.
- DONE: Re-observe both same-kind GitHub cases at their pinned heads.
  `qnow#1057@ca1d613c` stayed head-stable with one complete thread page, one REST
  review page, no nested overflow, 3 raw/0 normalized unresolved external
  threads, and 7 raw/2 normalized external reviews. `qnow#1124@ebddb0ab` stayed
  head-stable with complete first pages, no nested overflow, 2/2 threads and 1/1
  review. `reviewDecision` remained empty in both, confirming it is not a
  substitute for the declared population.
- DONE: Commission exactly one fresh validation Science Officer EM.
  The independent EM returned `proceed/high`, `multi_model: not_needed`, with
  all six adjudications supported and no dissent. No optional second model was
  commissioned.
- DONE: Separate local candidate validation from delivery proof.
  Draft PR #214 remains at old head `40fdf8484202232c793ffbdd3e4241b3eaee8f6a`,
  so it is not exact-candidate evidence. This PASS authorizes no push, Ready,
  merge, or terminalization; after the candidate is delivered, its complete
  feedback observation and exact-head CI must be recorded at the applicable
  boundaries.

Lenses: behavior PASS (0 findings); contract/schema PASS (0); state/concurrency PASS (0); security/privacy PASS (0); runtime/platform PASS (0); docs/policy PASS (0); delivery PASS (0) — inputs were the exact six-file diff, governing ACs, policy mods, focused mutants, repository exits, and pinned GitHub responses; falsifiers were a surviving refusal/mutation, incomplete provider population, stale head, unsafe boundary, extra authority surface, or unsupported active command.
Diff coverage: N/A — docs/policy-only product surface; the executable changes are test oracles, while 23 feedback mutants and four portable mutants exercised every declared new refusal group.
Adversarial: PASS — attacked pagination, nested overflow, author inversion, head drift, mutable content/state, canonical serialization, disposition evidence, resolver absence, `UNKNOWN`, stack isolation, all four timings, the creation exception, and self-assignment; no mutant survived.
Cross-model: not_needed — the required fresh EM returned `proceed/high` with no contested, irreversible, low-confidence, or unresolved call.
E2E: N/A — ideation-approved workflow-policy/config slice with no product UI or executable application path; live GitHub GraphQL/REST probes preserve the same-kind provider boundary.
Origin re-observation: PASS — Reported scenario: review findings can exist while validation and `reviewDecision` do not expose them | Originating runtime kind: GitHub PR GraphQL review threads plus REST PR reviews | Re-observation artifact/revision: `iamcxa/qnow#1057@ca1d613c817a10d02235c7c2e137ec40722116a8` and `iamcxa/qnow#1124@ebddb0ab52f5661ddf5f4933036e089865b8a06e` on 2026-08-13 | Equivalent-runtime rationale: same provider, repository-explicit APIs, actors including bots, pagination, head binding, and accepted population rules used by the delivery policy | Falsifier kind: existence-disproof | Result: complete head-stable responses reproduced the resolved-thread and positive unresolved-thread populations while `reviewDecision` stayed empty.

### Engineering judgment

```yaml
science_officer_em_upward_report:
  em_judgment: "Exact candidate 107fb9546d560a421e187ae2f77e26cd056ee7a6 satisfies AC1-AC4 and the approved subtraction constraints; proceed to the next authorized Draft-delivery step, without treating validation as delivery."
  evidence_synthesis: "The candidate is exactly one commit over base 281bd7f69db38089ca5f487b9da0596fe11c6c64 and changes the approved six existing files by +477/-12, with no kc-pr-flow file, new state file, ledger, resolver integration, startup/idle polling loop, product document, or architecture document. The contract and portable-delivery suites pass at the candidate, including mutants for provider pagination, population filters, mutable content/state, canonical serialization, head drift, UNKNOWN handling, all four boundaries, resolver fallback, stack isolation, and self-assignment; diff-check passes and the packaged/vendored kernels are byte-identical. Fresh read-only GitHub probes remained head-stable: qnow#1057 produced 3 raw/0 normalized unresolved external threads and 7 raw/2 normalized external reviews; qnow#1124 produced 2/2 threads and 1/1 reviews, with complete first pages and no nested overflow. Existing Draft PR #214 remains at old head 40fdf8484202232c793ffbdd3e4241b3eaee8f6a with an empty normalized population, so that observation is not candidate-head delivery proof and must be repeated after the candidate is pushed."
  risk_tradeoff_call: "The change purchases fail-closed protection against unread or edited GitHub review feedback and default follow-through ownership. Its durable cost is maintaining a detailed GitHub GraphQL/REST observation and fingerprint contract at the existing delivery seam; the remaining operational risk is incorrect execution of that policy, bounded by fresh exact-head validation and repeated boundary observations. A resolver integration, daemon, startup/idle polling regime, or second durable ledger would add ownership and synchronization cost without serving an unmet accepted criterion."
  recommendation: "Proceed through the existing Gate Authority to captain-approved delivery of exact candidate 107fb9546d560a421e187ae2f77e26cd056ee7a6; after its PR head is updated, perform and record the complete candidate-head observation before Ready, immediately before merge, and before terminalization. This recommendation grants no push, Ready, merge, state-transition, or archive authority."
  route: proceed
  confidence: high
  multi_model: not_needed
  fo_boundary: "The FO may relay this judgment, account for evidence, and perform authorized state or delivery mechanics; it does not adjudicate findings or gain push, Ready, merge, terminalization, or archive authority."
  engineering_judgment:
    question: "Does exact candidate 107fb9546d560a421e187ae2f77e26cd056ee7a6 satisfy issue 213 AC1-AC4 and the approved scope/subtraction constraints sufficiently to proceed from validation?"
    revision: "107fb9546d560a421e187ae2f77e26cd056ee7a6 against base 281bd7f69db38089ca5f487b9da0596fe11c6c64"
    evidence_synthesis: "The candidate is exactly one commit over base 281bd7f69db38089ca5f487b9da0596fe11c6c64 and changes the approved six existing files by +477/-12, with no kc-pr-flow file, new state file, ledger, resolver integration, startup/idle polling loop, product document, or architecture document. The contract and portable-delivery suites pass at the candidate, including mutants for provider pagination, population filters, mutable content/state, canonical serialization, head drift, UNKNOWN handling, all four boundaries, resolver fallback, stack isolation, and self-assignment; diff-check passes and the packaged/vendored kernels are byte-identical. Fresh read-only GitHub probes remained head-stable: qnow#1057 produced 3 raw/0 normalized unresolved external threads and 7 raw/2 normalized external reviews; qnow#1124 produced 2/2 threads and 1/1 reviews, with complete first pages and no nested overflow. Existing Draft PR #214 remains at old head 40fdf8484202232c793ffbdd3e4241b3eaee8f6a with an empty normalized population, so that observation is not candidate-head delivery proof and must be repeated after the candidate is pushed."
    adjudications:
      - finding: "AC1-provider-population-and-fingerprint"
        disposition: supported
        basis: "AC1 and the pr-merge GitHub observation contract require explicit repository/PR identity, start and end head reads, complete GraphQL thread pagination, fail-closed nested-comment overflow, complete REST review pagination, external unresolved threads, external non-empty or CHANGES_REQUESTED reviews including bots, and canonical mutable body/state/commit coverage. Candidate tests reject the named population, pagination, head-drift, mutable-content, mutable-state, and serialization mutants; current qnow probes match the declared populations."
      - finding: "AC2-four-boundaries-UNKNOWN-and-fallback"
        disposition: supported
        basis: "AC2, the validation/done stage bindings, and pr-merge require observation at validation entry for an existing PR, before Ready, immediately before merge, and before terminalization. Every boundary compares identity, head, population fingerprint, and evidenced dispositions; malformed, incomplete, drifting, failed, or ambiguous reads become UNKNOWN and block. Resolver absence routes the complete set to the ordinary implementation worker, and any code change requires fresh validation."
      - finding: "AC3-self-assignment"
        disposition: supported
        basis: "The sole active canonical Draft command adds --assignee \"@me\" while the released inline-body command remains disabled and unchanged. The focused missing-self-assignment mutant removes only that flag and is rejected."
      - finding: "AC4-six-file-and-no-parallel-framework"
        disposition: supported
        basis: "The exact merge-base map contains only docs/dev/README.md, docs/dev/_mods/kernel.md, docs/dev/_mods/pr-merge.md, kc-dev-flow/references/kernel.md, and the two existing contract tests. There is no kc-pr-flow diff, new state file, resolver mode, daemon, or feedback ledger. Startup and idle gain only the required terminalization decision when that boundary is reached; no independent startup/idle observation loop was added."
      - finding: "iteration-size-and-subtraction"
        disposition: supported
        basis: "The work-item authority records the captain-approved one-small-S2 exception for two value surfaces sharing the existing delivery seam. The 489-line, six-file change stays below the topology trigger. Without-it mutants establish the retained observer/barrier, validation report binding, provider-neutral kernel invariant, and self-assignment need; the optional resolver change, standalone plan, new ledger, and extra polling surface remain subtracted."
      - finding: "candidate-delivery-proof"
        disposition: supported
        basis: "Local validation is bound to candidate 107fb9546d560a421e187ae2f77e26cd056ee7a6, but current Draft PR #214 remains on 40fdf8484202232c793ffbdd3e4241b3eaee8f6a. The governing contract correctly treats the old-head observation as non-transferable and requires a new complete observation after candidate delivery and before each subsequent boundary."
    risk_tradeoff: "The change purchases fail-closed protection against unread or edited GitHub review feedback and default follow-through ownership. Its durable cost is maintaining a detailed GitHub GraphQL/REST observation and fingerprint contract at the existing delivery seam; the remaining operational risk is incorrect execution of that policy, bounded by fresh exact-head validation and repeated boundary observations. A resolver integration, daemon, startup/idle polling regime, or second durable ledger would add ownership and synchronization cost without serving an unmet accepted criterion."
    recommendation: "Proceed through the existing Gate Authority to captain-approved delivery of exact candidate 107fb9546d560a421e187ae2f77e26cd056ee7a6; after its PR head is updated, perform and record the complete candidate-head observation before Ready, immediately before merge, and before terminalization. This recommendation grants no push, Ready, merge, state-transition, or archive authority."
    route: proceed
    confidence: high
    dissent: ""
    disproof_condition: "Change the route to return if an exact-candidate contract test fails, a live same-kind probe contradicts the declared population or pagination behavior, a current candidate-head observation cannot produce a stable canonical fingerprint and complete dispositions, any delivery path crosses Ready/merge/terminalization on non-pass evidence, the assignee mutant survives, or the merge-base map gains a resolver, ledger, startup/idle polling, or seventh product surface."
    authority_boundary: "The captain retains scope, exception, push, readiness, and merge authority; repository Gate Authority owns stage advancement; Spacedock work-item and execution-state authority owns durable status, terminalization, and archive transitions; the declared GitHub delivery owner owns provider observations and mutations. This EM record is advisory only."
```

### Summary

Exact candidate `107fb9546d560a421e187ae2f77e26cd056ee7a6` passes AC1-AC4 at the
approved six-file/no-ledger/no-resolver scope. The provider populations,
mutable-content fingerprint contract, fail-closed outcomes, disposition
evidence, ordinary-worker fallback, all four boundaries, and self-assignment
survive adversarial validation; Draft PR #214 remains stale and must not be used
as candidate delivery proof until it is updated and re-observed.

### Post-delivery observation — PR #220

Observation evidence: `PASS` — start/end state `OPEN`, Draft `true`, and head
`107fb9546d560a421e187ae2f77e26cd056ee7a6`; GraphQL thread pages 1, raw
threads 0, nested comment overflow false, normalized external unresolved
threads 0; REST review pages 1, raw reviews 0, normalized external reviews 0.
Canonical population input: `{"head":"107fb9546d560a421e187ae2f77e26cd056ee7a6","items":[],"layer":"single","pr":220,"repository":"iamcxa/kc-claude-plugins","scheme":"github-pr-feedback/v1"}`.
PR feedback: {"scheme":"github-pr-feedback/v1","repository":"iamcxa/kc-claude-plugins","pr":220,"layer":"single","head":"107fb9546d560a421e187ae2f77e26cd056ee7a6","fingerprint":"sha256:8a63c4e81ab1f67d6161a0c84bcc60619ebc36e7dfa09909354471654daf8757","dispositions":[]}
