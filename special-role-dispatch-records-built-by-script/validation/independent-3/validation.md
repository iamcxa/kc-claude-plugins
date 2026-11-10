# Independent validation, merged candidate

Verdict: **PASSED**, PR #827 head `39a76c68836f471fc0c42c18eab12641196860ed`, base `d8dbfcb1051d7c696aca139ed9ade332ee85abaf`. This report supersedes independent-2 only for candidate identity, integrated-main checks, counts and current hosted evidence. There are no new Material, Deferred risk, Polish or Needs decision findings. The prior Material F1 (input CRLF bytes rewritten) remains closed by rerun raw-byte evidence and four caught repair-removal controls (`evidence/repair-bytes.json`, `evidence/repair-mutations.json`).

The candidate was read and run from a fresh `git archive` export in `/tmp/pr827-independent-3/candidate`; product HEAD and bytes were not mutated. Temporary fixtures use the real Spacedock CLI with isolated Git repositories under `/tmp`; no worktree was added to or removed from the shared product repository. Profile remains Pilot: limited real record persistence/recovery, not native reviewer execution or adopter rollout.

## Acceptance criteria and falsifiers

### AC-1: PASS

The record has the workflow HEAD, model, exact supplied inputs, commit and identical stdout. Raw CRLF/LF captures also pass.

Evidence in `evidence/`: test_dispatch_stage.log; repair-bytes.json. Without-it observation: AC-1-no-commit.log: removing commit fails the HEAD assertion.

### AC-2: PASS

Missing Package root or completion recipient refuses, with empty stdout, checker diagnostics, unchanged HEAD and no leftover record. Both missing fields also exercised separately.

Evidence in `evidence/`: test_dispatch_stage.log; probes.json. Without-it observation: AC-2-no-checks.log: removing record checks makes the expected refusal fail.

### AC-3: PASS

Commit refusal keeps the pending disk record and withholds stdout; dirty retry refuses; manual commit then retry reuses record 1.

Evidence in `evidence/`: test_dispatch_stage.log. Without-it observation: AC-3-early-prompt.log: printing before commit violates empty stdout.

### AC-4: PASS

An owed chief-engineer call dispatches successfully; the spy sees state commit and no dispatch build.

Evidence in `evidence/`: test_dispatch_stage.log. Without-it observation: AC-4-build-path.log: removing the role branch routes to dispatch build and fails.

### AC-5: PASS

Sonnet refuses with the opus-floor diagnostic and no record; opus and supplied Astra pass.

Evidence in `evidence/`: test_dispatch_stage.log; probes.json. Without-it observation: AC-5-no-floor.log: removing rank check admits Sonnet.

### AC-6: PASS

Every excluded stage-only flag and design-director refuses with exit 2 and unchanged scope.

Evidence in `evidence/`: test_dispatch_stage.log. Without-it observation: AC-6-allow-advance.log: relaxing the advance exclusion makes refusal assertions fail.

### AC-7: PASS

New calls use independent per-role sequence numbers, unchanged retries reuse; all base tests are AST-identical and pass.

Evidence in `evidence/`: test_dispatch_stage.log; test_dispatch_records.log; test_role_triggers.log; retained-test-cases.json. Without-it observation: AC-7-global-numbers.log: counting other roles loses chief-engineer-1.

### AC-8: PASS

Workflow directs role calls through the script; reviewer-record pin and quoted +6 step pass. The merged total is 5939 with both accepted +6/+2 steps.

Evidence in `evidence/`: lint-skills.log; test_sd_dispatch.log; integration-audit.json. Without-it observation: AC-8-no-instruction.log: pin catches missing instruction; AC-8-no-budget.log: 5939 exceeds 5933.

### AC-9: PASS

ADR 0074 preserves the original D1-D3 ruling and reserved number; candidate and both installed ADR commands exit 0.

Evidence in `evidence/`: adr-lint.log; adr-lint-prescribed.log; adr-lint-candidate.log. Without-it observation: AC-9-no-words.log: removing Words yields precisely its missing-Words defect.

### AC-10: PASS

Startup rises from current main 5933 to 5939 (+6). Captured prompts contain 39-44 words and empty stderr; refusals have empty stdout and 4-49 stderr words. Other named lifecycle code is byte-identical to main.

Evidence in `evidence/`: words.json; wc-words.log; integration-audit.json; candidate.patch. Without-it observation: AC-10-changed-idle.log: altered idle code breaks the byte-equivalence check.

## Merge-main check and word-count ruling

The exact candidate is one merge commit with parents `3567082b0ec1eeb59346b2d82887a07bc5ffc2fb` and `d8dbfcb1051d7c696aca139ed9ade332ee85abaf`. The main parent contains #825, #826 and #828 (`evidence/main-history.log`, `evidence/integration-audit.json`). Its only diff from main remains the six approved files. The role writer, its tests and `role_triggers.py` are byte-identical to the preceding repaired candidate; AST comparison of `dispatch_records.py` shows only `check_coverage` changed, which role mode does not invoke. All 23 directly imported local checker symbols are also AST-identical to the repaired parent (`evidence/imported-symbols.json`). The actual role checks and the real state-commit seam were rerun at this merged head.

The inherited changes add bound-question reason checks, scalar/list screenshot support, folder coverage input, numbered Captain-step paths, the exact attribution exemption, and invalid amendment-move reporting. The role branch runs folder and strict-name record checks; it does not run coverage, delivery or the new L4 history law. No adopted workflow pin or CI trigger changes in this task. No changed role behavior was observed or found from the inherited changes (`evidence/merge-main.patch`, `evidence/integration-audit.json`, complete package checks).

The original AC-8/AC-10 total of 5937 described the premerge base (5931 plus this task's six). This dispatch explicitly requires 5939 after merging main; the original ideation gate already approved the combined eight-word increase from 5931 to 5939. Current main is 5933, this task adds six, and both `captain`/`loaded` budget steps survive. This is the accepted combined arithmetic, not a new budget grant or an unrecorded criterion rewrite. Quotes were compared with the task's original ideation gate (`evidence/entity-read-before.json`, task body).

## Commands and evidence boundary

All 28 package commands exited 0, covering 1312 unittest cases including 11 optional skips; all 27 package test files are accounted for (`evidence/checks.json`, `evidence/summary.json`). The stage suite has 40 passing real-binary cases (`evidence/test_dispatch_stage.log`). `run_checks.py` derives commands from the candidate CI workflow; the local plugin-root dependency is explicitly `/Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3`, and CLI is `/Users/kent/.local/bin/spacedock` version 0.27.2 (`evidence/spacedock-version.log`). Optional skips are not passed checks.

`guards.py` records each guard command and exit. With read-only `GIT_DIR` from the assigned worktree and `GIT_WORK_TREE` set to the export, the exact prescribed command `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.37.0/scripts/adr_lint.py docs/adr --since d8dbfcb1051d7c696aca139ed9ade332ee85abaf --require 0074` exits 0 (`evidence/adr-lint-prescribed.log`). The loaded Codex skill-root and candidate copies also exit 0. Number guards, design presentation, dispatch records and affected-document checks pass; the live number-guard rerun has no stale-fetch warning. Comment ratio is 1/192, 0.5%, below 5%; the only added comment is the required ADR pointer, read manually (`evidence/comment-ratio.log`). Every affected document has the implementation disposition and a checked validation verdict (`evidence/doc-impact.json`, `evidence/doc-verdicts.json`). The implementation dispatches and three follow-ups trace to accepted scope or the authorized F1 repair/merge.

The two installed 0.37.0 package paths are not assumed identical: `design_surfaces.py` and `dispatch_records.py` differ in inherited-main changes; the other five guard scripts compared are identical (`evidence/installed-packages.json`). Guards follow the loaded skill root, the specifically prescribed ADR command was additionally run, and all candidate behavior tests use the exported candidate. A preliminary equality assertion about installed copies failed and was corrected as a validator-environment assumption; it was not treated as a product failure.

Exact-head hosted run [42807539449](https://github.com/iamcxa/kc-claude-plugins/actions/runs/42807539449) completed successfully. Its primary log confirms pinned Spacedock CLI/plugin 0.27.2, all 40 stage cases, dispatch integration and observer recovery, separately from local plugin 0.27.3 evidence (`evidence/ci.json`, `evidence/ci-full.log`). CI triggers are unchanged; cost per PR was not measured. PR state and reviews were read only (`evidence/pr-final.json`, `evidence/pr-review-comments-final.json`). A Codex receipt names this candidate and reports no major issues. Copilot's quota refusal on the previous head is not clean review evidence. RoboRev and delivery remain FO-owned.

## Sufficiency, necessity and limits

The supported FO route writes and checks a complete record, commits real state, then emits exactly the committed role prompt; failed validation and failed commit preserve the intended boundary and recovery. Each retained change maps to that goal: parser/floor/routing/commit/output behavior has a removal control, exact input handling has separate raw-byte controls, tests detect their corresponding removal, workflow wording and budget have omission controls, and the ADR carries the accepted durable decision. No new platform, model resolver or adoption automation was introduced.

The accepted limits still hold. A wholly manual call with no dispatch record can clear its trigger; a supplied opus role call can be written for prod/database tasks, while the next `role_triggers.py` check still requires fable/Astra; an unknown model family is refused (`evidence/limits.json`, `evidence/probes.json`). Those are the explicitly accepted D2/D3 boundaries, not new defects. Batch-wide single-record placement, actual Agent/Paseo prompt forwarding, live reviewer behavior, host skill discovery, real human gates, delivery-hook body, adopter installation/sync, native execution and publication were not exercised. Tests prove script output and real local Git/CLI seams, not those external actions. No product push, PR write, review request, ready-state change or merge was performed.

## Captain acceptance script

Run unchanged in a fresh shell:

```sh
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/special-role-dispatch-records-built-by-script/validation/independent-3/acceptance.sh
```

The five commented steps inside `acceptance.sh` name exact actions and expected observations: export this SHA; commit/failure-recovery tests (2, OK); refusal/owed-role/model/flag tests (4, OK); raw CRLF/LF tests (5, OK); lint at 5939/5939 and final PASS. It was run exactly as written using `bash --noprofile --norc`; observed output is `evidence/acceptance.log`. There is no graphical user surface. This brief script covers the record route, major refusal/recovery boundaries, bytes and merged budget; it does not replace the full package suite, mutations, native reviewer/adoption proof or the delivery decision.
