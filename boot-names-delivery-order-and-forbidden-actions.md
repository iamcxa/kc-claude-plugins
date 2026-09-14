---
title: "The boot message names the delivery order and the forbidden actions: push and open the Draft PR before preparing validation; never create repositories, change settings or branch protection, or run CI off the PR branch"
status: ideation
source: "measured on ship-cloud-wrapper-r3, 2026-09-14/15 (questions log on spacedock-state/ship); Captain 2026-09-15 「r4 現在開」"
product: kc-ship-flow
planning-window:
planning-outcome:
sprint: ship-cloud-wrapper-r4
sprint-readiness: ready
started: 2026-09-14T22:34:15Z
completed:
verdict:
worktree:
issue:
pr:
mod-block:
id: v9mf30n3s03ev5dvtn08vsed
gates:
    version: 1
    records:
        - id: gate:v9mf30n3s03ev5dvtn08vsed:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:v9mf30n3s03ev5dvtn08vsed-backlog-1
              briefing:
                id: briefing:v9mf30n3s03ev5dvtn08vsed:backlog:attempt-1:revision-1
                digest: sha256:6e0ae11f0de7900b54443904f24aa2d52402ffbfd890d6ae90c959c8fc379543
                room-ref: ./boot-names-delivery-order-and-forbidden-actions/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:v9mf30n3s03ev5dvtn08vsed:backlog:1
                briefing: briefing:v9mf30n3s03ev5dvtn08vsed:backlog:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-09-14T22:30:10.444389Z"
                decision: approve
                reason: 'backlog admission on the batch conn: brief carries bite, consumer, AC-1..4, non-goals, route-back. Enter ideation.'
                conn:
                    quote: r4 現在開
                    source: Captain chat 2026-09-15, opening the ship-cloud-wrapper-r4 batch of three (pilot profile)
              application:
                target-stage: ideation
                state: consumed
        - id: gate:v9mf30n3s03ev5dvtn08vsed:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:v9mf30n3s03ev5dvtn08vsed-ideation-1
              briefing:
                id: briefing:v9mf30n3s03ev5dvtn08vsed:ideation:attempt-1:revision-1
                digest: sha256:50f95320bcc756fab9115026123c798817e0f61453cb8357f2d39775ab0f7d22
                room-ref: ./boot-names-delivery-order-and-forbidden-actions/review/ideation/briefing-1
---

bite: (1) 2026-09-14, two of five r3 workers (`pr-merge-released-body-pin-per-mod-version`, `ship-watch-runs-without-conductor-sql`) prepared their validation gate with the candidate existing only in the sandbox — no branch on origin, no PR — so the ship FO could not verify at a pinned SHA and had to message each worker to push first (two extra rounds, ~20 minutes each). (2) 2026-09-14, the `adopter-contract-test-ships-with-the-package` worker pushed a fixture branch to iamcxa/kc-claude-plugins for a live Actions probe (two runs, Kent pays the minutes), attempted `gh repo create` (403) and `PUT repos/…/branches/main/protection` (403); nothing changed only because the token lacked scope. The boot message (dispatch.sh 0.2.0 + #445 wording) forbids merging and gate decisions but says nothing about repository settings, repository creation, or CI runs outside the PR's own branch, and does not order delivery before validation.

consumer: every cloud worker booted by `kc-ship-flow/scripts/dispatch.sh` (`--message-file` boot) and `--resume`; the ship FO's watch, which reads the state branch expecting a pinned candidate at validation.

## Accepted outcome

A worker that reaches validation has already pushed its branch and opened the Draft PR, and no worker attempts an outward-facing repository action.

## Acceptance criteria

* **AC-1** The boot header (both dispatch and resume) carries, verbatim: "Before preparing the validation gate: push your branch to origin and open the Draft PR through the pr-merge mod; the gate question names the PR number and the candidate SHA." Verified by: `dispatch.sh --dry-run` boot output contains the sentence; `dispatch.test.sh` asserts it for both modes. Falsified by: either boot lacking it.
* **AC-2** The boot header carries, verbatim: "Never create a repository, change repository settings or branch protection, add secrets, or run CI on any branch other than this task's own; a needed permission is a `Q:` line, not an attempt." Verified and falsified as AC-1.
* **AC-3** `watch.sh` reports `question` (not `gate-prepared`) when a validation gate is prepared while the entity's `pr:` field is empty, with a one-line reason. Verified by: a fixture state with a prepared validation gate and empty `pr:`. Falsified by: `gate-prepared` on that fixture.
* **AC-4** No new fixture copies an existing file; comment lines added stay under the repository's 3% baseline or each carries a fact the code cannot state.

## Non-goals

- No token-scope or GitHub-side enforcement (Kent's tokens, not this package).
- No change to the conn/gate-authority wording #445 landed.

## Route-back conditions

- Back to backlog if `dispatch.sh`'s boot text moves into a template file under another task; re-point AC-1/AC-2 at that file.

Profile recommendation: pilot.

## Work profile receipt

```yaml
work_profile:
  schema: kc-dev-flow-work-profile/v3
  selected: pilot-product-slice
  recommended: pilot-product-slice
  basis: >
    Every cloud worker dispatch.sh/watch.sh boots reads this text; audience is
    every future worker on this and later sprints (not disposable), the fix
    creates persistent value (prevents the two dated repeat-incident classes),
    and likely iteration follows as boot wording gets exercised by more
    workflows. No production credentials/data, destructive external mutation,
    irreversible migration, or consumer-facing compatibility break is in
    scope; no SLO/support/release-ownership duty attaches.
  route: [shape, build, verify-deliver]
  obligations:
    architecture:
      - Locate the exact boot-header emission point(s) in dispatch.sh for
        both --message-file boot and --resume before editing.
      - Locate watch.sh's validation-gate-prepared reporting path and its
        read of the entity's pr: field.
    implementation:
      - Add the two verbatim sentences (AC-1, AC-2) to the boot header text
        used by both boot modes, not a copy in each.
      - Change watch.sh to report question (not gate-prepared) when a
        validation gate is prepared and pr: is empty, with a one-line reason.
    testing:
      - dispatch.test.sh asserts both verbatim sentences appear in
        --dry-run output for both boot modes (AC-1, AC-2).
      - A fixture state with a prepared validation gate and empty pr: proves
        watch.sh reports question, not gate-prepared (AC-3).
      - New fixtures do not copy an existing repository file or cached
        plugin file and carry no real repository SHA; added comment lines
        stay under the repository's 3% baseline (AC-4).
  scope_boundary: >
    No token-scope or GitHub-side enforcement change (Non-goal); no change to
    the existing conn/gate-authority wording from #445 (Non-goal); this is
    wording + a reporting-state check, not a new permission or auth mechanism.
  semantics_unchanged: true
  decision:
    authority: "Captain batch approval, 2026-09-15, 「r4 現在開」 (conn recorded by the ship first officer; applied here per dispatch fc20223438b3)"
    at: "2026-09-15T00:00:00Z"
```

## Ideation: shape

### Emission points confirmed (single shared place, not per-mode)

- `dispatch.sh:150` defines one variable, `boot_gate_line`, holding the existing
  gate-authority sentence. It is emitted at exactly two call sites: `do_resume()`
  (`dispatch.sh:201`, `printf '%s\n\n' "$boot_gate_line"`) and the fresh-boot loop
  (`dispatch.sh:324`, same `printf`). Both call sites read the same variable — AC-1
  and AC-2 land by appending to (or adding sibling variables beside) `boot_gate_line`
  once at line 150; no duplicate literal in either `do_resume()` or the boot loop.
- `watch.sh`'s validation-gate-prepared check is `gate_status()` (`watch.sh:129-157`),
  called from exactly one site, `poll_once()` (`watch.sh:310-319`:
  `gs=$(gate_status "$entity_path" "$stage"); if [ "$gs" = prepared ]; then echo "$slug gate-prepared"`).
  `poll_once` itself is the single call site for both `--once` (`watch.sh:382`) and the
  continuous loop (`watch.sh:385`) — so AC-3's branch (prepared-but-empty-`pr:` → `question`)
  is one change in `poll_once`/`gate_status`, not a duplicate per watch mode.
- `gate_status()` currently determines `prepared`/`not-prepared` from `status`+`gates.records`
  only; it already parses the frontmatter with `yaml.safe_load` (`watch.sh:145`), so reading
  `data.get('pr')` is a same-parse addition, not a second YAML pass.

### Accepted journey

1. Dispatch boots a worker (fresh `--message-file boot` or `--resume`); the shared
   `boot_gate_line` block now also carries AC-1 (push+PR before validation) and AC-2
   (forbidden repo-level actions; ask instead).
2. The worker runs its route, and — per AC-1 — pushes its branch and opens the Draft PR
   through `pr-merge` *before* calling `spacedock gate prepare` for `validation`.
3. `watch.sh` polls; `gate_status()` reports `prepared`, and because `pr:` is now
   non-empty, `poll_once` reports `gate-prepared` — the ship FO can verify at the pinned
   PR/SHA immediately, no round-trip.
4. Two rejected paths this closes: (a) a worker prepares the validation gate with the
   candidate only in-sandbox (no push, no PR) — `pr:` stays empty, so `poll_once` now
   reports `question` with a one-line reason instead of a `gate-prepared` the ship FO
   can't act on; (b) a worker attempts an outward-facing repo action (create repo, change
   branch protection/settings, add secrets, run CI off-branch) — AC-2's sentence tells it
   to ask (`Q:` line) instead of attempting, so `watch.sh`'s existing question/quota
   transcript-tail detection (unchanged) is what surfaces it.

### Explicit non-goals (carried from the brief)

- No token-scope or GitHub-side enforcement — Kent's tokens are out of this package's
  reach; AC-2 is wording that redirects the worker to ask, not a technical block.
- No change to the conn/gate-authority wording #445 landed — `boot_gate_line`'s existing
  sentence is kept verbatim; AC-1/AC-2 are additions alongside it, not edits to it.
- No rewrite of watch.sh's transcript-tail question/quota/stopped detection — AC-3 only
  changes the `prepared`-branch's outcome when `pr:` is empty; the quota/question/stopped
  paths for a not-yet-prepared gate are untouched.

### Stop numbers for this slice

- 2 boot-text call sites touched (`do_resume`, boot loop), 1 shared source line.
- 1 watch.sh call site touched (`poll_once`), 1 shared decision function (`gate_status`).
- 3 acceptance criteria are wording/one-condition changes (AC-1, AC-2, AC-3); AC-4 is a
  fixture-hygiene constraint on the tests that prove them, not separate production code.

### File-level "where it touches"

| File | Touches | Lines now | Lines after (est.) | Reconciled against journey |
|---|---|---|---|---|
| `kc-ship-flow/scripts/dispatch.sh` | Extend `boot_gate_line` (or add 1-2 sibling variables) at line 150 with AC-1 + AC-2 sentences; no change to the two `printf` call sites (201, 324) — they already interpolate the shared variable(s). | 389 | ~392-395 (new sentence text only; no new call sites) | Step 1 of the journey — one shared emission, both modes. |
| `kc-ship-flow/scripts/dispatch.test.sh` | New assertions on existing dry-run outputs: fresh-boot message body (near the `out_*`/`msg_*` block around lines 85-150) and resume message body (existing `l2` assertion block, lines 381-394) each gain 2 `grep -qF` checks for the AC-1 and AC-2 verbatim sentences. | 440 | ~448-452 | Proves step 1 for both modes without a new fixture. |
| `kc-ship-flow/scripts/watch.sh` | `gate_status()` (129-157) additionally returns/encodes the entity's `pr:` value (already inside the same `yaml.safe_load` parse); `poll_once()` (310-319) branches: prepared + non-empty `pr:` → `gate-prepared` (unchanged), prepared + empty/missing `pr:` → `question` with a one-line reason. | 388 | ~398-404 | Steps 3 and 4a of the journey. |
| `kc-ship-flow/scripts/watch.test.sh` | Existing fixtures `task-gate-prepared.md` and `task-folder-gate/index.md` currently have **no `pr:` field at all** and are asserted to report `gate-prepared` (lines 54-55, 113-116, 178-179). Under AC-3's literal condition ("empty") these would flip to `question` and break 3 existing assertions unless both fixtures gain a non-real `pr:` value (e.g. `https://example.test/pr/0`) to keep exercising the success path. A separate **new** fixture (not a copy of either — AC-4) supplies the prepared+empty-`pr:` case and a new assertion for `question`. | 249 | ~258-266 (2 edited fixtures' frontmatter + ~1 new small assertion block) | Proves steps 3 and 4a; the fixture edit is load-bearing, not incidental — flagged here so build doesn't silently break the 3 existing passing assertions. |
| New fixture (e.g. `fixtures/watch/dev/.spacedock-state/task-gate-prepared-no-pr.md`) | New file, not a copy; small hand-written frontmatter (stage `validation`, one unresolved attempt, `pr:` absent or empty), no real repository SHA. | 0 | ~16-18 | Proves AC-3's `question` branch; satisfies AC-4 (no copy, no real SHA). |

### Notable decision surfaced for build

The two existing `gate-prepared` fixtures lacking a `pr:` field is the one place this
slice's shape has a real fork: either (a) treat "missing key" the same as "empty string"
(matches AC-3's plain-English "empty" and closes the exact incident-1 shape most
literally), which requires editing both existing fixtures to add a `pr:` value so they
keep proving the success path, or (b) treat missing-key as a pre-AC-3 fixture bug to fix
regardless. Both land at the same code change in `gate_status`/`poll_once`; the only
open question is fixture edits, not production logic. Recommend (a) and call out the
fixture edit explicitly in the build stage's report so the 3 flipped assertions aren't
mistaken for a regression.

## Stage Report: ideation

- DONE: Locate the exact boot-header emission point(s) in dispatch.sh (--message-file boot and --resume) and watch.sh's validation-gate-prepared/pr-empty check point, confirming AC-1/AC-2/AC-3 land in one shared place, not a duplicate per mode.
  `dispatch.sh:150` (`boot_gate_line`) emitted at `dispatch.sh:201` (resume) and `:324` (boot); `watch.sh:129-157` (`gate_status`) called once from `poll_once` at `watch.sh:314-319`, itself the single call site for `--once` and the continuous loop.
- DONE: State the accepted journey, non-goals, stop numbers.
  See "Accepted journey", "Explicit non-goals", "Stop numbers for this slice" above.
- DONE: Produce a file-level "where it touches" table reconciled against the journey.
  See "File-level 'where it touches'" table above; includes a surfaced fork (existing gate-prepared fixtures lack `pr:` entirely) that build must resolve, not silently break.

### Summary

Confirmed both boot modes already share one emission point (`boot_gate_line`) and watch.sh's gate check already funnels through one function/call site, so AC-1/AC-2/AC-3 are each a single-place change. Surfaced a real shape decision for build: the two existing `gate-prepared` watch.sh fixtures have no `pr:` field at all, so a literal AC-3 implementation flips their expected outcome unless those fixtures are given a non-real `pr:` value — recommended fixing this explicitly rather than treating it as an incidental break.

