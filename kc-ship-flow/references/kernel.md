# kc-ship-flow kernel

kc-ship-flow is one of three independent units — plan-flow, kc-dev-flow and kc-ship-flow — connected only by versioned input/output contracts; this kernel adopts no rule from the other two.

## Principles placed from `## Ship-flow runtime` (DEV-117)

The review station runs the `kc-pr-review` skill only inside a Claude session — never a headless
call from this plugin — so the station is two scripts either side of that session run:
`references/stations/open-pr.md` opens the Draft PR before the session, and
`references/stations/disposition.md` dispositions the session's own findings after it. The
repository's own `kc-pr-flow/scripts/review-ablation.sh` runs `kc-pr-review` headless for its
ablation harness, but that script belongs to `kc-pr-flow`, not this station.

Placed segments (`references/placement.tsv`): `2f1d305eccd5`.

## Residuals (no enforcement script today)

Two `## Ship-flow runtime` sentences name no script, schema, or check and are not given one here —
per DEV-117's Non-goals, enforcing a principle with no script today means filing a ticket for it, not
fabricating a check:

- Dispatch a higher layer only after the lower layer is fully verified. No script orders dispatch
  across layers today.
- A worker's without-it command is meant to run in an isolated environment (temporary HOME, no agent,
  no network); `without-it.sh` (`references/stations/without-it.md`) strips only credential env vars,
  so the HOME/network isolation itself is unchecked.

See `references/placement.tsv` for the full segment-to-destination table this section was sorted
into, and `kc-ship-flow/scripts/prose-placement-check.py` for the check that every segment landed
somewhere.
