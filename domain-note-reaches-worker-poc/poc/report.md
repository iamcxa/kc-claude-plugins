# domain-note-reaches-worker-poc: measurement report

Run 2026-11-09 by the CE session (Paseo 2d26599b) at the Captain's request 「這件事我想要你從 relay 那邊把 poc 任務拿回來，讓你先做」; run count 「5次」; hosts 「完整比較只跑 Claude 和 Codex，Gemini 用 A 單次檢查」. The trap, the harness location and the judge model were chosen by the CE session, not ruled by the Captain; the task's backlog gate listed the trap and harness location as his to accept.

## Result

Without a note, no run planned the two-family browser runs (0 of 6). With the note delivered by A (committed copy plus an AGENTS.md pointer) or B (gitignored copy plus the same pointer), every Codex and Claude run opened the note (20 of 20; each transcript shows a read of its contents, not only a listing), and 18 of 20 were graded YES by the blinded judge. C (note as a dispatch checklist line) was graded YES 10 of 10. The result supports A and B as reaching C's level for these two hosts on this trap; it does not separate A from B. No winner is chosen here.

| Host | Variant | Runs | Opened the note | Judge YES | Judge PARTIAL | Judge NO | Mean seconds |
|---|---|---|---|---|---|---|---|
| Codex gpt-6.1-sol xhigh | none | 3 | 0 | 0 | 0 | 3 | 241 |
| Codex | A | 5 | 5 | 5 | 0 | 0 | 181 |
| Codex | B | 5 | 5 | 5 | 0 | 0 | 213 |
| Codex | C | 5 | n/a | 5 | 0 | 0 | 223 |
| Claude opus-5-5 high | none | 3 | 0 | 0 | 2 | 1 | 157 |
| Claude | A | 5 | 5 | 4 | 1 | 0 | 140 |
| Claude | B | 5 | 5 | 4 | 1 | 0 | 122 |
| Claude | C | 5 | n/a | 5 | 0 | 0 | 125 |
| Gemini 4 Argon high (agy) | A, one-off | 1 | 1 | 1 | 0 | 0 | 592 |

The two Claude PARTIAL grades in A and B quote plans that require a four-way matrix (CLI IPv4 or IPv6 × browser IPv4 or IPv6), which includes both browser-side runs; read against the rubric they are YES, so the judge erred there. In the baseline the judge graded a plan NO that varied only the CLI family with an optional IPv6 run, which the rubric calls PARTIAL. The judge is a single model and errs in both directions; the conclusion rests only on the YES column, where the baseline is 0 of 6 either way. Beyond the two pilots, the deciding quotes of five YES runs (codex-A-3, codex-B-4, codex-C-2, claude-B-3, claude-C-4) were read by hand; each requires both explicit browser-side resolutions.

## Method

- Repository: subspace-relay at ea535cdff86c97a370e68dda767701db384cd529, the parent of PR #442 (the pairing feature). Each run got a fresh one-commit repository with no other refs or remote, so neither the code nor git history held the answer, and learning.md did not yet carry the lesson.
- Task (harness/task.md): write the local validation plan, under Netlify dev, for "accept the approval only when the browser is on the same computer as the CLI request that started the pairing". Plan only; no implementation, servers or installs.
- Note (harness/netlify.md): one entry in learning.md's Applicability/Practice/Evidence shape, generalised from relay's pair-once lesson: run each browser case with localhost explicitly resolved once to 127.0.0.1 and once to [::1].
- Variants (harness/run.sh): none; A commits docs/domain/netlify.md and appends a "Domain notes" pointer section to AGENTS.md; B appends the same pointer, gitignores /docs/domain/, then places the file untracked; C appends the note's Applicability and Practice to the prompt as a checklist line.
- Hosts: Codex with a scratch CODEX_HOME (auth only; no user config, rules, memories or plugins), read-only sandbox, ephemeral. Claude with Kent's login and `--setting-sources project --strict-mcp-config`, write tools disallowed. Gemini through agy 1.5.3 in plan mode.
- "Opened the note": the transcript names docs/domain/netlify.md. "Applied": harness/judge.sh, claude-sonnet-5-5, with every mention of docs/domain and netlify.md masked so the variant is not visible. YES means the plan requires browser-side runs with localhost explicitly resolved to IPv4 and to IPv6.
- The first rubric (harness/score.sh, kept in the run lines) counted any answer naming both families; the baseline showed it counts incidental mentions (Claude scored 3 of 3 with no note), so the blinded judge was written before the 28 main runs were graded and applied to every run.

## Limits

- One trap, one repository, one note in docs/domain/. Choosing the right note among several is not tested.
- A plan task explores less than an implementation task.
- Discovery in A and B rode on the AGENTS.md pointer, which tells the worker to `ls docs/domain`; `ls` does not skip gitignored files. B without the pointer, where a gitignore-respecting search tool might skip the file, is not tested.
- B's FO-side pull before dispatch was not exercised; the run starts from its end state. Codex's read-only sandbox did read the gitignored file in 5 of 5 runs.
- The Claude leg was not isolated from the user-level CLAUDE.md. Codex attempted three account-level MCP connectors that failed authentication and were not used. The Gemini run used agy with the operator's own configuration, memories and MCP list; it was not isolated.
- How often a stale copy would hold dispatch (q2) is not measured.

## Cost, measured

Codex 18 runs: 8.06M input tokens (6.71M cached), 113k output, 3816 s total. Claude 18 runs: 12.07 USD at API prices, 2410 s total; the judge calls are not totalled. Gemini 1 run: 592 s.

## Records

harness/ (task, note, run, score, judge) holds no relay code and can sit beside this report. runs/<host>-<variant>-<n>/ (prompt.md, transcript.jsonl, answer.md, judge.json, seconds.txt, git status before and after) and results.json carry contents of the private subspace-relay repository, so they must not go to a public repository; they are kept on the operator's machine at ~/.local/share/domain-note-poc-2026-11-09/ (30 MB). The per-run repository copies were deleted.
