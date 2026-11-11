
## Stage Report: validation

- DONE: Independent verdict on PR #841 head 5bf7cf78 against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  REJECTED at 5bf7cf78866a2f0f6376c15b59fc400519c5ffeb; base e8664a72b0f904e5dda3c391d52ab3abaca876b4. All evidence below is under budget-overrun-holds-and-findings-meet-non-goals/validation-1/; README.md maps every criterion, limit and falsifier; export-integrity.json verifies unchanged candidate bytes.
- DONE: This task carries six Captain amendments; check that they do not contradict each other or the approved decisions, that each replacement criterion follows the amendment rules, and that amendment 6's permission was used only for synthetic data and expected text (list every test file changed, with the lines, and say for each whether any assertion or negative case was removed or weakened); replay the relay task and the archive counts yourself; judge the implementation report's stated compatibility limit for older designs that lack the new section; placement: the Captain approved dispatching workers from the First Officer's workspace until the task-workspace sandbox is repaired (host question dialog, 2026-11-11)
  README.md records each ruling and each of the six test files/lines; no old assertion or negative case weakened/removed (test-audit.json). history-audit.json verifies AC-7's verbatim move and fresh AC-10/11/12/13 ids. Replays and compatibility judgment are below; no product worktree created or changed.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.38.1/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  README.md gives the exact fresh-shell command for acceptance.sh's five steps; acceptance.log and acceptance-result.json record exit 1: steps 1-4 pass, both step-5 missing-section variants wrongly pass. adr.log exits 0 with --since e8664a72b0f904e5dda3c391d52ab3abaca876b4 --require 0077; findings F1/F2 are Material.
- DONE: AC-1 — Budget and pending cycles are visible
  Real-dispatch suite and mutation-forward-budget.log prove both countable and uncountable output; dropping forwarding fails both checks.
- DONE: AC-2 — first overrun holds before build and covering amendment resumes
  Real-dispatch suite exercises record removal/build spy/recovery; mutation-off-by-one.log and mutation-ignore-amendment.log fail at the bound and covering amendment.
- DONE: AC-3 — relay holds at its second implementation dispatch
  relay-replay.json/history-audit.json: first hold 42317d0c14d24228ddf08b6dd51f6575fc139bf4 names the actual Symptom; the base exits 0 there and has no hold before d85ce1527cbaa44d285e89e0c4f99a211e4ba964.
- DONE: AC-4 — four pinned archive surveys and all differences explained
  broad-replay.log/archive-replay.json: held/countable QNow 7/7→0/0, Relay 11/23→10/21, Web 5/20→0/0; this workflow stays zero held, 60 broad Budget matches→58 real records. budget-line-impostors.json identifies both exclusions; README.md explains every narrower-form difference.
- DONE: AC-5 — countable reminder removed; uncountable reminder and role events retained
  Full role/delivery/pr-watch suites pass; keep-countable-reminder and lose-uncountable-reminder mutants fail (mutations.json).
- DONE: AC-6 — legacy first-record exemption at dispatch and merge ask
  merge-transition-probe.json exercises the real role check with existing provider stubs: old first header passes, new admitted overrun blocks; mutation-ignore-first-header.log fails the legacy control.
- DONE: AC-8 — reserved ADR and prior decision amendment
  adr.log checks 68 ADR files with exit 0; adr-falsifier.log runs the base export with --require 0077 and exits 1 because that record is absent. ADR 0026 links the new decision.
- FAILED: AC-9 — missing Worth section refusal; same-entry amendment authority
  Existing positive/fenced controls and optional-worth mutant pass, but worth-counterexamples.json proves F1/F2 allow absent sections. The authority half passes, including mismatched/cross-entry/fenced bound controls and mutation-invent-amendment-bound.log.
- DONE: AC-10 — corrected gate content and independently recounted words
  word-count.json and lint log: workflow 5939→6008, ideation principles 643→687; one quoted +69 step names loaded moments. mutations.json catches both off-by-one word totals; backlog/ideation wording follows amendment 4.
- DONE: AC-11 — total caps, mixed minutes, record count and pending overlay
  Budget suite and real-dispatch cases pass cap/cap+1; total-form, total-off-by-one, highest-cycle, omitted-ideation, duplicate-pending and lost-minutes mutants fail (mutations.json).
- DONE: AC-12 — keep results, report remaining work, stop adding; Captain may replace
  acceptance.log step 3 preserves an existing result while holding before build; missing-default and missing-override mutants fail (mutations.json).
- DONE: AC-13 — only named repair-message headers count
  Header controls and all/no/body/none-prefix mutants pass/fail as intended. message-counts-40cfa1ae.json confirms archived=5 and rollout=7; message-counts-ba7d022e.json confirms rollout=8 after validation-1; the implementation's correction of FO's archived 7 is valid.
- DONE: Existing suites, document impact, comments, records and reserved numbers
  full-summary.json records all 28 unchanged CI commands exiting 0, with all skips retained; mutations.json catches 24 injected faults. All 14 doc-impact rows have checked dispositions; comment-ratio.log is 12/422 (2.8%, max 5%); dispatch-records.log checks 8 records; number-guards-network.log passes after the sandboxed fetch warning was resolved.
- DONE: Compatibility and minimal-necessity assessment
  design-installed.log exits 0 but design-candidate.log rejects this historical task's absent heading. corpus-check.json loses no prior diagnostics and adds only approved Worth/fixed-Budget refusals. Only Budget holds were grandfathered; this is the expected AC-9 compatibility cost, not permission to backfill old designs. Other retained changes map to criteria; goal sufficiency fails F1/F2.
- SKIPPED: Product repair, local model review, publication, merge, release and adopter delivery
  Not authorized to the validator. pr-final.json observes this exact head OPEN/draft and hosted unit tests SUCCESS, with docs deploy SKIPPED; that does not override F1/F2. Local binary/plugin are 0.27.2/0.27.3; CI cost was not measured and no CI change was made.
- F1 Material: A valid YAML status comment bypasses the Worth requirement (design_surfaces.py:1104).
  User/workflow: pilot FO preparing a PRFAQ design; harm: absent questions reach a presentable result; value-ac[AC-9] missing ideation section must refuse; trigger: native Spacedock reads ideation for `status: ideation # ready for review`, candidate exits 0 instead of the plain-status control's 1 (worth-counterexamples.json, commented-status).
- F2 Material: An HTML-commented heading satisfies the Worth requirement (design_surfaces.py:1102).
  User/workflow: ideation author leaves a commented scaffold; harm: rendered design has no section but check passes; value-ac[AC-9] missing section must refuse; trigger: inserting only `<!--\n### Worth questions\n-->` changes exit 1 to 0 (worth-counterexamples.json, hidden-heading; acceptance.log step 5).

### Summary

REJECTED: candidate 5bf7cf78866a2f0f6376c15b59fc400519c5ffeb fails AC-9 despite green existing suites and reproduced budget behavior. The six amendments and fixture-only permissions are satisfied; the historical-design refusal is a real, declared compatibility consequence, distinct from the two new false-pass findings. FO must disposition F1/F2 through the supported feedback route before any product repair or delivery; the validator changed only this task's report and evidence.
