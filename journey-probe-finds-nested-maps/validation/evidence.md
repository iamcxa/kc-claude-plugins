# Independent validation of PR #734

Verdict: PASSED at 159b21232dea8ce68fcf9402461e185ff59d327c, against base
8bf4f3582411e8e4238f19fbadda8ddeca6767be. No Material, Deferred risk, Polish,
or Needs decision finding. Gate approval and delivery remain the First Officer's
next handoff to the Captain.

## Artifact and method

Candidate code was assessed in a fresh detached worktree under the assigned
worktree, at `.validation-159b2123`, with no tracked or untracked candidate changes.
The complete diff contains only
`kc-dev-flow-2/references/sd/adoption.md` and
`kc-dev-flow-2/scripts/test_lint_skills.py`.
The candidate's seven-fixture test was executed, then its actual test method was
run against disposable documentation mutations. No product repair was made.

Package scripts came from the explicitly supplied Codex installation,
`/Users/kent/.codex/plugins/cache/kc-claude-plugins/kc-dev-flow-2/0.32.0`, under the skill's package-root rule;
the dispatch's Claude cache path was not used. The workflow was
`/Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2`.

## Acceptance and falsifiers

The retained `falsifiers.py` records the exact independent checks. Its first
three arguments are candidate checkout, installed package root and entity file.
It originally compared the diagram with the ideation path explicitly recorded
by the task; that source and its image are preserved here as `flow.mmd` and
`flow.png`. All test instances used disposable copies and disabled bytecode.

- AC-1: Flat, product-folder and deeper paths with spaces all print exactly the
  expected path. Reverting to the old flat wording fails extraction; adding
  `-maxdepth 1` fails with no nested path.
- AC-2: Empty, missing, non-map suffix/outside-root and YAML-directory fixtures
  pass their expected stdout/exit assertions. Removing file type prints the
  directory; removing suffix prints .tldr/.yml; changing suffix loses flat YAML;
  hiding the missing-root failure changes the required nonzero exit. All fail
  the candidate test. An additional root-only falsifier preserves path formatting:
  on an empty docs/journey plus other/a.yaml, the candidate prints nothing and
  `find docs/journey other -type f -name '*.yaml' -print` prints other/a.yaml;
  both exit 0, and the negative expectation rejects the mutant.
- AC-2 failure seam: chmod 000 on a synthetic child directory produced exit 1
  and stderr while still printing docs/journey/visible.yaml. Permission was
  restored in finally and the fixture removed. Partial stdout cannot establish
  successful traversal. This verifies the shell result, not an agent's reasoning.
- AC-3: The complete adoption reference equals base plus the exact approved
  replacement. All other bytes, including steps 2–6, runtime checks, required
  defaults, no-answer handling, Captain-insistence exception, re-sync and
  activation, are unchanged. Mutations of defaults, selection, no-answer behavior,
  failed-probe interpretation and approval each fail the comparison.
- AC-4: Whitespace split gives adoption 2069 to 2085 and Extensions 350 to 366.
  An extra instruction fails the count. The complete two-file diff changes no
  workflow, mod or instruction-output producer, so startup, either idle path,
  merge ask and archive each add zero words for the same task state.
- AC-5: Two-file scope passes; adding an adopter path fails it. The current
  Mermaid source exactly matches the retained rendered source. The validator
  viewed flow.png: both probe outcomes lead to Captain selection; no answer
  preserves defaults; insistence follows the failed reason; both paths reach
  concrete README review; approval/readiness activates and failure holds.
  Removing its approval edge fails source comparison. Removing the acceptance
  heading makes design_surfaces.py exit 1. Changing only the Mermaid fence to
  text still exits 0, confirming the stated checker limit.

The task's original seven-case Python reproduction was also extracted and run
unchanged in fresh bash: flat/nested/deep-space each exit 0 with their one path;
empty/non-map/yaml-directory exit 0 with []; missing exits 1 with [].

## Required checks actually run

Commands ran from the detached candidate. `<package>`, `<workflow>` and
`<task>` below refer to the exact paths above and this entity's .md file.

| Command | Observed result |
| --- | --- |
| `python3 -B kc-dev-flow-2/scripts/test_lint_skills.py` | 45 tests, OK, exit 0 |
| `python3 -B kc-dev-flow-2/scripts/lint-skills.py` | PASS; 5565 of 5565 words; exit 0 |
| `python3 -B <package>/scripts/adr_lint.py docs/adr --since 8bf4f3582411e8e4238f19fbadda8ddeca6767be` | 39 ADR files, 0 legacy; exit 0; no reserved/new ADR |
| `python3 -B <package>/scripts/number_guards.py check --workflow-dir <workflow> --task <task>` | PASS, no findings; no migrations-path; exit 0 |
| `python3 -B <package>/scripts/comment_ratio.py 8bf4f3582411e8e4238f19fbadda8ddeca6767be HEAD --workflow-dir <workflow>` | 33 code lines, 0 comments, 0.0%; maximum 5% met; exit 0 |
| `python3 -B <package>/scripts/dispatch_records.py <task-folder>` | 4 dispatch records complete; exit 0 |
| `python3 -B <package>/scripts/design_surfaces.py check <task>` | design surfaces presentable; scope check inapplicable at validation; exit 0 |
| `python3 -B <package>/scripts/doc_impact.py 8bf4f3582411e8e4238f19fbadda8ddeca6767be HEAD` | One document: maintain-flow/SKILL.md; exit 0 |
| `git diff --check 8bf4f3582411e8e4238f19fbadda8ddeca6767be HEAD` | No output, exit 0 |

Affected documents: adoption.md updated; maintain-flow/SKILL.md unaffected because
its existing test command and guidance still apply. No added comments require
qualitative disposition. Implementation dispatch 2 settles the shared-file order:
this task goes before the archive task; neither sibling code nor state was edited.

## Limits judged

- File presence deliberately does not validate YAML schema, support .yml, follow
  symlinked map directories, choose a map, or prove hosted release walks. Those
  are accepted non-goals, not missing proof for this correction.
- The actual Ask UI, agent behavior after errors, adoption and activation were
  not run. Their instructions are unchanged; the changed command itself is
  exercised. No claim of end-to-end host adoption is made.
- Mermaid was not rendered again because its source was unchanged. Its retained
  rendered image was independently inspected and its source matched exactly.
  The generic checker alone does not prove diagram semantics.
- PR creation, RoboRev and CI are provider evidence supplied by FO in
  dispatch/validation-1.md: PR #734, clean roborev:1260 and 4/4 CI on this head.
  These resolve the implementation report's then-pending external work; the
  validator did not query GitHub or rerun RoboRev. CI cost per PR is unmeasured;
  no CI job, trigger or dependency changed.
- Goal sufficiency: the exact documented command finds the accepted nested
  layouts. Minimal necessity: reverting the one phrase or restricting recursion
  breaks the test; the added test catches that regression. No other package
  surface is retained for this change.

## Captain acceptance

`acceptance.sh` has five numbered steps, exact commands and expected output.
It requires this repository checkout, the named Codex package, bash, Git,
Python 3 and ordinary POSIX tools. It creates/removes its own detached candidate,
does not write Git configuration, and runs in seconds. Run unchanged:

```sh
bash --noprofile --norc /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/journey-probe-finds-nested-maps/validation/acceptance.sh
```

The five steps cover candidate identity, all seven discovery fixtures, package
lint, exact scope/policy/word count and decision-record lint. They do not cover
live host adoption, hosted review, or the separate manual diagram comparison.
The initial sandbox attempt could not create Git metadata; the same script was
then run unchanged with the approved local permission retry and exited 0.
Observed complete output (test duration is incidental):

```text
Preparing worktree (detached HEAD 159b21232)
HEAD is now at 159b21232 fix(kc-dev-flow-2): discover nested journey maps during adoption
candidate=159b21232dea8ce68fcf9402461e185ff59d327c
test_documented_journey_probe_finds_regular_yaml_at_each_depth (__main__.RouteMutationTests.test_documented_journey_probe_finds_regular_yaml_at_each_depth) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.114s

OK
PASS: basic frontmatter, declared profile routes, role bindings and package script paths
references/sd/workflow.md: 5565 of 5565 words; no unlisted passage repeats it
Not checked: full Agent Skills conformance or host/workflow behavior
adoption=2069->2085; Extensions=350->366; scope=2 files; policy preserved
39 ADR file(s) checked, 0 legacy
```
