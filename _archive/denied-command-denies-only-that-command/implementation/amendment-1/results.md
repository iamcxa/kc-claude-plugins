# Narrowed implementation, Captain amendment 1

Candidate: cdb99da0e52e8b5cad3a7be04658dc282432b644
Base: e8664a72b0f904e5dda3c391d52ab3abaca876b4
Branch: spacedock-ensign/denied-command-denies-only-that-command

Only kc-dev-flow-2/extensions/paseo/EXTENSION.md differs from origin/main. Workflow README and lint-skills.py are byte-identical to origin/main, verified after fetching. The extension bytes are unchanged from the earlier candidate, so its preserved fresh-FO scenario transcript still describes this exact instruction (SHA-256 504d105493394a1441e406177ea33356404d05a8ccda97a09ce4be8afbf9d011). It proves the Codex/Claude procedure distinction; it does not prove runtime receipt or action after a denied command.

## What the amendment changes

Captain: 「縮成只傳理由（建議）」, task amendment 1. The dispatch's qnow-record audit is FO's source report, not a new reproduction by this worker: it found one recorded case of a worker missing the build-denial reason and guessing that it covered browser verification, and found no record that the whole task stopped. FO's 2026-11-11 outside-workspace-write probe observed the worker seeing only “rejected by user”. These findings remove the premise for a universal worker-facing continuation sentence and preserve the provider-specific reason delivery step.

AC-1, AC-2, AC-3, AC-4, AC-5, AC-6 and AC-8 were moved verbatim into amendment 1's Superseded text. AC-7 is unchanged. New AC-9 quotes 「理由有沒有送到」 and checks worker-side reason receipt; AC-10 quotes 「工人有沒有照著改」 and checks subsequent actual file writes and the completed small task. Byte hashes are in amendment-bytes.json and the original moved blocks are preserved. No frontmatter, Captain quote, Asked line or Supersedes list was changed.

## Ready for FO, not run here

The task-root packet is `replay-amendment-1/`: operator.md fixes the scoring rule before runs; runs.json lists six independent neutral prompt files and six exact reason files; source.json pins this candidate. FO directly starts and parents each worker in the mode that asks for approval, denies its real request for one new named home-directory text file, then either sends no follow-up (release behavior) or steers the exact reason (candidate behavior). The reason names an in-workspace destination and a route marker absent from the initial prompt; correct real writes plus the finished two-item summary establish action on the reason. A queued send, echoed reason or promised action is insufficient. The operator guide defines voids, missing evidence, same-turn failure and refusal-workaround failure before observation.

Runs: r01 sol no extra message; r02 sol with reason; r03 astra no extra message; r04 astra with reason; r05 sol with reason; r06 astra with reason. At most six new attempts including voids, as dispatched by FO on the Captain's word. The earlier six worker attempts remain void and are preserved in implementation/replay-results.json; none is promoted to a successful control. No new agent, denial, steer or external file was created this round. The implementation worker will score the timelines and file evidence FO returns.

## Checks and limits

Repository lint: 5939/5939, exit 0. Installed 0.38.1 ADR lint: 67 records, exit 0. Fresh-ref number guards: exit 0 on this candidate. design-surfaces and diff --check: exit 0. comment ratio: 0 added code/comment lines, 0%; maximum 5%, with the 20-code-line floor not reached. doc_impact.py lists zero affected retained documents for the final one-file diff. ADRs added: none; ADR 0052's authority is unchanged and this is its operating procedure's provider-specific delivery step. No new wording test is added and no runtime acceptance is inferred from static checks.

Reading cost: the workflow remains 5939 words and Dispatch facts remains 297 words; the Paseo callback remains 270→291 (+21). The withdrawn 33-word startup/dispatch increment and its budget step are gone. No CI trigger changed and per-PR CI cost was not measured. No worker product push or PR; prepared PR text is in /tmp/impl-denied-command-denies-only-that-command-pr.md. FO retains publication, RoboRev, hosted CI, replay denial, gate and delivery authority.
