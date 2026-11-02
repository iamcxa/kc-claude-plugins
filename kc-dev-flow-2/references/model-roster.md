# Repository stage workers

## Model table

<!-- see docs/adr/0049-special-roles-and-stage-defaults-follow-one-model-table.md -->

| Role | On Claude | On Codex |
|---|---|---|
| implementation | Sonnet / high | Sol / xhigh |
| chief-engineer | Opus / xhigh | Astra / xhigh |
| engineering-reviewer | Opus / xhigh | Astra / xhigh |
| design-director | Sonnet / high | Sol / xhigh |
| ideation | Opus / high | Astra / xhigh |
| validation | Opus / high | Astra / xhigh |
| observer | Sonnet / high | Sol / high |

For Codex, pass the model and Paseo `settings.thinkingOptionId` by hand.
Chief-engineer and engineering-reviewer run on a family other than the
implementation workers'. Stage-worker effort has no Spacedock dispatch field;
`dispatch-sets-reasoning-effort` owns that remaining seam.

## Adoption and introducing sync

Preserve an existing `.dev2/model-roster.json`; startup and ordinary sync do not
ask again or rewrite it. At adoption or introducing sync, run
`paseo provider ls --json | python3 <package>/scripts/model_roster.py question --code-root <absolute-code-worktree-root> --readme <workflow-README> --providers -`.
If Paseo is missing, pass empty input. Ask only on exit 0: the workflow lists
`paseo`, Codex and Claude are available, and no roster exists. Exit 3 skips;
exit 1 returns malformed input to FO. Otherwise ask nothing, write nothing and
retain README behavior; workers follow FO's family. Display the complete
[recommendation](model-roster-defaults.json) and ask through the host's question UI:

> Stage workers: ideation Opus/high on Claude, implementation Sol/xhigh and validation
> Astra/xhigh on Codex, all through Paseo. Save this shared repository choice or customize it?

Offer Accept and Customize. Preselection is not an answer. Cancel, empty response
or silence writes nothing, including no directory. Accept prepares the displayed
file; Customize collects each stage's exact tuple one at a time. Supported models
are `gpt-6-astra` and `gpt-6.1-sol` on `codex`, and `claude-opus-5-5` on `claude`,
with explicit `low`, `medium`, `high`, `xhigh`, `max` or `ultra` effort and host
`paseo`. `max` and `ultra` are accepted, not recommended; Claude's `ultra` is Paseo's
`ultracode`, a multi-agent mode. Other choices return to FO.
Set `selected_from` to the selected package version and `decision` to the explicit
answer reference; these are caller-recorded provenance, not authenticated consent.
Show the complete three-row candidate in the existing configuration review before
committing `<code-root>/.dev2/model-roster.json` through the repository's normal
change path. Explicit later edits or deletion take that same reviewed path.
Choosing Paseo does not enable its extension or grant access.

## Stage launch or continuation

Before record checks and Spacedock build, run
`python3 <package>/scripts/model_roster.py resolve --code-root <absolute-code-worktree-root> --stage <stage>`.
For validation repeat `--author-record <path>` for every contributing implementation
and repair record of the candidate, including continuations. Use the bound code
checkout, never cwd or the split-root state checkout. `repair` resolves the
implementation row. The command reads a clean committed snapshot, validates all
three rows and emits JSON; it writes no settings, state or dispatches.

Exit 0 with `source=readme-default` means absent: retain today's README model and
host behavior without a question or fabricated effort; workers follow FO's family. Exit 1 names invalid,
uncommitted, unreadable or unsupported present data: return it to FO; no fallback.
A committed deletion restores README behavior. Recommendations never update an
accepted snapshot. For configured settings use Paseo's route for the row's provider;
a native route request returns to FO. A `claude` row spawns in `auto` mode.

Keep `Model:` and add this header to the normal dispatch record, using resolver
values rather than copying the recommendation:

```text
Roster: source=repository; role=implementation; provider=codex; model=gpt-6.1-sol; effort=high; host=paseo; digest=sha256:DIGEST; commit=SHA
```

For absence use `Roster: absent; source README default`. For validation retain all
author references/tuples and `family` in the record and existing report/gate summary.
`same-family: openai` or `same-family: anthropic` means the validator and all
authors share a provider; otherwise `different-family`. These are informational,
not refusals or diversity claims. Missing/unknown author evidence is `unverified`.
The resolver understands these Roster headers and historical `Model: MODEL (Codex
via Paseo, thinking EFFORT;...)` headers; other formats remain unverified. Existing
names/folder/coverage/law checks remain due but do not prove roster consumption.

Preflight live provider/model/effort capability, listed extension eligibility,
workspace placement, permissions and existing worker identity before build.
Build with `--host` set to the row's provider. A generated Claude alias naming
the row's model family, such as `opus` for `claude-opus-5-5`, is no conflict.
Preserve generated prompt, identity and runtime fields. A non-null generated
model/effort conflicting with the tuple is a transport mismatch: return to FO,
never patch the envelope. Pass provider/model and emitted `thinking_option_id` as `settings.thinkingOptionId`
beside those fields on the existing Paseo route. After successful build immediately
spawn, then save its handle; checks and narration precede build.

A continuation resolves again and records its source. Reuse only when its effective
tuple matches the existing worker; changed tuples return to FO for authorized
fresh handoff, without mutating or duplicating a running worker. Capacity, network
and uncertain launches use current manual recovery, without model substitution.
Keep requested settings separate from supported child runtime/turn evidence of
actual model, effort, root and preserved permissions; for Claude use transcript
`model` and `perTurnEffort`. Echo or worker assertion alone is insufficient. Missing decisive evidence returns to FO.

FO and special roles retain current model floors, triggers and delivery duties,
including the Paseo worker-local commit and FO publication/review split. This
slice adds no personal store, capacity automation, new law,
native adapter or further provider.
