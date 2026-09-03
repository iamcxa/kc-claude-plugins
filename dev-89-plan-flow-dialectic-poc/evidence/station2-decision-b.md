## Captain ruling on Codex round-8 P0 (2026-09-03, evening)

Captain chose (b): keep Alternative A (three sentences into the Ship-flow runtime README with contract-test pins, no script enforcement this round). The user value must not claim enforcement. Enforcement of (b) isolation and (c) security-block in without-it.sh and the review step is a Production-round item, consistent with the Captain's Q4 answer "三條一起，Pilot 深度".

Corrected station-2 outputs for input A:
- Project name (headline): "The three ship-flow guarantees are written down and pinned"
- User value: "Kent completes the next three ship-flow UATs without re-deriving the three declared guarantees from each PR."
- Hypothesis (station 3, unchanged in shape): "If we write the three DEV-67 sentences into the Ship-flow runtime README with contract-test pins for Kent at UAT then Kent stops re-deriving them from the diff."
- Accepted outcome no longer uses "enforces"; the falsifier stays "Kent re-derives one of the three on any of the next three PRs".
- Premise falsifier (new, plan-flow rule): remove Alternative A; can the outcome "Kent stops re-deriving" still hold? No, because the sentences would not exist anywhere Kent can point to. The approach therefore builds the mechanism the value names. (Had the value said "enforces", the same test fails: a README enforces nothing.)

Captain's expectation: DEV-89 closes as `change`; plan-flow POC 3 carries the premise falsifier, the fallback rewrite for licence, the refusal-before-persona order, and the market-signal station.
