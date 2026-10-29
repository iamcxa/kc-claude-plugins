# Validation scope

This file records the package's validation evidence and its limits.

## Field use, measured 2026-10-12

Read from the archived task files on the dev2 and dev2-poc state branches of the four
adopting repositories (this one and three product repositories), from local Claude Code
session logs, and from local Codex session logs. Counts are of archived task files'
frontmatter, not of companion files.

| Claim | Evidence |
| --- | --- |
| Tasks run end to end | 89 archived tasks: 78 pilot, 2 prod, 9 POC |
| Delivery through a merged PR | 83 of them record `pr: pr-merge:`; every pilot and prod task, and 3 of the 9 POC tasks |
| The `dev` entry runs | `kc-dev-flow-2:dev` was invoked through the Skill tool in 8 adopter sessions |
| Engineering Reviewer runs | 11 dispatches in real work, 2026-09-17 to 2026-10-07 |
| Learning delivery | 3 learning.md Draft PRs created by `learn` were merged in one product repository (2026-09-20, 09-23, 10-08) |
| Observer | one run on an archived task reported 3 FO rule violations, each found in git by quote and commit |

## Still unproven or not built

- **Codex as the host:** no Codex session log references a dev2 stage skill, so Codex
  shorthand resolution, Codex worker inheritance and Claude/Codex lifecycle parity are
  untested. Every FO above ran in Claude Code.
- **Chief Engineer:** never dispatched; its behaviour is unobserved.
- **Production recovery exceptions:** not implemented; two prod tasks ran the normal route.
- **Direct POC eligibility:** not implemented; POC is used only when the user selects it.
- **Stage-entry content:** the skipped-stage-pin bug is not fixed and content at stage
  entry is not sealed. Dispatch records pin the package root and dispatch commit, not
  the content a worker read.
- **Gate correctness:** not proven. The observer and the decision ledger measure FO's
  gate records after the fact; they do not prevent a wrong record.

Use explicit workflow paths and check the live worker roster after resuming an
orchestrator; a resumed orchestrator does not establish that an old worker exists.

## Before field use

The sections below are the evidence gathered before field use and keep their own
limits. The packaged core comes from source commit
179b54eea2694806e9c268affb67c573dfdda632 (30 files before packaging). That source
added the thin `dev` entry and conditional document/check guidance after the
historical trials below. Those trials did not execute this final package.

## Historical bounded evidence

| Case | Observed result | Limit |
| --- | --- | --- |
| Claude Pilot, source f28873465da36159a30dd0e129423a665df295ad | Implementation, fresh independent validation, a same-candidate removal control, human approval, and local archive closure | No remote merge, pull request, deployment, or production delivery; completion messages required recipient correction |
| Claude existing-code Pilot, same source | Reused an existing CSV formatter, retained a manually used archive check, recovered from a real Git lock refusal, and passed implementation/independent checks including column-order and output-encoding controls | Design needed human correction; nonblocking finding disposition was incomplete and the validation gate remained unapproved |
| Codex profile trial, source c600daed70c54babd85dfa9f67b115427384ae71 | POC implementation, invalid-profile refusal before dispatch, and Production validation that rejected acceptance despite five passing local test groups because exercised recovery evidence was missing | Stage-scoped cases needed command corrections and an authorized replacement worker; no accepted gate or delivery |

A separate Claude correction replay on the latter source was **partial**:
record-only disposition was exercised and an actual defect with stale evidence
was held, but the design diagram still omitted a rejection branch and two cases
retried after preparation failed. This is not a complete gate-lifecycle pass.

An earlier local Codex test package, version `0.0.0-poc.c600daed`, installed and
exposed six skills. Native reads verified the three stage skills, version and
source bytes. It predates the seventh `dev` skill, so it is not evidence for
that entry, the final package's loading, or remote marketplace distribution.
It is not a published release.

The three trials use different tasks and source snapshots. Their results cannot
be combined into a same-version, full-lifecycle, two-host acceptance claim.
Timing and list-price telemetry do not establish lower cost or a size reduction.

## Packaging baseline checks

At packaging commit `8ca9700`, a model-free native Codex check installed the local candidate through the
repository marketplace, matched all 33 package files to the candidate, and found
all seven enabled skills through the host's `skills/list` interface, including
`dev`. A pre-install control found no skills for this plugin. Removal restored
the prior configuration and removed the temporary cache. This establishes local
installation and discovery, not model invocation, shorthand resolution, reference
following, worker inheritance, or remote publication.

Packaging baseline checks passed: routing lint, 15 mutation tests, repository skill
frontmatter, the native Codex manifest validator, and six model-free Spacedock
stage/host dispatch handoffs with refusal controls (CLI 0.27.2). Claude marketplace
schema and installation checks passed in a temporary home; no model smoke test
ran. Release configuration and version parity passed using a temporary validation
index to include the new files without staging the review candidate.
Public-content checks found no blocking or secret-pattern hits; a heuristic email
warning refers to the synthetic fixture author `fixture@example.invalid`.

## SD adoption checks and exclusions

The adoption addition promotes the Pilot fixture into one split-root workflow
source with a small POC adaptation. The existing CLI test now exercises both
ordered graphs across POC/Pilot/Prod, synthetic gate successors, exact stage-skill
handoffs on both hosts, canonical mod discovery, and implementation/validation
reuse of a real stamped task worktree. The copied mod stays byte-identical to the
explicitly supplied active SD package. Merge guard arms `pr-merge` and requests
hook invocation; it does not execute that hook. The no-hook negative control
finalizes locally, showing why pre-activation registration review is required.
Fresh validation is declared and transported, not a worker execution claim.

These tests use disposable code/state repos, synthetic state and labelled gate
decisions, not real user approval or product work. No model, PR creation, hook
body or remote merge runs. No actual project was commissioned or migrated.
A subsequent model-free Codex install matched all 34 adoption-snapshot files and
listed the seven enabled skills, including `dev`; the pre-install control found
none. Cleanup restored the prior configuration bytes and removed the cache.
That snapshot predates this evidence paragraph and the corresponding README
summary. It proves local installation/discovery of the adoption content, not
model execution, entry behavior, reference following or remote publication.
Maintenance lint requires the full source repository's frontmatter checker.

The limits that still hold are listed under "Still unproven or not built" above.

## Local learning recorder

The local slice adds an evaluate-learning skill and a stdlib recorder for
explicitly supplied evidence packs. Tests in disposable Git repositories cover
add/no-change/remove and mixed proposals; same-clone linked-worktree concurrent
claims; ineligible inputs; invalid/stale completion; explicit interruption
recovery; missing/torn records; and concurrent atomic completion. Synthetic
results test schema, ownership and persistence, not whether an agent selected
the right practice or whether a learning improved a real outcome.

Closure, merge, source PR and evidence are caller-supplied facts. The helper
performs no SD/provider queries, model calls, hook installation, background launch,
PR/issue posting or learning.md/AGENTS.md edits. A receipt records an evaluation,
not adoption. Owner-stop attestation is explicit caller input, not liveness
verification. POSIX/local-filesystem locking does not establish cross-clone or
distributed reliability. Historical seven-skill loading evidence predates the
new evaluator skill; it does not prove this new entry's discovery or behavior.

## Manually invoked learning delivery and notices

The `learn` skill now binds a named task's archived SD state and original merged
GitHub PR using existing read commands, delegates evaluation/materialization,
and preserves explicit commit/PR authority. These are skill instructions, not
an automatic collector or mechanically authenticated provider evidence.

The recorder's affected 14-case suite passed, retaining the nine local evaluation
controls and adding delivery/notice cases: a 12-process delivery claim race,
simulated accepted send with lost response and matching-PR recovery, no-change
refusal, candidate/plan mismatch, stale owner/digest/token, merged-state regression,
torn delivery/ack files, and presentation-version acknowledgement. Reading notices
on an empty repository leaves no state directory; acknowledged uncertain delivery
remains inspectable. Provider responses and sends in these tests are explicitly
simulated. No live GitHub PR, remote merge, hook or automatic startup was exercised.
The same tests preserve immutable completed evaluation bytes while delivery state
changes. The earlier skill-discovery evidence predates the new `learn` entry.


## Amendment structure and push-range law

Local implementation proof, 2026-10-29; source base
`5725d495bb83a17ec13616bb5421bf5ffdc71f70` (0.33.0). The candidate changes the
shared amendment parser, its full/dispatch callers, L2 output classification,
and adds L3 to the existing laws registry. No workflow, skill, mod, CI trigger,
package version or adopter configuration is changed. No new ADR is introduced:
the append-only and event-range rules are already accepted in ADRs 0005/0017.

The touched suites exercise structure, raw-byte transitions, event-time CLI
replays and callers. Ten isolated source mutations, run with `python3 -B` and
no copied caches, each make its behavioral test fail with an assertion (not an
import/runtime crash): first-section-only scanning, substring id extraction,
generic level-three entries, disabled fences, tip-only blobs, ignored deletions,
skipped index tasks, stripped fenced metadata, missing L2 classification and
missing-evidence-as-green. Full/seed/dispatch controls retain pending-worker
semantics. Unknown subprocess output and unreadable/missing history are exit 2.
Registry parity checks the L3 heading against the executable registry.

Historical CLI replays export the event's complete tracked tree, including its
records and referenced artifacts. Full check and dispatch `--names` refuse:

| State event | Task | Specific form refusal |
| --- | --- | --- |
| `169e815d299e737722aa4ce3e9780620d7c27c8b` | seed-check-requires-schema-fields | Amendment 2 outside the section; Supersedes prose |
| `a76431954dadf2a92092264ba6fabd1184393216` | idle-hook-names-merged-tasks-without-learn | Supersedes prose |
| `95fe8ce1bd7ff58798634b733abb4115fecfe23d` | read-adr-honors-adr-folder | Supersedes prose |
| `a9fca23f41f9063dbd090d9c8b2962f1a44d14c9` | batch-reaches-each-gate-together | Design fence encounters another opening delimiter before a close |

Moving just the misplaced heading into a section removes its location defect;
replacing just the malformed Supersedes values removes their grammar defects
in both CLIs. Other defects may still refuse the task. The `e9bac6a6d` idle-hook
snapshot has no invented Feedback Cycles amendment. Balanced backtick/tilde
examples, quoted headings, CRLF, terminal punctuation and valid worker payloads
have paired controls. An opening delimiter of the same type and sufficient length
with an info string before a close is diagnosed in the amendment region; shorter
nested delimiters remain literal fenced content.

The existing state-workflow laws command was run locally on an isolated full-history
state clone with explicit parent/event endpoints and the adopted README. Base exits
0 on each of the following ranges; candidate exits 1 with the L3 protected-span
violation independently of worker timing:

| Parent-to-event range | Protected change |
| --- | --- |
| `95fe8ce1bd7ff58798634b733abb4115fecfe23d^..95fe8ce1bd7ff58798634b733abb4115fecfe23d` | Supersedes metadata |
| `16129ea4c1a238dd885e9f08513ce3a52ad27f2d^..16129ea4c1a238dd885e9f08513ce3a52ad27f2d` | previously recorded payload |
| `34c820b5db98d5da119a1b021ce6af45d616acdc^..34c820b5db98d5da119a1b021ce6af45d616acdc` | Design metadata before an unmatched fence |

The three actual L3 outputs contain 21, 25 and 24 words respectively (each includes
a nine-word summary); complete stdout contains 39, 43 and 42 words versus 18 on
base. Per-file full/dispatch diagnostic word counts are retained in the JSON.

Positive committed fixtures append entries/moved blocks and preserve bytes across
archive, rename and flat/index moves, including delete/add correspondence without
a Git rename. Negative fixtures edit metadata/fences/payload, extend metadata,
remove/reorder/renumber entries or delete a task. Later repair/deletion in a range
does not hide its earlier event. A subsequent clean range does not re-report it.
Fixed-range L3 output survives working-copy/tip/archive/README changes. Ambiguous
correspondence/spans, missing or truncated parents and unreadable blobs are not green.
For unmatched fences only a change before the uncertain span is a definite violation.

Frozen corpus exports include every tracked Markdown task/fixture declaring
`variant: kc-dev-flow-2`, plus all tracked dependencies. The package's 174 includes
`_archive/prod-security-review-gates/security/replay-c2/fixture-relay-prod-task.md`;
there are 173 canonical task paths, not a skipped 174th task. Base and candidate full
and seed CLIs run per file, plus dispatch `--names` for every relevant recorded folder.
The corpus manifest asserts the expected count, so skipping a file fails the replay.
Scope history is unavailable in these archive exports; its identical CLI note is
retained in both verdicts. Event-history proof uses the separate full-history clone.

| Corpus pin | Files | Full passes, base/candidate | Seed passes, base/candidate |
| --- | ---: | ---: | ---: |
| package `731a165dfdf02549a9d13b0624174351e8a6d7be` | 174 | 86/76 | 19/19 |
| relay `7fbde2c526769e0968d05fac858fc63b31c6274c` | 97 | 67/55 | 9/9 |
| web `2c3a6dcbfb3a8e178d65151237a0c234351612c0` | 42 | 11/11 | 6/6 |
| qnow `934789a124e50dd45f37af59bb337573462739ea` | 135 | 47/43 | 0/0 |

All 988 mode verdicts are retained in generated `corpus-verdicts.json`; all 54
message/exit differences in `corpus-differences.json` cover the 32 files below.
There are 26 full-pass-to-refusal changes, six dispatch-pass-to-refusal changes,
and zero seed changes. Differences on already-refused tasks are retained too.
The table groups each file's changed modes; diagnostic text in the JSON names
its actual line/heading. Supersedes prose, bare amendment-labelled notes/proposals,
misplaced records and malformed headings are structural violations; examples need
fences and notes need non-amendment headings. No slug allowlist is used. Replacing
a malformed Supersedes value may also remove an old move/replacement diagnostic
because the new parser does not pretend prose is a valid id list.

| Corpus and file | Changed modes | Structural explanation |
| --- | --- | --- |
| package `_archive/fo-batch-sittings.md` | full, dispatch | Supersedes grammar |
| package `_archive/fo-write-rules-checked.md` | full, dispatch | Supersedes grammar |
| package `_archive/idle-hook-names-merged-tasks-without-learn.md` | full, dispatch | Supersedes grammar |
| package `_archive/kc-decision-log-cli.md` | full, dispatch | Supersedes grammar |
| package `_archive/peers-rules-name-each-host-binding.md` | full, dispatch | Supersedes grammar |
| package `_archive/read-adr-honors-adr-folder.md` | full, dispatch | Supersedes grammar |
| package `_archive/release-acceptance/index.md` | full, dispatch | Captain field, Supersedes grammar, duplicate number, heading, placement |
| package `_archive/release-walk-picky-reviewers-and-director.md` | full, dispatch | Supersedes grammar |
| package `_archive/seed-check-requires-schema-fields.md` | full, dispatch | Supersedes grammar |
| package `adr-required-statement.md` | full | Supersedes grammar |
| package `kc-decision-log-handoff-trial.md` | full | Supersedes grammar |
| relay `_archive/account-publish-ceiling.md` | full, dispatch | Supersedes grammar, heading, placement |
| relay `_archive/close-race-copilot.md` | full | Supersedes grammar |
| relay `_archive/decision-panel-host.md` | full | Supersedes grammar |
| relay `_archive/junk-share-edge-cost.md` | full, dispatch | Supersedes grammar, heading |
| relay `_archive/one-identity-entry.md` | full | Supersedes grammar |
| relay `_archive/owner-link-leak-safe.md` | full, dispatch | Supersedes grammar, heading |
| relay `_archive/owner-sees-all-feedback-room.md` | full, dispatch | Supersedes grammar, placement |
| relay `_archive/owner-sees-all-feedback.md` | full, dispatch | Supersedes grammar |
| relay `_archive/review-keyword-invocations.md` | full, dispatch | Supersedes grammar |
| relay `_archive/review-ui-consistency-relay.md` | full | Supersedes grammar |
| relay `_archive/review-ui-dialogs-specs-both-shells.md` | full | Supersedes grammar |
| relay `_archive/spacedock-install-beta.md` | full, dispatch | Supersedes grammar |
| relay `limit-telemetry-posthog.md` | full, dispatch | Captain field, Supersedes grammar, duplicate number, heading, placement |
| web `_archive/briefing-frame-and-controls.md` | full, dispatch | Supersedes grammar, heading |
| qnow `_archive/accept-branch-invitation.md` | full | Supersedes grammar |
| qnow `_archive/office-header-shows-phone.md` | full | Supersedes grammar |
| qnow `_archive/qnow-migration-baseline.md` | full, dispatch | Supersedes grammar |
| qnow `_archive/staff-multi-branch.md` | full | Supersedes grammar |
| qnow `_archive/vehicle-based-pricing.md` | full, dispatch | Supersedes grammar |
| qnow `branch-hours-generate-starts.md` | full, dispatch | Supersedes grammar |
| qnow `operator-secret-hardening.md` | full, dispatch | Captain field, Supersedes grammar, heading, placement |

Reproduce from the complete source checkout (Python with tarfile's `data` extraction
filter, Git, the declared Spacedock 0.27.3 package, and all four pinned state object
sets required). Export base `kc-dev-flow-2` with `git archive` into an external
scratch directory. Supply `DEV2_AMENDMENT_BASE` as its scripts directory;
`DEV2_AMENDMENT_CORPORA` as a JSON array of `{name, state, rev, tasks}` rows using
the four pins/counts above; `DEV2_AMENDMENT_STATE` as the package state repository;
`DEV2_AMENDMENT_README` as its adopted workflow README; `DEV2_AMENDMENT_SPACEDOCK`
as the declared Spacedock package root; and `DEV2_AMENDMENT_EVIDENCE` as an external
output directory. Then run from the repository root:

```sh
python3 -B -m unittest discover -s kc-dev-flow-2/scripts -p test_design_surfaces.py
python3 -B -m unittest discover -s kc-dev-flow-2/scripts -p test_dispatch_records.py
python3 -B -m unittest discover -s kc-dev-flow-2/scripts -p test_laws_check.py
```

Optional object-dependent replays report skips without those declared inputs;
ordinary structural/event fixture tests and mutation controls run without them.
Generated JSON retains per-file messages, historical law output, mutation assertion
failures and actual reading output; it is evidence of this local run, not hosted CI.

Reading was recounted using the design's manifest and `test_pr_watch.TasksTests`
provider fixtures: workflow 5754, dev entry 763, package mod 48, upstream startup
365, upstream idle 100, Delivery authority 461, Extensions 224, learn extension 280,
gate lifecycle 958, present-gate 675 words. Fixture stdout contributes 29 open-PR,
0 merged-PR, 5 archive and 90 four-gate-sitting words. Base/candidate lifecycle
totals stay 6959 startup, 862 idle/open, 833 idle/merged, 333 after archive and 2408
merge ask; startup with optional feedback stays 7558. No normal-path instruction
is added. A no-event L3 summary is nine additional words when read, bringing the
three-law summaries to 27; variable refusals/violations are retained and counted
separately in generated evidence. Stubs do not prove real host execution.

The inspected state CI package pin remains
`22219a3e4bc48a69a893bd757923e8c034d1ba6e`. This candidate is not activated there.
A published package pin adoption and an actual state-push run are still required
for hosted enforcement. CI cost per PR is **not measured**; the existing state-push
trigger is unchanged. GitHub API/PR CI is delegated to FO in this dispatch.
L3 excludes merge commits themselves, prior pushes, rewritten history, uncommitted
edits and never-recorded rulings. Missing rulings, initial quotation fidelity and
criterion ids omitted by meaning remain observer-owned; no semantic refusal,
automatic revert, permanent-red state or new pre-gate history call is claimed.

## Design ADR placeholders require a reservation, 2026-10-29

Stacked base: `b8a66e826c7524fa944a7165296acba94b3f5e13` (the validation-rerun
branch, on the amendment-form change). `dispatch_records.py --names` now refuses
positive-numbered implementation and implementation-message records for Pilot/Prod
when the last unfenced `## Design` (including ` — title` and `: title`) names
`docs/adr/<placeholder>-title.md` and `number_guards.task_facts` finds no reserved
ADR. It uses the existing numeric parser; migration numbers and dispatch-only
numbers do not satisfy it. The diagnostic supplies the existing allocator/record/
scope-copy/retry recovery. The first-record-only scope-copy check is unchanged.

The signal is the literal path, including in ordinary explanatory prose; it does
not classify intent, negation, decision quality or authorization. Fenced and
quoted examples, numbered citations, earlier Design sections and report-only
obligations do not signal it. POC and the folder/newest/coverage modes retain their
existing behavior. Missing/unusual design forms and obligations omitted from the
design remain observer work. No new ADR, declaration, hook or migration is added.

Reproduce the behavioral proof from the repository root:

```sh
python3 -B -m unittest discover -s kc-dev-flow-2/scripts -p test_dispatch_records.py -q
python3 -B -m unittest discover -s kc-dev-flow-2/scripts -p test_laws_check.py -q
```

The dispatch suite passes 87 tests, including `DesignAdrTests` and
`DesignAdrMutationTests`; the laws suite passes 59. The new tests assert:

- Raw #740 bytes from state commit `09da6be7ad5aaf687ea3f80e9553f3efb525cc17`
  refuse with the new diagnostic. Embedded task/record SHA-256 values are
  `9cdb2a04175c91eb996fb8c314067cfd6fe5fe4636ef399b97fc0effa4288406` and
  `5f80555583c521fc2f21cca8ea407d542335b8d371a8f34c934e8b1b40ae6c20`;
  the matched task path is at line 243. Released 0.33.0 exits 0 silently.
  The stacked base already exits 1 for its unrelated amendment form at line 293;
  candidate preserves that diagnostic. Allocator recovery clears the new refusal
  while retaining that pre-existing error. Deleting the task ADR line, leaving a
  migration only, or retaining a scope-only ADR number restores the new refusal.
- Flat/folder tasks, Pilot/Prod/POC, first/repeated/message records, heading suffixes,
  both reserved-number placeholder spellings, title placeholders, lists/tables/code,
  quotes/fences, numbered citations, replacement Design sections and unrelated
  modes exercise the boundary. Removing quote/fence filtering, applying the rule to
  POC, using the first Design, or skipping continuations fails its named control.
- The actual CLI governs a disposable shell build/spawn recorder. Missing input
  produces zero calls and 27 diagnostic words; corrected input records build then
  spawn with empty checker output. Disconnecting `check_task_facts` or its predicate
  fails the raw replay. A separate installed Spacedock build in a disposable repo
  produced a Codex envelope after actual allocator recovery (`ADR: 0001`, two words),
  with zero build calls on refusal. Real `worker.spawn` was unavailable: the next
  operation was a recorder, not a launched model. This does not prove native spawn.
- L2 classifies the diagnostic as a violation, not Cannot, for both task layouts.
  A later repair preserves the earlier event's result within the same fixed range;
  a range starting after that event is clear. Removing the diagnostic parser or
  reading today's task instead of event bytes fails this control. Eleven mutations
  run fresh Python `-B` processes in cache-free copies and each fails an assertion.

Committed corpus comparison used `git archive` snapshots and the stacked-base and
candidate CLIs over every `*/dispatch/*.md`, including archives. Pins and counts:

| State corpus | Commit | Records | Changed diagnostics |
| --- | --- | ---: | ---: |
| This workflow | `ac38184c7912d6eca53e0256dd498f935ac63d26` | 564 | 1 |
| Relay | `6742b0b757700fb9b19d9fdb6e61984e5a6543c8` | 296 | 0 |
| QNow | `77caf32322a54e806b8e5c8a0b094a5f2f60a5f7` | 249 | 0 |
| Web | `7f3f3861c9b68defa60a07fbdecdc26d6d1fdbf2` | 138 | 0 |

The changed record is this task's `implementation-1.md` (record SHA-256
`a2384c9bc19425ce90846fb8316dfeca1099fb644817780d5879a2501b312a5d`): its active
Design explains literal placeholder paths without quoting/fencing them. This is
the documented structural limitation, not a newly discovered ADR obligation. The
approved definition was preserved; FO must handle those explanatory examples
through the authorized correction route before a future dispatch using this check.
Existing reservations, amendment/renumber failures and unrelated verdicts remain.

The task's fixed lifecycle recipes were executed on exact base/candidate source
with the shipped watcher fixtures and installed Spacedock 0.27.3 instructions.
Startup/open-idle/merged-idle/archive/merge-ask totals are unchanged:
6967 / 870 / 833 / 333 / 2408 words. Executed output counts are 37 / 37 / 0 / 5 / 90;
workflow stays 5754 words. New failure-path reading is 27 diagnostic words plus
690 existing words (Number guards 222 and FO steps: number guards 468), two
allocator words and zero retry words: 719 total. The design's 468-word recovery
forecast omitted the separate 222-word Number guards section; both sections are
included here. Existing stacked-base errors, when present, are additional and
unchanged. No normal-path output, workflow-budget step or CI change was added.
CI cost per PR was not measured. These local results do not establish hosted CI,
RoboRev review, native model spawning, Captain acceptance or a merged delivery.
