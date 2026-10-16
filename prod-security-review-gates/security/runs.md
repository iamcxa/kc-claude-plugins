# AC-3 / AC-4 / AC-5 runs, 2026-10-16

Agent `kc-pr-flow:tob-security-reviewer` (Sonnet), unmodified. Each report is the agent's final message saved unedited (`&lt;` is as returned). Prompt = the extension's "Ideation review" brief with `<task file>` and `<base sha>` filled, plus one line naming the repository path. Inputs: `input-relay-design.md` (relay `spacedock-state/dev2` d3fe0ced `agent-front-door.md` lines 56-234, sha256 prefix fd1094c24d13, code at 485a5042) and `input-control-design.md` (`_archive/delivery-gate-verdict-form.md` lines 93-252, code at 0cdb40a7).

Brief revisions (differences only, EXTENSION.md "Ideation review" bullet):
- r0 = the design's draft (423 words).
- r1 = boundary sentence replaced by "A limit the design accepts, or a weakness already in the code, is a finding when the design newly gives that attacker a way to use it unweighed." (428 words).
- r2 = r0 boundary sentence restored; "how much an outsider can write," added to the threat-model list (429 words).

| Report | Tokens | Seconds | Injection finding | Unbounded session or comment creation | Control: severity values |
| --- | --- | --- | --- | --- | --- |
| r0-ac3-relay-1 | 84,858 | 170 | yes (HIGH) | no | |
| r0-ac3-relay-2 | 76,081 | 121 | yes (MEDIUM) | no | |
| r0-ac4-control-1 | 51,342 | 69 | | | MEDIUM, LOW |
| r1-ac3-relay-1 | 97,044 | 291 | yes (HIGH) | no | |
| r1-ac3-relay-2 | 77,013 | 136 | yes (HIGH) | no (comment volume listed under clean_patterns) | |
| r1-ac4-control-1 | 49,882 | 61 | | | LOW, LOW |
| r2-ac3-relay-1 | 90,775 | 293 | yes (MEDIUM) | no: named only in `limitations` as "Not reported as a finding" | |
| r2-ac3-relay-2 | 76,102 | 126 | yes (MEDIUM) | yes (LOW finding: no cap on anonymous sessions, scripted `comment` calls) | |
| r2-ac4-control-1 | 51,304 | 78 | | | MEDIUM, LOW |

Tokens are the harness `subagent_tokens` usage line; seconds are its `duration_ms`.

## Validation-gate replay on relay PR #347, 2026-10-16 (Captain amendment 1)

Agent `kc-pr-flow:tob-security-reviewer` (Sonnet), unmodified, the agent's own contract with `security_tier: standard`, `pr_number: 347`, `owner_repo: spacedock-dev/subspace-relay`. The PR is merged and later commits exist, so the diff was `git diff a5af7e3c...1c5b1870` (14 files, 267 additions, 13 deletions, saved outside the repository) and the tree at 1c5b1870 was a `git archive` export; relay was read only through `git archive`, `git diff` and `gh`, nothing in it edited. 1c5b1870 is the head at which relay's validation cycle 1 recommended PASSED. One run. Report: `validation-replay-pr347-1c5b1870.yaml`, the agent's final message saved unedited.

| Report | Tokens | Seconds | Unbounded comment or session write | Injection finding |
| --- | --- | --- | --- | --- |
| validation-replay-pr347-1c5b1870 | not seen: the harness `subagent_tokens` line did not reach this worker; the transcript's last request held 48,496 input-side tokens and its turns output 2,368 | about 63 (first to last transcript timestamp; not the harness `duration_ms`) | no: `findings: []` | no finding; `limitations` call agent-side prompt injection through any host's /llms.txt "a general property of the design" and out of scope |

Verdict: the validation-gate replay does not name unbounded comment or session writes. Its `limitations` line: "This is the standard tier, so no full data-flow trace of the Room POST handlers was done. They are outside the diff, and the diff adds no new action." The `comment-admission` task's own account of the original finding rests on code outside this diff (a cookieless `enter` mints a new Room session, each session holds up to `MAX_SESSION_RESULTS` = 100, nothing caps a Briefing or a Room) and on ADR 43, with `/llms.txt` only documenting the comment loop; so the finding came from the running handlers, not from a line the diff adds.
