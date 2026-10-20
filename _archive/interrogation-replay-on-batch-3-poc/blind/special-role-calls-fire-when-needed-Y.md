1. Q: Which judgment-based triggers must create an owed consultation even when the script reports zero events?
   Story: special-role-calls-fire-when-needed
   Grounds: The role skills list circling, conflicting evidence and material uncertainty, while `check()` recognizes only cycles and amendment fields (`kc-dev-flow-2/scripts/role_triggers.py`).
   Why it matters: This determines which existing guidance becomes an obligation.
2. Q: Before which action must an owed consultation finish: another repair, gate presentation, or delivery?
   Story: special-role-calls-fire-when-needed
   Grounds: The startup and idle hooks process printed actions, but `delivery_gate.py` lists no special-role consultation prerequisite (`kc-dev-flow-2/references/sd/mods/kc-dev-flow-2.md`; `kc-dev-flow-2/scripts/delivery_gate.py`).
   Why it matters: A consultation after the consequential action cannot influence that decision.
3. Q: When repeated repairs reveal both unclear sequencing and a disputed technical claim, does the work owe one role or both?
   Story: special-role-calls-fire-when-needed
   Grounds: Chief Engineer covers “blocked or repeatedly circling”; Engineering Reviewer covers conflicting material evidence (`kc-dev-flow-2/skills/chief-engineer/SKILL.md`; `kc-dev-flow-2/skills/engineering-reviewer/SKILL.md`).
   Why it matters: Overlapping triggers otherwise leave routing and consultation cost undecided.
4. Q: Should repeated new gaps in the same file trigger consultation even when each finding is below the threshold for another repair?
   Story: special-role-calls-fire-when-needed
   Grounds: The story names “two or more review rounds finding new gaps,” while the workflow defers non-Material, non-P1 findings from round three (`kc-dev-flow-2/references/sd/workflow.md`, “FO steps: review findings”).
   Why it matters: The new trigger could otherwise bypass the accepted rule that stops repair rounds.
5. Q: Does every change to merge, authority or irreversible-action rules owe an Engineering Reviewer call, or only changes with a disputed claim or material uncertainty?
   Story: special-role-calls-fire-when-needed
   Grounds: The story names these rule changes as missed calls; the Engineering Reviewer trigger list qualifies most technical decisions by uncertainty or conflicting evidence (`kc-dev-flow-2/skills/engineering-reviewer/SKILL.md`).
   Why it matters: This separates a categorical trigger from a judgment-based one.
6. Q: Must a proposed design that reverses an earlier Captain ruling trigger consultation before approval, even though it is not yet a Captain amendment?
   Story: special-role-calls-fire-when-needed
   Grounds: The story includes “a design or amendment reversing an earlier Captain ruling”; the workflow excludes changes requested while the accepting gate remains open from amendments (`kc-dev-flow-2/references/sd/workflow.md`, “Captain amendments”).
   Why it matters: Amendment-only detection would miss reversals during design.
7. Q: Who may waive a required consultation, and can a waiver recorded after merge discharge an obligation that existed before merge?
   Story: special-role-calls-fire-when-needed
   Grounds: `cleared()` accepts any nonblank waiver reason without checking its author or date; the story identifies a Chief Engineer call “waived after the merge” (`kc-dev-flow-2/scripts/role_triggers.py`).
   Why it matters: Waiver authority determines whether required consultation can be silently bypassed.
8. Q: Which review events count toward a circling trigger when external-review rounds, validation returns and Stage Report cycles describe different sequences?
   Story: special-role-calls-fire-when-needed
   Grounds: `events()` reads only `- Cycle N` under `### Feedback Cycles`, while the story reports `## Stage Report: ... (cycle N)` and the workflow separately defines external-review rounds (`kc-dev-flow-2/scripts/role_triggers.py`; `kc-dev-flow-2/references/sd/workflow.md`).
   Why it matters: Different counters could trigger consultation at different times or count one event twice.
9. Q: When the script finds no recognized cycle or amendment structure, should it report no obligation or insufficient evidence?
   Story: special-role-calls-fire-when-needed
   Grounds: `check()` returns success with “0 event(s) read”; the story says some repositories lack the structures it recognizes (`kc-dev-flow-2/scripts/role_triggers.py`).
   Why it matters: Missing evidence currently looks like a clean result.
10. Q: Should equivalent existing consultation records count when they say “third repair cycle” or appear outside `## FO alignment`?
    Story: special-role-calls-fire-when-needed
    Grounds: `cleared()` requires the literal `Cycle 3` token and `alignment()` restricts record location; the story identifies completed calls missed for both reasons (`kc-dev-flow-2/scripts/role_triggers.py`).
    Why it matters: Compatibility rules determine whether rollout produces unnecessary repeat calls.
11. Q: What evidence must establish that consultation actually occurred beyond a correctly formatted `Reviewer:` line?
    Story: special-role-calls-fire-when-needed
    Grounds: `cleared()` accepts a model token, date and question without reading a response, while Engineering Reviewer returns a revision-bound assessment (`kc-dev-flow-2/scripts/role_triggers.py`; `kc-dev-flow-2/skills/engineering-reviewer/SKILL.md`).
    Why it matters: Recording an intention to consult must not accidentally satisfy the story’s promise that a call fires.
12. Q: What change makes an earlier consultation expire and require another call?
    Story: special-role-calls-fire-when-needed
    Grounds: One `Cycle 3` record clears every later cycle, and amendment calls are matched by number and calendar date rather than assessed revision (`kc-dev-flow-2/scripts/role_triggers.py`, `check()` and `cleared()`).
    Why it matters: New evidence or changed work could otherwise remain covered by stale advice.
13. Q: If two First Officer sessions observe the same obligation before either records completion, may both dispatch the role?
    Story: special-role-calls-fire-when-needed
    Grounds: `tasks()` emits consultation instructions on every scan, and its test expects repetition until a record appears (`kc-dev-flow-2/scripts/pr_watch.py`; `kc-dev-flow-2/scripts/test_pr_watch.py`).
    Why it matters: Concurrent sessions could create duplicate expense and conflicting advice.
14. Q: Which judgment-based triggers override the proof-of-concept profile’s default of no consultation?
    Story: special-role-calls-fire-when-needed
    Grounds: The package says “POC defaults to no consultation,” while the role skills include circling and material technical uncertainty without a profile exemption (`kc-dev-flow-2/README.md`; `kc-dev-flow-2/skills/chief-engineer/SKILL.md`; `kc-dev-flow-2/skills/engineering-reviewer/SKILL.md`).
    Why it matters: Profile handling changes both coverage and the amount of process imposed on exploratory work.
15. Q: Must consultation dispatches receive the adopter’s `Dispatch facts`, including secret-access restrictions, just as stage workers do?
    Story: special-role-calls-fire-when-needed
    Grounds: Stage `context-sections` include `Dispatch facts`, but the role agents do not specify that input; secret enforcement belongs to the adopter (`kc-dev-flow-2/references/sd/workflow.md`; `kc-dev-flow-2/agents/chief-engineer.md`; `kc-dev-flow-2/agents/engineering-reviewer.md`; `docs/adr/0003-secret-reads-are-enforced-by-the-adopter.md`).
    Why it matters: Automatically recruited roles need the applicable evidence-access boundaries.
16. Q: What should the First Officer do when a required consultation cannot start or returns no usable answer?
    Story: special-role-calls-fire-when-needed
    Grounds: Both roles require their declared model and reasoning, while `owed_line()` offers dispatch or waiver without a failure or retry policy (`kc-dev-flow-2/agents/chief-engineer.md`; `kc-dev-flow-2/agents/engineering-reviewer.md`; `kc-dev-flow-2/scripts/role_triggers.py`).
    Why it matters: An unavailable role could otherwise cause repeated dispatches, indefinite delay or an unjustified waiver.
17. Q: What added consultation cost and delivery delay must this story stay within?
    Story: special-role-calls-fire-when-needed
    Grounds: Both agents require Opus with `xhigh` reasoning, and the recorded fixture states “Opus cost per owed call is not measured” (`kc-dev-flow-2/agents/chief-engineer.md`; `kc-dev-flow-2/agents/engineering-reviewer.md`; `kc-dev-flow-2/scripts/test_delivery_gate.py`, `DECLINES['special-role-triggers']`).
    Why it matters: Broader triggers introduce an ongoing cost whose acceptable boundary is unspecified.
18. Q: Do the new obligations apply to existing active tasks, archived tasks, or only events after adoption?
    Story: special-role-calls-fire-when-needed
    Grounds: The idle scanner excludes `_archive`, while Observer checks archived tasks for owed calls (`kc-dev-flow-2/scripts/pr_watch.py`, `entities()`; `kc-dev-flow-2/skills/observer/SKILL.md`).
    Why it matters: Activation scope determines whether historical misses become current work.
19. Q: Does completion require verified behavior in all four named repositories, including their existing workflow copies, or only a package release?
    Story: special-role-calls-fire-when-needed
    Grounds: The story names every First Officer in four repositories as consumers; adoption requires a per-adopter workflow merge and does not automatically rewrite existing workflows (`kc-dev-flow-2/references/sd/adoption.md`).
    Why it matters: Package delivery alone does not establish that consumers receive the changed behavior.
20. Q: Which reported missed calls and legitimate no-call cases must become acceptance cases?
    Story: special-role-calls-fire-when-needed
    Grounds: The story cites reports in `fo-batch-sittings/dogfood/`, absent from this snapshot, while current tests construct cycle and amendment fixtures (`kc-dev-flow-2/scripts/test_role_triggers.py`).
    Why it matters: The expected outcomes need primary evidence rather than reproducing the helper’s existing assumptions.
21. Q: Must acceptance observe actual consultation dispatch in both Claude and Codex hosts, or is a First Officer’s scenario answer sufficient?
    Story: special-role-calls-fire-when-needed
    Grounds: Maintenance requires fresh First Officer scenarios for orchestration rules, while the README explicitly leaves actual host resolution needing a separate behavioral test (`kc-dev-flow-2/skills/maintain-flow/SKILL.md`; `kc-dev-flow-2/README.md`).
    Why it matters: Recognizing when to call a role does not prove the intended role actually runs.
