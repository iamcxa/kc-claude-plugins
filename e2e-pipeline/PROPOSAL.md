# Proposal: RN Web snapshot limitation + unmapped page scale gap

## Signals

### Signal 1: RN Web a11y snapshot gap
- ID: sig-20260306-001
- Source: journal
- Date: 2026-03-06
- Confidence: high
- Related proxy signal: mapping-freshness

### Signal 2: Unmapped page scale gap
- ID: sig-20260306-002
- Source: journal
- Date: 2026-03-06
- Confidence: high
- Related proxy signal: flow-coverage

## Current State

1. **RN Web (Expo) a11y snapshot does not expose `data-testid` or `aria-label` attributes.** The e2e-mapper agent relies on snapshot for element discovery, but for RN Web apps, snapshot gives false confidence — selectors based on data-testid/aria-label will work in `is visible` but won't appear in snapshot output. There is no documented dual-verification strategy in the mapping workflow.

2. **When planning ambitious multi-page flows (~17 steps), approximately 15 unmapped pages were discovered.** The current mapping approach (map pages on demand) breaks down at scale — users don't know which pages are unmapped until they try to write a flow that references them. There is no "coverage map" showing mapped vs. unmapped pages.

## Suggested Changes

### Change 1: Dual-verification strategy for RN Web
Add to the e2e-mapper agent's mapping workflow:
- After snapshot-based element discovery, run `is visible` verification for each data-testid and aria-label selector
- Mark selectors that pass `is visible` but don't appear in snapshot as "DOM-only" in the mapping YAML
- Add a note in common-patterns.md explaining when to use snapshot vs. `is visible` for verification
- In flow YAML steps, use `type: verify` with `is visible` for DOM-only selectors instead of `type: snapshot`

### Change 2: Mapping coverage report
Add a new step to e2e-map skill:
- After mapping completes, scan the app's route table (from codebase or sitemap) and compare against mapped pages
- Output a coverage summary: `Mapped: 12/27 pages (44%). Unmapped: /booking/services, /booking/confirm, ...`
- Include this in the mapping YAML as a `coverage:` metadata section
- e2e-flow skill can use this to warn when a flow references an unmapped page

## Impact Scope
- Files likely affected: `agents/e2e-mapper.md`, `skills/e2e-map/SKILL.md`, `skills/e2e-flow/SKILL.md`, `references/common-patterns.md`
- Cross-plugin dependencies: none

## North Star Alignment
How this moves toward: "Browser E2E testing is fully automated — map UI, write flows, run tests, verify checkpoints — with zero manual selector maintenance"
- Dual-verification eliminates false confidence in RN Web mappings -> fewer broken flows
- Coverage report makes the unmapped gap visible -> users can prioritize mapping work
- Both changes move toward proactive maintenance rather than reactive discovery
