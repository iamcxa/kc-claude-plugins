---
title: The delivery check settles a check run its repository skips by design, so an all-green adopter PR is not held
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
---

## Scope

- Source: issue iamcxa/kc-claude-plugins#677; the Captain asked that it be fixed before this release (「把 #677 排在這次發版之前修好」, 2026-10-19, chat).
- Bite: `delivery_gate.py check` (kc-dev-flow-2 0.25.0) holds every ask where a check run concludes SKIPPED or NEUTRAL, which its module docstring states as intended ("an empty rollup, SKIPPED and NEUTRAL included"). Observed three times on 2026-10-19, each ending in a Captain override:
  - spacedock-dev/subspace-relay#398 at 0b7b7c43 and #401 at 9ba2c31d: "6 of 18 checks on this head are not finished and successful: 'workflow' 'release-preflight' 'resolve-paired-web' 'paired-release' 'Header rules -'", while ci-gate, test, typecheck, lint, browser and the e2e jobs were green; the four jobs are skipped by relay's path classifier and checked by ci-gate both ways; Netlify's "Header rules" and "Pages changed" are NEUTRAL. Reported by the relay dev2 FO; #401's resolution carries an `Override:` line (「越過」).
  - spacedock-dev/subspace-web#150 at 93ba01e5 (mergeStateStatus CLEAN): "4 of 7 checks on this head are not finished and successful: 'resolve-release-relay' 'release-pair' 'Pages changed -' 'Redirect rules -'"; the release jobs run only on Release Please's PR and Netlify skips the two rule checks when nothing changes. Reported by the web dev2 FO; the Captain authorized the merge over the hold (「授權你合併 150」).
- Consumer: every adopter FO's merge ask (relay, web; this repository's own CI runs no skipped job today) and the Captain, who otherwise overrides each relay and web delivery.
- Upstream first: GitHub's own model of required checks (branch protection or rulesets, `gh pr view --json statusCheckRollup` fields, `mergeStateStatus`) and each adopter's aggregate job (relay's ci-gate) before the package judges CI meaning itself.
- Candidate directions to measure at ideation, not chosen: settle SKIPPED, and NEUTRAL on a check that is not required; consult only required checks; an adopter-declared list of checks that may skip.
- Non-goals: to be set at ideation.

## FO alignment

Alignment: not needed before ideation; the Captain asked for this fix before the release.
Release review: not needed: workflow maintenance, on no journey map.
Surfaces: none
Visible change: none

## Peers

- Peer: subspace-relay dev2 FO = Claude session 62aab0fa-e10d-40ce-a62c-07dcf7d48e04 (Captain named it); reports of #398 and #401 relayed through the Captain's chat, 2026-10-19.
- Peer: subspace-web dev2 FO = Paseo agent 295b873d-3038-42f3-9aae-1c3325e30e4d (envelope source-agent-id); report of #150, 2026-10-19, forwarded at the Captain's direction it quotes (「delivery_gate 直接轉給 plugin fo」).
