# Independent validation, cycle 2

Verdict: **PASSED for the accepted task scope** at PR #841 head
`6da9a765ee04e1e2c7836517ba01f75b0ea91d73`. This is a new validator's execution,
not adoption of validation-1's conclusions. No product file was edited.

The task base and merge base against observed origin/main are
`e8664a72b0f904e5dda3c391d52ab3abaca876b4`; observed origin/main was
`546a136386c94c58e430c91a6f3457b38bd73880`. Product execution used fresh `git archive`
exports of the candidate, the task base, and rejected head
`5bf7cf78866a2f0f6376c15b59fc400519c5ffeb`. Read-only git inspection and package
governance checks used the assigned worktree pinned to the same candidate.
Identity and exact diffs: `identity.json`, `candidate.patch`, `repair.patch`.

## Direct result and criteria

All 28 commands extracted from the unchanged CI workflow passed in this run:
`tests.json`, `full/full-checks.json`, `full-run.log`, and each named `full/*.log`.
The 24 previous Budget/Worth mutations were executed here and caught as assertion
failures, with zero errors accepted as kills: `mutations.json` and
`mutation-*.log`. The repair proof independently ran three final tests against
the rejected implementation and four reverse mutants: `repair-proof.json` and
the named raw logs. Existing test fixtures are reused; their successful reports
from prior workers are not evidence for this verdict.

| Criterion | Observed evidence | Executed falsifier |
| --- | --- | --- |
| AC-1: Budget and spent cycles printed | full dispatch suite and Captain step 3 exercise the real builder; countable and uncountable values are forwarded and stamped | `mutation-forward-budget.log` fails when forwarding is removed |
| AC-2: first overrun stops, approved raise resumes | real build test checks no output artifact, removed pending record, no build invocation, and resumed cycle 2 | `mutation-off-by-one.log`, `mutation-ignore-amendment.log` |
| AC-3: relay implementation-2 stops | `relay-replay.json`: first budget hold at 42317d0c14d24228ddf08b6dd51f6575fc139bf4, names the recorded CI/contract symptom; base exits 0 there | base arm stays unheld before the chief-engineer event at d85ce152; raw reasons retained |
| AC-4: four pinned archive counts explained | `pins.json`, `archive-replay.json`, `ideation-recount.log`, `count-differences.json`; differences detailed below | reran broad parser beside fixed forms; each dropped task's exact nonmatching Budget is retained and accounted for |
| AC-5: reminder removed only for countable budgets; calls retained | full role, delivery and idle-consumer suites; countable/uncountable controls | `mutation-keep-countable-reminder.log`, `mutation-lose-uncountable-reminder.log` |
| AC-6: old first record is exempt at dispatch and merge | full role suite plus `merge-transition-probe.json`: old-record merge ask exits 0, newly admitted overrun exits 1 | `mutation-ignore-first-header.log`; admission-header toggle reverses the actual merge-ask result |
| AC-8: reserved decision record and amendment | package ADR lint exits 0, 68 records; ADR 0077 and ADR 0026 amendment read against Captain words | `adr-control.log` exits 0; deleting only 0077 in a throwaway copy exits 1 in `adr-removed-0077.log` |
| AC-9: visible Worth section and authoritative Budget amendment | `worth-probe.json`, full design/dispatch/role suites; native commented and quoted status; hidden headings; real section control | rejected head passes the two bad designs; repaired head refuses; raw-reader, comment-blind, ignored-native-error and ignored-response-binding mutants fail; `mutation-invent-amendment-bound.log` |
| AC-10: proper gate content, one word-budget raise | `candidate.patch`, full lint, `word-count.json`, `independent-word-count.json`; backlog shows Budget, ideation shows answers; one +69 step quotes gate and amendments | `mutations.json` records both count-minus-one and count-plus-one refused by the equality check |
| AC-11: total cap and minutes notice | real total-cap dispatch test, role and seed suites; pending overlay counts once | ignore-total, total-off-by-one, pending-double-counted, ideation-not-counted, highest-cycle-is-total, minutes-prefix-ignored and minutes-notice-lost mutations |
| AC-12: preserve results, report remaining, stop adding | real dispatch fixture keeps existing results bytes and removes only pending dispatch; Captain replacement clause present | default-outcome-lost and captain-override-lost mutations |
| AC-13: named repair messages count, answers do not | role suite and `message-counts-40cfa1ae.json`, `message-counts-497b9f32.json`; normal stages once, special roles excluded | count-all-messages, count-no-messages, none-prefix-is-none and body-symptom-counts mutations |

AC-7 is superseded, moved verbatim under amendment 4. AC-10 is its replacement.
No old criterion was silently revived.

## Rechecked prior failures and native read boundary

`worth-probe.py` invokes the real CLI and verifies the native status is ideation,
then invokes each version's checker without changing the input bytes. Its saved
`worth-probe.json`/`.log` show: plain missing section refuses on both heads;
commented and quoted status with no section, and HTML-comment-only heading,
pass on the rejected head but refuse on this candidate; a visible section passes
on both. The final regression tests also cover flat/folder-form split-root tasks,
closed/unterminated comments, and comment/fence interactions.

The candidate refuses missing executables, invalid JSON, nonstring status and a
response bound to another file in its regression test. The independent CLI probe
adds real nonzero-reader and timeout failures; both exit 1 with a native-read
diagnostic. This is fail-closed, not a successful empty design. The native query
is conditional; `design-no-native.log` reruns the complete design suite with a
nonexistent native executable and preserves its successful result. The check
establishes a section, not truth or completeness of the three answers.

## Historical replay and compatibility

`export.py` re-exported exactly the four `pins.json` revisions. `replay.py` was run
against this candidate; the hypothetical post-release replay adds Budget headers
only to throwaway record inputs. It does not assert today's old relay task would
be stopped after upgrade. The separate merge transition proves old-header exemption.

The broad ideation counts were independently reproduced: qnow 7 held / 7 countable,
relay 11 / 23, web 5 / 20, and this workflow 0 held among 60 tasks with a text
Budget and implementation/validation records. With approved fixed forms, those
become qnow 0 / 0, relay 10 / 21, web 0 / 0, and this workflow 0 / 0.
All seven qnow and twenty web phrases use passes, rounds, ideation clauses or
free prose outside the accepted fixed forms. Relay excludes `llms-teaches-versions`
(rounds; not previously held) and `review-keyword-invocations` (ideation-prefixed;
previously held). The per-task source phrases are in `archive-replay.json`.
The candidate replay has 58 eligible this-workflow tasks, because the old broad
reader counted a fenced template in `seed-check-requires-schema-fields` and a
Budget under `### Delivery split` in `release-acceptance`; neither is an actual
supported Scope/Budget section. `count-differences.json` preserves both inputs.
This denominator correction changes no hold. No unexplained difference remains.

AC-13's original frozen state `40cfa1ae` reproduces 5 ordinary records and zero of
6 messages for `amendment-checked-when-written`, and 2 ordinary records plus 5 of
9 messages = 7 for `release-rollout-reaches-adopters-and-laws-pin`. At this run's
initial state `497b9f32`, the latter has a third ordinary record, so total 8; the
same five messages count. This is recorded-history growth, not a changed rule.

The chief engineer's compatibility risk is **confirmed**: `legacy-design.json`
uses this task's committed approved design at initial state `497b9f32`, hashes
its untouched bytes, and records base exit 0 / candidate exit 1 solely because
the real Worth heading is absent. The accepted rule gives only budget holds an
old-task exemption; no Worth exemption or automatic backfill was promised.
The corpus run checks both modes on all 623 task bodies across the pinned
exports, retaining per-file results in `corpus-check.json`; no earlier diagnostic
disappeared and additions are only Worth/fixed-Budget refusals. Those historical
tasks are not changed. If release requires backfilling or exempting old designs,
that is a Captain compatibility decision outside this repair.

## Amendment 6 and minimum necessary scope

All six changed test files were read against the task base, including their
negative cases. `test-scope-audit.json` records no removed test, and the repair
changes no pre-existing test function at all. Earlier authorized updates are:

- `test_delivery_gate.py`: one expected question prefix; the before-ask ordering,
  successful ask and other-problem assertions remain.
- `test_pr_watch.py`: two expected question fragments and the seed Budget plus its
  deletion matcher; the missing-Budget negative still removes the actual field.
- `test_sd_dispatch.py`: countable fixture budgets, their deletion matcher, and a
  synthetic Design/Worth section for criteria parity; all existing assertions,
  malformed criteria and native transport negatives remain.
- `test_design_surfaces.py`: countable fixture budgets and matching replacement
  strings, plus required Worth sections in unrelated feature fixtures; placeholder,
  quote, fence and missing-field negatives remain. Added tests cover new behavior.
- `test_dispatch_stage.py`: expected Budget header while preserving role-record
  bytes, new question text, and new dispatch/Worth cases. No older assertion lost.
- `test_role_triggers.py`: approved question wording and its measured 51-to-46
  expected word count; new Budget cases add coverage.

The repair changes only `check_task` plus new `worth_lines` and `worth_stage` in
production. `repair-scope-audit.json` verifies Budget/dispatch functions and the
delivery/idle consumers are unchanged from the rejected head. Every retained
production change maps to a current criterion, the shared native reader boundary,
or required ADR/word-budget policy. Reverse mutations justify those mechanisms.
No new Material-finding rule, free-prose budget parser, minute meter, broad YAML
rewrite or automatic old-design backfill was added.

The prior implementation's 15 sibling items remain open for FO disposition in
`../implementation-3/sibling-findings.json`. This run independently reproduces
its nine representative observations before and after; `sibling-compare.json`
confirms they are unchanged. Commented-stage security/design/built-screen bypasses,
hidden FO/criteria/amendment regions and unclosed seed comments are not fixed by
this candidate, and source-only entries are not promoted to runtime proof.
This validation neither repairs nor declines those separate findings.

## Required checks, documentation, and limits

`required-checks.json` records exact package commands and exits. ADR, comments,
dispatch records, installed-package task-design check and role admission pass.
The initial number check exited 0 with a stale-fetch warning; `number-fresh.log`
records the authorized fresh-fetch rerun, exit 0 without that warning. No migration
path is declared. Product comments were read; added real comments are ADR pointers,
and the seven apparent comment lines in test strings are Markdown fixture content.
Measured comment ratio is 12/517 = 2.3%, under 5% (`comments.log`).

All 14 `doc_impact.py` paths are covered in `doc-impact-verdicts.jsonl` and checked
against current behavior. `independent-word-count.json` independently calls `wc -w`
over source files and captured output: workflow 5939 to 6008, ideation principles
643 to 687; countable output 11 words, uncountable 14, overrun example 88, total 15,
mixed minutes 17. The old countable advisory was 51 words; forwarded advisory is
now absent, while role CLI itself still prints an 11-word Budget line. Design
estimates were approximate; these are the measured candidate values.

The local binary is Spacedock 0.27.2 and explicit plugin test root is
`/Users/kent/.claude/plugins/cache/spacedock/spacedock/0.27.3`; no claim of a local
paired 0.27.2 or 0.28.0 runtime is made. Unlike the implementation's disappearing
cache run, all 28 commands in this run pass first attempt with the declared root.
`pr.json` confirms the remote draft head matches; six reported checks succeeded
and docs deploy was skipped. This is not a branch-protection or merge verdict.
No CI configuration changed; cost per PR was not measured.

The direct ADR-negative probe first checked the wrong English substring after
correctly observing exit 1. `adr-probe-note.txt` and the raw negative output retain
that validator-only assertion mistake; the corrected probe checks the existing
`required ADR 0077 does not exist` diagnostic without changing product tests.

## Captain acceptance: five steps, fresh bash

Run this exact command from any working directory:

```bash
/bin/bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/budget-overrun-holds-and-findings-meet-non-goals/validation-2/captain.sh
```

The script needs Git, Python 3, the named local repository with the two pinned
commits, and the explicitly named Spacedock binary. It creates only a temporary
export and fixture repositories, deleting the export on exit. Its five comments
name each exact action and expected result: pin/export, visible-section/refusal
controls, real dispatch hold/resume, authority/message counts, and merge exemption.
The validator ran it unchanged under `env -i` and fresh `bash --noprofile --norc`;
`captain.log` records the output and final PASS, exit 0. It completes within five
minutes and has no screen to inspect. It does not replace the archive replay,
complete suite, hosted CI, review, Captain decision, merge, release or adoption.

## Finding disposition and handback

- F1 Deferred risk: old designs lacking the Worth section are refused. User/flow:
  an adopter re-presents a pre-release design after upgrade. Observable effect:
  additional design refusal, demonstrated in `legacy-design.json`. Protected field:
  `none: the accepted AC-9 applies the section rule to each design and promises no
  legacy exemption`; this is not a new Material breach. Trigger to reconsider:
  a Captain ruling requires existing designs to remain presentable unchanged, or
  release scope requires a migration/backfill. Return that choice to FO/Captain.

Prior validation-1 F1/F2 are independently repaired at this head. No new in-scope
Material or blocking finding was found. The accepted Pilot result is sufficient;
the identified historical and sibling limitations remain explicit. Product
publication, independent review disposition, gate preparation and delivery remain
FO/Captain-owned. `cleanup.json` records removal of this validator's entire scratch
root after evidence commit; no temporary copy is retained as supporting evidence.
