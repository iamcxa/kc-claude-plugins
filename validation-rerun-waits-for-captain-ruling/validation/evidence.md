# Independent validation evidence

Verdict: PASSED for b8a66e826c7524fa944a7165296acba94b3f5e13 against stacked base da5053febb546b2a7cf6ffe676b0d5a8b7e338a4 (PR #749). Reviewed all four changed files and the single added code comment. No product edit, configuration write, push, PR comment, review request, or merge was performed.

## Commands actually run

From the detached `/tmp/validate-pr750-b8a66e82` checkout:

```bash
python3 -B kc-dev-flow-2/scripts/test_dispatch_records.py
python3 -B kc-dev-flow-2/scripts/test_laws_check.py
python3 -B kc-dev-flow-2/scripts/test_pr_watch.py
python3 -B kc-dev-flow-2/scripts/test_sd_dispatch.py --sd-plugin-root /Users/kent/.codex/plugins/cache/spacedock/spacedock/0.27.3
python3 -B kc-dev-flow-2/scripts/lint-skills.py
python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.0/scripts/adr_lint.py docs/adr --since da5053febb546b2a7cf6ffe676b0d5a8b7e338a4 --require 0045
python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.0/scripts/comment_ratio.py da5053febb546b2a7cf6ffe676b0d5a8b7e338a4 b8a66e826c7524fa944a7165296acba94b3f5e13 --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2
python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.0/scripts/doc_impact.py da5053febb546b2a7cf6ffe676b0d5a8b7e338a4 b8a66e826c7524fa944a7165296acba94b3f5e13
python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.0/scripts/number_guards.py check --workflow-dir /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2 --task /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/validation-rerun-waits-for-captain-ruling.md
python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.0/scripts/design_surfaces.py check /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/validation-rerun-waits-for-captain-ruling.md
python3 -B /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.33.0/scripts/dispatch_records.py /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/validation-rerun-waits-for-captain-ruling
git -C /tmp/validate-pr750-b8a66e82 diff --check da5053febb546b2a7cf6ffe676b0d5a8b7e338a4 HEAD
```

All exit 0. Unit suites: 80 in 77.219 s, 58 in 98.877 s, 129 in 119.206 s. Native Spacedock test output is in `sd.log`. ADR lint: `43 ADR file(s) checked, 0 legacy`. Comments: `code lines 1705, comment lines 1, 0.1%`, maximum 5%. Number guards: `PASS: no findings`; migration guard skipped because no migrations path is declared; task reserves no migration. Design: presentable, scope check correctly skips validation. Dispatch records: `6 dispatch record(s) complete`. Lint: workflow 5754/5754 words.

## Acceptance criteria and falsifiers

| Criterion | Independently observed behavior | Killed mutation |
|---|---|---|
| AC-1 | Fresh, follow-up and filename-one live records refuse without a later native ruling; later ruling passes and input bytes remain unchanged. | Removing the predicate call fails the before-ruling assertion. |
| AC-2 | Six incident event-prefix fixtures: four refuse, two pass, retaining saved record text and full source IDs. | Replacing the first event's body/ruling with the later fourth-validation prefix fails its refusal and total-count assertions (`prefix-mutation.log`); filename-one exemption also fails. |
| AC-4 | Old/same-commit/edited/wrong-actor/wrong-task/wrong-stage/withdrawn rulings refuse; missing/shallow/rewritten/discontinuous/divergent history exits 2; supported moves and later rulings work. | Ignoring strict ancestry fails old/same-commit refusal. |
| AC-5 | Plain copies skip only the new rule regardless of Git cwd; bare script names still fail; real laws snapshot caller retains pass/violation output. | Cwd-based root detection fails the copied-folder assertion. |
| AC-6 | Existing folder/newest/coverage consumers and native route tests pass; lifecycle counts unchanged; refusal/error output 56/16 words. | Removing the recovery sentence fails its exactly-once assertion and count. |
| AC-7 | Three exact legacy cases: predicate 0 / full CLI 1; three supported-form complete controls: CLI 0. Free-form record holds until on-touch supported entry; partial ruling intentionally passes structure. | Gate-only recognition loses the supported amendment pass; relaxing inherited amendment-form checking loses the required legacy diagnostic/refusal. |

Eight mutations independently executed with Python `-B`, caches cleared in the copied mutation package, and restored after each run; every mutation produced AssertionError / exit 1. Seven are enumerated in `mutations.json`; the later-prefix mutation is separately recorded in `prefix-mutation.log`. These are throwaway probes, not candidate edits. `mutate.py`, `evidence.py`, and `reading.py` retain the local probe recipes and declare their machine-specific inputs; they are not shipped dependencies.

## Historical source and reading-cost checks

`source-proof.log` verifies all 27 fixture finding sets against their exact Git report and dispatch snapshots, the preserved amendment text, and every supplied exact dispatch text. Independently read the seven named report-to-dispatch changes and saved dispatches: retrospective first record; partial ceiling reply; older reply preceding new findings; explicitly deferred decisions; FO-only authorization; FO-directed repair; conflicting FO/worker attribution. The retrospective source report explicitly says records existed only under `/tmp/spacedock-dispatch`; its event changes no task bytes. The merge-gatekeeper source diff contains the Captain's free-form approval of repair/revalidation. Thus the accepted cost remains two record-addition false holds, including one actual rerun; these are bounded saved-source judgments, not a new historical enforcer or chat audit.

Base and candidate lifecycle recounts (`reading-base.log`, `reading.log`) both give startup 7521, idle/open 1424, idle/merged 1395, archive 895, merge 2970; actual provider-stub outputs 29/0/5/90. New clean/non-Git output remains zero. Real refusal/error tests give 56/16 words under one-token path/hash/reason assumptions. Workflow, mod, law, and CI diff is empty. CI cost per PR was not measured; no CI change.

## Findings, sufficiency, necessity, and limits

No new Material, Deferred risk, Polish, or Needs decision finding. The earlier F1 compatibility decision is settled by Captain amendment 1; AC-3 is withdrawn and AC-7 governs. The four-file change is sufficient for the accepted live-check goal: one existing command enforces the rule, two existing test files prove failure/recovery and its consumer boundary, and ADR 0045 records the durable decision. Removing the runtime check restores unauthorized passes; there is no new script, hook, workflow instruction, CI trigger, or historical enforcement feature in the product diff.

Affected documents: ADR 0045 updated and consistent; learning.md unaffected because its consumer-warning remains true and the real historical caller test proves no new output there. The design's unchanged Mermaid flow matches the skip/error/refusal/ruling branches on inspection; it was not re-rendered in this validation, and no changed UI is claimed.

Implementation limits accepted within the recorded scope: non-Git copies lack this new protection; legacy free-form rulings need faithful on-touch recording; the check does not authenticate Captain words, classify findings, prove per-finding semantic coverage, or enforce execution before dispatch. Unchanged candidate CI and RoboRev are FO-supplied evidence only: adr-path-check, live multi-profile route gate, Python unit tests, version parity, GitGuardian pass; `roborev:1326` clean. I did not independently query GitHub or rerun RoboRev. Local native route tests do not prove worker execution, human gate decisions, delivery-hook bodies, remote merge, or installation/adoption. Those are not accepted obligations of this bounded predicate.

The four-step fresh-shell acceptance run is reproduced in full in `acceptance.md`; exit 0, exact head, two live tests plus two saved-case tests and ADR lint. Git administration access required escalation for the unchanged script, after which it passed; this was a sandbox restriction, not a candidate failure.
