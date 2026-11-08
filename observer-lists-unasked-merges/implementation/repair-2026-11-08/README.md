# Implementation repair addendum — 2026-11-08

Product head: a43b537cd12d69a5ccfde38bf964c6ea35cb0de0
Parent: b36fbeeec3a6699c0a82a021dc4ee0142410f6c8
Base: 139feeaee7ce037a0c6535568cd6bd103155cbae

Only kc-dev-flow-2/skills/observer/SKILL.md changed in this repair. It now preserves the audit's own exit status before presentation and gives standalone report-row templates. The final template wording is retained under implementation-1-message-2 because the existing tests and repository lint pass; its format behavior is not promoted to a passing native result.

## Accepted F1 evidence

direct-execution.json records the actual tool result: exit 1 from an unpiped Python invocation. direct.stdout contains carried 54 of 82, the three named-kind lists, and all eight no-ask findings in the specified window. The initial sandbox attempt exited 2 because GitHub was unreachable; the unchanged approved retry exited 1. The sandbox output remains separate.

Fresh native sample 1 is agent 7962de54-0c75-4f1a-81bb-277752d22055; sample 2 is bb9e4713-50e5-496f-ad3e-088e82e4850a. Both report the audit's own exit 1, agreeing with the direct run. identity.json verifies that the exit-capture instructions read by both samples are byte-identical to that block in the final committed skill.

## Retained F2 evidence and disposition

observer-report-1.md and observer-report-2.md are the unedited final reports, including their tool transport header. observer-activity-1.json and observer-activity-2.json retain the available activity transcripts; tool-command previews in that surface are abbreviated.

Both format attempts retain the finding identifiers but shorten per-row fields; sample 2 also omits a standalone carried row. The original failing validation report remains unchanged under validation/. compare.py checks the native report against direct.stdout and the actual direct exit receipt. It rejects the original exit-0 claim and confirms exit 1 for both repair runs; its overall format result remains false. The parser excludes explicitly negated status text such as "not exit 2", after manual checking of that phrase.

FO explicitly declined F2 (Polish) at the gate in dispatch/implementation-1-message-2.md and ordered format reruns stopped. A third create-agent call was rejected before an agent was created; it is not native evidence and was not retried. The final row-template edit has test/lint coverage, not another native format pass. These retained failures are not rewritten or outcome-selected away.

## Checks and remaining ownership

The current wording passed test_merge_audit.py (17 cases), test_lint_skills.py (47 cases), and the repository lint-skills.py. The workflow remains at 5933 of 5933 words. Package ADR lint, number guards, design check, comment ratio and diff check passed. doc-impact.json still lists README.md: unaffected, because the named-CI-command entry remains accurate.

The full local package commands and their results are retained in suite/ and suite-summary.json at this head. Local dispatch uses CLI 0.27.2 and plugin files 0.27.3; this does not prove the hosted pinned installation. No CI configuration or version was changed by this repair; hosted cost per PR was not measured.

No product or state branch was pushed during the repair. FO owns publication, RoboRev, hosted CI, independent revalidation and the gate. The original validation-1 REJECTED verdict at b36fbeeec remains historical evidence, not a verdict silently rewritten for this head.
