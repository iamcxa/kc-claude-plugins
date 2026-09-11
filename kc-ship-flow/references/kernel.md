# kc-ship-flow kernel

kc-ship-flow is one of three independent units — plan-flow, kc-dev-flow and kc-ship-flow — connected only by versioned input/output contracts; this kernel adopts no rule from the other two.

## Principles placed from `## Ship-flow runtime` (DEV-117)

The review station runs the `kc-pr-review` skill only inside a Claude session — never a headless
call from this plugin. The repository's own `kc-pr-flow/scripts/review-ablation.sh` runs
`kc-pr-review` headless for its ablation harness, but that script belongs to `kc-pr-flow`, not
this station. Under DEV-157 (`ship-remove-duplicated-stations`) the station's own Draft-PR opener
and disposition step are removed: `kc-pr-review` now runs inside the cloud First Officer's own
`docs/dev` validation stage, and the Draft PR is opened by Spacedock's `pr-merge` mod, not by a
kc-ship-flow script.

Placed segments (`references/placement.tsv`): `2f1d305eccd5`.

## Residuals (no enforcement script today)

`## Ship-flow runtime` sentences that name no surviving script, schema, or check are not given one
here — per DEV-117's Non-goals, enforcing a principle with no script today means filing a ticket
for it, not fabricating a check:

- Dispatch a higher layer only after the lower layer is fully verified. No script orders dispatch
  across layers today.
- A worker's without-it command was meant to run in an isolated environment (temporary HOME, no
  agent, no network); the per-task check that verified it is removed under DEV-157 (dev flow's own
  validation gate is the acceptance now), so the HOME/network isolation itself was never checked
  and still isn't.
- The per-task review-disposition step's `findings_outside_brief` rule, the per-task Draft-PR
  opener's evidence-driven title/body, and the per-task UAT-ready notifier are all removed under
  DEV-157: dev flow's own `kc-pr-review` validation stage, Spacedock's `pr-merge` mod, and chat
  cover them per task now. See `references/placement.tsv` for each segment's residual reason.

See `references/placement.tsv` for the full segment-to-destination table this section was sorted
into, and `kc-ship-flow/scripts/prose-placement-check.py` for the check that every segment landed
somewhere.
