# Explicit Codex model binding

This opt-in dev2 source candidate wraps unchanged stock Spacedock. Select the
reviewed package by its absolute path; a fresh conversation must read this file
from that source, not an older installed cache. No installation is needed for
this source trial. Without `--policy`, `build` passes stock stdin, arguments,
stdout, stderr and exit code through, including Claude/pi/unconfigured Codex.

## First use

Prerequisites: Python 3, an adopted block-form Spacedock workflow, the reviewed
package checkout, an unchanged stock Spacedock executable, a writable evidence
directory outside the workflow's scanned dispatch records, and native host tools
that accept explicit model/effort arguments. The First Officer (FO) owns native
calls, task state, worker registration, lifecycle and reuse eligibility.

Define these operator inputs once, replacing every placeholder with a real
absolute path. The task and workflow may use a separate state checkout.

```sh
DEV2_PACKAGE=/absolute/reviewed/repo/kc-dev-flow-2
DEV2_STOCK=/absolute/stock/spacedock
DEV2_WORKFLOW=/absolute/project/workflow
DEV2_ENTITY=/absolute/state/task/index.md
DEV2_EVIDENCE=/absolute/local/evidence
DEV2_POLICY="$DEV2_EVIDENCE/policy.json"
DEV2_CAPS="$DEV2_EVIDENCE/host-capabilities.json"
DEV2_CHECKLIST="$DEV2_EVIDENCE/checklist.txt"
DEV2_SCOPE="$DEV2_EVIDENCE/scope.txt"
cd "$DEV2_PACKAGE/.."
```

Record the package source/commit and stock executable hash/version. Read the
current host's live `spawn_agent` schema, recording where/when it was read, and
save a capability JSON with `arguments` (argument names) and `supported_models`
(model names mapped to supported reasoning levels). For example, only if the
current schema actually supports these values:

```json
{"arguments":["task_name","message","fork_turns","model","reasoning_effort"],
 "supported_models":{"gpt-6.1-sol":["high"]}}
```

This snapshot is caller-supplied input, not proof of execution. Missing host
tools, unsupported values or unavailable raw metadata hold dispatch.

The packaged [version 1 policy](codex-model-policy-v1.json) maps haiku/luna,
sonnet/sol and opus/astra; implementation defaults to medium and the other
listed stages to high. Explicit declaration reasoning wins. To exercise an
approved ordinary-stage Sol/high pilot, copy the policy to `DEV2_POLICY`, give
it a distinct local `id`, and set the used stages' `reasoning_defaults` to
`high`. Keep the packaged file, agent/stage declarations and global config
unchanged. An explicit xhigh role still requests xhigh; do not launch such a role
in a high-only cohort or silently replace it with another worker/model.

Write the real task's checklist and bounded scope to the named files. For an
ordinary stage, wrapper options precede `--`; stock build options follow it:

```sh
python3 kc-dev-flow-2/scripts/codex_dispatch.py build \
  --spacedock "$DEV2_STOCK" --policy "$DEV2_POLICY" --capabilities "$DEV2_CAPS" \
  --stock-output "$DEV2_EVIDENCE/initial-stock.json" -- \
  --workflow-dir "$DEV2_WORKFLOW" --stage implementation \
  --entity-path "$DEV2_ENTITY" --checklist-file "$DEV2_CHECKLIST" \
  --scope-notes-file "$DEV2_SCOPE" > "$DEV2_EVIDENCE/initial-wrapper.json" \
  2> "$DEV2_EVIDENCE/initial-stderr.txt"
```

Check exit 0 before consuming output. Add ordinary stock stamping/worktree flags
only as the adopted workflow and task authorize; they can mutate task state.
Preflight resolves policy/capabilities before stock is called. `--stock-output`
retains raw stock stdout, including malformed/nonzero output, at the supplied
path. Use distinct evidence paths per attempt; retain stderr and the command's
exit separately. A write failure after stock ran can also leave partial state.

For special roles, use the same resolver and the unchanged agent declaration:

```sh
python3 kc-dev-flow-2/scripts/codex_dispatch.py convert \
  --policy "$DEV2_POLICY" --capabilities "$DEV2_CAPS" \
  --agent-file "$DEV2_PACKAGE/agents/engineering-reviewer.md" \
  --stage engineering-reviewer < /absolute/local/stock-helper.json
```

Chief Engineer and Engineering Reviewer retain their declared xhigh. Their
original Claude wording is interpreted by this explicitly selected Codex binding;
FO never asks a child to change its own model.

## Native dispatch and evidence

On this selected lane FO replaces the stock Codex adapter's immediate null-model
spawn step with the wrapper's emitted `spawn_args`, passed verbatim to native
`spawn_agent`, including `fork_turns="none"`, `model` and `reasoning_effort`.
The wrapper keeps the stock prompt string (including whitespace) and helper name
in `stock_helper`/`helper_name`; it normalizes only native `task_name` as before.
No upstream hook or second scheduler is introduced. Do not dispatch the older
stock null-model envelope when selected conversion fails.

Keep a small evidence index linking the source/candidate, exact command/input
paths, policy id/digest, capability provenance, stock envelope, wrapper output,
native call/returned handle and raw host session path/turn id. Retain the raw
request and its tool result under the same `call_id`. Stamp `binding`
into the existing FO roster with canonical entity path, stage, code worktree,
branch and completion epoch. Preserve requested declaration, resolved arguments
and observed model/effort separately. A pending transport receipt is unverified;
FO must compare actual host metadata before accepting execution. Retain raw
metadata for independent checking, without copying credentials or tokens.

The evidence helper requires complete native request arguments to equal the
wrapper's `spawn_args`/`followup_args`, including `message`. It also requires one
raw result after that request with the same `call_id`. For this native
collaboration host, spawn returns a JSON object containing `task_name`; it must
match the recorded handle and raw child identity/parent session. Successful
followup has empty result output, corroborated by the child's new turn and unique
acknowledgement. Missing, duplicate, error, wrong-handle or unknown result shapes
hold. A matching request alone is not proof that the host accepted it.

If the host stores `message` encrypted or omits it, the helper exits nonzero with
`HOLD`: exact payload equality is unverified even when the returned handle and
model/effort match. Obtain a supported host view of actual plaintext tied to the
same `call_id`; a requested payload receipt or child marker cannot replace that
proof. Do not manufacture plaintext, decode using private keys or silently mark
the limited evidence complete. Preserve the verified parts and the remaining gap
for independent validation; no new dispatch or retry is implied.

## Compatible continuation

A prior binding satisfies only model/policy compatibility. Before building or
sending, FO must verify the same canonical entity, stage, registered worktree,
branch and live addressable producer handle, completion epoch and authorized
remaining work. Reject any tuple mismatch before the wrapper/native call.
`followup_task` cannot change the live handle's settings. Independent validation
always builds fresh with `--fresh`, a separate handle and its own observed metadata.

For an eligible producer's bounded completion check, retain its original binding
as a JSON object in `prior-binding.json`. The real entity must still owe this
check at the same stage; do not clear completion or advance state first. Put the
exact ownership tuple, candidate, unique reply marker and no-product-edit scope
in the completion checklist/scope files, then build:

```sh
python3 kc-dev-flow-2/scripts/codex_dispatch.py build \
  --spacedock "$DEV2_STOCK" --policy "$DEV2_POLICY" --capabilities "$DEV2_CAPS" \
  --previous-binding "$DEV2_EVIDENCE/prior-binding.json" --target "$DEV2_PRODUCER" \
  --stock-output "$DEV2_EVIDENCE/followup-stock.json" -- \
  --workflow-dir "$DEV2_WORKFLOW" --stage implementation --entity-path "$DEV2_ENTITY" \
  --checklist-file "$DEV2_CHECKLIST" --scope-notes-file "$DEV2_SCOPE" --advance \
  > "$DEV2_EVIDENCE/followup-wrapper.json" 2> "$DEV2_EVIDENCE/followup-stderr.txt"
```

Define `DEV2_PRODUCER` as that exact registered handle, not a display name. Never
combine `--advance` and `--stamp`. Pass emitted `followup_args` unchanged to
native `followup_task`. It contains the intact stock pointer and target, with no
spawn arguments. Retain the call, returned acknowledgement/marker, new host turn,
completion epoch, unchanged candidate and before/after state/worktree ownership.
Save raw entity snapshots before/after the check so later validation can compare
the implementation state after the normal task transition.
A disposable positive fixture cannot prove continuation of the real producer.

## Holds and recovery

| Failure | Next operator action |
| --- | --- |
| Missing/malformed policy, capabilities or prior binding | Correct the named local input and rerun preflight. |
| Unsupported model/effort or missing native argument | Confirm the live schema/support; hold at the fixed model. |
| Advance binding/policy mismatch, absent target or `--fresh` | After FO confirms fresh-worker eligibility, build fresh without `--advance` and without `--target`. |
| Wrong/stale ownership tuple or uncertain native completion | Reconcile task/roster/host status before any send. Never silently replace a handle or resend. |
| Stock nonzero or successful output that cannot convert | Consume no dispatch arguments. Preserve exit/stderr/raw stdout; inspect stock state and dispatch artifacts before rebuilding. Stock may already have written partial state. |
| Capacity or observed model/effort mismatch | Hold and report; no model fallback, inherited null-model dispatch or automatic retry. |

Diagnostics advise and grant no recovery authority. Evidence paths are local and
must be supplied to a validator; missing raw evidence remains unverified.

## Local verification

Run the focused tests from a complete reviewed checkout:

```sh
python3 kc-dev-flow-2/scripts/test_codex_dispatch.py
python3 kc-dev-flow-2/scripts/test_codex_model_policy.py
python3 kc-dev-flow-2/scripts/test_sd_dispatch.py --sd-plugin-root /absolute/active/spacedock
```

The focused tests exercise mapping, advance refusal before stock, malformed
inputs, failure output retention and real-process stdin/argument/exit passthrough
for Claude, pi and Codex. Disposable evidence fixtures also reject changed native
messages and missing/error/duplicate/wrong-handle results, and hold opaque content;
their plaintext success control proves only the verifier, not actual host use.
They do not call a model. Run the small
`<package>/scripts/check_codex_dispatch_evidence.py --help` route with explicit candidate, baseline
and FO receipts to reconcile protected bytes and actual pilot continuation;
its raw host log access is a declared machine-local prerequisite. A fresh
independent validator repeats these checks and challenges the supplied evidence.
Green deterministic tests alone do not prove native spawn or continuation.

Declaration reading remains bounded to adopted block-form `defaults`, `states`,
`name`, `model` and `reasoning` scalars and the existing agent frontmatter reader.
Unrecognized scalars, anchors and unsupported layouts refuse; this is not a
general YAML parser. The wrapper performs conversion only, preserving stock
assignment assembly, all gates, lifecycle and delivery authority.
