1. Q: Once a consultation is owed, which action must wait for its result?
   Story: special-role-calls-fire-when-needed
   Grounds: `pr_watch.tasks()` prints owed calls but returns success; both role skills say they have no gate authority (`kc-dev-flow-2/scripts/pr_watch.py`, `kc-dev-flow-2/skills/chief-engineer/SKILL.md`, `kc-dev-flow-2/skills/engineering-reviewer/SKILL.md`).
   Why it matters: A reminder and a prerequisite produce different workflow behavior.
2. Q: Which judgment signals require a call, rather than merely asking the First Officer to consider one?
   Story: special-role-calls-fire-when-needed
   Grounds: The story names repeated gaps, reversed Captain rulings and authority changes; `role_triggers.events()` recognizes only cycle lines and amendment fields (`kc-dev-flow-2/scripts/role_triggers.py`).
   Why it matters: The boundary determines whether this changes actual consultation behavior or only record parsing.
3. Q: When repeated review gaps expose both unclear delivery direction and a disputed technical claim, which role should be called first?
   Story: special-role-calls-fire-when-needed
   Grounds: Chief Engineer handles work “repeatedly circling”; Engineering Reviewer handles conflicting material evidence (`kc-dev-flow-2/skills/chief-engineer/SKILL.md`, `kc-dev-flow-2/skills/engineering-reviewer/SKILL.md`).
   Why it matters: Overlapping triggers could otherwise produce inconsistent routing or duplicate consultations.
4. Q: May the First Officer waive a call about authority or irreversible risk without a new Captain decision?
   Story: special-role-calls-fire-when-needed
   Grounds: `owed_line()` allows “if you will not” with a recorded reason, while architecture decision 0011 reserves authority, irreversible changes and money for the Captain (`kc-dev-flow-2/scripts/role_triggers.py`, `docs/adr/0011-fo-decides-for-the-captain-by-a-delegation-ladder.md`).
   Why it matters: An unrestricted waiver could preserve the missed consultations this story targets.
5. Q: Does a waiver recorded after merge settle the obligation, or must it remain recorded as a missed consultation?
   Story: special-role-calls-fire-when-needed
   Grounds: The story identifies a relay call “waived after the merge”; `cleared()` accepts waivers without checking their date (`kc-dev-flow-2/scripts/role_triggers.py`).
   Why it matters: Historical paperwork could otherwise appear equivalent to timely advice.
6. Q: What counts toward “two or more review rounds finding new gaps” when external review verdicts and validation repair cycles occur in the same task?
   Story: special-role-calls-fire-when-needed
   Grounds: The story uses two rounds; `check()` uses cycle number three; the workflow defines an external round as one reviewer verdict on the pull-request head (`kc-dev-flow-2/scripts/role_triggers.py`, `kc-dev-flow-2/references/sd/workflow.md`, “FO steps: review findings”).
   Why it matters: Different counting units change when consultation starts.
7. Q: Which changes marked `Supersedes: none` must still trigger independent assurance?
   Story: special-role-calls-fire-when-needed
   Grounds: The story names a merge-rule change with that marker; `events()` ignores field values starting with `none` (`kc-dev-flow-2/scripts/role_triggers.py`).
   Why it matters: Additions can change authority without replacing a numbered criterion.
8. Q: Must a reversal of an accepted Captain ruling trigger consultation when it occurs in a new task rather than an amendment to the original task?
   Story: special-role-calls-fire-when-needed
   Grounds: The story names designs reversing earlier rulings; `read_task()` and `events()` inspect only the named task (`kc-dev-flow-2/scripts/role_triggers.py`).
   Why it matters: Detecting these reversals may require evidence beyond one task’s amendment section.
9. Q: When does a completed consultation expire after further repairs or changes to the claim?
   Story: special-role-calls-fire-when-needed
   Grounds: `check()` accepts one `Cycle 3` record for all later cycles, and `cleared()` binds amendment calls only to a number and date (`kc-dev-flow-2/scripts/role_triggers.py`).
   Why it matters: Advice on an earlier problem could suppress consultation on a materially different one.
10. Q: What evidence must exist before a consultation counts as completed?
    Story: special-role-calls-fire-when-needed
    Grounds: `cleared()` accepts a matching `Reviewer:` line without checking a returned report, conclusion or artifact revision (`kc-dev-flow-2/scripts/role_triggers.py`).
    Why it matters: Recording an intended dispatch could otherwise clear an obligation without receiving advice.
11. Q: Should the two existing calls described as “third repair cycle” count without rewriting their original records?
    Story: special-role-calls-fire-when-needed
    Grounds: The story says those calls occurred but were not counted; `cleared()` requires the literal token `Cycle 3` (`kc-dev-flow-2/scripts/role_triggers.py`).
    Why it matters: The answer separates actual missed calls from incompatible receipt wording.
12. Q: Should a task with no recognized cycle or amendment structure be reported as clear or as insufficient evidence?
    Story: special-role-calls-fire-when-needed
    Grounds: The story names unrecognized stage-report headings and missing amendment sections; `check()` reports success when it reads zero events (`kc-dev-flow-2/scripts/role_triggers.py`).
    Why it matters: Unsupported record formats currently look like an absence of consultation needs.
13. Q: Which task-state revision governs a consultation when the latest feedback has not yet been committed?
    Story: special-role-calls-fire-when-needed
    Grounds: `read_task()` reads committed bytes, while `pr_watch.tasks()` discovers tasks and reads their frontmatter from disk (`kc-dev-flow-2/scripts/role_triggers.py`, `kc-dev-flow-2/scripts/pr_watch.py`).
    Why it matters: A mixed snapshot can omit a new trigger or assess a different state from the worker’s.
14. Q: If two First Officer sessions detect the same obligation before either records a result, should they share one consultation?
    Story: special-role-calls-fire-when-needed
    Grounds: `pr_watch` keeps session-specific watch state, and `test_a_live_task_owing_a_role_call_prints_the_line_until_it_is_recorded` expects repeated dispatch instructions (`kc-dev-flow-2/scripts/pr_watch.py`, `kc-dev-flow-2/scripts/test_pr_watch.py`).
    Why it matters: Concurrent sessions can duplicate expensive calls and receive conflicting advice.
15. Q: May an active worker continue changing the artifact while a newly triggered consultation evaluates it?
    Story: special-role-calls-fire-when-needed
    Grounds: Repairs may dispatch immediately, while Engineering Reviewer assesses an exact revision (`kc-dev-flow-2/references/sd/workflow.md`, “Stages”; `kc-dev-flow-2/skills/engineering-reviewer/SKILL.md`).
    Why it matters: Continued work can invalidate the advice before the First Officer receives it.
16. Q: What should happen when a dispatched role times out or returns no usable report?
    Story: special-role-calls-fire-when-needed
    Grounds: `role_triggers.py` models calls as cleared or owed, while the role skills prescribe report shapes without a pending or failed-call lifecycle (`kc-dev-flow-2/scripts/role_triggers.py`, both role `SKILL.md` files).
    Why it matters: Repeated idle checks could launch retries indefinitely or leave work stalled without an owner.
17. Q: Do risk-based triggers override the proof-of-concept profile’s default of no consultation?
    Story: special-role-calls-fire-when-needed
    Grounds: The story includes every First Officer on the route, while the package says “POC defaults to no consultation” (`kc-dev-flow-2/README.md`, “Authority and loading”).
    Why it matters: Profile precedence changes whether an early experiment with persistent consequences receives advice.
18. Q: When mandatory Production security review already covers a disputed security claim, what additional uncertainty warrants Engineering Reviewer?
    Story: special-role-calls-fire-when-needed
    Grounds: Engineering Reviewer includes material security uncertainty, while Production already requires security review during design and validation (`kc-dev-flow-2/skills/engineering-reviewer/SKILL.md`, `docs/adr/0019-prod-ideation-security-review-binds-design.md`, `docs/adr/0021-prod-validation-security-review-reaches-past-the-diff.md`).
    Why it matters: The answer determines whether overlapping reviews add assurance or repeat the same assessment.
19. Q: What standing Captain authorization and spending limit cover automatically triggered consultations?
    Story: special-role-calls-fire-when-needed
    Grounds: Both agents require Opus with `xhigh` reasoning, and architecture decision 0011 says money is never delegated (`kc-dev-flow-2/agents/chief-engineer.md`, `kc-dev-flow-2/agents/engineering-reviewer.md`, `docs/adr/0011-fo-decides-for-the-captain-by-a-delegation-ladder.md`).
    Why it matters: Automatic calls need a defined cost boundary without recurring permission questions.
20. Q: Which review materials must remain untrusted data when they are passed into an automatically triggered role?
    Story: special-role-calls-fire-when-needed
    Grounds: The Production security brief explicitly treats repository content as data, while the advisory-role briefs request contracts and primary evidence without the same explicit boundary (`kc-dev-flow-2/skills/validation/profiles/prod.md`, `kc-dev-flow-2/skills/engineering-reviewer/SKILL.md`).
    Why it matters: Review comments or artifacts could otherwise redirect the consultation or request unauthorized actions.
21. Q: Should deployment of this change surface existing unpaid consultation obligations on active tasks?
    Story: special-role-calls-fire-when-needed
    Grounds: The story measures gates since October 17; `pr_watch.entities()` scans active tasks and excludes archives (`kc-dev-flow-2/scripts/pr_watch.py`).
    Why it matters: A prospective rule and a backlog sweep create different immediate workloads and costs.
22. Q: Does acceptance require observed behavior in all four adopting repositories, or only a verified upstream package change?
    Story: special-role-calls-fire-when-needed
    Grounds: The story names four consumers, while the package requires adopted workflow copies and does not migrate projects automatically (`kc-dev-flow-2/README.md`, `kc-dev-flow-2/skills/maintain-flow/SKILL.md`).
    Why it matters: Publishing improved rules does not establish that existing First Officers receive them.
23. Q: Which missed-call examples and legitimate no-call examples must a fresh First Officer handle correctly before this story passes?
    Story: special-role-calls-fire-when-needed
    Grounds: `test_role_triggers.py` tests record syntax; maintenance requires fresh First Officer scenarios for orchestration rules, including a case where the rule must not apply (`kc-dev-flow-2/scripts/test_role_triggers.py`, `kc-dev-flow-2/skills/maintain-flow/SKILL.md`, “Behaviour replay”).
    Why it matters: Parser tests alone cannot demonstrate timely judgment or prevent unnecessary consultations.
