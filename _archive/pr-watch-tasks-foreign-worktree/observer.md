For `pr-watch-tasks-foreign-worktree` (foreign-worktree watcher repair), both Captain resolutions lack the required recommendation declaration; merge coverage remains unverified.

```ui
Card("Independent observer report", [
  Findings([{severity: "medium", title: "violation | Missing recommendation declarations", detail: "Rule: “Otherwise the reason carries Recommendation: followed.” (FO steps: review findings). Evidence: “absent” in both Captain resolution reasons; neither contains Override either (backlog 5465d22ee; validation 97cafa6da)."}]),
  Text("ok | rule: “A Captain ruling is his reply to the question it settles” (FO steps: review findings) | evidence: backlog question “獨立審查說原本的合約不能直接跑” matches reason “answering 「獨立審查說原本的合約不能直接跑”; full whitespace-normalized comparison passes (5465d22ee)."),
  Text("ok | rule: “A Captain ruling is his reply to the question it settles” (FO steps: review findings) | evidence: validation question “決定：合併 #858” matches reason “answering 「決定：合併 #858”; full comparison, including nested quotation marks, passes (97cafa6da)."),
  Text("ok | rule: “FO records the choice” (backlog) | evidence: First Officer’s delegated ideation resolution records “quote: 五張都准，授權代記設計關卡（建議）” and its host-dialog source (3f48e998e)."),
  Text("ok | rule: “FO runs python3 <package>/scripts/design_surfaces.py check” (backlog/ideation) | evidence: “seed fields and FO alignment recorded” and “design surfaces presentable”; archived-byte replays both exit 0 (faaccf509 / 854322279)."),
  Text("ok | rule: “gate prepare, which takes --reference <check record>” (Delivery authority) | evidence: “reference:pr-watch-tasks-foreign-worktree:validation:attempt-1:revision-1:item-2”, time “2026-11-12T19:22:52Z”, head “e1fbb6ee5abbd7cefd67f57493ab1481a04ed073”; digest, requested head and both clause comparisons match (726f12c79)."),
  Text("ok | rule: “FO confirms both goal sufficiency and minimal necessity” (validation) | evidence: sufficiency “a task whose stamped worktree is absent from this machine”; necessity “kc-dev-flow-2/scripts/pr_watch.py and kc-dev-flow-2/scripts/test_pr_watch.py change against the PR's base” (726f12c79, merge/ask-1.json)."),
  Text("ok | rule: “naming the finding, reason, candidate revision and the lines or evidence it rests on” (FO steps: review findings) | evidence: overlap-risk finding “FO declines F1 Deferred risk at e1fbb6ee5”; “validation/overlap-prs.json records it; the validator observed no failing workflow on this head” (7e7f6a0c2)."),
  Text("can't tell | rule: “merging the full head” (Delivery authority) | evidence: “error connecting to api.github.com”; remote merge records unavailable."),
  Text("Coverage: Pinned dda02cf8552bc0447fd5672e6d756d4c440cb445..e6446302a2f884544b71fd3b127db1b5c8aa826a. Read README, task history and First Officer changes, dispatches, briefings, ledger, merge reference and Captain-step records; sampled worker evidence without judging product correctness. Role check exited 0 with no next lines. Design archives stayed in memory; scope-history check reported “not in a git checkout”. Merge audit exited 2, captured immediately; no carried line emitted. Fetch was suppressed under the no-write boundary; warning: “records may be stale or invisible”. Missing records may mean chat approval or state outside this repository. Batch timing, publication authority and delivery-hook execution remain unverified.")
])
```

```text
Remaining: Report filing; unverified coverage noted above.
Next: First Officer saves this report (you).
Closable: no
```
