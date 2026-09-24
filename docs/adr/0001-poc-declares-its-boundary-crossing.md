# 0001. A kc-dev-flow-2 POC declares when its proof crosses the POC boundary

Date: 2026-09-24

## Status

Accepted

## Context

An adopting project ran a series of small POC-profile tasks, each framed as a
user step. Across them the code accumulated a cross-session mapping between
work items and agent sessions, patched onto an existing watcher. No task
admitted that state: every check passed, and the gap to the target architecture
surfaced only at the first explicit comparison.

On `main` at `e6c45768` (read 2026-09-24), `kc-dev-flow-2/references/profiles/poc.md`
stopped proof only on an exceeded limit or needed user intervention; `pilot.md`
has a "Return to profile selection if …" list, but POC had none. The baseline
kc-dev-flow keeps such a list in `choose-work-profile` § Promotion ("persistent
valuable state, … beyond-session operation, or retry/recovery duty"), but only
at profile selection; no later stage looks for a crossing. The existing
doc-impact and retained-document checks fire only on touched paths, so an
architecture held outside the repository never reaches them.

## Decision

**Words:** 「確認」 — Kent, 2026-09-24, accepting this record, drafted from the task brief he relayed: 「若本次 proof 產生任何需跨 session／跨回合保存的狀態，或建立了外部系統需長期維護的接縫（seam），視同越過 POC 邊界：停止 product proof，在回報中標記 `boundary-crossed: persistent-state`（附一句證據），並將此事實交回 planning 決定升級（Pilot+）或明確丟棄——不得在 POC 下繼續擴充此類工作。」

**Options considered:**
- a POC-declared `boundary-crossed:` report marker, raised by implementation and independently by validation, presented by FO at the existing validation gate
- a POC ideation stage or architecture gate — rejected; the package keeps POC at four stages
- a runtime check that blocks POC close — rejected; the package ships skill instructions, not mechanical gates
- POC preselecting Pilot — rejected; profile selection stays with the user

A POC whose proof creates state that must persist across sessions or turns, a
seam an external system must keep working, beyond-session operation or
retry/recovery duty stops extending that work and records `boundary-crossed:`
with its kind and one sentence of evidence. Validation checks for the crossing
independently. At the validation gate FO shows the marker and offers profile
selection or removal of the crossing work with recorded cleanup, and does not
recommend delivering that work as POC.

## Consequences

A crossing now has a named report field and a gate presentation, so it no
longer passes as an ordinary POC result. It still depends on a worker noticing
the state; nothing parses reports for it. Reopen if crossings are observed going unreported, or if an adopter
needs the POC to continue past a crossing without a profile change.
