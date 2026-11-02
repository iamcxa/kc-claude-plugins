# Validation rerun evidence — PR #763, Captain amendment 1

Observed 2026-11-02. Candidate c129cb215c2630d08853eeffae0fd5a2ee7e40c6, base and origin/main 146727ded0d4ce8014ea0b41a45dc3409d6b269b, unchanged since validation-1, so its judgements' inputs are unchanged. Worker: Paseo agent 5c429108-ba82-4cf4-86f3-2bddc0c82686, Claude Opus high. Checks ran in a detached throwaway worktree, since removed.

FO transcript: ~/.claude/projects/-Users-kent-conductor-workspaces-kc-claude-plugins-colombo/5c030106-8d82-4542-855e-1498b2563c69.jsonl. Row numbers are at the read, 75686 rows.

## Real stage workers (AC-1)

Codex, read here independently of native-runs/README.md:
- Row 75490: create_agent, provider codex/gpt-6.1-sol, workspaceId, notifyOnFinish true, modeId auto-review, Spacedock's generated bootstrap.
- Saved record special-roles-follow-the-model-table/dispatch/implementation-1.md carries the exact sentence; `--names --strict` exit 0.
- Row 75528: event="finished", source bc46043b, reply ends `Done: special-roles-follow-the-model-table completed implementation.` The reply also carries a summary and status block above that line.
- `paseo agent logs bc46043b`, 118 lines: 0 matches for send_agent_prompt, team-lead, SendMessage or Send message.

Claude, this worker:
- Row 75652: create_agent, provider claude/claude-opus-5-5, workspaceId wks_9ead9a5df649c8c9, notifyOnFinish true, modeId auto. Generated dispatch; saved record validation-2.md carries the exact sentence.
- This worker made no SendMessage or send_agent_prompt call and did not load either tool. Self-report; the timeline is the proof.
- The callback fires when this turn ends, so this worker cannot observe it. FO records the received row.
- This worker's timeline holds the words in Read output and in its own grep commands, so count tool rows rather than word matches.

Falsifier: the command-line and `main` arm was read from the design's 2026-11-02 table, not rerun, under "Do not start agents yourself". Same-day transcript counts: command line with no later send 22 agents, 0 callbacks.

## F2 re-judged

| Checker, target | Installed 0.34.0 | Candidate |
| --- | --- | --- |
| --names --strict validation-2.md | 0 | 0 |
| --coverage task --stage validation | 0 | 0 |
| task folder | 1: validation-1.md and validation-2.md | 1: validation-1.md only |

- The rerun's own record passes every preflight on the candidate. Falsifiers on a disposable copy: replacing the sentence returns exit 1 naming validation-2.md; changing `paseo` to `xpaseo` in a copied README returns exit 1 naming validation-2.md.
- Dropping validation-1.md from a disposable copy returns exit 0, 4 records.
- validation-1.md is the instruction that run actually received. The workflow's Stages text says records exist "so the instruction a worker followed outlives the session that wrote it". Rewriting it to pass, as validation-1 suggested, would make it false.
- A grep of delivery_gate.py and laws_check.py found it only in laws_check.py; other callers were not searched, and how laws_check.py treats this exit was not read.
- Installed 0.34.0 refuses the new sentence until release, which is the expected order for a checker change in this same PR.

## Reruns at the candidate

| Check | Result |
| --- | --- |
| adr_lint.py, Claude cache, --since base; again with --require 0048 | exit 0 each, 47 files, 0 legacy |
| test_dispatch_records, with SPACEDOCK_BIN and SD_PLUGIN_ROOT | exit 0, 100 tests, OK |
| test_sd_dispatch.py, Claude cache Spacedock 0.27.3 | exit 0; states "Not run: skill discovery/reading, worker execution, human gates, delivery hook body or remote merge" |
| implementation-proof-1.py | exit 0; 25 tests, 820 > 819 refused, missing Words label refused |
| lint-skills.py | exit 0, 5781 of 5781 |
| workflow.md, lint-skills.py, test_sd_dispatch.py against base | identical |
| number_guards.py | exit 0, no findings |
| comment_ratio.py | exit 0, 75 code, 1 comment, 1.3%; the comment points at ADR 0048 |
| doc_impact.py | ADR 0045 and learning.md for review, ADR 0048 updated; implementation dispositions stand |
| design_surfaces.py check | exit 0 |
| PR #763 | OPEN, Draft, exact head; five checks SUCCESS |
| RoboRev job 1396 | verdict_bool 1, SEVERITY_THRESHOLD_MET; fields status and git_ref read null this time, so the exact-range match is carried from validation-1 |
| FO rows 75388, 75402, 75436 | errored 1aef76e0, finished e97e30ec, permission-required e627ae31 |
| `paseo agent run --help`, 0.14.0 | 0 matches for notify or callback |
| `git worktree list` | one special-roles worktree |

## Not verified

A Codex FO as receiver, delivery across hosts, and a Claude stage worker spawned at a lower tier than Opus high. AC-1's and AC-2's command-line falsifiers were read, not rerun.
