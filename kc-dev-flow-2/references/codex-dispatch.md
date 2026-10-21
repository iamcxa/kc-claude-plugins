# Codex dispatch model policy

Opt-in, Codex host only. Without it, every Codex ensign inherits the first
officer's model and reasoning tier.

Requires a Spacedock release that contains `spacedock dispatch build --host codex
--model NAME --reasoning-effort LEVEL` (spacedock-dev/spacedock#844). Check
`spacedock dispatch build --help` for both flags before using this; stock builds
without them ignore the declared model.

1. Resolve the policy for the stage (or a special agent):

   ```bash
   python3 <package>/scripts/codex_model_policy.py \
     --policy <package>/references/codex-model-policy-v1.json \
     --workflow-dir <workflow-dir> --stage <stage> --flags
   # special agent: replace the last two selectors with --agent-file <package>/agents/<name>.md
   ```

   Output is `--model X --reasoning-effort Y` (drop `--flags` for JSON). An
   unmapped model or missing effort exits non-zero naming the input; stop and fix
   the declaration or policy, do not dispatch with null.
2. Append those flags to `spacedock dispatch build --host codex ...`.
3. Pass the emitted `model` and `reasoning_effort` verbatim to `spawn_agent`.
4. A reuse followup cannot change a live worker's model or effort. A stage that
   needs different values gets a fresh dispatch.

Effort comes from the declared `reasoning` first, then the policy's
`reasoning_defaults` for the stage name. Model names map from the declared
Claude-style model through the policy's `models` table.

Observed: only `gpt-6.1-sol` ran on a live Codex host (the #668 pilot).
`gpt-6-luna` and `gpt-6-astra` have not been observed on a live host.
