# Independent validation of PR #827, repair recheck

Verdict: **PASSED** at `3567082b0ec1eeb59346b2d82887a07bc5ffc2fb`.
Base: `6a495cb8c4055f9a6eba8a05419c2d2fad1a90f1`; prior rejected head:
`8574e879b85197d31239ee2d9a9af0c5d0cb5392`.
This report supersedes independent-1's verdict for the new candidate only.
Evidence paths below are relative to this document. Candidate execution used a
fresh `git archive` export; mutations and synthetic Git fixtures lived under
temporary directories. No product worktree was created, removed, edited or pushed.

## Findings and repair disposition

F1, previously **Material**, is **closed** at this head. The previous script still
rewrites both supplied CRLF inputs in independently exercised role and stage calls;
the new script preserves their exact UTF-8 bytes in the on-disk and committed
records, and role stdout equals the raw record. Both LF records are byte-identical
between the two exact revisions, with identical SHA-256 values, using controlled
fixture dates and identical input bytes (`evidence/repair-bytes.json`, raw `.bin`
captures, `repair_probe.py`). No text-mode subprocess capture is used for this proof.

The repair changes exactly the three authorized production substitutions and adds
the five regression tests. All pre-existing test functions remain AST-identical
(`evidence/source-integrity.json`, `evidence/repair.patch`,
`evidence/retained-test-cases.json`). Reverting each input read separately, role
stdout separately, or all three together makes the matching raw-byte assertions
fail (`evidence/repair-mutations.json` and its four logs). These are assertion
failures, not import errors or timeouts. There are no new Material, Deferred risk,
Polish or Needs decision findings within the accepted boundary.

## Acceptance criteria and falsifiers

- AC-1: PASSED. Complete header, workflow SHA, model, supplied bytes, committed record and exact stdout are exercised. Removing state commit fails the committed-record assertion (`evidence/AC-1-no-commit.log`); raw CRLF/LF evidence above closes the former gap.
- AC-2: PASSED. Missing Package root or completion independently and together refuses with empty stdout and no saved record; bypassing both checks makes the invalid call return 0 (`evidence/probes.json`, `evidence/AC-2-no-checks.log`).
- AC-3: PASSED. Failed commit keeps the record, withholds the prompt, refuses retry before reconciliation and reuses the committed record afterward. Early prompt printing fails the empty-stdout assertion (`evidence/AC-3-early-prompt.log`).
- AC-4: PASSED. An actually owed chief-engineer call uses state commit and never dispatch build. The fixture's five implementation headings represent four repair passes under the existing trigger. Routing it through build fails the spy assertion (`evidence/AC-4-build-path.log`).
- AC-5: PASSED. Sonnet refuses without a record; Opus and the supplied Astra model pass. Removing the rank check makes the Sonnet refusal fail (`evidence/AC-5-no-floor.log`).
- AC-6: PASSED. All eight excluded stage-only options and design-director refuse with exit 2 and unchanged state. Allowing advance returns 0 and changes state, failing its assertion (`evidence/AC-6-allow-advance.log`).
- AC-7: PASSED. Role-local numbering, immediate retry reuse and all retained stage/record/trigger tests pass. Global numbering breaks chief-engineer-1 (`evidence/AC-7-global-numbers.log`, `evidence/checks.json`, `evidence/test_dispatch_stage.log`).
- AC-8: PASSED. Workflow instruction, reviewer-record pin and Captain-quoted +6 budget step pass at 5937 words. Deleting the instruction fails the transport check; deleting the budget step makes 5937 exceed 5931 (`evidence/AC-8-no-instruction.log`, `evidence/AC-8-no-budget.log`, `evidence/lint-skills.log`).
- AC-9: PASSED. ADR 0074 records the accepted D1-D3 ruling and matches the task's original Captain words. The prescribed installed ADR linter, with `--since 6a495cb8c4055f9a6eba8a05419c2d2fad1a90f1 --require 0074`, exits 0; removing Words exits 1 for that defect (`evidence/adr-lint-prescribed.log`, `evidence/AC-9-no-words.log`).
- AC-10: PASSED. Startup is 5931 to 5937 words; actual role success/refusal stdout and stderr are saved and counted with `wc -w` (`evidence/words.json`, `evidence/wc-words.log`). The idle/archive/merge readers are byte-identical to base; changing an idle reader trips its comparison (`evidence/unchanged-lifecycle.json`, `evidence/AC-10-changed-idle.log`). The authorized CRLF repair intentionally changes that input boundary on the shared stage reader; LF record bytes and other lifecycle readers stay unchanged.

All eleven original criterion controls and four repair controls were independently
run with `python3 -B` in disposable copies without Python caches. The control
logs were inspected for the intended assertion or diagnostic, rather than treating
any nonzero exit as sufficient (`evidence/mutations.json`).

## Verification and sufficiency

All 28 package-check commands exited 0, with 1275 unittest cases including 11 optional skips (`evidence/checks.json`, `evidence/summary.json`). The real-binary stage suite has 40 passing cases and no skips (`evidence/test_dispatch_stage.log`).
The runner's Python-only workflow selection was supplemented by a separate full
`test_dispatch_stage.py` invocation with the real binary; the merged check inventory
confirms that every package test file was exercised. Optional skips remain skips.
The prescribed installed ADR, design, dispatch-record, document-impact and comment
checks exited 0 (`evidence/guards.json`). The first number guard warned that its
network fetch was blocked; the authorized narrow rerun completed with no warning
and no findings (`evidence/number-guards-live.log`). Comments are 1/192 added code
lines, 0.5%, below 5%; the sole new comment is the required ADR pointer.

The role path satisfies the accepted limited-use goal across real state commits,
failure withholding and reconciliation. Each of the six changed files maps to the
role writer, regression protection, required workflow instruction and budget, or
ADR 0074; removal controls and the repair reversion justify those changes. No
additional abstraction, adoption change or production obligation was introduced.
`evidence/doc-impact.json` and `evidence/doc-verdicts.json` cover every listed
document and confirm the implementation report's updated/unaffected dispositions.

## Captain acceptance

There is no changed application screen. Prerequisites: this assigned repository
with the pinned commit available, Python 3, Git, tar, bash, and the declared
`/Users/kent/.local/bin/spacedock` binary (0.27.2 in this run).

```bash
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/special-role-dispatch-records-built-by-script/validation/independent-2/acceptance.sh
```

The unchanged script has four steps: export the full pinned SHA; check commit and
recovery (2 tests, OK); check malformed input, owed-role routing, floor and flags
(4 tests, OK); check role/stage CRLF and LF plus legacy LF compatibility (5 tests,
OK), then print PASS. It ran in a fresh `bash --noprofile --norc` shell and exited
0 (`evidence/acceptance.log`). The recorded test durations total under one minute, within
the five-minute budget. It does not launch a live reviewer, prove model behavior,
adopt the package, cover every legacy case, publish, or approve delivery.

## Implementation limits and current remote evidence

- Manual calls with no record remain outside the accepted D3 scope; an eligible Reviewer line still clears an owed call without a dispatch record (`evidence/limits.json`). This is the accepted boundary, not a new defect.
- The writer enforces the Opus floor only; a prod Opus reviewer call still leaves the higher Fable/Astra obligation owed at the later trigger (`evidence/limits.json`). The unchanged trigger also owns the database floor. Unknown model families refuse (`evidence/probes.json`).
- Local integration uses real Spacedock CLI 0.27.2 and active plugin root 0.27.3. Exact-head hosted run 42776608725 completed successfully, including the pinned 0.27.2 plugin checkout/install and stage, transport and recovery checks (`evidence/ci-refresh.json`, `evidence/ci-full.log`). Hosted evidence is distinguished from local evidence.
- PR #827 is OPEN/Draft at the validated head. The remote Codex review receipt names that head and reports no major issues; its summary is completed with no findings. Inline comments were empty when read (`evidence/pr-final.json`, `evidence/pr-review-comments.json`). This is read-only review evidence, not a validator-issued review or merge approval.
- RoboRev remains delegated to FO and is unclaimed here. Native reviewer execution, instruction-following, installation/adoption and release remain unverified. The package wrapper emits bytes for FO to forward; these checks do not prove that FO actually forwards them unchanged.
- No CI trigger changed; cost per PR was not measured. Main remains the recorded base (`evidence/remote-main.json`). Overlapping budget/ADR tasks still require the normal landing-order and recount check if the base changes.

FO retains gate, delivery and remaining review ownership. Product bytes and the
task's frontmatter stay unchanged; only this task's state evidence/report is
published through the prescribed state-commit helper.
