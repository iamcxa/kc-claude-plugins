---
title: "The pr-merge extension has no adopter seam, so a fleet-wide title rule has nowhere to live"
status: implementation
source:
product: kc-dev-flow
planning-window:
planning-outcome:
sprint: dev-flow-pr-merge-adopter-seam
sprint-readiness: ready
started:
completed:
verdict:
worktree:
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
