# implementation-1

Dispatched: from workflow checkout at 6d344bcb6ced154fb1aeb3b4e362676c80aec443 (kc-claude-plugins, detached; the workflow README there was the 2026-10-08 copy, not the 0.21.0 sync)
Model: sonnet
Recorded: 2026-10-13, after the fact by FO; the original dispatch files were under /tmp/spacedock-dispatch/

## Checklist

PR 1 (kc-dev-flow-2): extensions/journey-map with EXTENSION.md, map_footprint.py add/check/audit/schema, contract-versions.json and test_map_footprint.py listed in the kc-dev-flow-2 tests workflow; AC-1 and AC-2 (footprint half) and AC-4 green with their falsifiers shown failing
PR 2 (kc-journey-map): source field through model.mjs, lib/schemas.mjs, journey-fold.mjs (splice only), journey-reconcile.mjs, tests, scripts/journey-dev2-loop-smoke.sh and its path-filtered workflow; AC-1/AC-2 (map half), AC-5 and AC-6 green, with the CI cost per PR measured or stated as not measured
Amendment 1 (Captain, 2026-10-13): the extension and the journey-map docs tell FO and readers where the contract's history lives (the schema command for the current table, the producer's release-please CHANGELOG for every version, ADRs for the first shape and each MAJOR) and when to read them; written as a new AC "Amended by Captain, amendment 1" with a check that can fail

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.20.0

Profile: pilot. Approved design: `## Design` as of the scope-one attempt, D1 and D2 as recommended, and Amendment 1 under `## Captain amendments`.

Delivery: two pull requests in iamcxa/kc-claude-plugins from branches off origin/main. Use Conventional Commit titles scoped to the plugin, for example `feat(kc-dev-flow-2): …` and `feat(kc-journey-map): …`. Open each as Draft. Do not bump versions; release-please owns them. Follow the repository CLAUDE.md commit rules: stage named files only, no empty commits.

This repository's workflow lists roborev, codex, copilot and learn. Run the roborev gate before each push, as the roborev extension says.

Stop and return to FO on any stop condition in the design's Slices paragraph.
