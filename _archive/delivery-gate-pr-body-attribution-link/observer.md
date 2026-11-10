# Observer report: delivery-gate-pr-body-attribution-link

Observer: kc-dev-flow-2:observer, gpt-6-astra (Codex via Paseo, thinking xhigh), 2026-11-10. The lines below are the observer's reply as delivered to FO; FO added nothing to the findings.

ok | rule: "A Captain ruling is his reply to the question it settles" (FO steps: review findings) | evidence: question「決定：第 20 批這四張」; reason「answering 「決定：第 20 批這四張」; full comparison matches (2ba456a44)
ok | rule: "A Captain ruling is his reply to the question it settles" (FO steps: review findings) | evidence: question「決定：第 20 批四張設計」; reason「answering 「決定：第 20 批四張設計」; full comparison matches (55d5c2925)
ok | rule: "A Captain ruling is his reply to the question it settles" (FO steps: review findings) | evidence: question「決定：合併 #825」; reason「answering 「決定：合併 #825」; full comparison matches (17c1b83b7)
ok | rule: "plain approval accepts that recommendation only when the gate question says so" (FO steps: review findings) | evidence: 「核准即接受上列每一項建議」; 「Recommendation: followed」 (55d5c2925)
ok | rule: "FO runs python3 <package>/scripts/design_surfaces.py check" (backlog) | evidence: "seed fields and FO alignment recorded"; history replay exit 0 (f4e39a680)
ok | rule: "FO runs python3 <package>/scripts/design_surfaces.py check" (ideation) | evidence: "design surfaces presentable"; history replay exit 0 (d1e8466a7)
ok | rule: "FO runs python3 <package>/scripts/delivery_gate.py check before the merge ask" (Delivery authority) | evidence: "reference:delivery-gate-pr-body-attribution-link:validation:attempt-1:revision-1:item-2"; time "2026-11-10T10:59:09Z"; head "2a72c89b9aa9d114e45aeb16b746b8ca9f747bb8"; hash, head and both clauses match (4dac28ec6)
ok | rule: "FO confirms both goal sufficiency and minimal necessity" (validation) | evidence: sufficiency "a gate text naming a PR body"; necessity "only kc-dev-flow-2/scripts/delivery_gate.py and kc-dev-flow-2/scripts/test_delivery_gate.py change" (4dac28ec6)
ok | rule: "FO counts rounds and records the count" (FO steps: review findings) | evidence: "External rounds: 1." (f35f3ac8d)
ok | rule: "A merge ask names each listed reviewer that was not read" (Extensions) | evidence: "copilot not run"; "Second reviewer: Copilot because the PR changes the merge-ask check." (f35f3ac8d)
observed | rule: "Reviewer: <agent> <model> <date> — <question>" (Stages) | evidence: "absent"; role_triggers prints no next line (3cd5898c6)
can't tell | rule: "present the exact candidate and PR body before authorized push/create" (Delivery authority) | evidence: "FO published the product branch, opened the Draft PR"; the earlier grant is in chat, outside the collected evidence (3cd5898c6)
can't tell | rule: "FO commits task state only through SD commands" (Workflow State) | evidence: "absent"; the commit tool's run record is not in the state checkout (3cd5898c6)
ok | rule: "merging the full head `<package>/scripts/delivery_gate.py check` passes, with `--match-head-commit` set to it" (Delivery authority) | evidence: "carried: 9 of 11" (gh pr list, state refs)
observed | release PRs carry no task ask | evidence: "release: #819" (gh pr list)
observed | sync PRs carry no task ask | evidence: "sync: #824" (gh pr list)

Coverage (observer's words, translated by FO): b63df43d5..3cd5898c6. Read the full history, FO record diffs, three briefings, the ledger, four dispatch records, Captain steps, merge records and the applicable rules; worker attachments sampled, product content not judged. Dispatch coverage passed for three stages. No agent approval, amendment, Override, Precedent, decline or peer-relayed approval. merge_audit first exited 2 with a fetch warning; the authorized rerun exited 0 with no warning. A missing record may mean a chat grant or evidence in another repository. The history export replay did not run the scope check; the state worktree was clean and HEAD unchanged.
