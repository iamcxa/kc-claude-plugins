# Roadmap — kc-claude-plugins ship-flow

Workflow-level roadmap for ship-flow pitches in this repo.

<!-- section:now -->
## Now (in flight)

| Pitch | Title | Status | Appetite |
|-------|-------|--------|----------|
<!-- /section:now -->

<!-- section:next -->
## Next (shaped, ready to start when Now clears)

| Pitch | Title | Status | Appetite |
|-------|-------|--------|----------|
| 001-selector-grammar-alignment | e2e-pipeline selector grammar alignment (mapper ↔ agent-browser runtime) | (pitch) | medium-batch |
<!-- /section:next -->

<!-- section:later -->
## Later (ideas with potential, not yet shaped)

| TID | Size | Claim | Source |
|-----|------|-------|--------|
| ui-verify-text-strip-audit | S | Audit ui-verify text= strip-regex in skills/ui-verify/bin/run.js:208,218 — verify if intentional adapter; preserve, migrate, or unify with main pipeline. | pitch 001 |
| agent-browser-selector-grammar-doc | S | Pull canonical out-of-tree agent-browser CLI selector grammar reference into references/agent-browser-selector-grammar.md so future selector-engine drift is detectable. | pitch 001 |
| compiled-vs-llm-divergence-baseline | S | Add a compiled-vs-LLM divergence reporter; baseline current eval-fallback hit count per flow BEFORE 001.2 ships so the post-merge regression wave is bounded and explainable. | pitch 001 |
<!-- /section:later -->

<!-- section:not-doing -->
## Not Doing (explicitly rejected with reason)

| Claim | Reason |
|-------|--------|
| Switch runtime from agent-browser to Playwright wholesale (issue's option 2) | Loses agent-browser's CDP-only lightweight model (~50MB vs Playwright ~300MB); breaks existing CI compile path; abandons 50+ documented agent-browser invocations across 8 agents. High cost, low marginal value over option 1+3 hybrid. |
| Pure runtime translation layer with mapper still emitting Playwright forms (issue's option 3 standalone) | Leaves source-of-truth (e2e-mapper Selector Priority) emitting forms the runtime can't natively parse; translation hides the contract violation rather than fixing it; every selector-engine change becomes a translation-layer maintenance burden. |
| Document the mismatch as intentional and accept eval-fallback as canonical (issue's option labeled but explicitly rejected by author) | Silent false-positive risk persists; compiled-script divergence remains; defeats the purpose of having a deterministic compiled CI path. |
<!-- /section:not-doing -->

<!-- section:shipped -->
## Shipped

| Pitch | Title | Shipped At |
|-------|-------|------------|
<!-- /section:shipped -->
