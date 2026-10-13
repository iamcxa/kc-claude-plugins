# ideation-3

Dispatched: from workflow checkout at 6d344bcb6ced154fb1aeb3b4e362676c80aec443 (kc-claude-plugins, detached; the workflow README there was the 2026-10-08 copy, not the 0.21.0 sync)
Model: sonnet
Recorded: 2026-10-13, after the fact by FO; the original dispatch files were under /tmp/spacedock-dispatch/

## Checklist

A scope-one design: a Captain ruling reaches the map (gate footprint -> archive fold -> docs-only map PR writing answer, status and source -> reconcile counts), with only the footprint schema and the map's question fields, and no renderer change
Each scope-one step keeps its one-command write, its gate line and its reconcile count; everything moved to task journey-map-progress-and-provenance is removed from this design and named there by pointer only
Acceptance criteria re-cut from AC-4, AC-5, AC-6 and the parts of AC-1 and AC-2 scope one needs, each with a reproducible evidence clause and falsifier, and D1 and D2 restated for the Captain within scope one

## Scope notes

Package root: /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.20.0

Profile: pilot. Variant: kc-dev-flow-2.

The Captain decided `revise` at the ideation gate. The recorded reason is in frontmatter: gate:journey-map-dev2-contract:ideation, resolution:spacedock:journey-map-dev2-contract:ideation:1. He accepted the direction and asked to narrow this task to scope one. Scope two is now task `journey-map-progress-and-provenance` (backlog). Its body lists what moved: the evidence ladder, ADR by reference with the `Map:` line, fold-pending marks and the UI preview, drawn-commit provenance, the tuple list form and story-id identity, the service seam, three schemas, and AC-3, AC-7, AC-8, AC-9 and AC-10.

Rewrite `## Design` and `## Acceptance criteria` for scope one. Keep the first attempt's measured facts that scope one still uses, such as the qnow baseline. Since no renderer change is planned, update `## FO alignment`'s Surfaces and Visible change lines only if your design shows they changed, and say so in the report. Surfaces belong to FO; propose the new lines in the report and do not edit them yourself. Move `preview/` content only by pointer; do not delete it.

Answer in the design whether scope two will have data as soon as scope one merges and is synced, given that relay and qnow are in active development. Base the answer on what scope one writes and when; do not guess.

Append a new `## Stage Report: ideation`; earlier reports stay. Send completion to team-lead.
