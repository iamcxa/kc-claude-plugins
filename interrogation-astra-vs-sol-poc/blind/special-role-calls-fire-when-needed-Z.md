1. Q: Before which action must a needed consultation finish, and does an unanswered consultation stop that action?
   Story: special-role-calls-fire-when-needed
   Grounds: `pr_watch.tasks()` emits consultation instructions during startup or idle in `kc-dev-flow-2/scripts/pr_watch.py`; `kc-dev-flow-2/README.md` says neither role is “a routine gate.”
   Why it matters: A reminder that arrives after implementation or merge would not prevent the failures described.
2. Q: What evidence should establish that a design reverses an earlier Captain ruling when neither `Supersedes:` nor `Design:` names the replacement?
   Story: special-role-calls-fire-when-needed
   Grounds: The story names “a design or amendment reversing an earlier Captain ruling”; `events()` in `kc-dev-flow-2/scripts/role_triggers.py` recognizes only particular amendment fields.
   Why it matters: Detecting an unrecorded reversal requires a comparison against prior decisions, beyond recognizing new text.
3. Q: What distinguishes repeated findings that require consultation from unrelated findings that happen to concern the same file?
   Story: special-role-calls-fire-when-needed
   Grounds: The story identifies “two or more review rounds finding new gaps in one file or sentence”; `kc-dev-flow-2/skills/chief-engineer/SKILL.md` names work “repeatedly circling.”
   Why it matters: File overlap alone could summon advisers for ordinary review while missing one underlying problem spread across files.
4. Q: When repeated repairs also expose a contested technical claim, should both roles be called or should one consultation determine whether the other is needed?
   Story: special-role-calls-fire-when-needed
   Grounds: `kc-dev-flow-2/skills/chief-engineer/SKILL.md` covers circling work, while `kc-dev-flow-2/skills/engineering-reviewer/SKILL.md` covers conflicting evidence on material claims.
   Why it matters: Both triggers can apply to the same incident, changing dispatch order, delay and cost.
5. Q: Which consultation obligations may the First Officer waive without a Captain decision?
   Story: special-role-calls-fire-when-needed
   Grounds: `owed_line()` offers “if you will not” record a waiver, and `cleared()` accepts any nonblank reason in `kc-dev-flow-2/scripts/role_triggers.py`.
   Why it matters: Unrestricted waivers could preserve the reported absence of calls while making every check pass.
6. Q: What evidence must exist before a consultation counts as completed rather than merely requested?
   Story: special-role-calls-fire-when-needed
   Grounds: `cleared()` in `kc-dev-flow-2/scripts/role_triggers.py` accepts a `Reviewer:` line containing an agent, model, date and question without reading a response.
   Why it matters: Recording an intended call currently satisfies the same check as receiving usable advice.
7. Q: Which changes to the reviewed artifact or decision invalidate an earlier consultation?
   Story: special-role-calls-fire-when-needed
   Grounds: The engineering-reviewer report includes an exact `revision` in `kc-dev-flow-2/skills/engineering-reviewer/SKILL.md`, but `cleared()` checks only the amendment token and calendar date.
   Why it matters: Advice about an earlier version could clear an obligation after the relevant claim has changed.
8. Q: What new evidence should require another chief-engineer consultation after an earlier call has been satisfied?
   Story: special-role-calls-fire-when-needed
   Grounds: `check()` in `kc-dev-flow-2/scripts/role_triggers.py` collapses every cycle numbered three or higher into one obligation cleared by `Cycle 3`.
   Why it matters: One early call currently suppresses further calls even if repairs continue or a different blocker emerges.
9. Q: How should a resumed or concurrent First Officer distinguish an unanswered consultation already running from one that still needs dispatch?
   Story: special-role-calls-fire-when-needed
   Grounds: `pr_watch.tasks()` repeats owed instructions, while `cleared()` in `kc-dev-flow-2/scripts/role_triggers.py` recognizes completed-call text or waivers but no pending state.
   Why it matters: Recovery can otherwise duplicate expensive calls or treat a lost call as completed.
10. Q: When stage reports, feedback-cycle entries and external-review verdicts describe the same work, what constitutes one consultation-triggering round?
    Story: special-role-calls-fire-when-needed
    Grounds: The story contrasts `Stage Report: ... (cycle N)` with `- Cycle N`; `kc-dev-flow-2/references/sd/workflow.md` separately defines a round as an external reviewer’s verdict.
    Why it matters: Combining these sources without deciding their relationship could double-count repairs or miss repeated reviews.
11. Q: Should an unrecognized or missing event format mean no consultation is needed, or that the need cannot be determined?
    Story: special-role-calls-fire-when-needed
    Grounds: `events()` and `check()` in `kc-dev-flow-2/scripts/role_triggers.py` return success with zero recognized events; the story reports this outcome for two repositories.
    Why it matters: Successful parsing and absence of evidence currently produce the same reassuring result.
12. Q: Must existing calls written as “third repair cycle” or under another heading satisfy their obligations without rewriting historical records?
    Story: special-role-calls-fire-when-needed
    Grounds: The story reports genuine calls rejected for wording or placement; `test_each_near_miss_leaves_the_event_owed()` and `test_only_the_fo_alignment_section_can_clear_an_event()` in `kc-dev-flow-2/scripts/test_role_triggers.py` enforce those restrictions.
    Why it matters: Compatibility determines whether adoption recognizes earlier work or creates duplicate consultation requests.
13. Q: How should a newly recognized consultation obligation be handled when the relevant action has already merged or the task is archived?
    Story: special-role-calls-fire-when-needed
    Grounds: The story includes a consultation “waived after the merge”; `test_an_archived_task_owing_a_role_call_prints_nothing()` in `kc-dev-flow-2/scripts/test_pr_watch.py` explicitly excludes archived work.
    Why it matters: Retrospective accounting and advice that can still change an outcome require different behavior.
14. Q: Which new triggers override the proof-of-concept profile’s default of no consultation?
    Story: special-role-calls-fire-when-needed
    Grounds: `kc-dev-flow-2/README.md` says “POC defaults to no consultation,” while `check()` in `kc-dev-flow-2/scripts/role_triggers.py` does not inspect the profile.
    Why it matters: Applying every trigger uniformly could add obligations to a deliberately lighter route.
15. Q: What ensures a freshly dispatched adviser receives the adopter’s secret-access restrictions before its first tool call?
    Story: special-role-calls-fire-when-needed
    Grounds: `docs/adr/0003-secret-reads-are-enforced-by-the-adopter.md` records two secret leaks despite written bans; the role wrappers in `kc-dev-flow-2/agents/` invoke their skills without naming the workflow’s `Dispatch facts`.
    Why it matters: More automatic consultations create more execution contexts that need the existing permission boundary.
16. Q: What may continue when a required role cannot run on its declared model and reasoning level?
    Story: special-role-calls-fire-when-needed
    Grounds: `kc-dev-flow-2/references/sd/workflow.md` requires the roles’ declared settings, “never a cheaper one”; `owed_line()` in `kc-dev-flow-2/scripts/role_triggers.py` offers dispatch or waiver without distinguishing unavailability.
    Why it matters: Runtime failure needs a defined outcome without silently weakening the role or blocking unrelated work.
17. Q: What consultation spending or elapsed-time limit should return the decision to the Captain?
    Story: special-role-calls-fire-when-needed
    Grounds: Both role agents declare `model: opus` and `reasoning: xhigh`; `kc-dev-flow-2/references/sd/workflow.md` requires preserving the approved budget and stop condition.
    Why it matters: Broader triggers can consume the task’s budget even when each individual call is justified.
18. Q: Must the new behavior work for adopters using the previous workflow instructions, or is an approved workflow update required before it applies?
    Story: special-role-calls-fire-when-needed
    Grounds: The story names every adopting First Officer as a consumer; `kc-dev-flow-2/skills/maintain-flow/SKILL.md` requires new First Officer steps to surface through scripts the previous release already invokes.
    Why it matters: Publishing changed instructions does not establish that existing sessions will encounter or follow them.
19. Q: Which judgment-based missed calls should become observer violations rather than observations?
    Story: special-role-calls-fire-when-needed
    Grounds: `kc-dev-flow-2/skills/observer/SKILL.md` treats missing `Reviewer:` lines for stronger-model ideation or twice-rejected validation as “observed,” but treats script-reported obligations as “violation.”
    Why it matters: The story’s broader meaning of “needed” must align with how compliance is assessed.
20. Q: Which reported incidents and ordinary-work counterexamples must a fresh First Officer handle correctly before this story is accepted?
    Story: special-role-calls-fire-when-needed
    Grounds: The story cites reports in `fo-batch-sittings/dogfood/`, which is absent from this snapshot; `kc-dev-flow-2/skills/maintain-flow/SKILL.md` requires First Officer scenarios including one where the rule must not apply.
    Why it matters: Parser tests cannot demonstrate that appropriate calls actually happen, and the cited incidents need primary evidence before becoming acceptance cases.
