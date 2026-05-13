# Learned Patterns

Cross-project patterns accumulated during plugin forge operations.

Curate periodically and PR valuable entries back to the origin repo.

---

## Tool output fabrication under context pressure (2026-04-06)

Agents under context pressure may construct plausible-looking tool outputs (like a timestamp-based handoff ID) instead of calling the actual tool. The fabricated output appears valid but breaks downstream consumers that depend on the tool-generated format. Found in kc-session-handoff: agent could fabricate a handoff ID from current timestamp instead of reading the journal tool's Path field.

**Applies to**: Any skill where a downstream consumer depends on tool-generated identifiers
**Action**: Red Flag the specific fabrication pattern + require the data come from a named tool field (e.g., "handoff ID MUST come from journal tool's `path` response, never from timestamp").

## Confirming the action is not directing the action (2026-04-06)

Agents conflate user confirmation of a state change (e.g., "yes, resume that session") with authorization to start working on a specific task. "Let's go" confirms the resume but doesn't specify which remaining item to execute. Found in kc-session-resume: agents treated "sure" as implicit direction to start the first remaining task.

**Applies to**: Any skill with a present-then-act pattern (show state → get direction → execute)
**Action**: Enumerate what counts as direction ("work on X", "start with the bug fix") vs. what only counts as confirmation ("ok", "let's go", "sure"). Require explicit task specification before starting work.
