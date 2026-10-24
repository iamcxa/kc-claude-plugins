# Addendum from the kc-paseo-plugins dev2 FO, 2026-10-23 (relayed, not a ruling in this session)

From Paseo agent 8b2c2fc2, after the first picky-user run finished. The Captain's words in its session (relayed): 「你現在這個流程有個問題，顯然這次成果沒完全 cover 到抱怨的內容，為什麼？是不是驗收時沒拿著本來的清單再看一次？且第二個問題是，應該在驗收時把本來的使用者找來讓它再看一次是否抱怨消失了，不是嗎？」

What happened (peer's account): the director turned 17 complaints into 2 tasks and deferred or declined the rest; validation checked each task against its own criteria; nobody went back to the original complaint list; the original reviewers re-reviewed the final build only when the Captain asked (Astra: 3 fixed, 2 partly fixed, 3 not fixed, no new complaints; Gemini still running at the time); the Captain got "all tasks passed", not where each complaint stands.

Peer's proposal (not approved scope):
1. A traceability table in the director's ruling: one row per merged complaint, with the verdict, the task and criterion carrying it, and its status at acceptance (fixed, partly fixed, deferred to a named release, will not fix) with the reason.
2. A closing "original reviewer re-review" before the Captain's UAT: the same models and personas re-run their own steps against their own list, mark each item, and add any new complaint.
3. The Captain's UAT starts from that table.
4. Validators of a path task also re-run the reviewer steps behind the complaints that task claims to fix, not only its criteria.
