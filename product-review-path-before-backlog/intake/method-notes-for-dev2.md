# Proposal to the dev2 maintainer: a product self-improvement path before the dev2 autopilot

The Captain asked for this on 2026-10-23: 「能不能在 dev2 的自駕路徑之前，多加入一個產品自我改善路徑，做法是由不同模型扮演挑剔的使用者，找出不滿意的地方，讓設計總監（dev2 新角色）來評估是否該解決，要怎麼解決，何時解決」. It was dogfooded by hand once in kc-paseo-plugins, on the project-env settings screen at main 40849b4. Every artifact is in this folder, state branch spacedock-state/dev2, commit 538180d and later.

## What ran

1. **Harness.** An isolated Paseo built from main, with fake op, security and git and four projects of different shapes (`harness/`). Measured: about 2 minutes to set up.
2. **Two picky users on different models.**
   - **Astra** (codex, gpt-6-astra): an experienced user. Brief in `astra-brief.md`, report in `astra-review.md`, 25 and 11 screenshots.
   - **Gemini** (antigravity, gemini-3.8-flash-high): a first-week newcomer. Brief in `gemini-brief.md`, report in `gemini-review.md`.
   - Each brief gives a persona, eight scenarios at 1280 and 400 px, and the FO's five deferred findings for a user verdict. Each reviewer returns ranked complaints, a verdict on each deferral, what they would miss, and a recommend or not.
3. **Design Director.** Claude Opus with fresh context (`design-director-brief.md`). It reads both reviews, past Captain rulings, the ADRs, the journey map and the code; reproduces anything in doubt; and rules per merged complaint: real?, solve / do not solve / Captain decision, how, and when (this round / r1b / later / never). It proposes at most three backlog tasks and says which must run in sequence. Output: `design-director.md`.
4. **Captain backlog gate.** The Director's two tasks plus its two recommendations, approved with 「准」 and filed as project-env-save-blocks-half-changed-connection and project-env-every-row-findable. The normal dev2 path runs from ideation onward.

## Findings from the run

- **Both models found the same top blocker on their own.** The footer Save commits a connection change while Done is disabled. The FO had deferred this in an earlier task's validation. The two reports overlapped heavily on everything else as well.
- **The Director's verdict on the method.** It found almost no new kind of defect. Its value was ranking the items five earlier tasks had deferred "to the Captain's UAT", where nobody owned them. The new finds were small: project order changes on save, mid-word wrapping, no route to rows with no field.
- **Cost of a bad fixture.** The harness's fake vault had no field values, so both reviewers reported "every field fails Test" as a blocker. That cost one rerun. Smoke-test the fixture, with one Test that passes, before dispatching reviewers.
- **The two models disagreed on the hover bubble and the deferred (d) item.** The Director took a side and said why. Treat model consensus as a signal, not a verdict.

## Proposed for dev2

1. **A new role, `design-director`.** It takes picky-user reports, past rulings, the ADRs and the journey map. It returns a ruling table and at most three backlog tasks with sequencing.
2. **A "product review" path before backlog.** It runs at least two picky-user reviewers on different providers or models with different personas, then the Director, then the Captain's backlog gate. Triggers: a release's tasks are all merged and before the Captain's UAT; or the Captain asks.
3. **Route deferred findings into this path.** Every FO decline that waits on the Captain's UAT feeds the reviewers' brief and the Director's table, so it gets an owner.
4. **Harness smoke check.** Before reviewers start, confirm one Test passes in the fixture.
5. **Open for the maintainer:**
   - whether the reviewers' persona and scenarios should come from the journey map's stories;
   - whether the Director should also own the ideation-stage design review that per-task workers do today, since per-task UI review missed whole-screen issues in r1.5.
