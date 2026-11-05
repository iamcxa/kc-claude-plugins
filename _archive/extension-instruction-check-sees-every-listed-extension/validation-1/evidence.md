# Independent validation evidence for PR #787

Candidate: `272721000cce947c8f2dcdd3a40c22cdf11dee09`.
Fetched origin/main / base: `d37c6dc653e0f45d6ca630c2faa6121c0863a57e`.
State replay snapshot: `acb39aba17babc61ad66edb93d79d8a9f680bfaa`.
Approved live-record observation snapshot: `962a430f0`.
Date: 2026-11-05. No product edits, historical record edits, agents launched, push or PR writes.

## Acceptance script

Run this exact five-step script in a fresh Bash shell:
```bash
/bin/bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/extension-instruction-check-sees-every-listed-extension/validation-1/acceptance.sh
```
Prerequisites: Git, Python 3.12 or later, Bash, the source and state checkouts and installed package paths declared in the script. It creates an exact detached checkout beneath the assigned worktree and removes it on exit. The recorded run exited 0; `acceptance.log` is its complete observed output. No graphical surface changed. This bounded script covers the detector's observable missing/supplied instruction behavior, shipped instruction selectors, history-law consumer, archived replay, scope, lint and ADRs; it does not run all package tests or prove live worker obedience, release walks, adoption or delivery.

## Primary runs

- `checks.json` records the exact argv, exit code and log for all 25 CI-listed package test commands and supporting checks. Python bytecode writes were disabled. All 25 package commands passed; the full dispatch suite ran 115 tests and laws suite 65.
- The dispatch suite's optional native-builder test initially skipped without SD_PLUGIN_ROOT. The explicitly named native-builder run supplies SD_PLUGIN_ROOT and SPACEDOCK_BIN; `native-dispatch.log` and the corrected check entry are authoritative. The current native executable reports Spacedock 0.27.2 (native-version.log), with the explicitly selected plugin root 0.27.3. The implementation report's earlier native-version observation is not treated as current; this mixed local binary/plugin run is distinct from CI's configured pinned binary and plugin.
- One unrelated laws-history replay remains skipped: DEV2_OBLIGATION_SOURCES was not supplied. The new Paseo L2 test ran in the suite, acceptance script, and mutation check.
- `pr.json` confirms an open Draft PR at the exact candidate; `ci.json` confirms the hosted package-test run succeeded on that head. This resolves the implementation report's earlier absent PR/hosted-CI evidence. It does not grant delivery.
- Both the active Codex package and the dispatch-named Claude package's adr_lint script passed: 58 ADR files checked, 0 legacy, exit 0. Their dispatch_records.py and adr_lint.py files were compared byte-for-byte and match. No new ADR or number reservation is required by the approved design.
- No CI files or triggers changed. Cost per PR was not measured.

## Criteria and falsifiers

- AC-1: ExtensionInstructionTests reads all nine shipped definitions and gets exactly three instructions. Unanchoring the scope-note reader and removing that reader each fail its exact-three assertion.
- AC-2: real folder-mode checks cover Codex and Claude Paseo headers, host=paseo roster, missing/supplied/wrapped/not-run instructions, local headers, unlisted extension and below-heading text. Selecting all headers, excluding Claude or requiring exact whitespace each fails.
- AC-3: later ideation, implementation and validation spawns are judged; roborev applies to later implementation spawns. Messages and recovery records stay exempt. Restricting to first cycles, restricting roborev alone or including messages each fails.
- AC-4: release-acceptance is required only on an acceptance task's first implementation record. Ignoring task frontmatter or selecting later cycles each fails. The pre-existing quiet-without-instruction case remains green.
- AC-5: all 82 records in the 12 named archived folders are replayed by each real CLI with an explicit workflow README. Candidate: 30 paseo (16 ideation, 14 implementation) plus 7 roborev; installed 0.35.0: no extension diagnostics. No validation or message extension diagnostic. Excluding Claude fails the exact-count assertion.
- AC-6: the actual laws_check subprocess consumes the new diagnostic as an L2 dispatch-record violation. Changing the diagnostic prefix fails the test. laws_check.py itself is unchanged.
- AC-7: the Git diff contains exactly dispatch_records.py and its two named test files. A temporary README edit fails the exact whitelist. Workflow remains 5891/5891 words; comment ratio is 0/99 added code lines, 0.0%, below 5%; lint and version parity pass.
- `mutations.json` and `mutation-*.log` record all 13 rejected mutations, run with python3 -B and cleared caches. `restored-focused.log` confirms the restored candidate passes all 16 instruction tests; clean Git status was checked before removing the mutation checkout.
- The implementation report's per-moment counts were independently measured by wc -w: sentence 12, paseo diagnostic 24, roborev diagnostic 30; docstring 771 to 824 (+53), changed paragraph 50 to 103. Clean-run/startup/record-writing text is unchanged.

## Approved decisions and replay limits

D1 (all Paseo workers), D2 (first sentence only), D3 (follow-up messages exempt), and D4 (owning FO records dated omissions before next dispatch) are approved by the recorded ideation gate, not unresolved choices.
`corpus.json` compares the installed and candidate predicates on 106 actual task folders, excluding archived validation-fixture folders. At both the D4 snapshot and the pinned current snapshot, 64 tasks change: 144 new paseo omissions plus 101 roborev omissions; none removed, all on spawn records. Live totals are paseo 6 and roborev 6, against baseline roborev 1: 11 newly flagged records, exactly D4. Five tasks own six paseo records; journey-server-host-pilot owns the five newly flagged roborev records. Their FOs retain next-touch correction ownership.

The archive CLI also reports five unchanged completion-recipient errors (four follow-up messages and one validation record) in both versions. AC-5's counts and exclusion concern extension diagnostics, as the design's replay table does; the entire archived folders are not claimed clean. `batch-replay.json` retains raw stdout, stderr and exit codes, and `replay.py` asserts the other diagnostics are unchanged.

## Document dispositions and scope

- docs/adr/0045-validation-reruns-require-a-later-recorded-captain-ruling.md: unaffected; the names-only live-ruling predicate and its caller are unchanged.
- docs/adr/0048-paseo-stage-workers-complete-by-final-reply-and-hand-publication-to-fo.md: unaffected; completion/publication authority is unchanged.
- learning.md: unaffected; retained practices are obeyed through the consumer, corpus and word-count checks above.
- Goal sufficiency: shipped scope-note forms reach the existing folder checker and historical consumer; real omissions are detected. Minimal necessity: the changed parser/selectors and tests are tied to the falsifiers; three existing history fixtures add the now-required roborev path so their unrelated amendment assertions keep their intended meaning; the docstring describes the changed usage.

## Limits and execution corrections

No new Material, Deferred risk, Polish or Needs decision finding. Accepted limits remain: first sentences only, trusted header text and not-run explanations, no message/recovery enforcement, runtime README selection and YAML block lists deferred to named follow-up tasks, and no claim that workers obey written instructions or release-acceptance walks actually occurred. The release-acceptance selector is exercised with synthetic task records; no actual acceptance walk was launched. RoboRev remains FO-owned and was not rerun by validation.

The first acceptance attempt hit a sandbox denial creating Git metadata; the unchanged script passed with approved filesystem access, and the final report-path invocation also passed. An extra wrapper selector named a nonexistent NativeBuilderTests class; the existing ContextNoticeTests test is the correct selector. During its extra rerun, validator cleanup started early and removed the checkout, yielding FileNotFoundError; the exact checkout was restored and that named test rerun before final cleanup. Initial, interrupted and final logs are retained so neither harness error is presented as a product defect or silently counted as a pass.


### State synchronization correction

The prescribed spacedock state commit command committed and pushed the task report/evidence to spacedock-state/dev2 at 016335e51122b170729552138663c61129dc0a2e. The preceding line assigning pending state synchronization to FO is superseded: synchronization has already occurred automatically. No product-branch push or PR write was performed.
