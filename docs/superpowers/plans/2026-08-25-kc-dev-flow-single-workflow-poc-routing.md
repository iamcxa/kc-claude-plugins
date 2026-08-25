# KC Dev Flow Single-Workflow POC Routing Implementation Plan

> **Governing workflow:** REQUIRED SKILL: Use `kc-dev-flow:continue-dev-flow` with work item `single-workflow-poc-routing` (`ah`). At every stage, load the repository-local contract and let its Production route, Spacedock state, gates, and Captain authority govern. Only after the item reaches `implementation`, use `superpowers:subagent-driven-development` or `superpowers:executing-plans` as worker methodology inside the loaded build contract. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make POC a bounded exploration-or-proof route whose conclusion and Captain-owned handoff close safely inside the existing single workflow.

**Architecture:** Keep the current Spacedock graph and all three route slugs. Extend the profile loader to accept v3 receipts and enforce the four POC-only entry fields, then add one small wrapper that validates POC outcome and handoff receipts before delegating gate preparation, downstream creation, and gate consumption to Spacedock 0.27.0. Package and self-adopted copies remain byte-identical; prose skills explain the authority boundary but do not replace the executable checks.

**Tech Stack:** Python 3.9+, Markdown/YAML-shaped receipts parsed with the Python standard library, Spacedock 0.27.0 CLI, repository-native executable contract tests.

**Spec:** `docs/superpowers/specs/2026-08-25-kc-dev-flow-single-workflow-poc-routing-design.md`

## Global Constraints

- Keep the workflow graph `backlog -> ideation -> implementation -> validation -> done` unchanged.
- Keep Spacedock item `single-workflow-poc-routing` (`ah`) as the sole execution-state record; this plan is its shape artifact, not a parallel tracker.
- Complete and approve the Production shape gate before Task 1; reload the repo-local contract after every accepted transition.
- Superpowers may organize workers inside `implementation`; it never selects the profile, advances Spacedock, owns a gate, or grants merge/release authority.
- Keep the machine slugs `poc-exploration`, `pilot-product-slice`, and `production` unchanged.
- New profile choices use `kc-dev-flow-work-profile/v3`.
- The v4 loader accepts active v2 Pilot and Production receipts; it refuses active v2 POC receipts.
- A v3 POC requires exactly one non-placeholder `poc_decision`, `poc_falsifier`, `poc_budget`, and `poc_stop_when` value.
- Pilot and Production receipts carry no empty POC fields.
- Gate approval judges evidence quality; only the Captain authorizes downstream creation, deferral, or decline.
- A downstream delivery item starts at backlog, uses `source: poc:<exact-source-id>`, and has no work-profile receipt.
- Add no Explore workflow, Explore stage, fourth profile, Spacedock engine change, cross-entity transaction, model call, provider credential, new CI job, protected Environment, or release claim.
- Copy no file from `iamcxa/dev-flow-behavioral-gate-design`.
- Package and `docs/dev/_mods` copies of the loader, close guard, kernel, and profile contracts remain byte-identical where the contract test declares parity.
- Measure the incremental runtime inside the existing CI command before release; no CI-cost claim is allowed before measurement.
- Stop and return to the Captain when the diff exceeds 24 changed files, 1,200 changed lines, or 650 combined lines in `poc-close-guard.py` plus its test.

## File Map

| Responsibility | Files |
|---|---|
| Receipt parsing and selected-route loading | `kc-dev-flow/scripts/profile-contract-loader.py`, `kc-dev-flow/scripts/profile-contract-loader.test.py`, `docs/dev/_mods/profile-contract-loader.py` |
| POC close-path validation and Spacedock delegation | `kc-dev-flow/scripts/poc-close-guard.py`, `kc-dev-flow/scripts/poc-close-guard.test.py`, `docs/dev/_mods/poc-close-guard.py` |
| Real runtime and package/adopter contract | `kc-dev-flow/scripts/poc-close-guard.test.py`, `scripts/kc-dev-flow-multi-profile-gate.py`, `scripts/kc-dev-flow-minimal-stack-ablation.test.py`, `scripts/kc-dev-flow-contract-test.py` |
| Loaded POC behavior | `kc-dev-flow/references/kernel.md`, `kc-dev-flow/references/profiles/poc-exploration/{base,build,prove}.md`, matching files under `docs/dev/_mods/` |
| Routing and adoption instructions | `kc-dev-flow/skills/{choose-work-profile,continue-dev-flow,adopt-dev-flow}/SKILL.md`, `docs/dev/README.md` |
| User-facing contract and migration | `kc-dev-flow/README.md`, `kc-dev-flow/RATIONALE.md`, `kc-dev-flow/MIGRATION.md` |

## Where It Touches

`Lines after` is the shape estimate, not a target. Implementation stops on the
diff thresholds above even when a rewritten file retains its original length.

| Path | Lines now | Lines after |
|---|---:|---:|
| `kc-dev-flow/scripts/profile-contract-loader.py` | 298 | 330 |
| `kc-dev-flow/scripts/profile-contract-loader.test.py` | 1,070 | 1,190 |
| `docs/dev/_mods/profile-contract-loader.py` | 298 | 330 |
| `kc-dev-flow/scripts/poc-close-guard.py` | 0 | 230 |
| `kc-dev-flow/scripts/poc-close-guard.test.py` | 0 | 360 |
| `docs/dev/_mods/poc-close-guard.py` | 0 | 230 |
| `scripts/kc-dev-flow-multi-profile-gate.py` | 469 | 490 |
| `scripts/kc-dev-flow-minimal-stack-ablation.test.py` | 282 | 310 |
| `scripts/kc-dev-flow-contract-test.py` | 828 | 900 |
| `kc-dev-flow/README.md` | 151 | 180 |
| `kc-dev-flow/RATIONALE.md` | 126 | 140 |
| `kc-dev-flow/MIGRATION.md` | 190 | 235 |
| `kc-dev-flow/references/kernel.md` | 180 | 200 |
| `kc-dev-flow/references/profiles/poc-exploration/base.md` | 28 | 38 |
| `kc-dev-flow/references/profiles/poc-exploration/build.md` | 74 | 86 |
| `kc-dev-flow/references/profiles/poc-exploration/prove.md` | 48 | 80 |
| `kc-dev-flow/skills/choose-work-profile/SKILL.md` | 92 | 112 |
| `kc-dev-flow/skills/continue-dev-flow/SKILL.md` | 134 | 170 |
| `kc-dev-flow/skills/adopt-dev-flow/SKILL.md` | 156 | 175 |
| `docs/dev/README.md` | 318 | 370 |
| `docs/dev/_mods/kernel.md` | 180 | 200 |
| `docs/dev/_mods/profiles/poc-exploration/base.md` | 28 | 38 |
| `docs/dev/_mods/profiles/poc-exploration/build.md` | 74 | 86 |
| `docs/dev/_mods/profiles/poc-exploration/prove.md` | 48 | 80 |

## Accepted Journey

Every step below is **DESIGNED** until Task 3 runs it against Spacedock 0.27.0.

1. `profile-contract-loader.py` reads an exact work item and accepts a v3 POC only when its decision, falsifier, budget, and stop point are present and mechanically non-placeholder.
2. The implementation provider builds the shortest safe probe and records a `poc_outcome` in validation.
3. `poc-close-guard.py prepare` validates the exact v3 POC outcome, then invokes `spacedock gate prepare` for that item.
4. A Captain decision is recorded with raw `spacedock gate record` without `--consume`; approval spends no downstream-task authority.
5. For `stop` or `change`, the authorized actor records `poc_handoff.disposition: not_applicable`; `poc-close-guard.py consume` validates it, invokes `spacedock gate consume`, and the existing terminal merge guard completes the item.
6. For `proceed`, the Captain separately chooses `created`, `deferred`, or `declined`.
7. For `created`, `poc-close-guard.py create` queries `source=poc:<exact-source-id>` including archived items. Zero matches permits `spacedock new`, one returns the existing item for retry, and multiple stop without mutation.
8. The actor records the resolved exact downstream ID in `poc_handoff.to`; `consume` resolves one matching downstream item and refuses an orphan or duplicate before delegating to Spacedock.
9. The downstream item stays at backlog, starts from current trunk, and receives a separate Captain profile choice.
10. On command failure, the wrapper returns non-zero without consuming the POC gate. The exact work item remains the recovery record.

## Rollback and Release Boundary

- Before an adopter cuts over, active v2 POCs finish on its pinned 3.x loader/contracts or the Captain re-records them as v3.
- Rollback means restoring the previous package/vendor pair together; never pair a v4 guard with a v3 loader or vice versa.
- Release Please owns the 4.0.0 manifest and changelog bump. The first implementation commit carries a breaking-change footer; implementation does not hand-edit released version fields.
- The release check is the existing `marketplace-parity` job plus the manually approved release gate. This slice adds no workflow and no stochastic test.

---

### Task 1: Enforce v3 POC Entry Receipts

**Files:**
- Modify: `kc-dev-flow/scripts/profile-contract-loader.py:13-119`
- Modify: `kc-dev-flow/scripts/profile-contract-loader.test.py:32-260`
- Modify: `docs/dev/_mods/profile-contract-loader.py:1-298`
- Modify: `scripts/kc-dev-flow-contract-test.py:320-390`

**Interfaces:**
- Consumes: the exact work-item bytes and current `ROUTES` table.
- Produces: `resolve_work_item(path: Path) -> dict[str, str]` accepting v3 for every profile, v2 only for Pilot/Production, and returning the four POC fields for a v3 POC.
- Produces: `is_placeholder_scalar(value: str) -> bool`, shared later by the close guard through import rather than duplicated policy.

- [ ] **Step 1: Extend the fixture writer without changing production code**

Add optional receipt fields to `write_work_item`:

```python
def write_work_item(
    root: Path,
    profile: str,
    workflow_stage: str,
    name: str,
    *,
    schema: str = "kc-dev-flow-work-profile/v3",
    route: list[str] | None = None,
    sprint: str | None = "kc-dev-flow/S4",
    sprint_readiness: str | None = "ready",
    poc_fields: dict[str, str] | None = None,
) -> Path:
    if poc_fields is None and profile == "poc-exploration" and schema.endswith("/v3"):
        poc_fields = {
            "poc_decision": "Choose whether to fund the delivery slice",
            "poc_falsifier": "The integrated probe loses the accepted state",
            "poc_budget": "One local run and one review",
            "poc_stop_when": "Stop after the first integrated result",
        }
```

Render `poc_fields` directly below `basis`, preserving the dictionary order shown above.

- [ ] **Step 2: Add failing schema and mutation cases**

Add table-driven checks proving:

```python
required_poc_fields = (
    "poc_decision",
    "poc_falsifier",
    "poc_budget",
    "poc_stop_when",
)

invalid_values = (
    "",
    "   ",
    "null",
    "~",
    "TBD",
    "TODO",
    "<the next commitment this evidence decides>",
)
```

For each required field, delete it once and require a specific `exactly one <field>` refusal. For each invalid value, replace one field and require `<field> must be a concrete scalar`. Also prove duplicate fields refuse, a v2 POC at `implementation` refuses with `active v2 POC must finish on v3.x or be Captain re-recorded as v3`, and unchanged v2 Pilot/Production work.

- [ ] **Step 3: Run the focused test and observe RED**

Run:

```bash
python3 kc-dev-flow/scripts/profile-contract-loader.test.py
```

Expected: FAIL because the loader rejects v3 and still accepts an active v2 POC.

- [ ] **Step 4: Implement the minimal receipt rules**

Add these constants and helper:

```python
PROFILE_SCHEMA_V2 = "kc-dev-flow-work-profile/v2"
PROFILE_SCHEMA_V3 = "kc-dev-flow-work-profile/v3"
POC_FIELDS = ("poc_decision", "poc_falsifier", "poc_budget", "poc_stop_when")
NULL_LIKE = {"null", "~"}
PLACEHOLDER_WORDS = {"tbd", "todo"}


def is_placeholder_scalar(value: str) -> bool:
    normalized = value.strip().strip("\"'").strip()
    folded = normalized.casefold()
    return (
        not normalized
        or folded in NULL_LIKE
        or folded in PLACEHOLDER_WORDS
        or re.fullmatch(r"<[^>\n]+>", normalized) is not None
    )
```

In `resolve_work_item`, accept only v2 or v3. Refuse v2 when `profile == "poc-exploration"`. For a v3 POC, extract every `POC_FIELDS` member with `_one_field`, reject `is_placeholder_scalar(value)`, and include it in the returned receipt. Do not require or synthesize those fields for Pilot or Production.

- [ ] **Step 5: Run the focused test and observe GREEN**

Run:

```bash
python3 kc-dev-flow/scripts/profile-contract-loader.test.py
```

Expected: `profile contract loader test: PASS`.

- [ ] **Step 6: Update the adopted loader and repository fixture**

Apply the identical loader change to `docs/dev/_mods/profile-contract-loader.py`, then run:

Update `scripts/kc-dev-flow-contract-test.py`'s `write_profile_work_item` to emit v3, with the four fields only for POC. Add one explicit v2 Pilot and one explicit v2 Production load; require both to retain `receipt_schema == "kc-dev-flow-work-profile/v2"`.

```bash
cmp kc-dev-flow/scripts/profile-contract-loader.py docs/dev/_mods/profile-contract-loader.py
python3 scripts/kc-dev-flow-contract-test.py
```

Expected: `cmp` exits 0 and the current contract test passes.

- [ ] **Step 7: Commit the schema boundary**

Stage only the three files and commit:

```bash
git add kc-dev-flow/scripts/profile-contract-loader.py \
  kc-dev-flow/scripts/profile-contract-loader.test.py \
  docs/dev/_mods/profile-contract-loader.py \
  scripts/kc-dev-flow-contract-test.py
git commit -m "feat(kc-dev-flow)!: require bounded v3 POC receipts" \
  -m "BREAKING CHANGE: Active v2 POCs must finish on the pinned 3.x package/vendor pair or be Captain re-recorded with the v3 POC fields before the 4.x cutover."
```

### Task 2: Add the POC Close Guard

**Files:**
- Create: `kc-dev-flow/scripts/poc-close-guard.py`
- Create: `kc-dev-flow/scripts/poc-close-guard.test.py`
- Create: `docs/dev/_mods/poc-close-guard.py`

**Interfaces:**
- Consumes: `profile-contract-loader.py`'s `_one_field`, `is_placeholder_scalar`, and `resolve_work_item` functions.
- Produces: `parse_outcome(path: Path) -> PocOutcome` and `parse_handoff(path: Path) -> PocHandoff`.
- Produces: CLI subcommands `prepare`, `create`, and `consume`; all return 2 for a contract refusal and preserve the delegated Spacedock exit code for a runtime failure.

- [ ] **Step 1: Write parser refusal tests**

Create an executable standard-library test that imports the guard and builds exact v3 POC fixtures. Cover exactly one section and YAML root, allowed values, outcome/handoff compatibility, and required/empty fields:

```python
def require_refusal(text: str, phase: str, expected: str) -> None:
    item = write_poc(text)
    try:
        GUARD.validate(item, phase)
    except GUARD.CloseError as error:
        require(expected in str(error), f"wrong refusal: {error}")
        return
    raise SystemExit(f"POC close guard accepted {expected}")
```

Required rules:

```text
prepare: one poc_outcome; direction in proceed|stop|change; concrete evidence,
strongest_limit, reversal_fact, cleanup.
consume: all prepare rules plus one poc_handoff.
stop/change: disposition=not_applicable and empty to/reason.
proceed: disposition=created|deferred|declined.
created: concrete to and empty reason.
deferred/declined: empty to and concrete reason.
```

- [ ] **Step 2: Write fake-Spacedock delegation tests**

Create a temporary executable named `spacedock` that appends JSON-encoded argv/stdin to a log and emits controlled `status --json` results. Assert:

```python
prepare = run_guard("prepare", "--question", "Supported?", "--artifact", "review.md", "--summary", "POC")
require(prepare.returncode == 0, prepare.stderr)
require(logged_argv[-1][1:4] == ["gate", "prepare", POC_ID], "wrong prepare delegation")

consume = run_guard("consume")
require(consume.returncode == 0, consume.stderr)
require(logged_argv[-1][1:4] == ["gate", "consume", POC_ID], "wrong consume delegation")
```

Also make the fake return 42 for `new` and require the wrapper returns 42 without invoking `gate consume`.

- [ ] **Step 3: Run the new test and observe RED**

Run:

```bash
python3 kc-dev-flow/scripts/poc-close-guard.test.py
```

Expected: FAIL because `poc-close-guard.py` does not exist.

- [ ] **Step 4: Implement the receipt model and exact-section parser**

Create immutable records:

```python
@dataclass(frozen=True)
class PocOutcome:
    direction: str
    evidence: str
    strongest_limit: str
    reversal_fact: str
    cleanup: str


@dataclass(frozen=True)
class PocHandoff:
    disposition: str
    to: str
    reason: str
```

Implement `one_yaml_section(text, heading, root_key)` using the loader's existing exact-heading and fenced-YAML pattern. Use `_one_field` for required values. Add `_one_optional_field` with a `([^\n#]*)` capture so `to:` and `reason:` must each occur exactly once but may be intentionally empty. `validate(path, phase)` must call `resolve_work_item`, require v3 POC at `status: validation`, then apply the compatibility table above.

- [ ] **Step 5: Implement downstream identity and idempotency**

Use one query function:

```python
def find_downstream(spacedock: Path, workflow_dir: Path, source_id: str) -> list[dict[str, object]]:
    result = run_spacedock(
        spacedock,
        "status",
        "--workflow-dir", str(workflow_dir),
        "--where", f"source=poc:{source_id}",
        "--archived",
        "--all-fields",
        "--json",
        capture=True,
    )
    entities = json.loads(result.stdout).get("entities")
    if not isinstance(entities, list):
        raise CloseError("Spacedock status returned no entity list")
    return entities
```

`create` validates `direction: proceed`, reads a body file, requires exactly `source: poc:<source-id>`, refuses any `## Work profile receipt`, then applies zero/create, one/reuse, multiple/refuse. It prints one JSON object containing `disposition`, `id`, and `slug`; it never writes the POC item.

`consume` requires `created.to` to equal the exact ID of the sole source match. Deferred and declined dispositions never query or create an item. After validation, delegate only `spacedock gate consume <poc-id> --workflow-dir <dir>`.

- [ ] **Step 6: Run the guard tests and prove executable parity**

Run:

```bash
chmod +x kc-dev-flow/scripts/poc-close-guard.py kc-dev-flow/scripts/poc-close-guard.test.py
python3 kc-dev-flow/scripts/poc-close-guard.test.py
```

Expected: `POC close guard test: PASS`.

Apply the identical guard file under `docs/dev/_mods/`, then run:

```bash
cmp kc-dev-flow/scripts/poc-close-guard.py docs/dev/_mods/poc-close-guard.py
```

Expected: exit 0.

- [ ] **Step 7: Commit the close guard**

Stage only the three created files and commit:

```bash
git add kc-dev-flow/scripts/poc-close-guard.py \
  kc-dev-flow/scripts/poc-close-guard.test.py \
  docs/dev/_mods/poc-close-guard.py
git commit -m "feat(kc-dev-flow): guard POC outcome handoffs"
```

### Task 3: Prove the Real Spacedock Close Paths

**Files:**
- Modify: `kc-dev-flow/scripts/poc-close-guard.test.py:1-360`
- Modify: `scripts/kc-dev-flow-multi-profile-gate.py:105-470`
- Modify: `scripts/kc-dev-flow-contract-test.py:40-420`
- Modify: `scripts/kc-dev-flow-minimal-stack-ablation.test.py:1-282`

**Interfaces:**
- Consumes: the guard CLI from Task 2 and a resolved Spacedock 0.27.0 executable.
- Produces: deterministic local evidence for stop/change/proceed closure, idempotent creation, route preservation, and package/adopter parity.

- [ ] **Step 1: Add the guard to the package contract**

Add the close-guard files to `required`, require both package executables, run `poc-close-guard.test.py`, and assert package/adopter byte parity for `poc-close-guard.py`. Keep Task 1's v2 Pilot and Production compatibility cases unchanged.

- [ ] **Step 2: Convert route fixtures to v3 without changing topology**

In the multi-profile gate fixture, render:

```yaml
schema: kc-dev-flow-work-profile/v3
```

and add the four POC fields only when `profile == "poc-exploration"`. Keep `GRAPH_STATES`, `ROUTES`, and expected transitions byte-for-byte unchanged. Change assertions from receipt schema v2 to v3 for new fixtures.

- [ ] **Step 3: Add real-runtime close helpers**

Extend `poc-close-guard.test.py` with a split-root fixture that writes outcome and handoff sections, executes the guard against the resolved Spacedock binary, records approval without `--consume`, and finishes the existing terminal merge guard.

The test matrix is:

```python
cases = (
    ("stop", "not_applicable", "", ""),
    ("change", "not_applicable", "", ""),
    ("proceed", "deferred", "", "Captain deferred delivery"),
    ("proceed", "declined", "", "Captain declined delivery"),
)
```

Each case must reach archived `status: done` and must not create a source-linked item.

- [ ] **Step 4: Add created, retry, failure, and duplicate cases**

For a proceeding POC:

1. Invoke `create` with a backlog body containing the canonical source and no profile receipt.
2. Do not edit the POC yet; invoke the same command again and assert both JSON results name the same ID.
3. Query `source=poc:<poc-id>` and assert exactly one entity.
4. Record `disposition: created` and that exact ID; consume and finish the merge guard.
5. In a separate fixture, make downstream creation fail and assert the POC remains at validation with the approval pending.
6. In a separate fixture, seed two matching sources and assert `create` and `consume` both refuse without consuming the POC.

- [ ] **Step 5: Run focused tests and observe GREEN**

Run:

```bash
python3 kc-dev-flow/scripts/profile-contract-loader.test.py
python3 kc-dev-flow/scripts/poc-close-guard.test.py
python3 kc-dev-flow/scripts/profile-spacedock-route.test.py
python3 scripts/kc-dev-flow-multi-profile-gate.py --json
```

Expected: every command passes; the gate reports all three profiles and `terminal: all profiles reached done`.

- [ ] **Step 6: Mutation-prove the new guards**

Temporarily mutate one assertion target at a time in a temporary repository copy, never the working tree:

```bash
python3 scripts/kc-dev-flow-minimal-stack-ablation.test.py
```

Extend the copied-fixture mechanism with two ablations. Required observed failures are: one missing POC field passes only when the loader check is removed, and one missing handoff passes only when the close-guard invocation is removed.

- [ ] **Step 7: Commit the runtime proof**

Stage only the tests changed in this task and commit:

```bash
git add kc-dev-flow/scripts/poc-close-guard.test.py \
  scripts/kc-dev-flow-multi-profile-gate.py \
  scripts/kc-dev-flow-contract-test.py \
  scripts/kc-dev-flow-minimal-stack-ablation.test.py
git commit -m "test(kc-dev-flow): prove recoverable POC closure"
```

### Task 4: Publish the Single-Workflow Contract and Migration

**Files:**
- Modify: `kc-dev-flow/README.md:1-151`
- Modify: `kc-dev-flow/RATIONALE.md:1-126`
- Modify: `kc-dev-flow/MIGRATION.md:1-190`
- Modify: `kc-dev-flow/references/kernel.md:34-101`
- Modify: `kc-dev-flow/references/profiles/poc-exploration/base.md:1-28`
- Modify: `kc-dev-flow/references/profiles/poc-exploration/build.md:1-74`
- Modify: `kc-dev-flow/references/profiles/poc-exploration/prove.md:1-48`
- Modify: `kc-dev-flow/skills/choose-work-profile/SKILL.md:11-92`
- Modify: `kc-dev-flow/skills/continue-dev-flow/SKILL.md:10-121`
- Modify: `kc-dev-flow/skills/adopt-dev-flow/SKILL.md:18-119`
- Modify: `docs/dev/README.md:30-318`
- Modify: matching `kernel.md` and POC profile files under `docs/dev/_mods/`

**Interfaces:**
- Consumes: the exact v3 and guard behavior proven in Tasks 1-3.
- Produces: one consistent adopter contract for choosing, loading, closing, migrating, and rolling back POC work.

- [ ] **Step 1: Add failing prose contract assertions**

In `scripts/kc-dev-flow-contract-test.py`, require normalized text for:

```text
Load development constraints in proportion to work risk, so agent behavior is just sufficient without losing verification or authority boundaries.
Could credible negative evidence cancel or materially change the next commitment this item asks the Captain to accept?
POC — bounded exploration or technical proof.
kc-dev-flow-work-profile/v3
poc_decision
poc_falsifier
poc_budget
poc_stop_when
poc_outcome
poc_handoff
source: poc:<exact-source-id>
```

Also refuse `Explore workflow`, `Explore stage`, a fourth profile, and any instruction to use `gate record --consume` for a POC validation gate.

- [ ] **Step 2: Run the contract test and observe RED**

Run:

```bash
python3 scripts/kc-dev-flow-contract-test.py
```

Expected: FAIL on the first missing new contract phrase.

- [ ] **Step 3: Update the loaded POC contracts**

Make the kernel say that new choices are v3, active v2 Pilot/Production remain loadable during cutover, and active v2 POC fails closed. Define POC as bounded exploration or technical proof and keep the existing authority and promotion boundaries.

Make `base.md` own the fixed decision/falsifier/budget/stop boundary, `build.md` own the shortest safe real probe and stop behavior, and `prove.md` own the exact `poc_outcome` fields plus the distinction between evidence approval and downstream authority. Keep conditional-reference JSON and typed observation JSON unchanged.

- [ ] **Step 4: Update routing and close-path skills**

`choose-work-profile` asks the negative-evidence question first. A yes recommends POC; a no compares existing Pilot/Production risks. Its candidate receipt uses v3 and emits the four POC fields only for POC.

`continue-dev-flow` invokes the adopted `poc-close-guard.py` for POC validation prepare/create/consume operations, records gate approval without consume, and leaves terminal merge handling with the adopted delivery authority. It must state that a raw Spacedock call can bypass the procedure and that the claim is only about the declared KC Dev Flow close path.

`adopt-dev-flow` vendors the guard beside the loader, binds both paths in `## Local Profile`, and requires a close-path smoke in addition to profile-stage loader parity. It installs no second workflow or state holder.

- [ ] **Step 5: Update README, rationale, migration, and local adoption**

Put the subtitle immediately below `# KC Dev Flow`. Change the route table's POC result to a supported decision, show proceed/stop/change and post-approval create/defer/decline in the Mermaid chart, and state that Explore is a use of POC.

Add the bounded evidence claim to `RATIONALE.md`; do not claim POC always improves development. Replace the top 3.x-to-4.x migration order with: inventory active receipts, finish/re-record v2 POCs, vendor loader/guard/contracts atomically, switch new choices to v3, run all loader and close-path checks, then update the installed plugin. State the paired rollback order.

Update `docs/dev/README.md`'s Local Profile to bind `_mods/poc-close-guard.py`, update its task example to v3 without empty POC placeholders, and document the attended POC terminal sequence.

- [ ] **Step 6: Apply adopted-copy parity and observe GREEN**

Apply identical edits to the adopted kernel and three POC profile contracts, then run:

```bash
cmp kc-dev-flow/references/kernel.md docs/dev/_mods/kernel.md
for file in base.md build.md prove.md; do
  cmp "kc-dev-flow/references/profiles/poc-exploration/$file" \
    "docs/dev/_mods/profiles/poc-exploration/$file"
done
python3 scripts/kc-dev-flow-contract-test.py
```

Expected: every `cmp` and the full contract test pass.

- [ ] **Step 7: Commit the public contract**

Stage only the files listed in this task and commit:

```bash
git add kc-dev-flow/README.md \
  kc-dev-flow/RATIONALE.md \
  kc-dev-flow/MIGRATION.md \
  kc-dev-flow/references/kernel.md \
  kc-dev-flow/references/profiles/poc-exploration/base.md \
  kc-dev-flow/references/profiles/poc-exploration/build.md \
  kc-dev-flow/references/profiles/poc-exploration/prove.md \
  kc-dev-flow/skills/choose-work-profile/SKILL.md \
  kc-dev-flow/skills/continue-dev-flow/SKILL.md \
  kc-dev-flow/skills/adopt-dev-flow/SKILL.md \
  docs/dev/README.md \
  docs/dev/_mods/kernel.md \
  docs/dev/_mods/profiles/poc-exploration/base.md \
  docs/dev/_mods/profiles/poc-exploration/build.md \
  docs/dev/_mods/profiles/poc-exploration/prove.md
git commit -m "docs(kc-dev-flow): route exploration through bounded POC"
```

### Task 5: Verify Scope, Runtime, and Release Inputs

**Files:**
- Modify only if a discovered contract gap requires it: files already owned by Tasks 1-4.
- Evidence only: `.context/` timing and verification logs, never committed.

**Interfaces:**
- Consumes: the exact implementation head from Tasks 1-4.
- Produces: exact-head local evidence, measured incremental CI runtime, rollback readiness, and a clean handoff for review/PR creation.

- [ ] **Step 1: Measure the existing CI command on base and head**

Use a temporary clean worktree at the plan's recorded base and the implementation worktree at head. Run each three times:

```bash
/usr/bin/time -p python3 scripts/kc-dev-flow-contract-test.py
```

Record all six `real` values and the median delta in `.context/kc-dev-flow-s4-runtime.md`. Do not convert runtime to dollars. If the head median adds more than 20 seconds, stop and identify the exact test responsible before release.

- [ ] **Step 2: Run the complete deterministic stack**

Run:

```bash
python3 scripts/kc-dev-flow-contract-test.py
python3 scripts/kc-dev-flow-minimal-stack-ablation.test.py
python3 scripts/kc-dev-flow-multi-profile-gate.py --json
./scripts/release-metadata.test.sh
./scripts/version-parity-check.sh
./scripts/skill-frontmatter-lint.test.sh
./scripts/skill-frontmatter-lint.sh
```

Expected: all pass. The multi-profile gate remains manual/release-scoped; no model call occurs.

- [ ] **Step 3: Audit shape stop numbers and scope exclusions**

Run:

```bash
git diff --stat origin/main...
git diff --numstat origin/main... -- \
  kc-dev-flow/scripts/poc-close-guard.py \
  kc-dev-flow/scripts/poc-close-guard.test.py
git diff --name-only origin/main...
```

Stop rather than continue if any global stop number is crossed. Also require no changed path under the behavioral-gate laboratory, no new workflow file, and no edit to Spacedock's graph state list.

- [ ] **Step 4: Self-review against every acceptance criterion**

For each of the design spec's 11 acceptance criteria, name one passing command or exact document section. Mark probabilistic profile-effect evidence and a release canary explicitly out of scope; neither may be inferred from this slice's green tests.

- [ ] **Step 5: Confirm repository and release state before handoff**

Run:

```bash
git status --short --branch
git log --oneline origin/main..HEAD
gh pr list --state open --head iamcxa/dev-flow-explore-router
```

Expected: only intended commits, no uncommitted files, and no duplicate open PR. Verify Release Please will propose 4.0.0 from the breaking commit while leaving current plugin and marketplace versions at identical 3.0.0 before that release PR.

- [ ] **Step 6: Request implementation review and PR authority**

Present the exact head, stop-number result, test receipts, measured median runtime delta, and rollback boundary. Do not push, create a PR, make it ready, merge, or release without the Captain's corresponding authority. Default any authorized PR to Draft.
