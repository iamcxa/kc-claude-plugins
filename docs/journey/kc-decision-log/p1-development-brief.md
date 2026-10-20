## The problem

The user directs several AI agents across products and tools, and wants one versioned source of his rulings that every agent reads at the same version: 「我需要指揮不同 FO，跨產品，跨 LLM，跨工具去達成我的目標」 (2026-10-19). Today his rulings live in a private decision repository that agents already write to through reviewed PRs. No agent has a tool to read a ruling at an exact commit and hand that exact reference to another agent; a session on 2026-10-19 found no ADR tool at all. Agent memories are per agent and unversioned.

Source: `docs/journey/kc-decision-log/journey.yaml` (SHA-256 `13efda3ac00816428bed0fccda13a0ebf01135efe43561b4579b22b66eedd289`), journey `kc-decision-log-design`, release `P1`, stories S01, S10, S11, S19, S20, S21, S22. Companion detail: `slice-map.md` § P1 and § 已確認選擇 (D1–D13).

Facts, verified 2026-10-20:
- A query prototype in the user's private decision repository has `parse`, `makeSnapshot` and `effective` (`source.mjs`, 136 lines) and `createService` (`service.mjs`, 67 lines). Its build reads ADRs from a fixed Git commit. It has no CLI entry point.
- All 15 real records in that repository carry a `**Decision key:**` line; native dev2 ADRs carry none.
- Claude read an ADR at a full commit with `git show <commit>:<path>` (exit 0).
- Paseo lists the `codex` provider as available. Spacedock's worker host follows the first officer's runtime, so a Claude first officer cannot spawn Codex workers.
- `scripts/version-parity-check.sh` fails when a tracked plugin directory has no `marketplace.json` entry.

Assumptions: Codex's environment can run Node 24 and read the same local clone (unverified). The 16–30 active-hour estimate is an uncalibrated judgment (`p1-estimate.md`).

Technical questions for ideation (they do not change value, scope or acceptance): the CLI command grammar and JSON field names; how the prototype's six gaps are fixed (native ADR IDs, raw-byte digest, byte-order sorting, per-record validation, skipping non-ADR files, parser strictness against `adr_lint.py`); the synthetic decision repository's layout.

## Accepted outcome

The user names one synthetic decision repository and a full commit. Claude reads one ruling with the CLI and gets its exact reference and original status, then writes that reference into the second dev2 task's description. A Codex first officer, started through Paseo, runs that task. Its Codex worker re-reads the ruling with the same CLI in its own environment, confirms the match, and implements a small CLI feature that the ruling decides. The PR is merged, and the user gets back task, gate and PR evidence tied to that reference.

The work runs as two dev2 tasks under the Pilot profile: task one builds the CLI and the read-only skill (S01, S10, S11) with a Claude first officer; task two is the synthetic handoff task (S19–S22) with a Codex first officer. The code lives in a new `kc-decision-log` plugin in kc-claude-plugins, listed in the marketplace from 0.1.0 and marked experimental. The prototype is copied and rewritten, not changed. Appetite: four full working days.

## Non-goals

- dot reading or joining the handoff (P4a; dot has no terminal and needs an MCP server or connector).
- More than one decision space, upper/engineering layering, or cross-space references (P4b, D6).
- OS-level isolation between two users; P1 claims no tenant isolation.
- CLI writes: no Git writes, ADR numbering, task creation, PR opening or merging (D3). No automatic Git updates, package upgrades or deployment.
- Hooks (D10, S30; shared with dev2 task `agent-reads-governing-adr`).
- Automatic push between agents; the user does not relay the handoff either (D1).
- Reading engineering repositories' dev2 ADRs, which lack Decision keys (D9).
- New GitHub accounts, credentials or access.

## Acceptance criteria

- **AC-1** With the synthetic decision repository as the only configured binding, the CLI refuses an unconfigured binding, a wrong repository or path, a missing commit or a non-full commit, and exits non-zero. Messages may name the reason. It treats neither caller claims nor arbitrary paths as authorization and adds no access.
- **AC-2** Reading at D0, the CLI claims only D0 even after the tracked ref moves to D1. It returns repository, path, ADR ID, full commit, a digest of the raw bytes and the original Status, with the same result in JSON and human-readable modes.
- **AC-3** On synthetic data, the CLI reports Status exactly as written: an Accepted record with a Decision key, Proposed, an explicit same-binding supersession, a missing Decision key, two Accepted records with one key, and a broken chain. `effective` follows D9: a missing key or several Accepted records under one key give `unresolved`. The CLI never edits source text, and it reports `unresolved` separately from tool failure.
- **AC-4** The Claude first officer writes the reference (sender, receiver, task, repository, ADR, commit, digest) into task two's description, and the user relays nothing. The Codex worker runs the same CLI in its own environment, and the CLI compares the expected digest, exiting non-zero on a mismatch. Work starts only when `effective` points at the handed-over record. Otherwise the worker stops and reports, without silently changing the target. A pasted claim or another runtime's login does not count.
- **AC-5** When the synthetic ruling says "deploy" or "send", the task record shows no deploy or send action. Peer permission prompts go back to their holder or the user; no first officer answers them.
- **AC-6** Task two completes through dev2/Spacedock to a merged PR. The user merges it, or explicitly authorizes the Claude first officer to merge that PR; Codex does not merge. The user gets back the task, gate and PR references and can match them to this task's content, round and adopted ADR commit. Where that link cannot be shown, it is reported as unknown. Protected logs are not copied, and no separate ledger is created.
- **AC-7** The read-only skill tells an agent holding a ruling reference to re-read it with the CLI and compare the digest, and to stop on a mismatch. Task two's Codex worker uses it, and the use is recorded.

## Route-back conditions

The accepted outcome or non-goals changed. Stop and return a structured planning delta that names the changed premise, affected acceptance evidence, and recommended change or stop.

Also route back when: the Codex first officer or worker cannot run the CLI or read the clone (P1 fails; do not substitute `git show`); active effort is projected beyond the four-day appetite; or a fix would need a new credential, access grant or host change.
