# e2e-pipeline selector grammar alignment (mapper ↔ agent-browser runtime) — Spec

## Problem

The e2e-mapper agent emits Playwright-style selector strings (role=tab[name=...], >> nth=N, text=, has-text()), but e2e-test-runner shells out to agent-browser CLI which uses Chrome/Chromium via CDP and only parses CSS / @eN snapshot refs / its find role|text|testid|label semantic-locator subcommand. Mappings produced by /e2e-map therefore pass /e2e-test only via the runner's eval-based DOM fallback — silent false positives. Compiled deterministic scripts via e2e-compile.js lack that fallback and would fail systemically once the eval crutch is removed. The compiler's selectorToA11yPattern() partially mitigates, but the mapper-to-runner contract was never formalized.

## Acceptance Outcome

After /e2e-map over a Recce-style app, every selector in the resulting mapping is one the agent-browser CLI parses without eval fallback — verified by running each selector through agent-browser is visible / wait / click directly and getting non-zero/visible/found responses. Compiled scripts via e2e-compile execute the same flows end-to-end without the _poll_visible eval fallback being the only thing keeping them green. Captain observes runner-reported eval-fallback hit count = 0 on a fresh /e2e-map → /e2e-test run.

## Appetite

medium-batch

## Children

- 001.1-mapper-emit-native
- 001.2-runner-consumer-alignment
- 001.3-compiler-fixture-migration

## Assumptions

(fill in at shape stage)

## Rabbit Holes

- ui-verify-text-strip-audit
- agent-browser-selector-grammar-doc
- compiled-vs-llm-divergence-baseline

## Deletes

(fill in from deleted_from_shape)
