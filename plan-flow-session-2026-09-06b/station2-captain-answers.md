# Station 2 — Captain's answers, 2026-09-06 (verbatim, Ask UI)

Q1 (demand reality), four mined observations offered; the Captain chose three:
> 今天三次 merge main 全卡在 README 散文
> 規則只活在散文或我的記憶檔
> 三百行 runtime 散文沒辦法驗證
Not chosen: "舊 ship-flow README 讓人分不清哪個是哪個" (the collision is a fact for B6, not a pain the Captain felt).

Q2 (smallest usable this week): > B1 到 B5 一次走完
Q3 (do nothing / closest tool): > 腳本留 scripts/ship-flow，adopter 手抄
Q4 (wedge): > 只有 kc-claude-plugins，Kent 當 FO

Read by the FO:
- Refusal seam: behaviour (three README prose conflicts in one merge station, 2026-09-06), workaround with cost (prose edit per adopter, rules in FO memory files, conflicts resolved by hand), one named human (Kent as FO), one observation (merge commits 7c57a30c, 6ac488a3, db3d19dd — every hunk inside `## Ship-flow runtime`). Passes.
- Q2 sets the batch at B1–B5 (DEV-115..119); B6 retire (DEV-120) and B7 plan-flow plugin (DEV-121) stay Backlog for the next session. B4 is a POC ticket and precedes B5 per the POC-before-dependents rule.
- Q3 names the do-nothing baseline: vendoring by hand (the `_mods` pattern). Premise P2.
- Q4 keeps adopters out of this batch; "installable" is proven only by the repository installing its own plugin.
