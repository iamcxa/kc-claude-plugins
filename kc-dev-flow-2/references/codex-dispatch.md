# Explicit Codex model binding

This opt-in source candidate wraps the installed, unchanged Spacedock CLI.
Select the packaged [version 1 policy](codex-model-policy-v1.json) by its absolute
path. Do not write model policy into global Codex configuration. With no selected
policy, Spacedock's existing host behavior remains in effect.

Read the current host's live `spawn_agent` schema and save a capability JSON with
`arguments` (the argument names) and `supported_models` (model names mapped to
supported reasoning levels). This is a local snapshot of that host, not a
portable model registry. The converter checks both against the requested binding.

For an ordinary stage, run the package wrapper with the existing Spacedock build
arguments after `--`. It resolves policy/capabilities before calling stock build,
including builds that stamp state:

```sh
python3 <package>/scripts/codex_dispatch.py build \
  --spacedock /absolute/stock/spacedock \
  --policy /absolute/package/references/codex-model-policy-v1.json \
  --capabilities /absolute/local/host-capabilities.json \
  -- --workflow-dir /absolute/project/workflow --stage implementation \
  --entity-path /absolute/project/task.md --checklist-file /absolute/checklist.txt
```

For a special role, use `<package>/scripts/codex_dispatch.py convert --policy FILE --capabilities
FILE --agent-file FILE --stage ROLE < helper.json`, naming its unchanged agent
declaration and the already assembled stock helper envelope.
Both inputs use the same resolver. Explicit `reasoning` wins over policy defaults;
the Engineering Reviewer and Chief Engineer keep their declared `xhigh`.
Agent text naming Claude Opus describes the original host; on this selected
Codex lane the policy resolves that declaration to the emitted Codex binding.
Do not edit the agent text or ask the child to change its own model.

Pass the resulting `spawn_args` object verbatim to native `spawn_agent`, including
`fork_turns="none"`, `model`, and `reasoning_effort`. The converter preserves
the helper's prompt string, including whitespace. A conversion failure is a hold:
do not spawn from the older null-model envelope or inherit the parent's settings.

Stamp the returned `binding` object into the FO's worker roster. Pass a prior
binding file with `--previous-binding` when checking reuse. `reuse=false` means
spawn fresh; `followup_task` cannot switch the live handle's settings.
`reuse=true` satisfies only model/policy compatibility, not lifecycle, stage,
ownership or completion freshness. Pass `--fresh` for independent validation;
an implementation worker must not become its own independent validator.

For an eligible existing worker, pass `--previous-binding FILE --target HANDLE`
to `build` before `--`, and stock `--advance` after it. The wrapper compares
policy/model/effort before invoking stock advance. A mismatch, missing target,
or `--fresh` refuses that advance before build; issue a fresh build without
`--advance` and without `--target` instead. A matching stock advance envelope
omits `name`; the converter emits `followup_args` with the intact stock pointer
and target, for native `followup_task`. It emits no spawn arguments in this case.
Do not use another handle to sidestep the comparison. FO must still check worker
ownership and its current completion epoch before reuse.

This candidate performs conversion only. FO owns dispatch, host metadata
verification, roster lifecycle and state. A generated payload is not runtime
proof. No installation, provider change, fallback or background service is added.

The stock Codex adapter still emits a null model and instructs immediate spawn.
There is no upstream plugin hook here: for this explicitly selected dev2 lane,
FO replaces that immediate spawn step with this wrapper and consumes its
`spawn_args` instead of the stock null-model transport. The wrapper retains the
original stock envelope as `stock_helper` for provenance; it does not alter its
prompt/name. The source agent's Claude wording is interpreted by this host
binding before native spawn. Stock Spacedock retains assignment assembly and
all state, gates and lifecycle rules.

Declaration reading is bounded to the adopted block-form workflow's `defaults`,
`states`, `name`, `model` and `reasoning` scalars. The wrapper reuses the package's
frontmatter reader for agents. Unrecognized model/reasoning scalars, anchors and
unsupported stage layouts refuse conversion; this is not a general YAML parser.
Without `--policy`, `build` delegates the supplied stock arguments and exit code
directly, leaving Claude/pi and unconfigured Codex behavior intact.
