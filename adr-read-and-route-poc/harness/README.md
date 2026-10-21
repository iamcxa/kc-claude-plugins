# Harness: do agents consult the governing ruling and put new information in the right home?

Disposable POC harness (profile `poc`). Everything it reads is fictional. It is not the shipped `read-ruling` skill, S30, or dev2's `agent-reads-governing-adr` hook.

## What it runs

10 hand-written scenarios (`scenarios.json`) x 4 arms x 2 hosts, one run each, about 80 runs; arm A3 runs on Claude only (Codex 0.162.1 silently skips an untrusted SessionStart hook and its trust bypass was not approved), so 70 cells.

| Arm | What the agent is given |
| --- | --- |
| A0 | nothing: the two repositories and the task |
| A1 | skill `read-ruling` teaching `git show` + `shasum` + reading the Status line, plus the routing table |
| A2 | skill `read-ruling` teaching the `kc-decision-log` preview CLI (`vendor/cli.mjs`, a verbatim copy), plus the same routing table |
| A3 | A2 plus a session-start hook that lists ruling titles (`templates/hook.sh`) |

Hosts: Claude Code (`--model sonnet`) and Codex (`-m gpt-6.1-sol`, reasoning effort high). The exact argv of every run is in `results/<run id>/meta.json`.

The routing table under test is `templates/routing.md`, a translation of the section 「什麼寫進哪裡」 of `docs/journey/kc-decision-log/boundary-contract.md` on branch `origin/docs/kc-decision-log-boundary` (PR #691). The authorisation row is in the skill but no scenario tests it.

## The world

`world.py` builds, per run and deterministically (fixed dates, so commit ids and digests are identical on every build, asserted against `expected_world.json`), two git repositories: `mira-decisions` (22 ADRs at D0, 23 at D1; the cadence key runs 0002 weekly -> 0014 daily -> 0023 daily at 07:00, so at D1 ADR 0002 is superseded in two steps; near-duplicate titles such as a Deprecated monthly report and a Proposed hourly kiosk refresh) and `mira-app` (23 dev2-format ADRs, tasks, a story map, `AGENTS.md`/`CLAUDE.md` with no word about ADRs, `.agent/notes.md`). Both ADR folders pass the real `adr_lint.py`.

## Measures (defined in `expectations.json` before any run)

1. Consulted the governing ruling before deciding: from tool calls and outputs only, scored where a governing ruling exists and the task does not cite it (S1, S2, S5, S6, S7). No prompt tells the agent to consult or confirm anything.
2. Handoff version and digest matched: scored on the three scenarios whose task file carries a Reference block (S8 valid, S9 cited record already superseded, S10 digest does not match). The prompt only asks it to report the ruling it relied on, with the digest it read; the digest must also appear in a tool output.
3. New information in the home the routing table names: from the filesystem diff of the run's workspace, not from the agent's own list.
Secondary: whether the `choice` equals the ruling's answer.

## Isolation (proved by probe before any scenario run; probes are outside `results/`)

- Claude: `--setting-sources project --strict-mcp-config`, auto memory off, `--settings` with the sandbox on and writes limited to the run directory. Probe: no user CLAUDE.md, no user plugin skills, project skill and project SessionStart hook both visible.
- Codex: per-run `HOME` and `CODEX_HOME` (only a symlink to the login file), `--disable memories`, `-s workspace-write`. `codex debug prompt-input` shows only Codex's bundled system skills plus the project skill.
- Each run gets a fresh workspace under `$ADRPOC_RUNS` (default `/tmp/adrpoc-runs`).

## Re-run

    python3 run.py run --scenarios S1,S2 --arms A0,A1 --hosts claude,codex --rep 1 --jobs 3
    python3 score.py                  # re-grades every results/<run id>/ and writes ../results.md and ../results.json
    python3 score.py --run S6-A0-claude-r1

Needs python3, node 24, git, and logged-in `claude` and `codex`. `score.py` needs no agent and no network.

## Rules fixed before the first scenario run

- Declared: about 80 runs; Amendment 2 moved the world to a larger one after the first 20 runs, so the cap counts those 20 too: 70 planned + 20 = 90, hard stop 96. A run that returns no answer is retried once and the retry counts; ledger in `../ledger.jsonl`. Hard stop at 96 runs (+20%); the FO is told before passing it.
- No scenario, expectation or skill text changes after the first scenario run without a dated line in `../CHANGES.md` giving the reason.
- Stored per run: argv, prompt, schema, the normalised tool-call trace (outputs cut at 20 KB), the final answer, the workspace diff, and the raw host output gzipped.

## Probes

`../probes/` holds the four harness smoke runs (scenario ids `SMOKE`, `SMOKE2`; they check that skills load, the hook injects on Claude, the sandbox allows the intended writes, the CLI runs on both hosts). They ran on the world before `package.json` was added and grade nothing. Six more manual isolation probes ran from a scratch directory before the harness existed; none is stored.
