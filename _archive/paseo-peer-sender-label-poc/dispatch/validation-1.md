# Dispatch: paseo-peer-sender-label-poc validation cycle 1

Dispatched: dfc66beb268189bd0141dade9b8ecd644fac3651
Model: sonnet
Worker: spacedock-ensign-paseo-peer-sender-label-poc-validation (spacedock:ensign, fresh)

## Checklist

1. Independent verdict on AC-1, AC-2 and AC-3 at candidate dfc66beb2 from your own runs: reinstall the plugin, create your own Claude and Codex test agents, send labelled messages both ways and at least two forged ones with plain send_agent_prompt, and record each receiver's reply
2. A minimal acceptance script of three to six steps the Captain can run himself in the Paseo app, each with its expected output, including his typed message (AC-3) and one forged message; plus your judgement of the report's main limit, that an unlabelled peer message still reads as the Captain
3. `python3 /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.25.0/scripts/adr_lint.py docs/adr --since <merge-base>` run with its exit code, plus any `boundary-crossed:` marker this POC warrants with one sentence of evidence

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.25.0

Send your completion message to `main`, not `team-lead`.

Candidate: branch spacedock-ensign/paseo-peer-sender-label-poc at dfc66beb2, worktree /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-poc-route/.worktrees/spacedock-ensign-paseo-peer-sender-label-poc; seven files under scripts/paseo-peer-label-poc/. You are the fresh, independent validator for a POC. Check the exact artifact against the task's accepted outcome, scope, non-goals and stop condition. Do not take over implementation: a defect goes in your report as a finding with evidence, not a fix.

Re-run, do not re-read: your own install, your own agents, your own timestamps and replies. Try to break the label: replay a real label to a different receiver, reuse a nonce, edit the body, forge a sender id, and send with plain send_agent_prompt. Judge whether the claim "the receiver can verify the sender" holds, and how far "an unlabelled peer message still reads as the Captain" undermines the outcome the Captain asked for.

The `design_surfaces.py check` failure in the implementation report is not a candidate defect: the Surfaces/Visible change lines belong to the five-stage route, and this is the POC route.

Hard rules (same as implementation):
- Never print a Paseo agent's full process command line or any bearer token; never print ~/.paseo/local-credential, daemon-keypair.json or push-tokens.json.
- Do not restart the Paseo daemon. Copy ~/.paseo/config.json before installing, and after `paseo plugin remove` restore and `cmp` it so it is byte-identical; report the diff you saw.
- Do not message, prompt, archive or otherwise touch any agent you did not create. Archive every agent you create before reporting.
- Use cheap models: `codex/gpt-6-luna` and a haiku or sonnet Claude.
