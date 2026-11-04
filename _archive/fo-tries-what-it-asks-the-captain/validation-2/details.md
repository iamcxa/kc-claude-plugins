# Independent validation of PR #773, cycle 2

Verdict: **PASSED** for the accepted scope under Captain amendment 1.

Candidate: `128fe3e3fed70fa64ded8657f5a1b36933af3ced`.
Assigned base `origin/main`, fetched as `e1bee223c47a1cd534a665a47776b683375b34fc`; merge base and implementation comparison base `713d4e6ed6381e65fa6d8305e08b282ceb56a8fb`. Main advanced through docs-site PR #776; the independently recounted workflow, mod and delivery inputs are unchanged from the implementation base. This is Pilot validation with `Surfaces: none`. Product bytes were not changed.

## Authority and prior findings

Captain amendment 1 is present in the task and was committed after validation-1. It quotes 「准」 answering the explicit question to waive F2/F3 (the prose coverage exclusion) and accept F4/F5 (installed-checker drift and the shortened First Officer completion record) without holding this rerun. No criterion is superseded. This validation applies that ruling rather than granting a waiver or treating the underlying records as repaired.

F1, the Material P2 false hold on recorded route output, is repaired. Independently captured `GET /health 200` passes `steps` when shown in its matching Observed fence, including a named card. Both legacy and separate-summary `question` calls pass with the output in the latest validation report; additional probes place it in the question itself. An independent missing path still holds in every relevant route. Restoring raw-message path scanning makes the positive regression fail; disabling message path scanning makes its negative control fail (implementation-replays/mutation-24.log and mutation-25.log). No live HTTP endpoint was contacted: a harmless fresh shell emitted the route-style text.

The waived F2/F3 cases still reproduce as disclosed parser limits. The required .claude dispatch checker still rejects the six current dispatch records; the active .codex and candidate checkers reject only the previously accepted shortened completion record. Their source hashes and outputs are retained. The two new dispatch records have the same installed-checker mismatch, with no new failure class; the candidate checker accepts them. F4/F5 remain accepted issues, not repaired product behavior. No new Material, Deferred risk, Polish or Needs decision finding is established by this rerun.

## Acceptance criteria and falsifiers

- AC-1: Missing observations and an unrun step with no Captain-only explanation hold and name step 1. Removing S2 fails the designated regression (mutation 1).
- AC-2: The QNow archived-script card replay holds both a copied nonexistent path and an omitted fenced command. Creating the named file passes. Removing S4 or command coverage fails the corresponding test (mutations 2 and 3).
- AC-3: The message's command and URL each need a recorded step; the completed record passes. Removing link coverage fails (mutation 4).
- AC-4: A Captain-only step needs its reason; missing or one-word reasons hold, while the stated account reason passes. Removing S3 fails (mutation 5).
- AC-5: Both question call forms hold the missing-record relay replay with one problem and one next line, reject the later wrong head, and accept the dispatched candidate. Removing the record clause or candidate check fails (mutations 6 and 7).
- AC-6: The three-step fixture and three independently executed harmless shell commands produce `captain steps complete: 3 steps, 1 left to him`. Corrupting the count fails (mutation 8). The F1 route-output repair and independent-path controls above extend the successful value boundary beyond the original fixture. The password/approval field is a parser fixture; no account or password was used.
- AC-7: Lint reports 5836 of 5836 words. The +55 ledger quote matches the accepted ideation gate and ADR 0054; restoring the old observer chat-only phrase produces the exact required lint defect (observer-mutation.json).
- AC-8: Existing question and POC recipe callers retain their expected behavior, including the intentional hold without the Captain record. Removing the record from a legacy positive fixture fails its existing test (ac8-falsifier.log). The exact full-discovery command passes 890 tests with six existing skips, exit 0 (full-suite-standard-temp.log; full-suite-result.json).
- AC-9: Independent recount against current origin/main confirms workflow 5781 to 5836, workflow plus mod 5829 to 5884, mod 48 unchanged, validation passage 64 to 33, new section 86. Idle/open/merged/archive inputs, merge ASK literal, and check/write_record behavior are unchanged by byte and AST comparisons. Adding a word fails lint. The required success line is nine whitespace-split words, correcting the design table's eight as implementation had disclosed.

All 26 implementation mutations were rerun from candidate source. Observer restoration and the separate legacy-caller mutation also failed as expected. Eighteen independent CLI probes cover the real-command success, named card, parser shapes and F1 routes; the implementation's own positive CLI and four gate-output cases were rerun separately. The implementation acceptance.sh was also run unchanged from a copied evidence folder with its declared worktree override.

## Implementation limits and retained scope

Prose requests, inline code, quoted fences, list-marker fences and indented code remain undetected. The CLI probes reproduce those limits; prose is explicitly waived, and the other shapes were previously disclosed and routed through the engineering reviewer. Normal, longer-closing and unclosed fences hold when unrecorded, including non-shell tags. An unclosed named-file fence requires the remaining text as one step. Diagram/evidence fences hold unless recorded or matching an observation. No tag exemption was restored.

Checks establish form, coverage, path existence and candidate binding. They do not authenticate observations, prove execution, open preview pages, or intercept chat when the First Officer skips the checker. A justified unrun credential step is accepted. Synthetic URLs and browser wording in fixtures do not prove a browser visit. The observer can read the record under the changed rule; no real adopted archive or agent-compliance run is claimed.

The accepted goal is sufficient at the bounded detector scope: both historical replay shapes hold, and exercised valid steps pass including the repaired observed-output presentation. Each retained product change maps to the detector, gate binding, approved word-budget ruling, observer alignment, required decision record or caller regression. The two additional fixture files were previously authorized by the First Officer; no further product file was added in the repair. Removing the relevant guard causes the named falsifier to fail. Existing adopters' next validation question intentionally needs the new record; ADR 0054 states that compatibility effect.

## Required checks and documents

Both the explicitly dispatched .claude package and active .codex package ADR lint ran with `docs/adr --since e1bee223c47a1cd534a665a47776b683375b34fc --require 0054`: exit 0, 51 records, 0 legacy. Number guards, design check, doc impact and diff check pass. The comment check reports 1 comment / 508 added code lines, 0.2%, under 5%; every added comment/docstring was read. No added comment needs repair.

All eight affected-document dispositions were checked at the candidate: ADRs 0020, 0037, 0044, 0049 and 0051 retain their budget, worker, summary, model and merge responsibilities; package README entry/adoption, maintain-flow commands and learning's independent-recount practice remain applicable. Changed workflow, observer and ADR 0054 carry the new rule. No product diagram was changed.

The live read-only GitHub result confirms this head, open Draft status, six successful checks and one skipped deployment. Stored RoboRev job 1448 independently binds the implementation base to this head, status done and clean verdict_bool=1; no new reviewer was invoked. That stored verdict is not a review against the later docs-site base. Local discovery does not execute standalone Spacedock integration programs or extension tests; the successful hosted package job includes its explicit CI commands. CI cost per PR was not measured; no CI trigger changed.

## Five-step Captain acceptance

Run `/bin/bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/fo-tries-what-it-asks-the-captain/validation-2/acceptance.sh`.

The self-contained script names the assigned checkout and installed ADR tool and contains five exact steps with expected output: verify the head, run 22 focused tests, run repository lint, check reserved ADR 0054, and check genuinely captured route-style output. Its unchanged bytes ran in a fresh shell with CAPTAIN_STEPS_WORKTREE pointing to the detached exact-head candidate. acceptance.log records exit 0: the exact SHA, 22 tests OK, 5836/5836 words, 51 ADR files with 0 legacy, and `captain steps complete: 1 steps, 0 left to him`.

There is no graphical interface in this change. The script exercises local CLI behavior and temporary fixtures, without credentials. It does not prove preview availability, sign-in, observation truth, host compliance, installation, adoption, release or merge.

## Test environment accounting

The initial full-discovery attempt put generated fixtures beneath the detached checkout to retain isolation. Tests that deliberately create plain, non-Git copies then discovered the enclosing worktree. That superseded run was interrupted (exit 130); its log is retained. A partitioned rerun with GIT_CEILING_DIRECTORIES exercised 890 tests but two plain-copy cases still failed because dispatch_records discovers ancestor .git paths directly. Both cases pass unchanged with the normal TMPDIR=/tmp (plain-copy-rechecks.log). The two standalone integration files reported no unittest tests (exit 5), not a product failure. No source change was made to address these validation-environment mistakes. The final exact full-discovery run uses the normal temporary directory and passes all 890 tests with six existing skips, exit 0 (full-suite-standard-temp.log).

## Ownership

Only the task report and task-scoped evidence are written to shared state. Task frontmatter, older reports, dispatch records, installed packages and product bytes are preserved. The detached worktree is removed after checks. The First Officer retains gate and delivery ownership; this report grants no approval, merge or release authority.
