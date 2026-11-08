# 0070. Stage worker dispatches are built by a package script that writes their record

Date: 2026-11-07

## Status

Accepted

## Context

Three sessions left dispatch records late, reconstructed or incomplete: the
kc-paseo-plugins batch r1b-polish-1 reconstructed its records after dispatch;
the qnow observer found an unrecorded addendum; the kc-plugin observers found
late and incomplete records in batches 14 and 15. The task
`dispatch-build-writes-the-dispatch-record` records those sources.

Spacedock 0.27.2 writes the dispatch artifact but not the task's dispatch record.
It has no dispatch hook and does not read the model roster. Its stamp commit
already includes the task folder, providing a seam for a package-owned writer.
ADR 0014 keeps the package and workflow preflight checks separate, and ADR 0027
places structured write checks at the write.

## Decision

**Words:** 「核准（建議）」 — Captain, host question dialog, 2026-11-07,
batch 17 ideation approval. The question's dispatch-record excerpt was
「派工紀錄 D1 用套件裡的派工腳本並新增一份決策紀錄（ADR）、D2 模型與名冊仍由我手填、D3 版本與工作流程檢查這次不併進腳本」;
it specified 「核准即接受每張設計對其決定寫下的建議。要改哪件直接說。」.
Source: the task's ideation gate resolution, attempt 1, recorded at
2026-11-07T15:37:23.875685Z on `spacedock-state/dev2`.

**Options considered:**
- Build through a package script that writes and checks the dispatch record,
  leaving Spacedock unchanged (chosen).
- Change upstream Spacedock: outside this package; no dispatch hook exists at
  the pinned version.
- Resolve model and roster inside the script: not chosen; retain FO-supplied flags.
- Include package-version and workflow-checkout checks: not chosen; retain their
  existing separate commands and Captain-facing holds.

**Recommended:** the package script, FO-supplied model and roster, and separate
package-version and workflow-checkout checks, as accepted by the Captain.

**Protects:**
- `kc-dev-flow-2/scripts/dispatch_stage.py` — `main`, the write/check/build order

FO builds stage-worker dispatches with `dispatch_stage.py`. It writes the record
from the build's checklist and scope-notes inputs, adds the supplied model and
workflow-checkout SHA, checks it, then builds. The stamp commit carries the record;
reuse-advance dispatches use `spacedock state commit` before returning the envelope.
Model and roster remain FO-supplied. The two pre-dispatch checks remain separate.

## Consequences

Record writing no longer depends on a separate manual step when FO uses the
script. This remains prose-enforced: Spacedock's skill still names its own
builder, and a direct call bypasses the writer. `dispatch_records.py --coverage`
still holds missing records after a worker report. Follow-up messages remain
manually recorded. A real-binary split-root test checks the stamp's commit seam.
Reopen on ADR 0014's condition: a dispatch-time hook in Spacedock.
