violation | rule: “Otherwise the reason carries `Recommendation: followed`.” (FO steps: review findings) | evidence: backlog reason ends “accepts outcome, scope and Budget as seeded and the trial route rules.”; declaration absent (08d44f81d).

violation | rule: “Otherwise the reason carries `Recommendation: followed`.” (FO steps: review findings) | evidence: ideation reason ends “accepts the design with that placement.”; declaration absent (d9bb6957d).

violation | rule: scope notes carry “Send your completion message to `main`” (Stages) | evidence: all four dispatch records instead say “Your final reply is your completion message: Paseo delivers it to FO when your turn ends.” Required line absent; this establishes a recorded-rule mismatch, not a delivery failure (845957979, dispatch/*.md).

ok | rule: “A Captain ruling is his reply to the question it settles” (FO steps: review findings) | evidence: backlog question “獨立審查說原本的合約不能直接跑” matches reason “answering 「獨立審查說原本的合約不能直接跑”; whole-question comparison passes (08d44f81d).

ok | rule: “A Captain ruling is his reply to the question it settles” (FO steps: review findings) | evidence: ideation question “「做新東西前先查既有的」” matches reason “answering 「「做新東西前先查既有的」”; whole-question comparison passes (d9bb6957d).

ok | rule: “A Captain ruling is his reply to the question it settles” (FO steps: review findings) | evidence: validation question “決定：合併 #859” matches reason “answering 「決定：合併 #859”; whole-question comparison passes (4b62f72b4).

ok | rule: “FO runs `python3 <package>/scripts/design_surfaces.py check --seed <task>`” (backlog) | evidence: “seed fields and FO alignment recorded”; in-memory archive replay exits 0 (353e835dd).

ok | rule: “FO runs `python3 <package>/scripts/design_surfaces.py check <task>`” (ideation) | evidence: “design surfaces presentable”; in-memory archive replay exits 0 (725e2a410).

ok | rule: “Before merging or asking, FO runs `python3 <package>/scripts/delivery_gate.py check <task>`” (Delivery authority) | evidence: “reference:new-work-checks-what-exists-first:validation:attempt-1:revision-1:item-2”, “time”: “2026-11-13T00:30:53Z”, “head”: “1fc2f05f88b18a62d4eda598158ffa385df9fae8”; digest, head and both clause comparisons pass (ae2318dd5).

ok | rule: “FO confirms both goal sufficiency and minimal necessity” (validation) | evidence: “sufficiency”: “the stage principles carry one check home before new work”; “necessity”: “docs/adr/0083-workers-check-the-existing-chain-before-new-work.md” (ae2318dd5, merge/ask-1.json).

can't tell | rule: “merging the full head” (Delivery authority) | evidence: “error connecting to api.github.com”; external merge evidence unavailable.

Coverage: Window 91f0143c49..8459579792. Read task history, changed state, four dispatches, three briefings, amendment, merge reference and Captain-step records; sampled worker evidence without judging it. Required role check exited 0 with no `next:` lines. Design archives stayed entirely in memory; ideation scope comparison reported “not in a git checkout”. Merge audit exited **2**, captured directly, with fetch suppressed to preserve no-write scope; warning: “records may be stale or invisible”. No `carried:` result was produced. Missing records may mean chat approval or state outside this repository. No files written.

```text
Remaining: First Officer disposition; external merge coverage.
Next: Save and assess this report (you).
Closable: no
```
