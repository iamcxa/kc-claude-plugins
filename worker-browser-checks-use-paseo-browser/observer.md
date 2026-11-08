# Observer report: worker-browser-checks-use-paseo-browser

Window: first commit of the task file (98f35d610, 2026-11-06) to STATE HEAD 5babe271c. RULES: docs/dev2/README.md (kc-dev-flow-2 0.35.0 sync, 04809c3c6). Package 0.35.0. PR iamcxa/kc-claude-plugins#810 read once with `gh pr view` (head fef21735308e7e807d04a93a5506de5284dde436, merged 2026-11-08T08:13:34Z as 4deaa2aa1).

Counts: violation 4, can't tell 4, ok 11, observed 1.

## Violations

violation | rule: "FO runs `python3 <package>/scripts/dispatch_records.py <task folder>` before committing and fixes each part it lists" (Stages, dispatch paragraph) | evidence: replaying `dispatch_records.py` on `git archive a113aa3e9` exits 1 with six lines, all on `engineering-reviewer-1.md` ("needs a 'Dispatched:' line with a full 40-character SHA", "needs a 'Model:' line", "needs a non-empty '## Checklist' section", "needs a non-empty '## Scope notes' section", "needs a 'Package root:' line...", "needs a scope-notes line naming main as the completion recipient"); the record was committed in a113aa3e9 (2026-11-08 11:26:53) and repaired in cc856a639 (13:14:45) after validation-2 reported it ("dispatch/validation-2-message-1.md: ... answering its report that the reviewer record lacks dispatch-record fields") (a113aa3e9, cc856a639)

violation | rule: "FO adds no words of its own and does not move or rewrite a criterion" (Captain amendments) | evidence: the commit that adds the Amendment 1 entry also rewrites AC-1, AC-2 and AC-4 in place under the same ids: removed "-**AC-1** The paseo extension's scope-note quote ends with the browser sentence, and the quote's first sentence is unchanged." and added "+**AC-1** The paseo extension's scope-note quote ends with the sentence `Before using Paseo's browser tools, read extensions/paseo/browser.md under your Package root.`"; same for AC-2 and AC-4; the `Superseded text:` blocks were added in the same commit. README gives the move and the fresh id to the worker; the worker renamed to AC-6/7/8 later in f5b4866b9 (a113aa3e9)

violation | rule: "Design: <optional: the design paragraph it overrides>" (Captain amendments, entry form) | evidence: "Design: 「保留四個限制的處理方法，加上「登入要人機驗證時算作有人在場、用 Paseo」，拿掉「沒人看著也預設 Paseo」」" is the replacement direction, word for word the recommendation inside the `Asked:` question, and does not occur in `## Design`; the Proposition paragraph there, "opens it in Paseo's browser tools (`mcp__paseo__browser_*`) unless the repository's own instructions name another tool", is unchanged at HEAD (a113aa3e9)

violation | rule: `role_triggers.py` prints a `next:` line (Observer, Read) | evidence: `python3 role_triggers.py STATE worker-browser-checks-use-paseo-browser --rev HEAD` printed "next: worker-browser-checks-use-paseo-browser has 2 validations with a Material or Needs decision finding and 1 replacing amendments: before the next step, answer: is what I am solving still the outcome first asked for; can this gap be tested now, or am I waiting; what breaks if this criterion or process is deleted?" (HEAD 5babe271c)

## Can't tell

can't tell | rule: "A Captain ruling is his reply to the question it settles, given after that question was put" and "When the Captain chooses differently from the recommendation, FO writes `Override: ...`" (FO steps: review findings) | evidence: for validation attempts 1 and 2 the question quoted in the resolution `reason` ("#810（工人做瀏覽器驗收預設用 Paseo 分頁）要怎麼處理？我改變建議了..." and "#810 的說明沒有規定...要怎麼處理？...") is not the question in that attempt's briefing (briefing-1 recommends "建議接受並合併"; his choice was `revise`; no `Override:` line, reason says "Recommendation: followed"). The revised questions' delivery and timing are in the host dialog and chat, outside state (aa6670bdd, review/validation/briefing-1 and briefing-2)

can't tell | rule: "FO adds no words of its own" (Captain amendments) | evidence: the `Asked:` line ends "Option chosen: 「照建議改（建議）」 — 「先請獨立審查者確認，再退回實作修改；#810 這輪不合併」"; the words after the dash occur only in this entry. If they are the dialog's option description, the source is the host dialog, outside state (a113aa3e9)

can't tell | rule: "FO runs `python3 <package>/scripts/delivery_gate.py check` before the merge ask" (Delivery authority) | evidence: files for the asked heads exist, but each is later than the commit that added its briefing. ask-2.json: head "fef21735308e7e807d04a93a5506de5284dde436", time 2026-11-08T05:22:46Z; briefing-2 added at 8cb0fc8b1, 05:21:42Z. ask-1.json: head "90192bb64db4614de9a7a94cc782ee5fa44748db", time 02:58:59Z; briefing-1 added at 1ee493daa, 02:58:52Z. No file postdates the approval at 2026-11-08T08:13:28Z; the post-approval run before merging leaves no record I can find (PR merged 08:13:34Z at the same head, read from GitHub). The files cannot show whether FO ran the check before presenting

can't tell | rule: "After each worker report, before advancing or preparing its gate, FO runs `python3 <package>/scripts/dispatch_records.py --coverage <task> --stage <stage>`" (Stages) | evidence: a shell run leaves no record; replay at HEAD with the task file exits 0 for ideation, implementation and validation ("dispatch coverage complete: validation"), and `dispatch_records.py <task folder>` now exits 0 ("9 dispatch record(s) complete") (HEAD)

## Ok

ok | rule: "FO runs `python3 <package>/scripts/design_surfaces.py check --seed <task>`" (backlog) | evidence: replay at the briefing's sha 416271a92 exits 0, "seed fields and FO alignment recorded" (ef76e28f4)

ok | rule: "FO runs `python3 <package>/scripts/design_surfaces.py check`" (ideation) | evidence: replay at 575534bf5 exits 0, "design surfaces presentable"; second line "scope check not run: not in a git checkout" is replay-copy only (01ecc7500)

ok | rule: "FO confirms both goal sufficiency and minimal necessity" (validation) | evidence: ask-2.json `sufficiency`: "the paseo extension's dispatch quote now ends with a pointer read only before using Paseo's browser tools, and the 228-word guide sends attended pages and logins..."; `necessity`: "only kc-dev-flow-2/extensions/paseo/EXTENSION.md and kc-dev-flow-2/extensions/paseo/browser.md differ from the merge base (validation cycle-2 report, Astra, 2026-11-08)." ask-1.json holds both keys too (93b9ac629)

ok | rule: Captain ruling quotes his words and answers a question put before it, backlog and ideation (FO steps: review findings) | evidence: reasons quote 「核准（建議）」 and the question equal to the briefing's question; the ideation question says "核准即接受每張設計對其決定寫下的建議", so the approval-accepts-recommendation sentence is present (aa6670bdd precursor rows bb343a888, e0033a889)

ok | rule: "His plain approval accepts that recommendation only when the gate question says so" (FO steps: review findings) | evidence: validation-2 question names the merge, the full head and "Approval also covers later external-review rounds on this PR, unless he says he merges or holds"; his reason quotes 「合併，另開任務（建議）」; the PR merged 6 s after the resolution at head fef21735, matching `--match-head-commit` (5babe271c)

ok | rule: "FO records the alignment result as a `Result:` line before dispatching the worker" (ideation) | evidence: "Result: aligned at backlog..." added in 82ba380c3 (2026-11-07 16:10:44); `dispatch/ideation-1.md` added in e317d3dca (16:11:08)

ok | rule: "for validation a `Candidate: <full head SHA>` line per head validated" (Stages) | evidence: "Candidate: 90192bb64db4614de9a7a94cc782ee5fa44748db" in validation-1.md; "Candidate: fef21735308e7e807d04a93a5506de5284dde436" in validation-2.md (ae29228f6 / ff16ee3de)

ok | rule: "FO names the amendment in the next dispatch's checklist" (Captain amendments) | evidence: implementation-1-message-2.md item 1: "read `## Captain amendments` Amendment 1 and the replaced AC-1, AC-2 and AC-4" (57029de15); validation-2.md: "Judge Captain amendment 1" (ff16ee3de)

ok | rule: "FO runs the stage's minimal acceptance script under Captain steps, names its record on the summary's `Captain steps:` line" (validation) | evidence: briefing-1 "Captain steps: .../captain-steps/1.md" and briefing-2 ".../captain-steps/2.md"; 2.md step 1 "Ran: env -i bash --noprofile --norc ... 2026-11-08T05:19:00Z, exit 0" (1ee493daa, 8cb0fc8b1)

ok | rule: "FO counts rounds and records the count in the committed gate summary" and "A merge ask names each listed reviewer that was not read" (FO steps: review findings, Extensions) | evidence: briefing-1 "External rounds: 1."; briefing-2 "External rounds: 2." and "copilot not run: ... answer=review:5816743305" with `review/copilot-not-run.txt` (1ee493daa, 8cb0fc8b1)

ok | rule: where `peers` is listed, no Captain ruling quotes a peer in place of his words (Observer, Read) | evidence: the four resolution reasons quote only his dialog choices; the Scope relay "(Paseo 519ab4c8, 2026-11-06, relayed, confirmed here by his 「開」)" is a Scope source, not a ruling (98f35d610)

## Observed

observed | `Reviewer:` line | evidence: "Reviewer: kc-dev-flow-2:engineering-reviewer gpt-6-astra 2026-11-08 — (Codex via Paseo, xhigh) ... Captain amendment 1 followed it." added in 6e5e12439 (13:22:20); triggers: ideation ran on claude-opus-5-5 (dispatch/ideation-1.md), validation sent back once, Surfaces none. Order in state: revise resolution 2026-11-08T03:17:59Z (11:17:59 +0800), reviewer record and Amendment 1 entry both in a113aa3e9 (11:26:53)

## Coverage

Read fully: the task file at HEAD (frontmatter, Scope, Design headings, Acceptance criteria, Captain amendments, all five stage reports), the four ledger rows, both validation briefings and the backlog and ideation briefing summaries, ask-1.json and ask-2.json, captain-steps/2.md, dispatch records ideation-1, validation-1, validation-2, implementation-1-message-2, validation-2-message-1, engineering-reviewer-1, and the README sections for the checks above. Diffs read for a113aa3e9, f5b4866b9, aa6670bdd and 1ee493daa. Sampled: the other dispatch records (checked by script, not read), captain-steps/1.md (listed, not read), review/engineering-reviewer-1.md (not read; content out of scope), worker reports and evidence logs (not judged). Not evaluated: the chat-only rules; `delivery_gate.py steps` (needs the message text, not in state); no `Precedent:`, `Override:` or `### FO declines` entries exist in the window, so those rules are not listed.
