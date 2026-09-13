---
title: "The pr-merge extension has no adopter seam, so a fleet-wide title rule has nowhere to live"
status: validation
source:
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: dev-flow-pr-merge-adopter-seam
sprint-readiness: ready
started:
completed:
verdict:
worktree: .worktrees/spacedock-ensign-pr-merge-extension-has-no-adopter-seam
issue:
pr:
mod-block:
id: 2f5a8kg1qwc5ba8jg3mcfjjw
gates:
    version: 1
    records:
        - id: gate:2f5a8kg1qwc5ba8jg3mcfjjw:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:2f5a8kg1qwc5ba8jg3mcfjjw-backlog-1
              briefing:
                id: briefing:2f5a8kg1qwc5ba8jg3mcfjjw:backlog:attempt-1:revision-1
                digest: sha256:e7c2a8e136175ae56326a860fa6d3f28da6973585f4e01dcdd041c0c4fcc081e
                room-ref: ./pr-merge-extension-has-no-adopter-seam/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:2f5a8kg1qwc5ba8jg3mcfjjw:backlog:1
                briefing: briefing:2f5a8kg1qwc5ba8jg3mcfjjw:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-09-12T09:58:36.464777Z"
                decision: approve
                reason: 'Captain approved in chat 2026-09-12: 「開」 to filing at Pilot after the AC-1..AC-4 presentation, then 「推」 to advance. Scope is the two asks presented: carry the title rule in the extension, and declare the post-:end adopter region and its precedence.'
              application:
                target-stage: ideation
                state: consumed
        - id: gate:2f5a8kg1qwc5ba8jg3mcfjjw:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:2f5a8kg1qwc5ba8jg3mcfjjw-ideation-1
              briefing:
                id: briefing:2f5a8kg1qwc5ba8jg3mcfjjw:ideation:attempt-1:revision-1
                digest: sha256:65f226cf1272408f974a5546994262f2a4e203b47e7961729b560b223b929e97
                room-ref: ./pr-merge-extension-has-no-adopter-seam/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:2f5a8kg1qwc5ba8jg3mcfjjw:ideation:1
                briefing: briefing:2f5a8kg1qwc5ba8jg3mcfjjw:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-09-12T17:10:40.357924Z"
                decision: approve
                reason: 'Captain approved in chat 2026-09-13: "approve", after the FO presented the shaped route (kc-dev-flow ships a Python check-pr-title.py with a release-please verdict fixture; the extension states the rule and binds it to the delivery unit title), the four rejected alternatives, the measured feat(): x disagreement, and the four items shape marked not-settled.'
              application:
                target-stage: implementation
                state: consumed
---

kc-dev-flow 4.4.0 pins the released pr-merge body's sha256 and ships the
extension as a canonical resource. The adopter `spacedock-dev/subspace-relay` ran the adopt-dev-flow sync on
2026-09-12 at `main` `3b8f233` and is the second adopter to do so, which is the residual #414
recorded for itself: *"Other adopters receive the block only after they run the
adopt-dev-flow sync."* The sync found one rule in that repository's
`docs/dev/_mods/pr-merge.md` with no upstream home — the pull request title must
be a Conventional Commits subject, refused by `scripts/check-pr-title.ts`. Both
of its call sites are inside `## Hook: merge`: once before the draft is presented,
and once chained as `check-pr-title.ts && gh pr create`. That section is inside
the sha-pinned released body, which may not be edited (Captain, 2026-09-11:
「不要去動那個上游」). The extension offers nowhere else to put it: the word
"adopter" appears once in its 424 lines, in the contract-test sentence, and
nothing declares whether adopter prose after the `:end` marker may override a
released section the way the extension's own `#### Local failure-policy override`
and `### Split-root audit-link correction` subsections do, or with what
precedence. The condition the rule guards is fleet-wide rather than that repository's:
`gh api repos/<r>` on 2026-09-12 reports `squash_merge_commit_title:
COMMIT_OR_PR_TITLE` with squash, merge and rebase all enabled for
`iamcxa/kc-claude-plugins`, `spacedock-dev/subspace-relay` and
`spacedock-dev/spacedock` alike, and this repository releases through
release-please. A pull request carrying two or more commits lands under the pull
request title; a title release-please cannot parse produces no release and
excludes that commit from every future changelog by type, permanently and
without a symptom.

## Accepted outcome

An adopter whose repository squash-merges under `COMMIT_OR_PR_TITLE` and
releases through release-please receives the title refusal from kc-dev-flow
itself, with no rule copied into its own mod and no edit to the pinned released
body. Separately, the extension and `adopt-dev-flow` both state whether an
adopter may add a rule of its own after the `:end` marker and what precedence
that region holds against the extension block, so the next adopter meets a
declared answer instead of silence.

## Non-goals

- Editing the released Spacedock pr-merge body or its pinned `pr_merge_released_body.sha256`.
- Changing Spacedock's shipped mod, its version stamp, or its merge-guard contract.
- The `spacedock-dev/subspace-relay` adoption of kc-dev-flow 4.4.0, which is gated separately on that repository's `slim-v0-terminal-review-pr58` stage boundary.
- Any Linear read or write.

## Acceptance criteria

- **AC-1** After a fresh `adopt-dev-flow` sync into a repository holding no local
  title prose, the title refusal is reachable from `## Hook: merge` in the
  resulting `_mods/pr-merge.md`, and that file's pre-marker body still hashes to
  `contract-manifest.json` `pr_merge_released_body.sha256`.
- **AC-2** A pull request title release-please cannot parse is refused before
  `gh pr create` would run, and a parseable title passes, both exercised against
  a fixture in this repository. Mutating the refusal's condition turns the
  refusing case green, proving the check and not its restatement.
- **AC-3** `references/pr-merge-extension.md` and `skills/adopt-dev-flow/SKILL.md`
  each state the post-`:end` adopter region and its precedence against the
  extension block. `scripts/kc-dev-flow-contract-test.py` still exits 0 for a
  conforming adopter and non-zero naming the drift when the marked block changes
  by one character.
- **AC-4** `spacedock-dev/subspace-relay`'s `docs/dev/_mods/pr-merge.md` at `main`
  `3b8f233`, rebuilt in a scratch worktree as
  pinned released body plus the verbatim extension, needs zero adopter-added
  prose for the title rule. Demonstrated by rebuilding the file and listing the
  behaviours the rebuild retains, not by asserting equivalence.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  route: [shape, build, verify-deliver]
  basis: >
    Captain approved in chat 2026-09-12 (「開」) after the Relay 4.4.0 adoption
    audit of `spacedock-dev/subspace-relay`. #414 selected POC because its falsifier
    was a single adopter and it recorded "the sync path is rewritten if other
    adopters need more"; that audit supplied the second adopter and answered the
    question, so this is a defined
    slice rather than a fresh exploration. Not Production: it moves no release
    identity, credential, or standing deployment path, and ships through the
    release-please lane #414 already used. The design question Pilot's shape stage
    owes is where the refusal mechanism lives — a kc-dev-flow-shipped checker, or
    a rule the extension states and each adopter binds in its Local Profile.
  obligations:
    architecture: [Released body and its pinned hash untouched; the refusal is reachable from the extension, not from adopter prose; the post-marker adopter region has one declared precedence]
    implementation: [references/pr-merge-extension.md; skills/adopt-dev-flow/SKILL.md; contract-manifest.json if a new resource is added; scripts/kc-dev-flow-contract-test.py]
    testing: [AC-1 to AC-4 at the candidate SHA; mutation proof on AC-2; drift mutation on AC-3]
  scope_boundary: >
    No Spacedock edit; no Linear; no change to `spacedock-dev/subspace-relay`; no edit to the
    released pr-merge body or its pinned hash.
  semantics_unchanged: false
```

## Shape

### Route decision

**The refusal ships from kc-dev-flow as a Node-free Python checker, and the
extension states the title rule and binds it to the delivery unit's title.**

`kc-dev-flow/scripts/check-pr-title.py` is a new canonical resource. A new
`### Released title override` subsection of `references/pr-merge-extension.md`
overrides the released `**Title:** {entity title}` draft line and the released
`--title "{entity title}"` create argument, requires the refusal to run before
the draft is presented, and applies to the single delivery unit and to every
native-stack layer's title. No adopter writes the rule.

Four alternatives were considered and rejected:

- **The extension states the rule; each adopter binds its own checker in its
  Local Profile.** Fails the accepted outcome's "from kc-dev-flow itself", and a
  new entry in `contract-manifest.json` `local_profile_interface.required_bindings`
  makes every existing adopter's Local Profile fail closed — `profile-contract-loader.py`
  raises `Local Profile is missing bindings` for an absent required binding and
  `LOCAL_PROFILE_REFIT_REQUIRED` when `local_profile_interface` changes at all.
- **Ship `spacedock-dev/subspace-relay`'s TypeScript checker as the resource.**
  `iamcxa/kc-claude-plugins` has no `package.json`, no lockfile, and no
  `node_modules` at `origin/main` `7b103a10`, so AC-2's "exercised against a
  fixture in this repository" would have nothing to run.
- **Vendor a copy of the checker into each adopter's `scripts/`.** That is the
  adopter-copied rule this work item exists to remove.
- **A CI job that lints the pull request title.** It reports after the draft has
  been presented, and it is a new standing lane.

### Accepted journey

Every step names the acting program and is marked OBSERVED or DESIGNED.

1. **DESIGNED** — the first officer, at `## Hook: merge` in an adopter's
   `docs/dev/_mods/pr-merge.md`, reads the extension's
   `#### Canonical Draft delivery unit` and resolves `UNIT_TITLE`. The released
   `**Title:** {entity title}` line no longer supplies it.
2. **DESIGNED** — the first officer resolves `KC_DEV_FLOW_ROOT` as the activated
   `kc-dev-flow` package root, the same root `skills/continue-dev-flow/SKILL.md`
   resolves `scripts/profile-contract-loader.py` from, and runs
   `python3 "$KC_DEV_FLOW_ROOT/scripts/check-pr-title.py" "$UNIT_TITLE"` before
   presenting the draft. An unresolvable root is a stop, not a skip.
3. **DESIGNED** — exit `0`: the checker writes the type it read to stdout and the
   first officer presents the draft. Exit `1`: refusal — the draft is not
   presented and `gh pr create` is not reached. Exit `2`: the checker could not
   decide, which is also a refusal.
4. **DESIGNED** — on captain approval the extension's canonical create command
   runs with the same refusal-checked `UNIT_TITLE` bytes, chained so a non-zero
   exit means `gh pr create` never runs.
5. **DESIGNED** — for a native stack, step 2 repeats per layer against that
   layer's own reviewed title; an unchecked layer title stops the stack before
   any push.
6. **OBSERVED** — the refusal mechanism behaves as steps 3-4 require, measured at
   a sibling's Node implementation of the same rule:
   `node scripts/check-pr-title.ts` at `subspace-relay`
   `~/conductor/workspaces/subspace-relay/barcelona`, 2026-09-12, exits `1` for
   `Release-please credentials and verified production promotion` and `0` for
   `feat(release): promote a verified release to production`.
7. **OBSERVED** — the oracle the Python checker must match is reachable inside
   this repository with no new dependency: `npm ci` over the existing
   `scripts/fixtures/release-please-runtime` lockfile (release-please `17.3.0`)
   then `parseConventionalCommits`, 2026-09-12, and it agrees with
   `subspace-relay`'s pinned `17.11.1` on all 17 probed titles.

**Unhappy paths, in the same terms.**

- `KC_DEV_FLOW_ROOT` unresolvable, or the checker file absent: the first officer
  stops, preserves pending delivery authority and state, and reports. It does not
  present an unchecked draft and does not fall back to local merge — the
  extension's `#### Local failure-policy override` already forbids that fallback
  for delivery failures.
- The captain asks to proceed past a refusal: the first officer explains that the
  refusal is the rule, not a tooling detour, and offers a corrected subject. Only
  a captain-authorised scope change to this work item can remove the rule.
- The checker exits `2`: treated as `1`. A checker that cannot decide and exits
  `0` is the defect wearing a green mask.
- A title passes the grammar but names the wrong type for the branch's commits
  (a `feat` branch presented as `docs:`): **not covered**, and not covered today
  either. It parses, releases nothing, and is invisible until a release run logs
  `No user facing commits found`. Recorded as a known limit, not a residual of
  this slice.

**`semantics_unchanged: false`.** This work adds one command grammar
(`check-pr-title.py <title>` with exit codes `0`/`1`/`2`), changes the merge
hook's runtime behaviour (a refusal before draft presentation), and grows
`contract-manifest.json` `resources` by three paths, which changes the contract
digest. It moves no authority, changes no stored format, and does not touch
`local_profile_interface`, so no adopter needs a Local Profile refit; an adopter
absorbs it by taking the new plugin version at its next stage boundary.

### The title rule's oracle

The checker must not invent the grammar that decides. release-please parses the
subject with its own conventional-commits grammar, and its decisions are not the
ones a hand-written regex reaches. Measured at both pinned versions on
2026-09-12 — `17.3.0` in this repository, `17.11.1` at `subspace-relay` — with
identical results:

| Subject | Verdict | Why it is in the fixture |
| --- | --- | --- |
| `feat(): x` | drops | A `(\w+)(\(.*\))?!?:` regex passes it. This is the dangerous direction. |
| `Revert "feat: x"` | drops | Reverts read as prose, not as a type. |
| `feat x` | drops | No `:` delimiter. |
| `Add a thing` | drops | The `9475d07` shape. |
| `feat:x` | parses | No space after the colon is still a commit. |
| `FEAT: x` | parses | The type is not case-normalised before parsing. |
| `feat: ` | parses | An empty description still parses. |
| `  feat: x` | parses | Leading whitespace is tolerated. |
| `feat(two words): x` | parses | Scope content is unconstrained. |
| `feat(a)!: x`, `fix(a,b): x`, `chore(deps): bump x`, `docs(dev): state the rule` | parses | `docs:` and `chore:` must pass: refusing a correctly non-releasing type moves the judgement call back to draft time. |

Two error directions are not symmetric. A checker that **passes** a title the
oracle drops reproduces the defect. A checker that **refuses** a title the oracle
parses is the same defect with the opposite sign — it returns a judgement call to
draft time. The fixture is weighted toward the first.

`kc-dev-flow/scripts/fixtures/pr-title/` carries the captured table with the
capture command, both release-please versions, and the capture date in its
header. A version skew between an adopter's release-please and the captured
fixture is a stop condition the extension names: re-derive the fixture, do not
assume.

### Persistence, recovery, and data-safety boundaries

- **Persistence:** none added. The checker reads `argv[1]` and a committed
  fixture; it writes nothing, holds no state, and touches no entity file. Entity
  state stays where the split-root contract puts it.
- **Recovery:** the refusal is idempotent and re-runnable — the operator fixes the
  subject and re-runs. No partial state exists to recover, because the refusal
  fires before the first push.
- **Data safety:** the checker takes the title as a single argv value and never
  through shell interpolation, matching the extension's existing rule for
  `UNIT_BODY_FILE` bytes. It has no network and no filesystem write. The oracle
  capture is the only step that fetches anything, it runs at build time only, and
  its output is committed.

### Acceptance checks that can falsify the slice

- **AC-1** — rebuild a scratch `_mods/pr-merge.md` as the pinned released body
  plus the new extension verbatim; assert `## Hook: merge` reaches the refusal
  through the extension's own override sentence, and that the pre-marker body's
  sha256 still equals `contract-manifest.json` `pr_merge_released_body.sha256`.
  Falsifier: change one byte of the pre-marker body and the pin comparison must
  name the pin key.
- **AC-2** — `kc-dev-flow/scripts/check-pr-title.test.py` drives
  `check-pr-title.py` as a process over every fixture row and asserts the exit
  code, not an imported predicate. Falsifier kind `mutation`: remove the
  empty-scope condition from the checker and the `feat(): x` row must turn from
  refuse to pass, reddening the test. Falsifier kind `refusal`: the checker must
  be watched exiting `1` on `Release-please credentials and verified production
  promotion` and `2` when the fixture is unreadable, before its silence on a
  good title counts as evidence.
- **AC-3** — bound the contract test's extension comparison at the `:end` marker,
  then two mutations: a one-character change inside the block must exit non-zero
  naming the byte and the resource path, and an appended section after `:end`
  must exit `0`. The second mutation's pre-change red is already recorded below.
- **AC-4** — rebuild `spacedock-dev/subspace-relay`'s `_mods/pr-merge.md` at
  `main` `3b8f233` in a scratch worktree as pinned released body plus the
  verbatim extension, and list which of that file's present behaviours the
  rebuild retains. Three are already known to need the list, not an equivalence
  claim: its `### The title rule` section (retained, by this slice), its
  split-root local customisation (retained by `### Split-root audit-link
  correction`), and its `### Fallback: no PR host available` section, which the
  pinned body replaces with `## Delivery without a PR` and is therefore a
  behaviour change the rebuild must declare rather than absorb.

### Where it touches

Delivery base `origin/main` `7b103a10`. `lines now` counted in that tree on
2026-09-12; `lines after` is this item's estimate.

| Path | lines now | lines after |
| --- | --- | --- |
| `kc-dev-flow/references/pr-merge-extension.md` | 424 | ~462 |
| `kc-dev-flow/skills/adopt-dev-flow/SKILL.md` | 282 | ~292 |
| `kc-dev-flow/scripts/check-pr-title.py` | 0 | ~90 |
| `kc-dev-flow/scripts/check-pr-title.test.py` | 0 | ~110 |
| `kc-dev-flow/scripts/fixtures/pr-title/release-please-verdicts.tsv` | 0 | ~30 |
| `kc-dev-flow/scripts/fixtures/pr-title/capture-oracle.cjs` | 0 | ~30 |
| `kc-dev-flow/contract-manifest.json` | 49 | 52 |
| `kc-dev-flow/MIGRATION.md` | 506 | ~520 |
| `scripts/kc-dev-flow-contract-test.py` | 2586 | ~2604 |
| `scripts/pr-merge-portable-delivery.test.py` | 330 | ~334 |
| `docs/dev/_mods/pr-merge.md` | 542 | ~580 |

Reconciled against the journey in both directions. Four rows are not in the
journey's prose and exist for reasons the journey cannot show:

- `docs/dev/_mods/pr-merge.md` must be re-synced in the same commit. The contract
  test compares this repository's own mod against the resource byte-for-byte, so
  an extension edit alone exits non-zero. Verified by the mutation recorded
  below.
- `scripts/pr-merge-portable-delivery.test.py` asserts the delivery-unit table
  rows verbatim, including the `Title` row bound to `UNIT_TITLE`. Changing that
  row's wording to name the refusal reddens it.
- `scripts/kc-dev-flow-contract-test.py` carries the `required` resource
  inventory and the sibling `.test.py` runners, so the three new files are
  invisible to CI until they are listed there.
- `kc-dev-flow/MIGRATION.md` carries the migration entry the Pilot base requires
  for a published change.

No file the journey depends on is missing from the table.
`docs/ship-flow/_mods/pr-merge.md` is deliberately absent: it carries no
`kc-dev-flow runtime extension` marker, so it is not an extension consumer.

### Stop numbers

Measured as the diff against `origin/main` `7b103a10`, read from the diff and not
from the table above. Implementation stops and reports on any of:

- **changed files > 13**
- **gross changed lines (additions + deletions) > 700**
- **`scripts/kc-dev-flow-contract-test.py` > 60 changed lines** — the named
  runaway area. Narrowing the extension comparison boundary sits next to the
  `required` inventory and the drift error text, and a boundary change that
  starts touching unrelated assertions is the shape being wrong, not the
  implementation being thorough.

These are stop conditions, not budgets. Crossing one reports what the work turned
out to be and waits for a captain choice.

### Slice count

`multi_slice_required: false`. The title rule and the post-`:end` region
declaration both land in `references/pr-merge-extension.md` and both change the
same comparison in `scripts/kc-dev-flow-contract-test.py`; neither can be
delivered without re-syncing `docs/dev/_mods/pr-merge.md` in the same commit. One
integrated slice, no `journey_slices` receipt.

### Captain-owned question raised by shape

`subspace-relay` already runs an oracle-backed Node checker that this slice's
Python checker would duplicate for that repository. The extension will state the
rule with kc-dev-flow's checker as the mechanism; whether an adopter may
substitute its own equivalent checker — and what would have to be true for the
substitute to count — is not decided here and is not in this slice.

### Reverse-recovery receipt

```yaml
reverse_recovery:
  trigger: >
    The work item claims kc-dev-flow has no seam for a fleet-wide pull request
    title rule and proposes to create one.
  boundary: >
    The merge-delivery journey from `## Hook: merge` to `gh pr create`, searched
    across the upstream chain — `spacedock-dev/spacedock` shipped mods,
    `iamcxa/kc-claude-plugins` `kc-dev-flow`, and the adopter
    `spacedock-dev/subspace-relay` at `main` `3b8f233`. Not searched: other
    adopters, none of which has run the 4.4.0 sync.
  layers:
    - surface: title refusal shipped by Spacedock's own pr-merge mod
      location: MISSING
      completeness: MISSING
      need: REQUIRED
      evidence: >
        Two strategies at `spacedock-v1` `70daeb659` — filename search for
        `*pr-title*`/`*conventional*` found nothing; content search for
        `COMMIT_OR_PR_TITLE|Conventional Commits|parseConventionalCommits` across
        `*.md`/`*.go`/`*.py` found nothing. The same grep instrument does find
        `pr-merge`, so it fires. `mods/pr-merge.md:57` prescribes
        `--title "{entity title}"` with no grammar. Required by the accepted goal.
      disproof_hook: >
        grep -rn 'COMMIT_OR_PR_TITLE|parseConventionalCommits' ~/conductor/repos/spacedock-v1
    - surface: title refusal shipped by kc-dev-flow
      location: MISSING
      completeness: MISSING
      need: REQUIRED
      evidence: >
        Two strategies at `origin/main` `7b103a10` — filename search for
        `*pr-title*`/`*check*title*` outside `.worktrees/` found nothing; content
        search for `parseConventionalCommits|COMMIT_OR_PR_TITLE|Conventional
        Commits subject` across `*.py`/`*.ts`/`*.sh`/`*.md`/`*.json` found
        nothing. `.github/workflows/` contains no title check either.
      disproof_hook: >
        grep -rln 'COMMIT_OR_PR_TITLE' --include='*.py' --include='*.md' . |
        grep -v '^./.worktrees'
    - surface: post-`:end` adopter region in an adopter's `_mods/pr-merge.md`
      location: scripts/kc-dev-flow-contract-test.py, the extension comparison
      completeness: EXISTS_BROKEN
      need: REQUIRED
      evidence: >
        The region is not merely undeclared — it is forbidden. The comparison
        takes the marker plus everything to end-of-file and requires byte equality
        with the resource, so any adopter prose after `:end` fails the contract
        test. Observed 2026-09-12: baseline exit 0; after appending
        `## The title rule (adopter-added probe)` after the `:end` marker, exit 1
        naming byte 23434. Reverted; `git status --short` clean.
      disproof_hook: >
        printf '\n## probe\n' >> docs/dev/_mods/pr-merge.md &&
        python3 scripts/kc-dev-flow-contract-test.py; git checkout -- docs/dev/_mods/pr-merge.md
    - surface: the extension's `UNIT_TITLE` binding, as the attachment point
      location: kc-dev-flow/references/pr-merge-extension.md, `#### Canonical Draft delivery unit`
      completeness: WORKING
      need: REQUIRED
      evidence: >
        The extension already displaces the released create command — "This is the
        only active PR-create command" — and binds the title as
        `reviewed UNIT_TITLE` with no grammar. `scripts/pr-merge-portable-delivery.test.py`
        asserts that row verbatim, so the binding is enforced prose, not commentary.
        It does not displace the released `**Title:** {entity title}` draft line;
        that displacement is part of this slice.
      disproof_hook: >
        python3 scripts/pr-merge-portable-delivery.test.py after editing the
        `Title` row must exit non-zero
    - surface: subspace-relay's `scripts/check-pr-title.ts`
      location: subspace-relay scripts/check-pr-title.ts at main 3b8f233
      completeness: WORKING
      need: REQUIRED
      evidence: >
        Driven as a process at `barcelona` on 2026-09-12: exit 1 on the `9475d07`
        subject, exit 0 on a conventional one. It is Node-bound — release-please
        `17.11.1` from `package.json`, imported from an internal build path — and
        its refusal prose names `spacedock-dev/subspace-relay`, so it cannot ship
        as a kc-dev-flow resource to a repository with no Node. It is the oracle
        this slice captures from, not the mechanism it reuses.
      disproof_hook: >
        node scripts/check-pr-title.ts 'Add a thing' in a relay checkout with
        node_modules present must exit 1
  decision: build
```

## Stage Report: ideation

- DONE: read `docs/architecture.md` before exploration; bootstrap a useful missing map before implementation, following `project-context-maintenance.md`
  Read `ARCHITECTURE.md` (this repository's map, 270 lines). Its only pr-merge claim — "an orthogonal delivery event mod. Any profile may use it when PR delivery is selected" — stays true, and its `scripts/` inventory lists repo-level checks only, so three new files under `kc-dev-flow/scripts/` change no stated claim. `project_context_claim_may_change` is false; no map edit and no `project_context` receipt.
- DONE: one accepted journey and explicit non-goals
  `### Accepted journey`, seven steps, each marked OBSERVED or DESIGNED and naming the acting program, with four unhappy paths in the same terms. Non-goals were admitted at backlog and are unchanged.
- DONE: persistence, recovery, and data-safety boundaries
  `### Persistence, recovery, and data-safety boundaries`: no state added, the refusal is idempotent because it fires before the first push, and the title crosses no shell interpolation.
- DONE: task-specific acceptance checks able to falsify the slice
  `### Acceptance checks that can falsify the slice`, one per AC, each naming its falsifier kind. AC-2 carries a `mutation` falsifier (drop the empty-scope condition, `feat(): x` must turn from refuse to pass) and a `refusal` falsifier (watch exit 1 and exit 2 before trusting a green).
- DONE: a file-level `where it touches` table
  Eleven rows against delivery base `origin/main` `7b103a10`, reconciled both ways. Four rows are not in the journey and carry their reason; `docs/ship-flow/_mods/pr-merge.md` is named as a deliberate exclusion because it carries no extension marker.
- DONE: the stop numbers implementation halts on
  Changed files > 13, gross changed lines > 700, and `scripts/kc-dev-flow-contract-test.py` > 60 changed lines as the named runaway area, all read from the diff against `origin/main` `7b103a10`.
- DONE: declare the observable semantics this work may change, recorded as `semantics_unchanged`
  `semantics_unchanged: false`, with the three changes named: one new command grammar, a refusal before draft presentation, and three added manifest resources changing the contract digest. Read in `profile-contract-loader.py` — not exercised — that `LOCAL_PROFILE_REFIT_REQUIRED` fires on a `local_profile_interface` change and that a missing required binding raises `Local Profile is missing bindings` — neither is touched, so no adopter needs a refit.
- DONE: reverse-recovery receipt (`brownfield_capability_change` fired)
  Five layers, each with a disproof hook. The decisive one is measured, not argued: post-`:end` adopter prose is currently *forbidden*, not merely undeclared — the contract test compares the marker to end-of-file, so baseline exit 0 became exit 1 at byte 23434 when a section was appended after `:end`, then reverted clean. `decision: build`.
- SKIPPED: journey-slicing receipt (`journey_slices`)
  `multi_slice_required` is false — both asks edit the same two files and neither can land without re-syncing `docs/dev/_mods/pr-merge.md` in the same commit. The reference's own rule is that the receipt records a true trigger, so recording one here would assert a slice split that does not exist. Judgment recorded in `### Slice count` instead.

### Summary

Shape selected the route the work item left open: the refusal ships from kc-dev-flow as a Node-free Python checker that the extension states and binds to the delivery unit's title, not as a rule each adopter binds itself. Four alternatives are recorded as rejected with the evidence that rejected them — the Local Profile binding route would fail every existing adopter closed, and the TypeScript route has nothing to run in a repository with no `package.json`. The riskiest DESIGNED step was retired to OBSERVED: release-please's parser is reachable inside this repository through the existing `scripts/fixtures/release-please-runtime` lockfile, and it disagrees with a hand-written grammar on `feat(): x` — the dangerous direction, now a fixture row.

Four things the next stage must not inherit as settled:

1. **What falsifies the step-7 oracle claim.** The claim is bounded: release-please `17.3.0` (this repository's lockfile) and `17.11.1` (subspace-relay's pin) returned the same verdict on the *17 probed titles* on 2026-09-12. Re-running `npm ci` over `scripts/fixtures/release-please-runtime` in a temp directory and re-probing falsifies it if any of those 17 rows differs between the two versions. A disagreement on an 18th title does not falsify the recorded claim but does falsify the design's assumption that one captured fixture serves both pins — which is why the extension names version skew as a stop condition. The reachability half is falsified by `npm ci` failing or by `release-please/build/src/commit.js` no longer exporting `parseConventionalCommits`. **Declared machine dependency:** the capture step needs Node and registry access; the committed fixture and the Python checker need neither.
2. **A fact supplied in the first officer's mid-task message is wrong and is not carried into the design.** The instruction to report that `spacedock state` exposes only `init` and has no `commit` subcommand does not hold on this host. `spacedock 0.27.2`: `spacedock state commit pr-merge-extension-has-no-adopter-seam --workflow-dir docs/dev` exits 0 with "Nothing to commit — state checkout already up to date", and `spacedock state bogusverb` answers `unknown subcommand (want: init|new|ready|sweep|commit)`. Only the `state --help` line is incomplete. Nothing in this slice depends on it either way: the refusal fires before the first push, and the sentinel ceremony runs after merge.
3. **The code repository is at detached HEAD** `7b103a10` (== `origin/main`), with three unrelated untracked files present. Build needs a branch before its first commit. No code was changed at this stage.
4. **Two seams the shape section leaves under-specified, and how to read them.** First, the checker's relationship to the fixture reads two ways in `## Shape` — `### The title rule's oracle` treats the table as the test's oracle, while `### Persistence` and AC-2's refusal falsifier have the checker reading it at runtime. The reading build should take, because it makes both halves true at once: the checker implements the grammar, loads the shipped fixture at startup, verifies its own decision against every row, and exits `2` on any disagreement or an unreadable fixture. That is a fail-closed self-test, and it is also why the fixture ships as a resource rather than living beside the test. Three paths go into `contract-manifest.json` `resources` on that reading — `scripts/check-pr-title.py`, `scripts/fixtures/pr-title/release-please-verdicts.tsv`, and `scripts/fixtures/pr-title/capture-oracle.cjs` — matching the manifest's existing pattern of shipping scripts and not their `.test.py` siblings; the `.cjs` earns its slot only as the re-derivation tool the version-skew stop condition tells an adopter to run. Second, journey step 2's `KC_DEV_FLOW_ROOT` has no resolution command. That gap is inherited, not invented: `references/profiles/pilot-product-slice/build.md` already names `kc-dev-flow/scripts/surface-map-check.py` as a plugin-relative path, and `subspace-relay`'s Local Profile resolves it by calling it an "Installed sibling". Build makes an existing precedent explicit rather than designing a new mechanism.

One note to the first officer, out of this slice's scope: `spacedock 0.27.2` does provide `gate consume`, so the extension's sentence "installed 0.26 does not provide them" is stale in the very file build will edit.

## Stage Report: implementation

- DONE: runnable integrated slice -- the refusal ships from kc-dev-flow itself
  `check-pr-title.py` + `### Released title override` in `pr-merge-extension.md`, re-synced verbatim into `docs/dev/_mods/pr-merge.md`; commit 019e4715.
- DONE: focused tests for owned logic and seam behavior
  `check-pr-title.test.py` drives the checker as a subprocess over all 13 fixture rows plus 3 boundary cases (refusal, unreadable fixture, missing argument); wired into `kc-dev-flow-contract-test.py`'s run() battery.
- DONE: diagnostics and bounded retry/recovery required by the shape contract
  Fail-closed self-test: the checker verifies its own grammar against the shipped fixture before evaluating any real title, so a broken grammar reports self-test disagreement (exit 2) instead of silently passing.
- DONE: AC-1 -- reachability plus released-body pin
  Grep-verified chain: `## Hook: merge` (line 49) -> released `**Title:** {entity title}` (line 61) -> `### Released title override` (line 407) names and overrides both the draft line and the create argument, names `check-pr-title.py`. Falsifier run: one byte in the pre-marker body -> exit 1 naming `pr_merge_released_body.sha256`.
- DONE: AC-2 -- refusal checker exercised as a process, both falsifier kinds
  `refusal` kind watched at exit 1 (non-conventional sentence) and exit 2 (fixture copied without its `fixtures/` sibling). `mutation` kind -- removing the empty-scope check reddens the suite via the self-test's own disagreement (exit 2 naming `'feat(): x'`), not via exit 0 as the AC's literal wording describes -- a stronger result from the fail-closed self-test design, not a weaker one.
- DONE: AC-3 -- contract test bounded at :end, both mutations observed
  `pr_merge_mod_extension` now slices `[start:end]` instead of `[start:EOF]`. One byte inside the block -> exit 1 naming the byte and both paths. Adopter prose appended after `:end` -> exit 0 (was exit 1 before this change). Verified under `--ablation-check` (fast path; the byte comparison is not gated by it) and one full non-ablation suite run, both PASS.
- DONE: AC-4 -- subspace-relay rebuild, behaviours listed not asserted equal
  Rebuilt released-body+extension in a scratch file against relay's actual `_mods/pr-merge.md` at `main` `3b8f233` (read-only, not edited). Title rule: retained with a different mechanism -- `check-pr-title.py` replaces `scripts/check-pr-title.ts`; relay's operator table for picking a type across a multi-commit branch is not covered by this slice (already the entity's declared "not covered" limit). Split-root audit link: retained by `### Split-root audit-link correction`. PR body template: retained. `### Fallback: no PR host available`: a behaviour change, not absorbed -- the pinned body's `## Delivery without a PR` uses a `local-merge:` sentinel where relay declares a `merge: local` policy; declared here, not fixed.
- DONE: post-:end adopter-region precedence declared in both places
  `pr-merge-extension.md`'s opening section and `adopt-dev-flow/SKILL.md` step 7 state the byte-equality check is bounded at `:end` and that the marked block wins on conflict as a declared operating rule for the first officer, not something the comparison itself enforces.
- DONE: implementation-exit surface map check
  `surface-map-check.py origin/main HEAD` against a 7-line Evidence block (fixtures and `.test.py` auto-excluded): `surface-map-check: OK (7 files checked)`.
- DONE: RoboRev implementation-exit observation
  `UNAVAILABLE(reason: unavailable)`. Agent `codex` OK per `roborev check-agents`; the pinned model `gpt-5.6-terra` is unconfirmable by that probe. No claim filed, no provider query made. capability: review_convergence, mode: observe, profile: pilot-product-slice, provider: roborev, identity_hash: sha256:1e0e247ecc76a78357f796ba69d47d2ecd994ae53f9d25d44f414779abfed111, config_hash: sha256:ae3555f0b3fcf5b626c39c614e3b2058bd2e31fb5840ce864edfaeded34f07f1 (`.roborev.toml`), request_count: 0, confirmation_count: 0.
- DONE: MIGRATION.md entry for the published change
  `## 2026-09-13 — the pull request title refusal ships from kc-dev-flow`, naming the new resource, the behaviour change, and that no Local Profile refit is needed.
- DONE: stop numbers, measured against origin/main after commit
  10 changed files (limit 13), 462 gross changed lines (limit 700), 36 changed lines in `kc-dev-flow-contract-test.py` (limit 60) -- `git diff --stat origin/main HEAD`.
- DONE: comment pass
  Kept the checker's grammar-source pointer (a fact the code can't state) and capture-oracle's logger note (corrected to name the right "released body" -- release-please's, not the pr-merge template's). Cut one restating sentence before commit (`self_test() below is what catches a regression here`).

### Summary

The refusal ships from kc-dev-flow itself: `check-pr-title.py` self-tests against a committed release-please oracle fixture (captured from the real `17.3.0` parser installed under `scripts/fixtures/release-please-runtime`) before deciding, and the extension chains it ahead of draft presentation and PR creation for every delivery unit. The contract test's drift comparison is now bounded at the `:end` marker, closing the "nowhere to put an adopter rule" gap the work item opened with; both AC-3 mutations were observed running, not asserted. Residual, not a defect: AC-2's mutation falsifier reddens via the checker's own self-test (exit 2, naming the disagreeing row) rather than the silent exit-0-then-caught-later shape the AC's wording describes -- stronger, not weaker, and consistent with the fail-closed design the ideation stage anticipated. Already-recorded known limit, unchanged by this stage: a coordinated edit to both the fixture row and the checker's grammar passes both the self-test and the process test; only re-running `capture-oracle.cjs` against live release-please catches that, which is why the `.cjs` ships as a resource rather than a throwaway script.

## FO note to validation — one finding from the first officer's own check

Raised by the FO while falsifying the build's drift claim, 2026-09-13. Not a
rejection: all three mutations behaved correctly (in-block edit exit 1 naming
byte 1216; append after `:end` exit 0; released-body edit exit 1 naming
`pr_merge_released_body.sha256`). Validation owns the judgment on this.

The new prose quotes the closing marker inline, backtick-wrapped, at
`docs/dev/_mods/pr-merge.md` line 132 and `kc-dev-flow/references/pr-merge-extension.md`
line 14. The file therefore contains two occurrences of the marker text and one
occurrence of the marker followed by a newline.

`scripts/kc-dev-flow-contract-test.py` is safe: its constant is the
newline-terminated form and it requires exactly one. A consumer that splits on
the bare marker text is not — the FO's own first attempt did exactly that and
silently measured a 715-character block instead of 26184, a 3% read that raised
no error. `skills/adopt-dev-flow/SKILL.md` instructs an adopter to write the
resource "between the markers" without stating which occurrence terminates it,
and `spacedock-dev/subspace-relay` is the next repository that will follow that
instruction.

Two readings, and validation should pick one rather than inherit both: the
inline quotation is safe because every implementation must use the
newline-terminated form, in which case the skill should say so; or the marker
should not appear inline at all.

## Stage Report: validation

- DONE: exact-revision journey evidence
  Candidate `019e4715`, base `7b103a10`. Journey step 4 driven through the real seam with `gh pr create` replaced by `echo would-create`: the released `**Title:** {entity title}` substitution (this work item's own title) exits 1 and the create command is never reached; `fix(kc-dev-flow): ship the pr-merge title refusal from kc-dev-flow itself` exits 0 printing `fix` and the create line runs. Checker invoked from a cwd outside the worktree, so `__file__`-relative fixture resolution is exercised, not assumed.
- DONE: AC-1 -- reachability plus released-body pin at the candidate
  Rebuilt an adopter mod as pinned released body + verbatim extension: byte-identical to `docs/dev/_mods/pr-merge.md`, released-body sha256 `ea187ab4...` == `contract-manifest.json` `pr_merge_released_body.sha256` at 10551 bytes. Falsifier run at the candidate: one byte appended inside the pre-marker body -> exit 1 naming `pr_merge_released_body.sha256` and the 10551/10552 byte counts. Reverted, tree clean.
- DONE: AC-2 -- refusal checker exercised as a process, both falsifier kinds, and the implementation's residual closed
  `refusal`: exit 1 on a non-conventional sentence, exit 2 on a checker copied without its `fixtures/` sibling, exit 2 on a missing argument. `mutation` at two layers -- dropping the empty-scope condition alone reddens via self-test (exit 2 naming `'feat(): x'`); dropping it *and* bypassing the self-test reddens the per-row process assertion with `'feat(): x': expected exit 1, got 0` and no other row. That second layer is what implementation recorded as a residual; it is now measured, and the AC's literal falsifier holds. Both mutations were run on an isolated copy; the candidate worktree was never mutated for AC-2.
- DONE: AC-3 -- contract test bounded at :end, both mutations re-observed at the candidate
  One byte inside the marked block -> exit 1 naming byte 15745 and both paths; `## The title rule (adopter-added probe)` appended after `:end` -> exit 0; baseline exit 0. Reverted after each, `git status --short` empty.
- DONE: AC-4 -- subspace-relay rebuild at the pinned SHA, behaviours listed
  Relay's `docs/dev/_mods/pr-merge.md` read from `git show 3b8f233:` (153 lines, no extension markers). Rebuild retains: the title rule (different mechanism -- `check-pr-title.py` replaces `node scripts/check-pr-title.ts`), the split-root audit link (`### Split-root audit-link correction` resolves the entity path through `spacedock status --resolve`, so relay's `{slug}/index.md` layout works without adopter prose), and the PR body template. Not retained, and corrected against implementation's account: relay's `### Fallback: no PR host available` is about `gh`/push *failing*, while the pinned body's `## Delivery without a PR` is about entities that produce *no diff* -- different conditions, not a substitution. The rebuild's answer to relay's condition is `#### Local failure-policy override`: stop, do not fall back to local merge. Implementation's "where relay declares a `merge: local` policy" is imprecise rather than wrong: relay's mod handles both a `merge: local` declaration and its absence, while relay's README at `3b8f233` declares only `state:` and `trunk:` and makes no such declaration.
- DONE: the oracle fixture re-derived from the live parser, not trusted
  `node kc-dev-flow/scripts/fixtures/pr-title/capture-oracle.cjs` against release-please `17.3.0` installed under `scripts/fixtures/release-please-runtime`: all 13 data rows identical to the committed TSV; the only diff is the capture date in the header. Self-test and process test both read that TSV, so this is the only step that grounds it.
- DONE: retry/recovery, duplicate, diagnostic, and data-safety results that apply
  Recovery: the refusal is idempotent -- re-running after a corrected subject is the whole recovery path, and it fires before the first push, so no partial state exists. Diagnostics: exit 1 prints the rejected title; exit 2 prints which condition could not be decided (unreadable fixture, self-test disagreement naming the row, or bad usage). Data safety: the title crosses no shell interpolation, the checker has no network and no filesystem write. Duplicate handling: not applicable -- the checker holds no state.
- DONE: delivery base decision (`delivery-branch-base.md`)
  No open artifact shares this candidate's lineage: no reliance on unmerged behaviour. PR #321 (`fix/kc-dev-flow-adoption-correctness`, not draft) shares three files -- `kc-dev-flow/MIGRATION.md`, `kc-dev-flow/skills/adopt-dev-flow/SKILL.md`, `scripts/kc-dev-flow-contract-test.py` -- in disjoint sections. `git merge-tree --write-tree abbe9269 HEAD` conflicts only on `docs/dev/_mods/profile-contract-loader.py`, a file this candidate does not touch. Recommend trunk base with that textual overlap recorded; the topology ruling is `pr-merge`'s `### Delivery topology decision`, not this stage's.
- DONE: stop numbers re-measured at the candidate
  `git diff --stat origin/main...HEAD` (three-dot, since `origin/main` moved to `e0826132`): 10 changed files (limit 13), 462 gross changed lines (limit 700), 36 changed lines in `scripts/kc-dev-flow-contract-test.py` (limit 60). None crossed.
- DONE: remaining production obligations and promotion triggers
  None crossed. No production credential, data, irreversible migration, unattended operation, or SLO duty. Consumers absorb this by taking the new plugin version; `local_profile_interface` is untouched, so no adopter Local Profile refit. `MIGRATION.md` carries the release obligation.
- SKIPPED: when the receipt declares `semantics_unchanged: true`, the named `equivalence_instrument` observed to fail against `equivalence_instrument_failure`, the case it must flag
  The work profile receipt declares `semantics_unchanged: false`, so the clause does not apply.
- SKIPPED: provider feedback disposition when a delivery artifact exists
  No delivery artifact exists. `gh pr list` shows no PR for `spacedock-ensign/pr-merge-extension-has-no-adopter-seam`; entity `pr:` is empty. Draft creation is Captain-authorized through `pr-merge` and has not been reached.
- FAILED: observe the full contract-test battery abort because `check-pr-title.test.py` failed
  Three attempts, none completed: the machine reached load average 509 with 188 defunct processes and a separate `kc-dev-flow-contract-test.py` hung 10h+ in the same worktree from an earlier stage. Runs timed out at 400s and 1500s and were killed; the mutation was reverted each time and `git status --short` is empty. What is established instead: the full non-ablation suite exits 0 at the candidate; the battery entry `run([sys.executable, "kc-dev-flow/scripts/check-pr-title.test.py"], "PR title check")` sits inside the `not require_ablation_only` block and `run()` raises through `require()` on a non-zero exit; and that exact command, from the same ROOT cwd, is green clean and red under mutation. Unproven: that the battery reaches the entry at runtime. Re-run when load is sane -- insert `raise SystemExit("probe")` after `rows = load_rows()` in `check-pr-title.test.py`, run `python3 scripts/kc-dev-flow-contract-test.py`, expect non-zero carrying `PR title check failed`, then revert.

### Findings

Three defects in bytes that ship to adopters. None falsifies an acceptance criterion; together they
block Draft creation, because `spacedock-dev/subspace-relay` is the next repository to run the sync
and all three land in its checkout. All three touch the same two files and belong in one correction
round.

1. **The extension quotes its own closing marker inline, and the sync instruction is a text search.**
   `references/pr-merge-extension.md` line 14 and the synced `docs/dev/_mods/pr-merge.md` line 132
   carry the `:end` marker text backtick-wrapped. `skills/adopt-dev-flow/SKILL.md` step 7 tells an
   adopter to write the resource "verbatim between its `:start` and `:end` markers" -- a prose
   instruction, not a script. An agent obeying it with a bare text search stops at the first
   occurrence and writes 14 lines instead of 477. The first officer's own tool already produced that
   shape: 715 characters read instead of 26184, silently. **Ruling: remove the inline quotation**
   ("after this file's own closing runtime-extension end marker" loses no meaning). The alternative
   -- keep it and document the newline-terminated form in the skill -- is wording against a failure
   shape that has already repeated, and leaves the hazard in every adopter's file.
   `scripts/kc-dev-flow-contract-test.py` itself is safe: its constant is newline-terminated and it
   requires exactly one. Worth the FO's judgment as part of the same round: a
   `pr_merge_mod.count("<!-- kc-dev-flow runtime extension:end -->") == 1` require on the *bare*
   form, beside the existing newline-form uniqueness check, turns "never quote it inline" into an
   enforcement point instead of a convention -- about four lines, well inside the 60-line stop number.
2. **The extension never names the version-skew stop condition the design depends on.**
   `grep -nE 'skew|17\.3|17\.11|capture-oracle|fixture|re-derive|release-please-verdicts'` over
   `references/pr-merge-extension.md` and `skills/adopt-dev-flow/SKILL.md` returns nothing. Shape's
   `### The title rule's oracle` states "a version skew between an adopter's release-please and the
   captured fixture is a stop condition the extension names"; the shipped extension names no such
   condition. The self-test proves only that the checker agrees with its own committed TSV, never
   with the adopter's parser, so an adopter on a newer release-please gets a confident green from a
   stale oracle with no instruction telling them when to re-derive.
3. **Two shipped resources cite a section that does not exist.**
   `scripts/fixtures/pr-title/release-please-verdicts.tsv` (header) and
   `scripts/fixtures/pr-title/capture-oracle.cjs` (comment) both point at
   `kc-dev-flow/references/pr-merge-extension.md`, "The title rule's oracle". That section exists
   only in this entity's `## Shape`, in the split-root state checkout, which no adopter receives.
   This is the same gap as finding 2 seen from the other end: fixing 2 gives these citations a real
   target.

**Worktree hazard, not a defect in the candidate.** A `kc-dev-flow-contract-test.py` run from an
earlier stage (PID 25649) has been alive over ten hours inside this entity's code worktree, driven
by a script that mutates `docs/dev/_mods/pr-merge.md` and reverts it. It is idle at the committed
state and the worktree is clean, but it should be terminated before the correction round is
dispatched into the same worktree. Not terminated here: it is another stage's process.

### Summary

All four acceptance criteria pass at candidate `019e4715`, each with its falsifier observed running
at that revision rather than carried over from implementation, and AC-2's residual is closed by
measurement: with the self-test bypassed, the per-row process assertion reddens on `feat(): x` alone,
exactly as the AC words it. The oracle fixture was re-derived from the live release-please `17.3.0`
parser and matches on all 13 rows, so the committed TSV is grounded rather than trusted. Three prose
defects in adopter-facing bytes -- the inline `:end` marker quotation, the absent version-skew stop
condition, and two resources citing a section that does not exist -- block Draft creation but not the
acceptance criteria, and route to one implementation correction round touching
`references/pr-merge-extension.md` and `skills/adopt-dev-flow/SKILL.md`. One item is FAILED for
environment reasons only: the machine reached load average 509 with a 10h-hung suite from an earlier
stage in the same worktree, so the battery-abort observation could not be completed in three attempts;
the candidate worktree is clean and unmodified after each.

## Stage Report: implementation (cycle 2)

- DONE: finding 1 -- remove the inline `:end` marker quotation
  `kc-dev-flow/references/pr-merge-extension.md` and the resynced `docs/dev/_mods/pr-merge.md` no longer backtick-quote `<!-- kc-dev-flow runtime extension:end -->` inline; the sentence reads "after this file's own closing runtime-extension end marker" instead. Commit `17915d9e`.
- DONE: finding 1 -- turn "never quote it inline" into an enforcement point
  `scripts/kc-dev-flow-contract-test.py` adds `pr_merge_mod.count(bare_end_marker) == 1` beside the existing newline-form uniqueness check, 8 lines including its comment (well inside the 60-line stop number). Falsifier kind `mutation`, run in isolation against a copy of the committed file (not the full battery, per the host-load caution): reintroducing the inline quotation moves the bare count from 1 to 2, which the new require would now catch -- verified by direct count comparison, not by re-running the whole suite for one string check.
- DONE: finding 2 -- name the version-skew stop condition
  New `### The title rule's oracle` section in `pr-merge-extension.md` (synced verbatim into `docs/dev/_mods/pr-merge.md`) states the self-test only proves agreement with the fixture's captured release-please version, names the version-skew stop condition, and gives the `capture-oracle.cjs` re-derive command. `skills/adopt-dev-flow/SKILL.md` step 7 gets one pointer sentence to that section rather than a second copy of the explanation.
- DONE: finding 3 -- shipped resources now cite a section that exists
  `scripts/fixtures/pr-title/release-please-verdicts.tsv` and `capture-oracle.cjs` were already citing `kc-dev-flow/references/pr-merge-extension.md`, "The title rule's oracle" -- unchanged by this round, since fixing finding 2 gives that exact heading a real target in the shipped file. Verified: `grep -n "The title rule's oracle" kc-dev-flow/references/pr-merge-extension.md` now matches.
- DONE: AC-1 and AC-3 mutations re-observed at the new candidate `17915d9e`
  In-block byte change inside `### The title rule's oracle` -> exit non-zero naming byte 17781 and both paths; reverted, tree clean. Adopter prose appended after `:end` -> exit 0 (adopter-owned region unaffected), matching the pre-existing designed behavior. Released-body pin unchanged by this round (no edit before the `:start` marker).
- DONE: full contract-test battery, run singly and bounded (host-load caution honored)
  `python3 scripts/kc-dev-flow-contract-test.py` at the clean candidate: `PASS`, one bounded background invocation, no chaining with a mutation in the same command this time -- the first attempt chained mutate+run+revert and the run alone exceeded a 150s bound under transient load; split into separate steps for the retry, each observed to completion.
- DONE: implementation-exit surface map check
  `surface-map-check.py 019e4715 HEAD` against a 4-line evidence block for this round's 4 changed files (all mapped to AC-1/AC-3, `without-it` bound to each path): `surface-map-check: OK (4 files checked)`.
- DONE: RoboRev implementation-exit observation
  Unchanged from cycle 1: `UNAVAILABLE(reason: unavailable)` -- pinned model `gpt-5.6-terra` remains unconfirmable per the stage-def fetch's own 2026-09-13 probe (agent `codex` OK). No re-probe spent since the probe is dated the same day and nothing in this round changes agent/model availability. No claim filed, no provider query made.
- DONE: stop numbers, re-measured against `origin/main` after commit
  `git diff --stat $(git merge-base origin/main HEAD) HEAD`: 10 changed files (limit 13, unchanged from cycle 1 -- this round edits existing files only), 518 gross changed lines (limit 700), 44 changed lines in `kc-dev-flow-contract-test.py` (limit 60, up from 36).
- DONE: worktree hazard the FO flagged
  No `kc-dev-flow-contract-test.py` process alive in this worktree; load average 7-12 at the time of this round's runs. Nothing to terminate.
- DONE: comment pass
  Kept the one new code comment (`scripts/kc-dev-flow-contract-test.py`, why a bare text search over prose can stop at the first occurrence) -- a fact the require's own message doesn't state. No comment cut; none added elsewhere, since the rest of this round is shipped prose, not code.

### Summary

Closed all three validation findings with one correction: removed the inline `:end` marker quotation, gave the version-skew stop condition a named home in `pr-merge-extension.md`'s new "The title rule's oracle" section (which also grounds the two resources that already cited it), and turned the marker-quoting rule into a contract-test enforcement point instead of leaving it a convention. Fixed one process mistake from this round's own first attempt: a chained mutate-and-revert command left `docs/dev/_mods/pr-merge.md` reverted to the pre-fix commit via `git checkout --`, silently discarding the resync; caught by re-grepping for the marker text before trusting the first mutation run, and re-synced before proceeding. All re-observed mutations and the full battery pass at candidate `17915d9e`; stop numbers stay well inside their limits.
