# Proposal: Add flow-writer agent role to e2e-pipeline

## Signal
- ID: sig-20260316-001
- Source: journal
- Date: 2026-03-16
- Confidence: high
- Related proxy signal: flow-coverage

## Current State
The e2e-pipeline has agents for mapping (e2e-mapper), testing (e2e-test-runner), verifying (e2e-flow-verifier), and analyzing (e2e-trace-analyzer). The e2e-flow-writer agent exists but is only dispatched during `/e2e-flow` skill invocations. There is no autonomous path from walkthrough observations to reusable flow YAML — the walkthrough produces observations and screenshots but requires manual authoring to convert them into executable flow files. This creates a gap where valuable walkthrough insights are never systematically captured as regression tests.

## Suggested Change
Extend the e2e-walkthrough skill to offer a "convert to flow" option at completion:
1. After walkthrough finishes, detect if the session produced navigations + interactions
2. Offer: "Convert this walkthrough to a reusable E2E flow?"
3. If accepted, dispatch e2e-flow-writer with the walkthrough step log as input
4. The flow-writer agent produces a draft flow YAML referencing the existing mapping
5. Save to `.claude/e2e/flows/` for future `e2e-test` execution

Alternatively, add a standalone `/e2e-flow --from-walkthrough <report-dir>` mode that reads a walkthrough report and generates flow YAML from the recorded steps.

## Impact Scope
- Files likely affected: `skills/e2e-walkthrough/SKILL.md` (add post-completion option), `agents/e2e-flow-writer.md` (extend input contract to accept walkthrough step logs)
- Cross-plugin dependencies: none

## North Star Alignment
How this moves toward: "Browser E2E testing is fully automated — map UI, write flows, run tests, verify checkpoints — with zero manual selector maintenance"
— Closing the walkthrough-to-flow gap means every exploratory session automatically produces regression test assets, moving from manual flow authoring to automated flow generation.
