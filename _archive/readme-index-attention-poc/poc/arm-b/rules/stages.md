## Stages

Stage workers run on the workflow's default model.
`kc-dev-flow-2:chief-engineer`, `kc-dev-flow-2:engineering-reviewer` and
`kc-dev-flow-2:observer` run on the model and reasoning their agent files declare, never
a cheaper one. FO records each chief-engineer or engineering-reviewer call under the
task's `## FO alignment` as `Reviewer: <agent> <model> <date> — <question>`.

`concurrency` limits only what `status --next` proposes. A feedback-reflow repair and an
FO fix authorized under Review-finding disposition step 3 are dispatched at once in the
entity's own worktree, after the existing overlap check against running worktrees; they
do not wait for another entity's worker in the same stage. The validation recheck of
that repair or fix does not wait for another entity's worker either, but it is
dispatched only after the repair or fix has completed and committed its candidate, so
the validator reads the bytes that will be delivered. A repair that outgrows what its
assignment names returns to FO as a scope change.

FO resolves `<package>` in this workflow from the `Package root:` line of
`kc-dev-flow-2:dev`. Before each worker dispatch FO runs `python3 <package>/scripts/package_version.py
<this README>`; exit 1 means the session loaded an older package than this README was synced
from, and FO holds the dispatch until the session runs the newer one. FO also runs
`python3 <package>/scripts/workflow_checkout.py <this README>`, which compares this file with
`origin/<trunk>`'s: exit 1 means they differ, exit 2 that it could not compare, and FO
holds the dispatch and shows the Captain what the script printed. Every worker dispatch FO builds carries that absolute path as a
`Package root: <absolute path>` line in its scope notes (`--scope-notes-file`), which
land in the dispatch file the worker reads first. Those scope notes, and every follow-up
message to a live worker, also carry ``Send your completion message to `main` (the README's Dispatch
facts: `team-lead` is not registered here).``: the builder's completion block names `team-lead`, and a
worker that skips the stage-definition fetch does not see the Signal fact. FO saves those scope notes, the
checklist, the model it dispatches on and the SHA it dispatches from as
`<task>/dispatch/<stage>-<cycle>.md` in the state checkout (a `Dispatched:` line with
the full SHA, a `Model:` line, `## Checklist` and `## Scope notes` sections, and for validation a
`Candidate: <full head SHA>` line per head validated),
committed with that dispatch's `spacedock state commit <slug> --workflow-dir <dir>`, so
the instruction a worker followed outlives the session that wrote it. A follow-up
message to a worker FO resumes is a dispatch too, and its record carries the same parts, including the `Package root:` line and a checklist of the items that message asks, never a pointer to another record.
A checklist or scope-notes line that names a package script writes
`<package>/scripts/NAME.py` with the absolute root substituted, never the bare script
name; before `dispatch build`, FO runs `python3 <package>/scripts/dispatch_records.py --names <record>`
on the saved record and rewrites each name it lists. When `status --set` refuses to leave a stage, run `spacedock status --workflow-dir
<dir> --read <task> --stage <stage> --checklist`, return any line it reports as neither
DONE nor SKIPPED to the worker, and do not edit the worker's report. The refusal itself
does not say why; other causes are a missing evidence line or Summary and an uncommitted
report.

