# 0027. FO-write rules are checked by the script FO already runs at the write

Date: 2026-10-20

## Status

Accepted

## Context

The batch-3 observers found four FO-write rules broken days after the write: a Captain ruling recorded before the question it settles (delivery-gate-settles-skipped-checks), a two-part finding declined with one part's reason (chat-only-evidence-observer-blind, special-role-calls-fire-when-needed), a Captain scope change after the backlog gate kept outside `## Captain amendments` (special-role-calls-fire-when-needed), and Release PR #672 merged on the approval of #682 (3m50s later, no task, no `delivery_gate.py` run). Spacedock 0.27.2 runs nothing when FO writes a task file, so each check sits at a script FO is already told to run (ADR 0014: prose-enforced until Spacedock gains a pre-write hook).

Measured as a replay over the committed state of four repositories (this workflow, subspace-relay, subspace-web, qnow; pins in the task's `## Design`): the 0.26.0 decline check held 3 of the 3 declined texts written after it merged although each carried reasons, because it read `( )` only and `e.g.` ended an item; the Scope check held 15 edits made after the backlog gate across the four repositories, all while the ideation gate was open, 9 of them recording a Captain ruling or his words and 6 not; the findings join held the one observed rule-2 violation that has F-numbered findings and none of the three other reports with F bullets. On this machine, read 2026-10-20 from `~/.claude/settings.json`, `permissions.defaultMode` is `auto` and no `allow`, `ask` or `deny` rule names `gh pr merge`, so no permission rule stops a merge deterministically.

## Decision

**Words:** 「要」 (D1), 「Ａ」 (D2, amendment 1 of the task), 「第九題要」 (D3), 「那就不做」 (D4, amendment 2), 「好」 (D5), 「可以」 (D6), 「好」 (D7, amendment 3) — Captain, 2026-10-20, chat, the batch-4 ideation sitting on fo-write-rules-checked.

**Options considered:**
- Rule 3 (D1): a Captain change to Scope between gates is an amendment, checked by `design_surfaces.py check` while `status: ideation`; the README says "between gates" (chosen); leave the 15 events unrecorded
- Rule 4 (D2): the `ASK` line gains "Every other PR, the Release PR included, is asked one at a time." and nothing reads the approved question (chosen); keep the cycle-2 `Merges:` line with head binding, a Captain-only read and a digest check — parked for the guard task
- Rule 4 (D3): the class line reads `class: <class> (verdict ask)` when the saved verdict is `ask`, so the carried-merge line printed on a verdict `ask` is visible (chosen); print the line only for verdict `merge`
- Rule 1 (D4): no check; the observer keeps reading it (chosen, replacing the four-verb phrase check); a phrase check on the follow-ups task
- Rule 2 (D5): read `[ ]` as well as `( )`, end no item at `e.g.` or `i.e.`, hold when declined items are fewer than the newest validation report's `- F<N> Deferred risk:` and `- F<N> Polish:` bullets, and ask validators for one bullet per finding and per part (chosen); parse fix only
- Rule 4 residual (D6): a merge of a PR with no task is outside every check, and this record states why (chosen); claim a stop that was not verified
- Guard (D7): file a task for a `PreToolUse` guard on `gh pr merge` that returns `ask`, covering Claude and Codex (Codex CLI 0.162.1 lists `hooks` as stable with `pre_tool_use`), whose first step is a POC proving the hook stops a merge on each host (chosen); design nothing here

**Recommended:** D1 yes, D2 narrow, D3 yes, D4 the phrase check, D5 all three parts, D6 yes, D7 yes. The Captain overrode D4: he chose no check, on FO's revised recommendation, because there is one case and matching words cannot stop that class of error.

The rule later work must follow: a first officer's write that an observer would otherwise find days later is checked by the script FO already runs at that write where a structured record exists. A Scope change after the backlog gate, found at the ideation gate, is restored or recorded as an amendment with his words and where he said them; a decline is counted against the validator's F-numbered findings; the `ASK` line tells FO that every other PR is asked one at a time. This record amends ADR 0005 (an amendment covers a change made between gates, not only during implementation or at a validation gate) and ADR 0025 (a reason may be in `[ ]`; the join). It records that ADR 0023's reopen condition, a merge landing on an approval whose question did not name it, fired on 2026-10-20 with #672, and ADR 0023's mechanism is unchanged.

## Consequences

Bounded claims, each with what it rests on:
- Rule 4 here is a sentence FO reads. No script reads the approved question, so a merge FO makes without running `delivery_gate.py check`, and any merge of a PR with no task (the Release PR, a learning PR), has no check. The premise is the settings read above; it holds for that machine on that date.
- Rule 1 is unchecked. Order cannot discriminate (24 of 24 follow-ups tasks that cite a task PR were filed before the approval they cite) and one case was observed. Reopen it as a read of a structured Captain-rulings field if one lands.
- The Scope check reads git history and the working copy, not what the Captain said in chat. An amendment covers every earlier unrecorded Scope edit, and the check cannot tell whether the amendment is about that edit or whether the words in it are his. It does not run outside `status: ideation`, so a Scope edit after the ideation gate is unchecked (none observed).
- The decline join sees only reports that state findings as F-numbered bullets; a half-reason inside one finding passes, and a stated reason is checked for presence, not truth (ADR 0025).
- Every merge run reads 13 more words, and the class line may carry `(verdict ask)`; a hold of the Scope check prints once, to FO.

Reopen if an observer finds one of rules 2 or 3 broken again with the check present and run, if Spacedock gains a pre-write hook, or when the guard task of D7 reports (if a hook's `ask` does not prompt under auto mode, its route is `deny`, a new question for the Captain).
