Observer report: task `fo-tries-what-it-asks-the-captain` (archived), window 321e1d763..79fb4abf3 (38 task-path commits). Scripts: candidate `decision_ledger.py` and `design_surfaces.py` (both differ from the installed 0.35.0 copies); `role_triggers.py` is identical in both.

Captain-gate-answer comparison rows (candidate rule: "compare its reason with its bound question using `decision_ledger.quotes_bound_question`", Read). `quotes_bound_question` returned False for all three. Its needle is `answering 「` + question + `」`, and every bound question already carries its own outer 「」.

violation | rule: "`answering 「` + the whole question + `」` must occur in the reason after removing all whitespace" (Read) | evidence: backlog reason "answering the batch 13 sitting 「決定：這批七張…要改哪張直接說。」"; bound question "「決定：這批七張…要改哪張直接說。」". The question text matches in full. The helper's needle "answering 「「決定" and the reason's "answering the batch 13 sitting 「決定" do not match, because the reason has "the batch 13 sitting" after "answering" and a single bracket. (c88c7ed6d)

violation | same rule | evidence: ideation reason quotes "answering 「決定：七張設計照建議進實作，但驗收到期提醒的 D7 改成…，可以嗎？」". Bound question is "「決定：七張設計都照各自寫下的建議進實作嗎（含 A 的 D1…）？要改哪件直接說。」 Approving accepts every recommendation each design states for its decisions." These are different questions. (89877bda6)

violation | same rule | evidence: validation reason ends "answering 「決定：照順序合併 #771、#772、#773 嗎？（#769、#770、#774、#775、#777 這次不合併）」". The bound question continues "Regular merges with --match-head-commit … Approval also covers later external-review rounds on these PRs, unless he says he merges or holds." The reason omits that tail. (be2fffa25)

Other findings:

can't tell | rule: "His plain approval accepts that recommendation only when the gate question says so" (Review-finding disposition) | evidence: the bound ideation question has "Approving accepts every recommendation…", but the reason records him answering a different question that lacks the sentence (89877bda6). Which question he saw is chat, outside state.

can't tell | rule: "When the Captain chooses differently from the recommendation, FO writes `Override: recommended <option>; …`" | evidence: ideation reason says "with the stated change to release-walk-due-trigger D7", with no `Override:` line (ledger `override: null`). The changed design belongs to another task, so this task's state cannot show whether his choice here differed.

violation | rule: "From round 3 a finding that is neither does not start a repair cycle: FO declines it in the committed gate summary, naming the finding, and files it as a new backlog task with `spacedock new` … or names the backlog task that already holds it" (FO steps: review findings, step 5) | evidence: "External rounds: 6." … "Declined: Polish, Codex round 6 P2 comment 4457041237: a path an acceptance step deliberately removes is held as missing" names no backlog task; `git grep 4457041237` at TO finds only observer.md and this briefing. (5ef7c2cc7)

violation | rule: "FO may explicitly decline evidenced Deferred risk or Polish … naming the finding, reason, candidate revision and the lines or evidence it rests on" (step 2) | evidence: the three `Declined:` lines name finding and reason, and the briefing summary holds no candidate head (`128fe3e3f` absent from it). (5ef7c2cc7)

ok | rule: "FO appends one entry per amendment … `Captain: 「<his words, verbatim>」 (where he said them)` / `Asked:` / `Supersedes:`" (Captain amendments) | evidence: "### Amendment 1 — 2026-11-04, chat / Captain: 「准」 (chat, 2026-11-04) / Asked: 「決定：#773 的 F2、F3 豁免…可以嗎？」 / Supersedes: none". It precedes the validation-2 dispatch that cites it. (8de6f7b8f, a1ee8e7a0)

ok | rule: "FO records the alignment result as a `Result:` line before dispatching the worker" (`ideation`) | evidence: "Result: aligned at backlog: …" added 15:46:56; ideation-1 dispatch file added 15:47:36. (3c89f6d8f, 7be72c4a4)

ok | rule: "FO reserves the number when it dispatches implementation (Number guards)" (FO steps: decision records) | evidence: "ADR: 0054" added 18:20:13; implementation entry dispatch commit 18:21:32. (dd680804f, cafedb79a)

ok | rule: "FO runs `python3 <package>/scripts/design_surfaces.py check`" | evidence: backlog copy at e01a80171 (`--seed`) exit 0, "seed fields and FO alignment recorded"; ideation copy at 2395ab628 exit 0, "design surfaces presentable".

ok | rule: "FO runs `python3 <package>/scripts/delivery_gate.py check` before the merge ask" | evidence: `merge/ask-1.json` time "2026-11-03T18:13:01Z", head "128fe3e3fed70fa64ded8657f5a1b36933af3ced"; briefing commit 5ef7c2cc7 at 18:13:21Z. The question names no head, so the head is matched to the validation-2 PASSED candidate.

ok | rule: "FO confirms both goal sufficiency and minimal necessity" | evidence: ask-1.json holds `sufficiency` "`delivery_gate.py steps` and `question` hold an ask whose fenced commands…" and `necessity` "the changed files are delivery_gate.py and its tests…".

ok | rule: "A merge ask names each listed reviewer that was not read" / "second reviewer: <name> because <trigger>" (Extensions) | evidence: "copilot not run: …" and "Second reviewer: Copilot because the PR changes merge or review rules." (5ef7c2cc7)

ok | rule: the `peers` check: no Captain ruling quotes a peer's words | evidence: Scope marks the peer-relayed quote "(relayed, not a ruling in this session)". All three gate reasons carry the Captain's own 「進」, 「可以」, 「可以」.

observed | rule: `Reviewer:` line record (`Surfaces: none`; ideation ran on `claude-opus-5-5` by Captain choice; validation sent back once) | evidence: two `Reviewer:` lines, chief-engineer and engineering-reviewer, both "opus 2026-11-03".

ok | rule: `role_triggers.py STATE TASK --rev TO` | evidence: "role triggers: 1 event(s) read … each with a call or a waiver." No `next:` lines.

can't tell | rule: "FO runs `python3 <package>/scripts/delivery_gate.py question …` before the validation `gate prepare`" | evidence: the shell run leaves no record.

Coverage: Read in full: gate entries and ledger rows; the three briefing `index.json` files; `merge/ask-1.json`; the Captain amendments, Needs decision and FO alignment sections; the README sections Captain amendments, Review-finding disposition, FO steps, Delivery authority, Extensions and Batch gates. Sampled: the 727-line task body (stage reports, PRFAQ), the dispatch files `ideation-1` and `validation-1`/`validation-2`, and the 38-commit log by subject and time. Not read: the validation-1/validation-2 evidence trees, `observer.md`, and the other review files. Not evaluated: the README "Captain steps" section, which this task's own PR introduced after the window; the chat-only rules; Precedent (the task has no `Precedent:` line). The ledger and design replays ran on copies exported at TO, with no write to STATE.
