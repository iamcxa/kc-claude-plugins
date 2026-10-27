---
title: The journey-extension install probe finds maps in nested product folders
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: validation
gates:
    version: 1
    records:
        - id: gate:journey-probe-finds-nested-maps:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:journey-probe-finds-nested-maps-backlog-1
              briefing:
                id: briefing:journey-probe-finds-nested-maps:backlog:attempt-1:revision-1
                digest: sha256:f3a012ccc0de1f03a67e45fc1124106055aa0816db1921076d713a47d5666f60
                room-ref: ./journey-probe-finds-nested-maps/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:journey-probe-finds-nested-maps:backlog:1
                briefing: briefing:journey-probe-finds-nested-maps:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-27T15:13:21.741603Z"
                decision: approve
                reason: Captain 「全准」 (chat, 2026-10-27) answering 「需要你決定：第 8 批 7 張任務的待辦關卡，要不要一起批准進入設計階段？同時把已經做完的 `peers-paseo-host-binding` 關掉。我建議全部批准，也關掉那張。」; accepts FO's recommendation
              application:
                target-stage: ideation
                state: consumed
        - id: gate:journey-probe-finds-nested-maps:ideation
          stage: ideation
          attempts:
            - id: gate-attempt:journey-probe-finds-nested-maps-ideation-1
              briefing:
                id: briefing:journey-probe-finds-nested-maps:ideation:attempt-1:revision-1
                digest: sha256:96acd95aae57b402d16244041075f269a7d395b73f58c6fe66c342cef2cc1eaf
                room-ref: ./journey-probe-finds-nested-maps/review/ideation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:journey-probe-finds-nested-maps:ideation:1
                briefing: briefing:journey-probe-finds-nested-maps:ideation:attempt-1:revision-1
                by: person:captain
                at: "2026-10-27T15:56:36.035887Z"
                decision: approve
                reason: Captain 「其他全照建議」 (chat, 2026-10-27) answering 「需要你決定：第 8 批的設計，照首席工程師的建議一起處理，可以嗎？6 張進入實作，1 張直接關掉，再送一份 issue 給 Spacedock。我和首席工程師都建議照這樣做。」, after he declined a second, unanchored batch review (「不須要」); accepts FO's recommendation
              application:
                target-stage: implementation
                state: consumed
started: 2026-10-27T16:00:15Z
worktree: .worktrees/spacedock-ensign-journey-probe-finds-nested-maps
pr: iamcxa/kc-claude-plugins#734
---

## Scope

- Source: the Captain 「開」 (chat, 2026-10-26), answering FO's ask to file this and the Codex-reader task.
- Bite: Codex P2 on iamcxa/kc-claude-plugins#716 (head 8340c3ba, 2026-10-25T04:30:35Z), unaddressed at merge: `kc-dev-flow-2/references/sd/adoption.md` probes `docs/journey/*.yaml`, but kc-journey-map's README documents `docs/journey/<product>/<journey>.yaml` for multi-product adopters, so the probe rejects valid maps and leaves both journey extensions off. Still on origin/main c70f1b22 (`git show origin/main:kc-dev-flow-2/references/sd/adoption.md`, 2026-10-26).
- Upstream first: kc-journey-map README (map locations) and its own map-finding code, before writing a new glob.

## FO alignment

Alignment: not needed: a recorded review finding against the documented map layout.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
Reviewer: kc-dev-flow-2:chief-engineer opus 2026-10-27 — batch 8 review at the ideation gate (the Captain's batch ruling 2026-10-27): per-task disposition, the Captain's decisions, order and batch risk.

## Design

### PRFAQ

**Proposition.** On installation, the First Officer (FO) can offer journey-map and release-acceptance together when the repository keeps its journey YAML inside a product folder. The Captain still selects the pair and reviews the concrete configuration before activation.

**Who benefits?** Multi-product adopters following kc-journey-map's documented `docs/journey/<product>/<journey>.yaml` layout. Single-product repositories keep the flat layout.

**What changes?** In `kc-dev-flow-2/references/sd/adoption.md`, Extensions step 1, replace only `needs a docs/journey/*.yaml file` and its immediately adjoining runtime phrase with the following exact wording (backticks retained):

> `release-acceptance` needs a `.yaml` file under `docs/journey/`, including product folders
> (`find docs/journey -type f -name '*.yaml' -print` from the code root), `python3` and `node`;

The command is recursive without a depth limit, uses a quoted filename pattern, lists regular files, and runs from the already-resolved repository code root. A successful traversal with at least one printed path passes the file-presence part. Empty output fails that part; a missing/unreadable root or traversal error is a failed probe with its reason, not a pass inferred from partial stdout. Keep the existing runtime and extension Needs checks. This is file discovery, not a YAML schema validator or proof that a release walk works.

**Does finding a map turn extensions on?** No. Preserve Extensions steps 2–6, including the single paired choice, required defaults, failed-probe reason, the existing Captain-insistence exception, and no-answer reporting. Passing the probe makes the pair eligible for selection; it does not select it. Re-sync preserves an adopter's existing extension list.

**Why a command instead of another glob?** A literal `**/*.yaml` depends on the invoking shell's recursive-glob settings. The existing `find` utility traverses the documented layouts without that setting. No runtime helper, dependency, map migration, host/server change, or new architecture decision record (ADR) is needed. No workflow template, extension tier, adopter file, CI trigger or version file changes.

**What is not included?** Recognizing `.yml`, following symlinked map directories, parsing arbitrary YAML as a valid journey, choosing a map among several, probing a hosted canvas, automatically enabling extensions, or repairing older adopter selections. The documented source suffix is `.yaml`; the downstream journey commands continue receiving explicit paths.

```mermaid
flowchart TD
 A["FO resolves code root and probes map plus runtimes"] --> B{"Needs pass?"}
 B -->|Yes| C["Offer journey-map plus release-acceptance together"]
 B -->|No| D["Show unchecked with reason"]
 C --> E{"Captain selection"}
 D --> E
 E -->|No answer or not chosen| F["Keep required defaults and report not chosen"]
 E -->|Chooses passing pair| G["Include both in proposed README"]
 E -->|Insists after failed probe reason| G
 F --> H["Captain reviews concrete README"]
 G --> H
 H -->|Approved and readiness passes| I["FO activates through Spacedock"]
 H -->|Not approved or readiness fails| J["Hold activation"]
```

### Chain and bounded existing-code check

Source: `git fetch origin` succeeded on 2026-10-27; pinned `origin/main` is `8bf4f3582411e8e4238f19fbadda8ddeca6767be`. Its `kc-dev-flow-2/.claude-plugin/plugin.json` says `0.32.0`. This is current fetched source, not a claim about live GitHub PR/review state; the GitHub API was not used.

1. **Spacedock first:** read installed 0.27.3 commission and refit source. Commission takes the selected template's adoption inputs; refit reviews scaffolding and proposed changes. A search of its Markdown sources found no `extensions:` entry. It does not own this package-specific map probe; no Spacedock patch is proposed.
2. **kc-dev-flow-2:** adoption Extensions step 1 still names `docs/journey/*.yaml`; both extension documents describe a map *under* `docs/journey/` without restricting depth. `lint-skills.py` checks required tiers against the template list, not map discovery. The defect is the already-named adoption seam, not a missing extension mechanism.
3. **kc-journey-map's own authority:** README lines 203–214 and skill lines 185–186 document flat and product-folder paths. `lib/journey-lint.mjs` accepts an explicit path; `lib/read.mjs:496` loads that supplied path with `parse(readFileSync(path, 'utf8'))`; `lib/journey-walk.mjs` resolves the supplied path and records its repository-relative source. Searches for recursive directory readers/globs and for journey path consumers found no reusable map-discovery CLI in this package. Thus the compatibility claim is documented placement plus explicit-path loading, not an invented upstream discovery API. Server room/asset discovery is outside this seam.
4. **Sibling adopters, read-only local snapshots:** relay `dhaka` has `docs/journey/spacedock-review.yaml`, qnow `qnow-adopt-dev2` has `docs/journey/qnow.yaml`, and web `dev2-fo` has no `docs/journey/*.yaml` at any depth. Their current local README lists are respectively `[learn]`, `[roborev, codex, copilot, learn, peers, journey-map]`, and `[learn, peers, roborev]`. These observations neither infer remote state nor authorize edits; the nested regression uses synthetic fixtures.

ADR 0035 (extension defaults and install choice) already rules the paired selection and preservation of adopter choices; the design follows it. ADR 0018 (shared journey host core) preserves YAML/readback behavior and does not make hosting an installation prerequisite. ADR titles were listed from current source and the assigned checkout; no task-local or top-level live-task `Override:` line was found that changes these decisions. No new ADR or number reservation is proposed.

### Probe evidence and reproduction

The ideation ran the exact proposed command through `sh -c` in seven disposable fixture roots. Results:

| Fixture | Old flat pattern: paths | Proposed command: paths | Exit |
| --- | ---: | ---: | ---: |
| `docs/journey/a.yaml` | 1 | 1 | 0 |
| `docs/journey/product/a.yaml` | 0 | 1 | 0 |
| `docs/journey/product A/domain/a map.yaml` | 0 | 1 | 0 |
| Empty `docs/journey/` | 0 | 0 | 0 |
| Only `.tldr`, `.yml`, and `.yaml` outside `docs/journey/` | 0 | 0 | 0 |
| Directory named `docs/journey/directory.yaml` | 0 | 0 | 0 |
| Missing `docs/journey/` | 0 | 0 | 1 |

The old-pattern baseline used `Path.glob('*.yaml')` filtered by `is_file()` because the existing adoption text has no executable probe. It reproduces the path-depth defect, not historical agent behavior. Fixtures contain a synthetic `journey: synthetic` line; presence testing deliberately does not claim complete schema validity. Mutations adding `-maxdepth 1`, changing the suffix to `.yml`, or selecting directories instead of files each lost the expected map and were caught by the fixture assertions.

Reproduce the decisive cases without any repository write:

```sh
python3 - <<'PYPROBE'
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
command = "find docs/journey -type f -name '*.yaml' -print"
cases = {
    'flat': ['docs/journey/a.yaml'],
    'nested': ['docs/journey/product/a.yaml'],
    'deep-space': ['docs/journey/product A/domain/a map.yaml'],
    'empty': [],
    'non-map': ['docs/journey/a.tldr', 'docs/journey/a.yml', 'other/a.yaml'],
    'yaml-directory': [],
    'missing': [],
}
with TemporaryDirectory() as tmp:
    for name, files in cases.items():
        root = Path(tmp) / name
        root.mkdir()
        if name != 'missing':
            (root / 'docs/journey').mkdir(parents=True)
        if name == 'yaml-directory':
            (root / 'docs/journey/directory.yaml').mkdir()
        for filename in files:
            path = root / filename
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('journey: synthetic\n')
        result = subprocess.run(['sh', '-c', command], cwd=root,
                                capture_output=True, text=True)
        expected = sorted(p for p in files
                          if p.startswith('docs/journey/') and p.endswith('.yaml'))
        assert sorted(result.stdout.splitlines()) == expected, name
        assert (result.returncode != 0) == (name == 'missing'), name
        if name == 'nested':
            assert not list((root / 'docs/journey').glob('*.yaml'))
        print(name, result.returncode, sorted(result.stdout.splitlines()))
PYPROBE
```

Implementation adds a focused case in existing `kc-dev-flow-2/scripts/test_lint_skills.py` that extracts the inline `find` command from adoption Extensions step 1 and executes it in these temporary fixtures. Do not hard-code a separate candidate command in the test: reverting the documentation to the flat pattern must make the extraction/behavior test fail, and adding a depth limit must fail the nested case. No new CI job or test dependency is needed; the existing test runner already exercises that file.

Diagram evidence: rendered with the locally installed Mermaid CLI 12.0.0 and inspected as an image; actors, failed-probe exception, selection, approval and hold branches match the prose. The sandbox initially blocked Chromium startup; the approved local renderer retry succeeded. The cache is a convenience, not a required package dependency: reproduction uses any installed `mmdc` with the fenced source as input. Disposable image and probe output are under `/var/folders/tm/dk0m7pgx4h3gxqv_v2v8nds00000gp/T/journey-probe-ideation-2j3ky060/`; the reproducible source and outcomes are retained here.

### Words FO reads at each lifecycle moment

Count convention: whitespace split, same as the package budget. At installation or a refit that revisits the recommendation, FO reads the complete adoption reference: **2069 before, 2085 after (+16)**; within that read, Extensions is **350 before, 366 after**. The proposed reference was formed by the exact replacement above; all other bytes were preserved. This cost buys a shell-independent command and an explicit repository root; it is not a word-reduction claim.

| Lifecycle moment | Before → after | Why |
| --- | --- | --- |
| Installation / refit recommendation | 2069 → 2085 | Complete adoption reference; +16 words once per read |
| Startup | Unchanged, +0 | Workflow, startup/idle mod and printed instructions unchanged |
| Idle on an open PR | Unchanged, +0 | Same `pr_watch.py` output and mod instructions for identical state |
| Idle on a merged PR | Unchanged, +0 | Same `pr_watch.py`/observer/learn instructions for identical state |
| Merge ask | Unchanged, +0 | Delivery check, reviewer text and journey-footprint rules unchanged |
| After archive | Unchanged, +0 | Same learn and journey folding instructions for identical state |

These zeroes are deltas across all affected passages and instruction-producing scripts, not invented totals for arbitrary task-dependent output. No text moves into another lifecycle moment. The flat and nested success paths each print one whitespace-free fixture path; the empty case prints none; the missing-root error is shown as the failed-probe reason. Paths with spaces have variable output word counts and are evidence data, not new instructions. A later diff touching workflow/mod/output producers invalidates this table and requires a recount.

### Unresolved decisions for the Captain

None beyond the ordinary design gate. Recommendation: approve the bounded recursive-discovery correction while keeping the existing selection policy. Cost: 16 extra adoption words, and the presence probe still cannot distinguish valid journey YAML from unrelated `.yaml`; adding schema validation or auto-selection would widen this task and is not recommended here. No new retained state, paid resource, production duty or profile change arises.

### Batch overlap

Files this design would change: `kc-dev-flow-2/references/sd/adoption.md` (Extensions step 1) and `kc-dev-flow-2/scripts/test_lint_skills.py` (execute that documented command). No shared ADR index, numbered record, workflow budget step, or extension tier table changes. Task files below were read as they stood on 2026-10-27; batch-8 siblings mostly have Scope only, so implementation must recheck their eventual file lists.

| Other task | Same file or check; ordering consequence |
| --- | --- |
| `archive-waits-for-observer-report` — require observer before archive | No same file currently named; observer/merge-hook checks are separate. Shared package lint run only. |
| `idle-hook-names-merged-tasks-without-learn` — remind about missing learning | No same file currently named; idle output/mod changes require its own per-moment word count. Shared package lint run only. |
| `copilot-not-run-line-carries-quote` — complete reviewer evidence | No same file currently named; delivery/reviewer checks separate. Shared package lint run only. |
| `dispatch-carries-reserved-adr-number` — retain reserved decision number | No same file currently named; dispatch/number-guard checks separate. Shared package lint run only. |
| `seed-check-requires-schema-fields` — enforce required task fields | No same file currently named; `design_surfaces.py` and schema checks separate. This design uses the currently installed checker and must be rechecked if that one changes. |
| `journey-probe-finds-nested-maps` — this install-probe correction | Owns the two paths above; no second writer. |
| `read-adr-honors-adr-folder` — honor caller's decision-record folder | No same file; kc-adr source/copy sync is separate. Shared package lint run only. |
| `adr-required-statement` — require decision-record statements | Historically edits `adoption.md` in another section. Its body explicitly records Captain closure on 2026-10-20 despite stale validation frontmatter; do not revive or absorb it. Recheck if FO reopens it. |
| `journey-server-host-pilot` — private shared journey host | No same file/check; `journey-server-host-pilot/index.md` and ADR 0018 preserve YAML behavior. Host/source changes are read-only dependencies here. |
| `ops-inbox-r1-setup-and-isolation` — isolate operations workflow setup | No same file/check; owns `kc-ops-inbox/**`, its workflow and decision records. |
| `pr-review-lite-value-pilot` — test useful lightweight PR review | No same file/check; review-capability scripts and its journey are separate. |
| `adr-silent-undo-probe` — measure unrequested decision reversal | No same file/check; fictional scenario harness in archived task state. |
| `comment-check-reaches-delivery-gate` — bind comment evidence to delivered head | No same file; delivery scripts/validation principles separate. Shared package lint run only. |
| `journey-canvas-hosted-poc` — test persistent hosted canvas | No same file/check; hosted sync/auth proof separate; no YAML-format migration. |

Recommended order: this correction can proceed independently of the currently named files; rebase/recheck the two-path diff after other batch designs land, serialize any later `test_lint_skills.py` or adoption edits, and rerun shared package checks on the combined candidate. No peer session was messaged and no sibling task was edited.

## Acceptance criteria

**AC-1** The documented probe finds regular `.yaml` files at flat, product-folder and deeper paths below the resolved code root's `docs/journey/`, including spaces, without enabling shell globstar. Evidence: execute the command extracted from candidate adoption text in those three fixtures and compare printed paths. Falsifier: restore the flat pattern or add `-maxdepth 1`; the nested expectation must fail. Ideation: seven-case probe and flat-only mutation passed; candidate extraction test is not yet implemented.

**AC-2** Empty/missing roots, non-map suffixes, outside-root YAML and `.yaml` directories do not satisfy map presence; traversal failure is shown as a failed probe. Evidence: execute the four negative fixtures above, assert output and exit code, and read the retained failed-probe wording. Falsifier: remove the file-type/suffix/root constraint or treat empty stdout/nonzero exit as success. Ideation: empty, missing, suffix/outside-root and directory cases passed; permission-error handling and actual host presentation remain unverified.

**AC-3** Discovery alone neither enables the pair nor changes runtime requirements, default tiers, no-answer handling, Captain-insistence exception, re-sync preservation, or approval before activation. Evidence: candidate diff is confined to the replacement and executable regression test; compare Extensions steps 2–6 and Before activation byte-for-byte with the pinned base, and run package `test_lint_skills.py` plus `lint-skills.py`. Falsifier: changing a required default or replacing the selection step fails the preservation review. Ideation: proposed reference preserves all non-replacement bytes; live Ask UI and real adoption are not exercised.

**AC-4** The package change adds 16 adoption words and no instruction words at startup, either idle path, merge ask, or archive. Evidence: whitespace-split the pinned base and candidate reference, verify 2069→2085 / Extensions 350→366, and inspect the complete diff for workflow, mod or output-producer changes; independently recount before approval if wording changes. Falsifier: an added runtime instruction or any different adoption count invalidates the measurement. Ideation: exact replacement measured; final implementation recount is outstanding.

**AC-5** The design remains a two-file package correction with matching PRFAQ and rendered Mermaid, and no adopter/host/schema/version change. Evidence: `design_surfaces.py check <task>` exits 0 now; later candidate `git diff --name-only <base> HEAD` names the two designed paths, and focused regression tests execute the documented command. Falsifier: removing a Mermaid branch/approval boundary, missing an acceptance declaration, or adding an adopter mutation breaks this evidence. Ideation: diagram rendered and visually compared; implementation candidate and its tests do not yet exist.

## Stage Report: ideation

- DONE: A design for the journey-extension install probe in kc-dev-flow-2/references/sd/adoption.md to find maps in nested product folders the way kc-journey-map's own README and code locate them, with the probe run against a flat and a nested fixture
  Pinned source 8bf4f3582411e8e4238f19fbadda8ddeca6767be / dev2 0.32.0; upstream documents both layouts and loads explicit paths. All seven reproduced fixtures pass; the old flat pattern misses nested/deeper maps.
- DONE: A `### Batch overlap` section naming each file the design would change and each other batch task (archive-waits-for-observer-report, idle-hook-names-merged-tasks-without-learn, copilot-not-run-line-carries-quote, dispatch-carries-reserved-adr-number, seed-check-requires-schema-fields, journey-probe-finds-nested-maps, read-adr-honors-adr-folder) and live task of other sessions (adr-required-statement, journey-server-host-pilot, ops-inbox-r1-setup-and-isolation, pr-review-lite-value-pilot, adr-silent-undo-probe, comment-check-reaches-delivery-gate, journey-canvas-hosted-poc (driven by other sessions; read only)) that changes the same file or check, so FO can order implementation
  All 14 named tasks accounted for; two proposed package paths; historical adoption overlap explicitly marked closed in its body, with stale validation frontmatter preserved.
- DONE: The words FO reads at each lifecycle moment, before and after, per root learning.md "Measure the words FO reads at each moment, not one file's size"
  Adoption 2069→2085, Extensions 350→366; startup, open/merged PR idle, merge ask and archive each +0 for identical task state; no moved instruction or output producer.
- DONE: Acceptance criteria with reproducible evidence clauses and falsifiers, and unresolved decisions for the Captain, each with a recommendation and what gets worse under it
  AC-1 through AC-5 each state proof and falsifier; no unresolved material choice beyond the design gate; +16 adoption words and presence-only validation are the stated tradeoffs.
- DONE: AC-1 current ideation evidence
  Flat/nested/deeper-space cases execute the proposed command; flat-only mutation loses the nested path. Candidate extraction test remains future implementation evidence.
- DONE: AC-2 current ideation evidence
  Empty/missing/non-map/outside-root/directory cases pass; wrong suffix and directory-only mutations lose expected maps. Permission errors and actual host reason presentation remain unverified.
- DONE: AC-3 current ideation evidence
  Disposable reference changes only the one probe phrase; preserved choices, runtimes and activation reviewed against ADR 0035. Candidate lint/test runs and live Ask UI remain unverified.
- DONE: AC-4 current ideation evidence
  Same whitespace counter over pinned base and exact proposed replacement yields +16; final candidate recount remains owed at implementation/validation.
- DONE: AC-5 current ideation evidence
  Installed design_surfaces.py exits 0: "journey-probe-finds-nested-maps.md: design surfaces presentable"; Mermaid CLI 12.0.0 renders and image matches branches/approvals; no implementation candidate yet.
- SKIPPED: Live GitHub PR/review state and hosted adoption
  Assignment permits git/local evidence; fetch succeeded, GitHub API not used. Neither provider state nor actual model-driven installation is claimed.

### Summary

Designed one recursive, read-only map-presence probe with no new helper or selection policy, plus a regression test that executes the documentation's command. Seven fixture cases and three falsifying mutations distinguish the fix from the flat-only defect; design checks and rendered diagram pass, while implementation and live installation evidence remain outstanding. Pilot scope and existing Captain approval boundaries remain unchanged.


## Stage Report: implementation

- DONE: Implement the approved design and acceptance criteria; only the files the design names
  Code 159b21232dea8ce68fcf9402461e185ff59d327c, one commit off fetched origin/main 8bf4f3582411e8e4238f19fbadda8ddeca6767be; diff names adoption.md and test_lint_skills.py under kc-dev-flow-2 only. No ADR, version, CI, adopter, host or schema change.
- SKIPPED: One Draft PR (Conventional Commit title scoped to the plugin) from a branch off origin/main (8bf4f3582411e8e4238f19fbadda8ddeca6767be) implementing the approved design and acceptance criteria in the task file; the kc-dev-flow-2/references/sd/adoption.md probe change and the tests the design names, as designed; only the files the design names
  Implementation and push are complete; FO owns opening the Draft PR because the worker sandbox cannot reach GitHub API. English title/body: /tmp/impl-journey-probe-finds-nested-maps-pr.md.
- DONE: Every acceptance criterion green with the evidence each names; each falsifier shown failing by a mutation you run (python3 -B, caches cleared)
  AC-1–AC-5 evidence and the checker limit follow below; Python ran with -B, disposable mutation copies excluded/cleared __pycache__, and all copies were removed. No live Ask UI or model-driven adoption claim.
- DONE: AC-1 — recursive regular-file discovery
  New test extracts the command from Extensions step 1 and runs sh in seven fixtures; flat/nested/deeper-space match printed paths. Before the documentation edit it fails (0 extracted commands); restoring the flat pattern or adding -maxdepth 1 each fails the test (depth limit fails nested).
- DONE: AC-2 — negative cases and traversal failure
  Empty, missing, .tldr/.yml/outside-root YAML and .yaml-directory fixtures assert paths and exit status; missing root also needs stderr. Removing file type, suffix or root constraints, changing suffix, or hiding traversal failure each fails the new test. A chmod-000 traversal returns nonzero with stderr despite printing visible.yaml; retained failed-probe wording was read, host presentation untested.
- DONE: AC-3 — selection, runtimes and activation preserved
  Candidate equals the pinned reference with just the approved phrase replaced; Extensions steps 2–6, re-sync preservation and Before activation are byte-identical. Mutating required defaults, selection, or empty/nonzero-result treatment fails this preservation comparison; test_lint_skills.py 45/45 and repository lint-skills.py exit 0.
- DONE: AC-4 — reading cost
  Whitespace recount: adoption 2069→2085 and Extensions 350→366 (+16); adding an instruction fails the count comparison. Complete diff contains no workflow/mod/output-producer change, so startup, both idle paths, merge ask and archive each add 0 instruction words; workflow remains 5565/5565.
- DONE: AC-5 — bounded scope and design agreement
  Installed design_surfaces.py check exits 0; removing the acceptance heading exits 1. Two-path comparison passes and an added adopter path fails it. Approved PRFAQ/Mermaid remain unchanged; deleting the approval→activation branch fails explicit diagram comparison. Generic checker accepts a changed Mermaid fence label and does not prove semantics; rendered diagram evidence is the retained ideation evidence, not a new rendering.
- SKIPPED: kc-dev-flow-2/scripts/lint-skills.py (the repository copy CI runs), /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.0/scripts/adr_lint.py docs/adr --since <base> exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.0/scripts/number_guards.py check exit 0; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.0/scripts/comment_ratio.py within its maximum; roborev evidence= line; push without force and without -u; PR body written for FO; FO reads CI on the PR head; CI cost measured or stated as not measured
  Available local portions: repository lint exit 0; installed Codex package /Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.0 scripts used per FO/runtime routing. adr_lint checks 39 ADRs exit 0; number_guards on candidate exit 0 (no migrations-path); comment_ratio: code lines 33, comment lines 0, 0.0%, maximum 5% met; diff --check passes. git push origin spacedock-ensign/journey-probe-finds-nested-maps succeeded without force or -u; PR body written. External portions are explicitly skipped below.
- SKIPPED: roborev evidence= line; FO reads CI on the PR head
  RoboRev not run: worker sandbox cannot reach the daemon, as FO instructed; no evidence= line exists. No gh command run. FO opens PR, runs RoboRev and reads CI on 159b2123. CI cost per PR not measured; no CI job/trigger/dependency change.
- DONE: Affected documents
  doc_impact.py <base> HEAD lists kc-dev-flow-2/skills/maintain-flow/SKILL.md — unaffected: existing test command and mutation guidance still apply; no lint behavior or maintenance route changed. adoption.md is updated with the exact approved probe phrase.
- DONE: Proceed with implementation-1 now: archive-waits-for-observer-report is not writing kc-dev-flow-2/references/sd/adoption.md; its implementation waits for spacedock-dev/spacedock#855 and is ordered last in batch 8, after this task merges
  Read FO's committed dispatch/implementation-2.md before editing; this task proceeds first and FO serializes the later adoption.md change.

### Summary

The documented install probe now discovers nested product maps, with an executable regression tied to the documentation and seven discovery mutations caught. Local checks pass at 159b2123 and the code branch is pushed; FO still owes Draft PR creation, RoboRev and CI evidence before validation/delivery. Pilot scope remains the approved two-file correction, with unchanged extension selection and activation authority.

## Stage Report: validation

- DONE: Independent verdict on PR #734 head 159b2123 against every acceptance criterion in the task file, re-running each evidence command and at least one falsifier per criterion yourself, and judging each limit the implementation report states
  PASSED at 159b21232dea8ce68fcf9402461e185ff59d327c against 8bf4f3582411e8e4238f19fbadda8ddeca6767be; all five criteria pass independently. Detailed commands, falsifiers and limits: [validation evidence](journey-probe-finds-nested-maps/validation/evidence.md).
- DONE: RoboRev on this head (FO, 2026-10-28): clean on 159b21232, evidence=roborev:1260; CI on this head read by FO: 4 of 4 pass
  Read dispatch/validation-1.md; these are FO-supplied exact-head results, not validator reruns or fresh GitHub queries.
- DONE: A minimal acceptance script the Captain can run (three to six steps, exact commands, expected output), run by you exactly as written in a fresh bash shell, with its observed output; /Users/kent/.claude/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.0/scripts/adr_lint.py docs/adr --since <base> with its exit code; your verdict naming the head, with findings classified by the workflow's Review-finding disposition
  [Five-step script](journey-probe-finds-nested-maps/validation/acceptance.sh) ran unchanged via bash --noprofile --norc, exit 0; full observed output is in evidence.md. The skill-routed Codex 0.32.0 package supplied adr_lint.py: 39 ADRs, 0 legacy, exit 0. No findings in any disposition class.
- DONE: AC-1 — nested discovery
  The candidate test executes all seven fixtures; flat, product-folder and deeper-space paths match exactly. Restoring the old phrase fails extraction and adding -maxdepth 1 loses the nested path.
- DONE: AC-2 — negative fixtures and failed traversal
  Empty/missing/suffix/outside-root/directory assertions pass; removing type, suffix or root constraints, changing suffix, or hiding nonzero exit each fails. chmod-000 traversal returns exit 1 plus stderr despite visible.yaml stdout.
- DONE: AC-3 — preserve choice and activation
  Entire adoption text equals base plus the exact approved replacement; mutations to defaults, selection, no-answer handling, failed-probe interpretation and approval fail this comparison. Candidate test suite: 45/45, lint exit 0.
- DONE: AC-4 — lifecycle reading cost
  Independent whitespace count: adoption 2069→2085; Extensions 350→366; extra instruction fails. No workflow/mod/output-producer change, hence startup, both idle paths, merge ask and archive each +0; workflow budget 5565/5565.
- DONE: AC-5 — bounded scope and diagram
  Exactly the two approved paths; added adopter path fails scope comparison. Current Mermaid matches retained rendered source, whose image was independently inspected; deleting approval edge fails comparison, removing acceptance heading makes design checker exit 1.
- DONE: Required workflow and document checks
  design_surfaces, dispatch_records (4 complete), number_guards, comment_ratio (33 code/0 comments; 0.0% ≤5%), adr_lint and git diff --check pass; no ADR reservation/migration. doc_impact names maintain-flow/SKILL.md: unaffected because its test command and mutation guidance still apply; adoption.md updated.
- DONE: Goal sufficiency and minimal necessity
  Exact documentation command finds the accepted layouts; without the phrase replacement discovery fails, and without the executable regression the old flat defect is unguarded. No helper, policy, version, CI, host, schema or adopter change is needed.
- DONE: Implementation limits assessed
  Generic design checker accepts a changed Mermaid fence: confirmed, with independent visual comparison supplying this task's proof. Presence-only YAML, .yml/symlink exclusions and unchanged model-driven selection are accepted boundaries; FO's supplied PR/review/CI results resolve the implementation's pending external work.
- DONE: Candidate preservation and cleanup
  Detached validation and acceptance worktrees removed; assigned branch remains spacedock-ensign/journey-probe-finds-nested-maps at 159b2123, clean. Only this task's state report/evidence changed; no code commit, Git config write, PR mutation or explicit push.
- SKIPPED: Live host Ask UI, actual adoption/activation and fresh hosted review queries
  No changed UI surface; unchanged host behavior is not claimed. The original diagram rendering was reused with exact source comparison and fresh image inspection. CI cost per PR was not measured; no CI trigger changed.

### Summary

Recommend PASSED for PR #734 at 159b21232dea8ce68fcf9402461e185ff59d327c: all five acceptance criteria, falsifiers and required local checks pass, and the five-step acceptance script exits 0. Candidate bytes are unchanged and disposable worktrees are removed; FO still runs the script before presenting the validation gate and the Captain retains delivery authority.
