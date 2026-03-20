# Phase 7: Cleanup - Context

**Gathered:** 2026-03-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Delete dead code files and fix any dangling references. Original scope was 3 items (CLEAN-01, CLEAN-02, CLEAN-03) but Phase 6 proactively completed CLEAN-02 and CLEAN-03 during feature wiring, leaving only CLEAN-01.

</domain>

<decisions>
## Implementation Decisions

### Remaining work
- CLEAN-01 only: delete `app/frontend/components/chat-drawer.ts` (confirmed zero imports — orphan file)
- CLEAN-02 (dead `phases` variable): already removed in Phase 6 plan 06-02 task 3
- CLEAN-03 (sidebar Add Target): already wired in Phase 6 plan 06-02 task 3

### Verification approach
- After deletion: grep for any remaining references to `chat-drawer` across the codebase
- No typecheck needed (file has no importers) but run anyway to confirm no regressions

### Claude's Discretion
- Whether to also clean up `chat-panel.ts` if it depends on `chat-drawer.ts` (check imports first)

</decisions>

<canonical_refs>
## Canonical References

No external specs — requirements fully captured in REQUIREMENTS.md CLEAN-01 entry and decisions above.

</canonical_refs>

<code_context>
## Existing Code Insights

### Files to check
- `app/frontend/components/chat-drawer.ts` — the file to delete (0 importers confirmed)
- `app/frontend/components/chat-panel.ts` — check if it imports chat-drawer (may also be orphaned)

### Established Patterns
- Preact+HTM components use import maps (browser-side), TypeScript LSP errors for missing modules are expected and pre-existing

### Integration Points
- No integration needed — pure deletion

</code_context>

<specifics>
## Specific Ideas

No specific requirements — straightforward dead code removal.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 07-cleanup*
*Context gathered: 2026-03-20*
