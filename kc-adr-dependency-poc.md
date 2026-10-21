---
title: dev2 uses an independent kc-adr package for ADR writing tools, installed and updated on Claude Code and Codex, and refuses loudly when it is absent or too old
variant: kc-dev-flow-2
profile: poc
merge: pr
status: validation
gates:
    version: 1
    records:
        - id: gate:kc-adr-dependency-poc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:kc-adr-dependency-poc-backlog-1
              briefing:
                id: briefing:kc-adr-dependency-poc:backlog:attempt-1:revision-1
                digest: sha256:d8d71475e10d32cce09012486c4aa2839131756a72eab60d9346a9a219f80c90
                room-ref: ./kc-adr-dependency-poc/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:kc-adr-dependency-poc:backlog:1
                briefing: briefing:kc-adr-dependency-poc:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-21T13:01:23.915549Z"
                decision: approve
                reason: Captain 「好，開」 (chat, 2026-10-21), answering FO's question put before it (quoted in the gate question); this briefing binds that question and answer after the fact.
              application:
                target-stage: implementation
                state: consumed
        - id: gate:kc-adr-dependency-poc:validation
          stage: validation
          attempts:
            - id: gate-attempt:kc-adr-dependency-poc-validation-1
              briefing:
                id: briefing:kc-adr-dependency-poc:validation:attempt-1:revision-1
                digest: sha256:af308fb00b04d0d360c5d7c9f875d5abcb030ac6fdbcbcd50dc81e9c6ea9715d
                room-ref: ./kc-adr-dependency-poc/review/validation/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:kc-adr-dependency-poc:validation:1
                briefing: briefing:kc-adr-dependency-poc:validation:attempt-1:revision-1
                by: person:captain
                at: "2026-10-21T16:40:31.399622Z"
                decision: approve
                reason: 'Captain 「可以」 (chat, 2026-10-22) to FO recommendation 「工具搬到 kc-adr，但用 dev2 的人只要裝 dev2 一個」: kc-adr holds the ADR writing tools as the source, dev2 carries a copy that CI syncs from kc-adr before each dev2 release, and CI fails when the copy and the source differ; the copy-at-release shape is untested and is verified first in the move task. Override: the POC recommended run-time resolution; Captain chose a CI-synced copy in dev2, on FO recommendation, for a single install; area: kc-adr packaging. The POC closes as passed.'
              application:
                target-stage: done
                state: pending
started: 2026-10-21T13:01:50Z
worktree: .worktrees/spacedock-ensign-kc-adr-dependency-poc
---

## Scope

- Source: the Captain, 2026-10-21. He chose (in the kc-adr session, relayed by Paseo agent 1bcf070c and then put to him here) that kc-adr is the package for agents reading and writing ADRs, dev2 its first consumer and moneyflow its second. Here he described his picture: 「我原本想像是，kc-adr是獨立的套件，dev2直接使用它，永遠取用最新的版本，等於在檔案層面用ln之類的方式硬連結，所以如果它更新那dev2也會更新，不受影響。這樣合理嗎？等於例如以後我做了fin flow它可以照樣取得adr工具包？」, then 「先poc看看怎樣更好？」 and 「好，開」 to FO's POC plan.
- Questions, each answered by a real install on Claude Code and on Codex, not by reading a neighbour's setup:
  1. Can a plugin declare a dependency on another plugin natively (Claude Code plugin manifest and marketplace; Codex plugin manifest)? Cite each tool's own docs or `--help`.
  2. Does a symlink from dev2 to kc-adr files survive `claude plugin install`/`update` from the marketplace and the Codex local install, and does a kc-adr update reach dev2?
  3. Can a dev2 script resolve the installed kc-adr at run time on each install layout (Claude marketplace cache, `~/.claude/plugins/local`, `~/.codex/local-plugins`), and refuse with a clear message when kc-adr is absent?
  4. How does dev2 refuse a kc-adr too old or too new for it (a version floor read at run time, and a CI job that tests the two together)?
- Arms: native dependency (if one exists), symlink, run-time resolution, and wrap-not-move (today's tools stay in dev2) as the control.
- Bar: installs on both hosts; a kc-adr update reaches dev2; absent kc-adr refuses loudly; an incompatible version is caught. The report recommends one arm and names what a move would change in the four adopters' READMEs and pins.
- Inputs: the kc-adr boundary contract (PR #691, `docs/journey/kc-decision-log/boundary-contract.md`), its wrap proposal (relayed 2026-10-21), `number_guards.py` (one script and one reservation file for ADR and migration numbers, ADR 0002), `adr_lint.py`, the ADR template.
- Non-goals: moving any tool now; changing any adopter; splitting `number_guards.py` (the report only says what a split would need).

## Acceptance criteria

These restate the Scope's bar line by line and add no requirement; FO omitted the section from the seed (the dev2-poc route has no ideation stage to write it), and the implementation report's design check exited 1 on its absence.

**AC-1** Each arm's install is observed on Claude Code and on Codex. Evidence: report.md result table, Installs column, one observed row per arm and host. Falsifier: a cell filled from documentation alone is marked as such.

**AC-2** For each arm, whether a kc-adr update reaches dev2 is observed on both hosts. Evidence: the result table's update column. Falsifier: an update run where dev2's resolved kc-adr version does not change.

**AC-3** For each arm, whether an absent kc-adr refuses loudly is observed on both hosts. Evidence: the result table's absent column with the printed message or state. Falsifier: an absent kc-adr that exits 0 or prints nothing.

**AC-4** For each arm, whether an incompatible kc-adr version is caught is observed on both hosts, and the report recommends one arm and names what a move would change in the four adopters' READMEs and pins. Evidence: the result table's version column, the Ruling and the adopter section. Falsifier: an out-of-range version that runs.

## FO alignment

Correction (FO, 2026-10-22): the validation resolution recorded 2026-10-22 quotes the Captain's 「可以」, which answered FO's packaging recommendation, not the close question (observer finding). He then answered the close question itself: Asked: 「kc-adr 接法的 POC，要照驗證結果結案嗎？」 Captain: 「同意結案」 (chat, 2026-10-22). This is the ruling the close rests on. The resolution's Override line is not in the parseable form; corrected here: Override: recommended run-time resolution; Captain chose a CI-synced copy in dev2; area: kc-adr packaging.

Not needed before implementation. The Captain asked for this POC (「好，開」, 2026-10-21) after FO showed him its four questions, arms and bar, restated above. Release review: not needed: the task belongs to no release.
Surfaces: none
Visible change: none

## Stage Report: implementation

- DONE: Answer the four questions in the task Scope with real installs, one arm at a time (native dependency if either host has one, symlink, run-time resolution, wrap-not-move as the control), on Claude Code and on Codex, each claim citing the tool's own docs, `--help` or the observed install result
  Claude has native dependencies (docs plugin-dependencies; observed install, update, uninstall, conflict). Codex has none (manifest docs, `app-server generate-json-schema` types, observed install). Symlink survives Claude install only as a frozen copy and is dropped silently by Codex. Run-time resolution met the bar on both hosts. Table in report.md.
- DONE: A report under the task folder in the state checkout (report.md) with one row per arm and host against the bar (installs, update reaches dev2, absent kc-adr refuses loudly, incompatible version caught), the recommended arm, and what a move would change in the four adopters' READMEs and pins
  `kc-adr-dependency-poc/report.md` in the state checkout. Recommends run-time resolution; adopter counts verified for three of four (carlove-v1 has no checkout locally, stated as unverified).
- DONE: Every probe runs with throwaway plugin roots and an isolated config (for example a temporary HOME or CLAUDE_CONFIG_DIR and a temporary Codex home), never the Captain's real ~/.claude or ~/.codex installs, and each probe directory is removed after; the report states the isolation used
  Temporary HOME, CLAUDE_CONFIG_DIR, CODEX_HOME under /tmp; directory deleted; real config files grep-clean and unmodified. One slip (a command ran once against the real config with a nonexistent path, wrote nothing) is disclosed in report.md.
- SKIPPED: roborev, comment_ratio.py, number_guards.py, doc_impact.py
  No repository diff exists (the POC writes only report.md in the state checkout); the task has no `## Number guards` section and `Surfaces: none`.
- FAILED: `python3 <package>/scripts/design_surfaces.py check <task>`
  Exit 1: `missing '## Acceptance criteria' section`. The POC route skips ideation, so the task never had one; I did not add one (task body is FO's). Returns to FO.

### Summary

Run-time resolution is the only arm that meets all four bar items on both hosts; Claude's native dependency works as an install-time add-on but Codex has no equivalent, and a symlink fails on both. A tag-name mismatch (Claude needs `<plugin>--v<version>`, release-please cuts `<plugin>-vX.Y.Z`) would affect the native arm and was read from files, not run. Not proved: a live model session, auto-update, disabled-but-installed kc-adr, carlove-v1 READMEs.

## Stage Report: implementation (cycle 2)

- DONE: kc-dev-flow-2/scripts/design_surfaces.py check on the task file: FO added `## Acceptance criteria` restating the Scope's bar; run the check and record its output and exit code
  `python3 -B <package>/scripts/design_surfaces.py check .spacedock-state/kc-adr-dependency-poc.md` printed `kc-adr-dependency-poc.md: design surfaces presentable` and `scope check not run: stage is implementation, not ideation`; exit code 0 (cycle 1 exited 1 on the missing section).
- DONE: Map AC-1 to AC-4 to report.md's result table, Ruling and adopter section, one line each, without changing report.md
  AC-1 -> result table, Installs column: one row per arm and host (A, B, C Claude and Codex; D control as one row for both hosts), each cell observed or marked (doc).
  AC-2 -> result table, "kc-adr update reaches dev2" column: observed on both hosts for C (Claude `update kc-adr` 2.3.0 to 2.4.0; Codex `marketplace upgrade` 2.2.0 to 2.3.0); A on Claude yes only by `update kc-adr`; B Claude no (copy stayed 2.0.0); n/a where install failed or nothing couples (A and B on Codex, D).
  AC-3 -> result table, "Absent kc-adr refuses loudly" column: C exit 3 with the printed install message on both hosts; A on Claude partly (dev2-native `failed to load`, no live model session); B bundled so never absent; n/a for A and B on Codex, and D.
  AC-4 -> result table, "Incompatible version caught" column (C exit 4 on both hosts, A on Claude at install and update) plus the `## Ruling` (run-time resolution) and `## What a move would change (the four adopters)` (three of four verified by `git grep`; carlove-v1 has no checkout and is marked unverified).

### Summary

The design check now exits 0 on the task file with FO's acceptance criteria in place. AC-1 to AC-4 each point at the existing report.md section that holds their evidence; report.md, the other task sections and every repository file are unchanged. Cells marked n/a in report.md (Codex native, Codex symlink, wrap control) are not observed failures of the criteria, they are arms with no mechanism on that host; AC-3's falsifier (exit 0 or silence) did not occur in any observed cell.

## Stage Report: validation

- DONE: Independent verdict on report.md at state 57a411c0d0ea54eb6d898b400c1333fd7f569472 against the Scope's four questions and bar: re-run at least one decisive probe per arm on each host yourself (native dependency on Claude and Codex, symlink on Codex, run-time resolution absent and out-of-range refusals on both), in a fresh isolated HOME, CLAUDE_CONFIG_DIR and CODEX_HOME, and judge each limit the report states
  Verdict recommended: PASSED. Re-run on Claude 2.1.305 and codex-cli 0.162.1; report.md is byte-identical at 57a411c0 and 4ebf5d3a (`git diff --stat` empty). A native: Claude install `(+ 1 dependency: kc-adr)`, `update dev2-native` "already at the latest", `update kc-adr` 2.3.0 to 2.4.0, 3.0.0 not taken (`highest ... satisfying ^2.0`), uninstall kc-adr gives `failed to load ... Dependency "kc-adr@vpoc-mk" is not installed`, `^4.0` unsatisfiable gives `Requires "kc-adr@vpoc-mk" ^4.0, installed 3.0.0`; Codex `dependencies` array accepted, `codex plugin add dev2-native` left kc-adr `not installed`. B symlink: Claude cache holds a real directory, stayed 3.0.0 after the source moved to 3.1.0; Codex drops it. C run-time: Claude and Codex each exit 3 absent, exit 4 on 4.0.0 against 3.0.0..4.0.0, exit 0 present; Claude `update kc-adr` 3.1.0 to 3.2.0 and Codex `marketplace upgrade` 4.0.0 to 3.5.0 to 3.6.0 each moved the resolved path with dev2-resolve untouched at 0.1.0. D control not run (no coupling). Limits judged below as F1 to F4.
- DONE: Confirm from each tool's own docs or --help the two load-bearing negatives: Codex has no plugin dependency field, and Codex drops a symlinked directory from an installed plugin
  Negative 1 holds: `codex app-server generate-json-schema` types PluginDetail, PluginSummary, PluginInterface, PluginInstallParams and every other Plugin* type carry no field whose body mentions "depend"; developers.openai.com/codex/plugins/build documents no dependency field. Negative 2 holds by observation only: Codex docs and `--help` are silent on symlinks; the marketplace checkout had `vendor-kc-adr -> ../kc-adr` and the installed cache did not, from a git marketplace and from a local-path marketplace, and an in-plugin link (`inner-link -> skills`) was dropped too, so the drop is not limited to links that leave the plugin.
- DONE: Confirm the real ~/.claude and ~/.codex configs hold no probe entry before and after your run, and state the isolation used; your verdict names the state revision, with findings classified by the workflow's Review-finding disposition
  Isolation: one `mktemp -d` under /tmp holding HOME, CLAUDE_CONFIG_DIR, CODEX_HOME and a git-config URL rewrite to a local bare repo; deleted afterwards. The four real files (known_marketplaces.json, installed_plugins.json, settings.json, config.toml) have identical shasum before and after, mtimes 20:03 or earlier (task started 21:01), and grep for probe names (mine and the implementer's) counts 0; no kc-adr entry exists under ~/.claude/plugins, ~/.codex/plugins, ~/.codex/local-plugins or ~/.agents. The implementer's slip claim (one `marketplace add /mk` on the real config, "Path does not exist") is consistent with that state; I had no pre-slip hash, so "wrote nothing" rests on those mtimes and the grep. Verdict state revision: 57a411c0d0ea54eb6d898b400c1333fd7f569472.
- DONE: python3 <package>/scripts/dispatch_records.py and design_surfaces.py check on the task
  `dispatch_records.py` printed `3 dispatch record(s) complete`, exit 0; `design_surfaces.py check` printed `design surfaces presentable`, exit 0.
- SKIPPED: adr_lint.py, comment_ratio.py, number_guards.py, doc_impact.py, roborev
  No repository diff or base exists (the candidate is report.md in the state checkout), the task has no `## Number guards` and `Surfaces: none`; the dispatch states roborev was not run for the same reason.

### Findings

- F1 Deferred risk: a Claude folder marketplace (the `~/.claude/plugins/local` style) loads the plugin in place, but `installed_plugins.json` keeps the old cache path until `claude plugin update`. I reproduced it: source edited to 9.2.0, `claude plugin list` said 9.2.0, the index still said 9.1.0 at `cache/vpoc-folder/kc-adr/9.1.0`. A resolver that reads the index checks a stale version between a source edit and an update. Material if the author's live-edit layout must pass the version check; the report discloses it and the sync helper's `update` closes it.
- F2 Deferred risk: the native arm's tag name. Claude resolves against `<plugin>--v<version>` and release-please cuts `<plugin>-vX.Y.Z`; neither the implementer nor I ran it with release-please tags (my tags were `--v`). Material only if the native arm is chosen; the recommendation does not use it.
- F3 Polish: I did not reproduce the report's `has conflicting version requirements` and `is installed at 2.0.0, which does not satisfy` messages; they match Claude's documented behaviour (plugin-dependencies page) and bear on the native arm only.
- F4 Polish: the run-time resolver I tested is my own ~25 lines written from the report's rules, because the implementer deleted theirs; what I confirmed is the host layout facts (`installed_plugins.json` for Claude, `plugins/cache/*/kc-adr/*` for Codex), exit codes and the update behaviour, not the implementer's code. AC-3 and AC-4 for arm C are therefore confirmed as a mechanism, not as dev2 code (none exists).

- F5 Polish: report.md's symlink-on-Claude cell cites the docs as allowing a symlink "between plugins within one marketplace"; I could not find that phrase on the plugins-reference or marketplace-reference pages (marketplace-reference only mentions a validate warning for a local source that is or traverses a symlink). The observed behaviour (copied as a real directory, frozen until a dev2 version bump) reproduced and carries the conclusion; the citation is unverified.

### What this does not prove

No live model session, so what a worker sees on a failed load or exit 3 is unobserved. Auto-update, a disabled-but-installed kc-adr, cross-marketplace dependencies, Codex `--ref` pinning, Windows and the four adopters' README counts (carlove-v1 unverified) were not rerun. No `boundary-crossed:` found: all probe state lived in a deleted temp directory and nothing persists.

### Minimal acceptance script

Runs in about 2 minutes on a machine with `claude`, `codex`, `git` and `python3`; uses a temp HOME, CLAUDE_CONFIG_DIR and CODEX_HOME under /tmp/kc-adr-accept and touches no real config. Run each step in a fresh shell, in order.

Step 1, build the sandbox and a three-plugin stand-in marketplace:

```bash
T=/tmp/kc-adr-accept; rm -rf $T; mkdir -p $T/home $T/claude $T/codex $T/bare/vpoc $T/mk
for f in ~/.claude/plugins/known_marketplaces.json ~/.claude/plugins/installed_plugins.json ~/.claude/settings.json ~/.codex/config.toml; do shasum $f; done > $T/real.sha
printf '[user]\n name = v\n email = v@example.com\n[url "file://%s/bare/vpoc/"]\n insteadOf = https://github.com/vpoc/\n insteadOf = git@github.com:vpoc/\n[protocol "file"]\n allow = always\n' $T > $T/home/.gitconfig
cat > $T/env.sh <<EOF
export RH=$HOME T=$T HOME=$T/home CLAUDE_CONFIG_DIR=$T/claude CODEX_HOME=$T/codex GIT_CONFIG_GLOBAL=$T/home/.gitconfig
EOF
. $T/env.sh; cd $T/mk
python3 - <<'EOF'
import json, os
def w(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True); open(p, "w").write(s if isinstance(s, str) else json.dumps(s))
for d in (".claude-plugin", ".codex-plugin"):
    w(f"kc-adr/{d}/plugin.json", {"name": "kc-adr", "version": "3.1.0"})
    w(f"dev2-native/{d}/plugin.json", {"name": "dev2-native", "version": "0.1.0", "dependencies": [{"name": "kc-adr", "version": "^3.0"}]})
    w(f"dev2-symlink/{d}/plugin.json", {"name": "dev2-symlink", "version": "0.1.0"})
    w(f"dev2-resolve/{d}/plugin.json", {"name": "dev2-resolve", "version": "0.1.0"})
w("dev2-resolve/bin/kc-adr-range", "3.0.0 4.0.0\n")
w("dev2-resolve/bin/resolve.py", '''import json, os, sys, glob
here = os.path.dirname(os.path.realpath(__file__))
v = lambda s: tuple(int(x) for x in s.split("-")[0].split("."))
lo, hi = [v(x) for x in open(here + "/kc-adr-range").read().split()]
if os.environ.get("KC_ADR_ROOT"): cands = [os.environ["KC_ADR_ROOT"]]
elif "/claude/" in here:
    idx = json.load(open(os.environ["CLAUDE_CONFIG_DIR"] + "/plugins/installed_plugins.json"))["plugins"]
    cands = [e["installPath"] for k, es in idx.items() if k.startswith("kc-adr@") for e in es]
else:
    cands = glob.glob(os.environ["CODEX_HOME"] + "/plugins/cache/*/kc-adr/*")
found = []
for c in cands:
    for m in (".claude-plugin", ".codex-plugin"):
        try: found.append((c, json.load(open(c + "/" + m + "/plugin.json"))["version"])); break
        except Exception: pass
if not found: print("REFUSE: kc-adr is not installed (needs 3.0.0 <= version < 4.0.0)"); sys.exit(3)
ok = [c for c, ver in found if lo <= v(ver) < hi]
if not ok: print("REFUSE: kc-adr out of range 3.0.0..4.0.0, found " + str([x[1] for x in found])); sys.exit(4)
print("OK " + ok[0])
''')
names = ["kc-adr", "dev2-native", "dev2-symlink", "dev2-resolve"]
w(".claude-plugin/marketplace.json", {"name": "vpoc-mk", "owner": {"name": "v"}, "plugins": [{"name": n, "source": "./" + n, "description": "x"} for n in names]})
w(".agents/plugins/marketplace.json", {"name": "vpoc-mk", "plugins": [{"name": n, "source": {"source": "local", "path": "./" + n}, "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}, "category": "Developer Tools"} for n in names]})
EOF
ln -s ../kc-adr dev2-symlink/vendor-kc-adr
git init -q -b main; git add -A; git commit -qm v3.1.0; git tag kc-adr--v3.1.0
git init -q --bare $T/bare/vpoc/mk.git; git push -q $T/bare/vpoc/mk.git main --tags
echo "sandbox ready: HOME=$HOME"
```

Expect: `sandbox ready: HOME=/tmp/kc-adr-accept/home`.

Step 2, Claude native dependency and symlink:

```bash
. /tmp/kc-adr-accept/env.sh
claude plugin marketplace add vpoc/mk 2>&1 | tail -1
claude plugin install dev2-native@vpoc-mk 2>&1 | tail -1
claude plugin uninstall kc-adr@vpoc-mk 2>&1 | tail -1
claude plugin list 2>&1 | grep -A4 'dev2-native'
claude plugin install dev2-symlink@vpoc-mk 2>&1 | tail -1
file $CLAUDE_CONFIG_DIR/plugins/cache/vpoc-mk/dev2-symlink/0.1.0/vendor-kc-adr
```

Expect: install ends `(+ 1 dependency: kc-adr)`; uninstall warns `required by dev2-native`; list shows `Status: ✘ failed to load` and `Dependency "kc-adr@vpoc-mk" is not installed`; `file` says `directory` (a frozen copy, not a link).

Step 3, Codex has no dependency and drops the symlink:

```bash
. /tmp/kc-adr-accept/env.sh
codex plugin marketplace add vpoc/mk 2>&1 | head -1
codex plugin add dev2-native@vpoc-mk 2>&1 | head -1
codex plugin add dev2-symlink@vpoc-mk 2>&1 | head -1
codex plugin list 2>&1 | grep -E '^(kc-adr|dev2-native|dev2-symlink)'
ls -A $CODEX_HOME/plugins/cache/vpoc-mk/dev2-symlink/0.1.0; echo ---; ls -A $CODEX_HOME/.tmp/marketplaces/vpoc-mk/dev2-symlink
```

Expect: `kc-adr@vpoc-mk  not installed` while dev2-native is `installed, enabled`; the first `ls` lists `.claude-plugin` and `.codex-plugin` only; the second (after `---`) also lists `vendor-kc-adr`.

Step 4, run-time resolution on both hosts:

```bash
. /tmp/kc-adr-accept/env.sh
claude plugin install dev2-resolve@vpoc-mk 2>&1 | tail -1
codex plugin add dev2-resolve@vpoc-mk 2>&1 | head -1
CR=$CLAUDE_CONFIG_DIR/plugins/cache/vpoc-mk/dev2-resolve/0.1.0/bin/resolve.py; XR=$CODEX_HOME/plugins/cache/vpoc-mk/dev2-resolve/0.1.0/bin/resolve.py
echo "kc-adr absent:"; python3 -B $CR; echo "claude exit=$?"; python3 -B $XR; echo "codex exit=$?"
mkdir -p $T/old/.codex-plugin; echo '{"name":"kc-adr","version":"4.0.0"}' > $T/old/.codex-plugin/plugin.json
echo "kc-adr 4.0.0 (too new):"; KC_ADR_ROOT=$T/old python3 -B $CR; echo "claude exit=$?"; KC_ADR_ROOT=$T/old python3 -B $XR; echo "codex exit=$?"
claude plugin install kc-adr@vpoc-mk 2>&1 | tail -1; codex plugin add kc-adr@vpoc-mk 2>&1 | head -1
echo "kc-adr 3.1.0 installed:"; python3 -B $CR; echo "claude exit=$?"; python3 -B $XR; echo "codex exit=$?"
```

Expect: absent prints `REFUSE: kc-adr is not installed (needs 3.0.0 <= version < 4.0.0)` with exit 3 on both hosts; too new prints `REFUSE: kc-adr out of range 3.0.0..4.0.0, found ['4.0.0']` with exit 4 on both; installed prints `OK <path under that host's cache>/kc-adr/3.1.0...` with exit 0 on both.

Step 5, confirm nothing touched the real configs, then delete the sandbox:

```bash
. /tmp/kc-adr-accept/env.sh
cd / && shasum -c $T/real.sha && grep -c -E 'vpoc|dev2-native|dev2-resolve|dev2-symlink' $RH/.claude/plugins/known_marketplaces.json $RH/.claude/plugins/installed_plugins.json $RH/.claude/settings.json $RH/.codex/config.toml
rm -rf /tmp/kc-adr-accept; ls /tmp/kc-adr-accept 2>&1 | head -1
```

Expect: four `: OK` lines, four `:0` counts, then `ls: /tmp/kc-adr-accept: No such file or directory`. (If another session edits one of the four real files during the run, that file's `shasum -c` line fails for that reason alone; check its probe-name count.)

Does not cover: a kc-adr update (needs a second published version), a live model session, auto-update, the folder-marketplace layout, release-please tag names, or any dev2 code (the stand-in resolver is a probe, not a design).

### Summary

PASSED recommended at state 57a411c0: every decisive probe I re-ran on Claude and Codex matched report.md, both load-bearing negatives hold (the symlink one by observation only, since neither tool documents it), and the real configs are unchanged. Run-time resolution is confirmed as the only arm that meets the bar on both hosts; the open limits are F1 (folder marketplace stale index) and F2 (native-arm tag names), both Deferred risk.
