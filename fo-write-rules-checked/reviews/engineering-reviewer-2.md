# engineering-reviewer-2 (second read)

Reviewer: kc-dev-flow-2:engineering-reviewer, opus, 2026-10-20. Read-only. Design at state HEAD de8b6b6c (fold 86c82034, 72cf1b6b against 8eda9070); ADR 0023 at origin/main ad44f0cb; package kc-dev-flow-2 0.26.0.

Verdict: the fold meets my D1 conditions. It meets my D2/D3 conditions 1 to 4 and 6, and condition 5 as adapted. One of the additions opens a merge the Captain did not authorize, and one changes a flow he accepted without asking him. Each is a few lines to fix and does not need a redesign.

- The opening. At merge time, when his approved question has no `Merges:` line, the not-carried line now ends "To carry it, end the question with 'Merges: …'". Nothing re-checks an approved briefing against its recorded digest. So that instruction tells FO to make the one edit that would forge his grant: append the line to the briefing he already approved. The prototypes build their own cases exactly this way (they edit `index.json` after approval), and the check carries.
- The changed flow. A repair FO lands under his grant now leads to a second ask for the merge. The Delivery authority paragraph in the README still tells FO the opposite. That reversal appears only in D2's "worse" list, not in the question the Captain will approve.

Neither one weakens ADR 0023's head, CI, base or `--match-head-commit` holds. Every hold still runs before the last line.

```yaml
engineering_reviewer_report:
  question: "D1 fold: do the ideation-only Scope check and a baseline taken at the commit that added the newest amendment meet conditions (a)-(d), and do they open any authority path?"
  revision: "design at state de8b6b6c (fold 86c82034, 72cf1b6b vs 8eda9070); measure/proto_scope.py, proto-scope-fixtures-output.txt, replay-output-*.txt"
  conclusion: "Met. (a) The hold line is addressed to FO and tells a worker to report it. The stage gate goes further than I asked: it removes the check outside ideation entirely. That is acceptable and disclosed. The README rule still covers implementation, but nothing checks it there, which is no worse than today. (b) Restore comes first and an amendment needs his verbatim words, asserted by AC-12. (c) The baseline is the file at the amendment's commit. An edit after the amendment holds, whether a line was added or removed, and the old 'any amendment' rule is the mutation that turns that case green. (d) The claim is restated. D1 touches no merge or approval path."
  material_evidence:
    - "proto-scope-fixtures-output.txt: special-role-calls HOLD; ideation-gaps clean at cfa03ada; edit after amendment 1 HOLD (added and removed); Non-goals fill clean; uncommitted amendment 2 covers an uncommitted Scope line; status done -> not run; git-archive extraction -> not run."
    - "Window column (grep of the four replay-output files): ideation-gate-open 2 + 4 + 4 + 5 = 15 held; the 2 qnow validation-gate-open events are amended, not held. This confirms the worker's 15 of 15."
    - "Remaining bound, stated in the design: the newest amendment covers every earlier unrecorded edit, and the stage is read from FO-controlled frontmatter."
  risk_tradeoff: "Low risk and reversible. Cost: a Scope edit during implementation or validation goes unchecked (none observed)."
  recommendation: proceed
  confidence: high
  disproof_condition: "A Scope edit after the ideation gate that an observer finds unrecorded would reopen the stage gate."
  authority_boundary: "The Captain rules D1 at the ideation gate; FO owns amendment entries (ADR 0005)."
```

```yaml
engineering_reviewer_report:
  question: "D2/D3 fold and additions: Captain-only source, head binding, strict grammar, commit-time amendment rule, 「」 echo replacing conn_quote, the teaching clause, the no-quote guard, and a repair under grant being asked again. Do any of them open a merge he did not authorize or weaken ADR 0023?"
  revision: "design at de8b6b6c; measure/proto_gate.py (approved, merges, amended_after, next_line), carry_sim.py, proto-gate-output.txt; ADR 0023 at origin/main ad44f0cb; 0.26.0 references/sd/workflow.md § Delivery authority; Spacedock 0.27.2 gate --help and the gate-resolution-frontmatter-contract spec"
  conclusion: "Conditions 1-4 and 6 are met. Condition 5 is adapted, and soundly so. Two additions need changes before the gate. (i) The teaching clause on the merge-time no-line run, combined with no digest check on the approved briefing, opens a merge he did not authorize. (ii) Head binding changes the README's repair-under-grant flow without his ruling, and the README sentence as written still authorizes the merge that the script now asks about. My first report helped cause (ii): its condition 1 let an FO repair approval inherit his line, while its condition 2 bound the line to one head, and those conflict on a repaired head. I accept the worker's resolution, which is to ask again."
  material_evidence:
    - "Teaching clause at merge time: proto_gate.next_line appends \" To carry it, end the question with 'Merges: <pr> at <head>'.\" whenever why == 'no-line', and that includes after a Captain approval exists (AC-1 says so for the approved special-role-calls case). Nothing in the package verifies a briefing after `gate record`: grep for 'digest' over 0.26.0 scripts finds only learning.py. The Spacedock spec checks a changed briefing only 'before semantic decision recording'. with_line() edits the approved index.json in place and the check carries. Failure shape: he approves a question without the line; the check tells FO to end the question with the line; FO edits the approved briefing; the check carries and FO merges."
    - "Cheap close, measured: the resolution frontmatter records `briefing.digest` (the RFC 8785 JSON digest of the briefing). Recomputation (sorted compact JSON, sha256) matches 155 of 155 bound briefings in this state branch, with 0 mismatches. So approved() can read the question only when the digest matches, and fall back to an ask otherwise, without a false ask on record."
    - "Repair under grant (item 5). README § Delivery authority, 0.26.0: approval covers 'later external-review rounds on the same PR, merging the full head `delivery_gate.py check` passes', and 'a repair whose validation passes … is recorded by FO … and pushed to that PR's branch'. Under the design, head-differs is an ask line with exit code 0, so the README still authorizes the merge the script asks about. Cost measured: gh pr view on the 29 Captain approvals that name a head and a PR shows 28 merged at exactly the approved head. The 1 that differs is #652's first approval, superseded by his second approval at the merged head. So the worker's '0 such repairs' is correct, and the reversal costs nothing observed."
    - "Commit-time rule (item 2), recomputed: of the 34 approvals, 10 have an amendment dated on or after the approval day; 1 has an amendment committed after the approval `at` (#652, first approval). That confirms 1 against 10, with 9 differing. A briefing-sha anchor would false-ask names-check-before-dispatch (its amendment came after the briefing and before the approval, and was a Design-only ruling), so `at` is the better anchor. Bound: `at` is when FO ran `gate record`, which is sometimes 'after the fact', so an amendment FO commits between his chat reply and the record passes. The ADR must state this; the rule need not change."
    - "「」 spans (item 3), verified: 34 Captain approvals, 0 with conn_quote, 4 with no span. The Spacedock spec says 'A citation is refused on `person:captain` resolutions', and `gate --help` (0.27.2) agrees. Judgment: the spans are sound as a presentation guard but not as provenance. They sit in the same FO-written field as the #682 paraphrase that misreported #672, and FO could type 「合併 #672」. What the echo buys is narrower: the carried line prints only what FO claims he said, never what FO inferred, and it puts any hold or question of his in front of FO. The no-quote guard gives almost no protection, since FO can type 「准」, but it fails safe, and only 1 of the 4 no-span approvals is recent (prod-security-validation-gate, 10-17). Two consequences: the carried line's 'his words were' claims more than state proves; and spans are cut at 100 characters without notice, which could drop a hold at the end (0 of 34 exceed 22 characters, so refusing to cut costs nothing)."
    - "Grammar allows several refs (`ITEM(?:, ITEM)*`). It cannot carry the Release PR through a task's check, because delivery_gate binds the PR head to the task's dispatched Candidate. But a two-PR line is the stacking ADR 0023 D2 rejects, and no task has needed it."
    - "Approve then revise: approved() takes the newest Captain approve, not the newest Captain resolution. A later Captain revise of the same head would leave the older approve carrying. There are 0 such records. This is a possibility, not a defect."
  risk_tradeoff: "A wrong task-PR merge is hard to undo once release-please takes it. Fixes, all small: (1) print the teaching clause only on the ask run (no Captain approval yet), never on a not-carried merge run; (2) approved() reads the question only when the briefing digest matches the resolution's `briefing.digest`, otherwise an ask, with an AC-1 case 'approved index.json edited after the record -> ask' and the mutation 'no digest check -> carried'; (3) the D2 gate question names the repair-under-grant reversal, and either the README phrase 'the full head `delivery_gate.py check` passes' becomes '… carries' (one word for one, budget unchanged) or the ADR rules that the next: line governs; (4) AC-10 adds the stated bounds: `at` is FO's record time, the spans are FO's transcription, and the reversal itself. Non-blocking: one ref per line; reword 'his words were' to 'the recorded reason quotes him:'; no silent cut at 100 characters; optionally require the newest Captain resolution to be the approve. Cost of (1)-(4): about 10 script lines, 2 AC cases, 0 README words with the one-word swap."
  recommendation: adjust
  confidence: high
  disproof_condition: "Evidence that something re-verifies a briefing's digest before delivery_gate reads its question would retire finding (i). A recorded case of the Captain ruling that a repaired head may merge on his earlier approval would turn (ii) from a question for him into a design defect."
  authority_boundary: "The Captain rules D2 and D3, including the repair reversal, and keeps merge authority. FO owns the question and the record. delivery_gate.py keeps its hold function. This report merges nothing."
```

```yaml
engineering_reviewer_report:
  question: "D6 rewritten and D7 split out: is the premise now true, and does D7 describe a guard that would actually stop a `gh pr merge`?"
  revision: "design § Chain check, D6 and D7 at de8b6b6c; the first report's settings read (2026-10-20)"
  conclusion: "The D6 premise is now true and matches the first read: auto mode, no ask or deny rule, no allow rule for `gh pr merge`. Not re-read. The named-carry sentence prints on the carried run, which is the moment the #672 slip happened. One wording in D7 undercuts the guard: it would 'otherwise leave the decision to the permission prompt'. Under auto mode that is no stop. The guard must return `ask` to force a prompt, and the D7 task must first confirm that a hook's `ask` actually prompts under auto mode."
  material_evidence:
    - "#682 merged 03:03:16Z and #672 merged 03:07:06Z, both outside any record in state. D6 leaves the only observed rule-4 violation unreached on purpose, and says so."
  risk_tradeoff: "Accepting D6 is a risk call on a publish-class action. D7 costs one filed task. Without the `ask` wording, a guard that only defers would add nothing under auto mode."
  recommendation: escalate
  confidence: medium
  disproof_condition: "A test showing a PreToolUse hook's `ask` does not prompt under auto mode would mean D7 needs a `deny` route instead."
  authority_boundary: "The Captain accepts D6 and orders D7. This report files nothing."
```

What must still change before the ideation gate:

1. Teaching clause and digest check (D2, item 4): print the teaching clause only on the ask run, before any approval exists; `approved()` reads a question only from a briefing whose digest matches the resolution, so a changed briefing falls back to an ask. AC-1 cases for both, each with its mutation.
2. Repair under grant (D2, item 5): name the reversal in the D2 gate question itself; then either swap "passes" for "carries" in the Delivery authority sentence, or have the ADR rule that the `next:` line governs.
3. ADR bounded claims (AC-10): the amendment rule compares against the time FO recorded the approval; the 「」 spans are FO's transcription; the repair reversal.
4. D7 wording: the guard returns `ask`; it does not defer to the permission prompt.

Optional, not blocking: one ref per `Merges:` line; reword "his words were"; no silent 100-character cut; require the newest Captain resolution to be the approve.

Counts re-derived by the reviewer: 34 Captain approvals, 0 with `conn_quote`, 4 with no 「」 span; 1 amendment after the approval by commit time against 10 by date; 28 of 29 approvals merged at the approved head (exception: #652's superseded first approval); 15 of 15 Scope holds while the ideation gate was open; 155 of 155 briefing digests recompute and match.
