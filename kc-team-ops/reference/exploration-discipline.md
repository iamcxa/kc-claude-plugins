# Exploration Discipline

When user asks to skip exploration ("spec is detailed enough", "just draft from the description"):

1. **Explain the risk**: codebase drifts from mental models, file paths go stale, hidden dependencies get missed
2. **User may override** after hearing the risk — they own the decision
3. **Never silently reduce** to a "spot-check" compromise

## Rationalization Table

| Rationalization | Why it's wrong |
|----------------|---------------|
| "Spec already has file paths" | Paths go stale; dependencies aren't in specs |
| "Quick spot-check of 2-3 files" | Spot-check is a compromise disguised as diligence |
| "I'll explore later if needed" | Later never comes; the comment is already posted |
| "Explorer will just confirm what we know" | Then it costs nothing; if it finds surprises, it saved the comment |
| "Code explorer is enough, docs are secondary" | Docs layer catches guideline updates that code-only misses; missing guideline update = regression |
| "I know which skills apply" | Skills change across projects; scan dynamically or miss project-specific ones |

## 🟢 Quick Depth Exemption

Skipping exploration is **not** a discipline violation when ALL of these conditions are met:

1. `em-lens-scanner` ran and returned **credibility HIGH** (file paths verified in codebase)
2. Symptom signal is **low** (issue has repro steps or identifies specific trigger)
3. User **explicitly accepted** 🟢 Quick depth (not defaulted, not auto-assigned)

If any condition is not met, exploration discipline applies in full. Quick depth is the only valid exemption — there is no "partial exploration" path.

### Quick Does Not Mean Unimportant

Quick means "context is already clear enough." The EM Lens entry scan verified the issue's factual accuracy against the codebase. Exploration adds architectural understanding — which small, well-described issues don't need.

### Red Flag

If you find yourself wanting to apply Quick to avoid slow exploration on a complex issue → STOP. That's the "I'll explore later" rationalization from the table above. Quick is for genuinely simple, well-described, unaligned issues.
