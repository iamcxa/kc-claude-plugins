# Independent validation: PR #810

- Date: 2026-11-08; profile: pilot; verdict: **REJECTED pending F1 Needs decision**.
- Candidate: `90192bb64db4614de9a7a94cc782ee5fa44748db`; base: `139feeaee7ce037a0c6535568cd6bd103155cbae` (the dispatch's origin/main).
- PR: https://github.com/iamcxa/kc-claude-plugins/pull/810; fresh `pr.json` confirms this head and Draft/Open.
- Product worktree: `/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-worker-browser-checks-use-paseo-browser`; unchanged and clean.
- Candidate execution: `git archive` export at `/tmp/paseo-validation-810.kHIx2L`; no new Git worktree, product edits, Git configuration writes or publication.
- Package scripts: `/Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0` as dispatched. Read-only Git-dependent checks use the candidate worktree's object database with `GIT_WORK_TREE` bound to the export and `GIT_OPTIONAL_LOCKS=0`.
- Authority: `../dispatch/validation-1.md` and `../dispatch/validation-1-message-1.md`; the latter confirms there is no Captain ruling for F1, attributes the hinted rerun to FO, and forbids another browser run.

## Criterion-by-criterion result

| Criterion | Verdict and actual evidence | Independently rerun falsifier |
| --- | --- | --- |
| AC-1: appended browser instruction | PASSED. Exact base quote plus the final browser sentence; first sentence unchanged. Candidate's existing consumer test passes. | Existing consumer rejects moving the new sentence first and rejects adding a second instruction line; both exit 1 in temporary exports with Python -B. |
| AC-2: bounded guide and limits | PASSED. `wc -w`: 235. Reviewed default, repo precedence, unchanged CI, missing/failed-tool fallback, per-step reporting, never treating not-run as clean, and all four limit/workaround pairs. | Existing acceptance grader rejects removing each of four workarounds and rejects a guide over 240 words. These detect documentation omissions, not vendor behavior. |
| AC-3: bounded FO reading | PASSED. Extension 1101 -> 1116 (+15); only dispatch/spawn reads added text. Guide is conditional worker reading. Workflow README, budget/linter and dispatch checker blobs unchanged; package lint exits 0. | Moving the complete guide into the FO extension exceeds +20; existing rejection exercised. |
| AC-4: unhinted complete Paseo walk | NOT MET AS WRITTEN; F1 Needs decision. First run chose Paseo without tool hints but required agent-browser fallback. Visible rerun completed screenshots and a real minimap click using Paseo, but its prompt explicitly named tools. | Empty browser evidence and an added alternate-adapter command are rejected by the existing grader. Manual prompt inspection finds the additional unchecked failure: a successful tool-hinted run is still scored green. |
| AC-5: measured Codex reachability | PASSED. Original Codex activity has exactly one successful `browser_list_tabs` call and its report. Live provider status confirms Codex and assigned worktree; this validator also called the tool once successfully. No unsupported Codex limitation was added. | Removing measurement is rejected. No claim of Codex canvas operation or cross-host availability follows. |

The implementation's unchanged `acceptance.sh` was run against a copy of its evidence and returned 27 passing checks. This is a structural/evidence replay, **not an overall acceptance verdict**: its Claude grader checks tool-name presence and fallback text, but does not check the no-tool-hint clause. Results: `acceptance.log`, `acceptance-results.json`, and the three `AC-1*.log` consumer/mutation logs.

## Primary browser evidence reviewed, not rerun

I opened all four before/after PNGs and read both complete saved activity logs, both prompts, both reports (including the first report's correction), and launch/provenance evidence. No new browser tab, browser interaction, worker, or fallback run was started by validation.

- Run 1: `../implementation/claude-prompt.txt`, `claude-activity.json`, `claude-report.md`. Fresh worker reads the guide, opens/snapshots with Paseo, then makes four failed screenshot calls (three `screenshot_no_frame`, one timeout); evaluate and click time out. It closes the Paseo tab, documents the repository-supported fallback, and the fallback images show the page-selector menu opening. This proves unhinted default selection and honest fallback reporting, not an all-Paseo successful walk. The corrected failure count supersedes the initial undercount.
- Run 2: `../implementation/attempt-2/{claude-prompt.txt,claude-activity.json,claude-report.md,claude-before.png,claude-after.png}`. Fresh Claude worker `a0076a47-a29b-4946-b2a3-e2477d4836dc`; before/after PNGs show a rendered board and the minimap expanding. Recorded fresh snapshot ref `@e34`, two screenshots and click use Paseo; no fallback. The report records visible state before/after, two 30-second waits, and an intentionally retained tab under FO's follow-up. The explicit `browser_new_tab` instruction in that same prompt prevents counting it as the unhinted run AC-4 requires.
- Runtime was started at `20eb8255daf0f1267a8c0dd16daf0705a7cf82ba`, not at the final documentation commit. Independent Git diff confirms final head adds only the visibility sentence and leaves all `kc-journey-map` bytes identical. The launch script names the assigned checkout and isolated storage; the recorded initial room has 14 shapes. I did not independently attest the historical running process bytes or installed dependency tree.
- Original Codex worker `07667725-e257-49f7-b859-a1f49e1187c3` has one measurement and no canvas test. Live status shows both named workers idle; see `live-probes.json`.
- The retained canvas servers (PIDs 96411/96412) were still alive at final inspection; `retained-processes.log`. FO owns stopping them and closing the retained tab after the Captain's review. The tab belongs to the other workspace; this validator's tab list does not establish its current presence.

## Finding disposition

- F1 Needs decision: the two runs do not establish the unchanged AC-4 promise.
  - User/normal workflow: a worker in an adopter listing paseo receives the extension quote and independently chooses a local browser.
  - Observed gap: the only unhinted run failed the Paseo screenshot/click path; the only complete Paseo run had explicit tool instructions. No candidate product defect is claimed from this gap.
  - Protected criterion: `value-ac[AC-4]` — one fresh Claude worker completes the real board-and-click check without a browser tool named in the ask.
  - Trigger: exact prompt/activity/image pairs above; FO confirms no covering Captain ruling in `dispatch/validation-1-message-1.md`.
  - Disposition: FO takes the evidence and decision to the Captain. No repair or new run is authorized here. The implementation followed FO's follow-up; responsibility for the hinted rerun is FO's. Remaining criteria PASSED. No Material product defect, separate Deferred risk, or Polish finding identified.

## Limits and goal sufficiency

The added visible-tab sentence is a useful workaround supported by this host's failed background and successful foreground observations, not proof of a universal necessary-and-sufficient condition or its precise cause. The final guide still fits 240 words. Its typing/IME, React Native ref, 15-second evaluate and signature-canvas descriptions retain the approved task's provenance: native setter/input/readback; fresh snapshot ref; park-and-poll; try drag then fallback. This validator did not reproduce those four vendor behaviors. Signature input remains explicitly untested; Clerk Turnstile remains the other FO's earlier report, not this local proof.

Goal sufficiency is incomplete only at F1. Minimal necessity is supported: base has no self-driven worker pointer/guide; the added pointer reaches the guide in run 1; removing a workaround or moving the guide into FO's always-read text is caught by the existing falsifiers. The change is only the two approved documents. No new durable decision, ADR, CI trigger, runtime code, adopter file or version changed.

## Other required checks

- Candidate `test_dispatch_records.py`: 115 tests run, 1 optional skip, exit 0; `dispatch-tests.log`.
- Candidate `lint-skills.py`: exit 0; `lint-skills.log`.
- `python3 -B /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.35.0/scripts/adr_lint.py docs/adr --since 139feeaee7ce037a0c6535568cd6bd103155cbae`: exit 0, 62 records, 0 legacy; no reserved or implementation-named new ADR requires `--require`.
- Number guards: exit 0; no migrations-path, migration guard explicitly skipped, no findings.
- Comment ratio: exit 0; 0 code / 0 comment lines, 0.0%, maximum 5%, not enforced below 20 code lines. No added code comments to review.
- Design surfaces: exit 0; presentable; scope check explicitly not run because stage is validation, not ideation. Task has no UI surface/design-director obligation.
- Document impact: exit 0, `[]`; two changed documents updated, no other listed document to disposition.
- Dispatch records: initial four and final five records complete, exit 0; follow-up obligations assessed, not silently promoted into Captain authority.
- `git diff --check`: exit 0.
- Exact commands, export cwd and exit codes for six package checks are in `checks-results.json`. CI cost per PR was not measured; no CI file/trigger changed. Remote CI, RoboRev, readiness and delivery remain FO-owned, not claimed by this report.

## Captain acceptance script (five steps)

This change has no new product screen: it changes worker instructions. Prerequisites are the named checkout containing both commits, the named package installation, Git, Python 3, Bash, tar and existing task evidence. Run exactly:

```bash
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/worker-browser-checks-use-paseo-browser/validation/captain-acceptance.sh
```

The script itself contains five numbered commands/observations: export the pinned head; inspect the quote/word counts and protected-file equality; replay existing checks/falsifiers on copied evidence; exercise the actual consumer and lint; run ADR lint. It was executed exactly as written in a fresh Bash shell, exit 0; observed output is `captain-acceptance.log`. Expected: candidate full SHA, 1116/235 words, 27 replay checks passed, one consumer test OK, lint exit 0, 62 ADRs and ADR exit 0, followed by the explicit AC-4 Needs decision notice. It creates only a scratch export under /tmp and requires no browser or network.

It does not cover a new live browser run, unhinted all-Paseo completion, the four earlier vendor observations, production authentication, CI, publishing or cross-host guarantees. Its exit 0 must not be read as resolving F1.

## Ownership and return

No product branch push, PR comment/review request, readiness change or merge was performed. Only this task's validation artifacts and appended Stage Report are written to shared state; unrelated concurrent state changes are excluded. FO retains the Captain decision, browser/server cleanup, review, CI and delivery.

