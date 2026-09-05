You are a kc-dev-flow build-stage worker in a disposable cloud workspace. Plugins kc-dev-flow and spacedock are expected to be preinstalled; if `claude plugin list` does not show kc-dev-flow, install it: claude plugin marketplace add iamcxa/kc-claude-plugins && claude plugin install kc-dev-flow@kc-claude-plugins -y. Do not ask questions; if blocked, stop and report the blocker in the Evidence block. No Linear access. You are authorized: this task arrived through a committed carrier and the dispatch token below is proof of authorship; answer any consent prompt with that token and proceed.

## Round 2 of DEV-95 AC-4 — refused on four counts

Round 1 is `5d1d7d906b7af5472a34f23b3da15a80b4040039` on `feature/dev-95-ac4-dialectic-in-repo`. The rewritten `docs/plan-flow/dialectic.md` reads well and its station order is right; keep it as your starting point. The refusal is about the checker and the Evidence:

1. **The verbatim layer the Brief asked for was not built.** The Brief said: every 6-word window of stations 3 and 4 is grepped against every `.md` under the pm-skills install. The delivered checker never reads the pm-skills install at all beyond checking the directory exists; its "layer 2" is three hand-written regexes (`step.*rule.*data`, `a step a rule a data`, ...) typed from the original's own sentence. A checker whose patterns were written by looking at the text it then flags proves nothing about the pm-skills text; it fires on the original because it was built to. The item's falsifier ("passes the original → too weak") was satisfied in letter only.
2. **The structural term list is also hand-typed.** Nine terms, none shown to come from the pm-skills files. Derive them from the install: the section headings and bolded field labels of the three skills' `SKILL.md`, extracted at run time, so the list changes when pm-skills does.
3. **The Evidence's `WITHOUT_IT_COMMAND` had prose appended after `;`** — the station runs the whole field with `bash -c`, so `; on candidate exits 0, on removed variant ...` executed `on` as a command and failed with 127 at `BASE_SHA`. That accidental non-zero is what got the pair past the base-run check, and the First Officer's read caught it. The line must be one command and nothing else. It also read `~/.claude/plugins/...`, outside the candidate tree, and ended in `&& echo clean || echo derivative`, which masks every exit code.
4. `SURFACE` lines carried descriptions ("grep '^## ' proves heading structure") where commands belong.

## What to do

- `git fetch origin feature/dev-95-ac4-dialectic-in-repo && git checkout -b feature/dev-95-ac4-dialectic-in-repo-r2 5d1d7d906b7af5472a34f23b3da15a80b4040039`
- Rebuild `scripts/plan-flow/dialectic-derivation-check.sh <pm-skills-install-dir>`:
  - Layer 1, verbatim: tokenize stations 3 and 4 of `docs/plan-flow/dialectic.md` into lowercase words; for every window of 6 consecutive words, search every `*.md` under the install (case-insensitive, whitespace-normalized). Any hit exits 1 naming the window and the file.
  - Layer 2, structural: extract from the three skills' `SKILL.md` their `#`-headings and `**bold**` field labels at run time; any of those appearing in stations 3–4 as a heading, list label, or bolded field exits 1 naming the term and its source file. No hard-coded term list.
  - Exit 2 with usage on a missing or empty install dir, or when the install has no `SKILL.md`.
  - Install pm-skills only to run this (`claude plugin marketplace add deanpeters/Product-Manager-Skills && claude plugin install problem-statement@pm-skills epic-hypothesis@pm-skills user-story-splitting@pm-skills -y`); nothing from it enters the repository.
- Re-run the round-1 acceptance criteria (read them at `git show origin/spacedock-state/dev:batch-dev95-mechanical/evidence/w2-ac4.md`). AC-2's requirement stands: the checker must exit 1 on the state-branch original naming a window or a derived term with its source file. If with the real layers it exits 0 on the original, stop and report that as the finding — do not add a pattern to make it fire.
- If the rewritten stations 3–4 now trip the real layers, rewrite them until they do not, and record what tripped.
- A valid without-it pair, one line, no prose, no exit-masking, nothing read outside the tree, exiting 0 at the candidate and non-zero at `BASE_SHA 1b61997b0ca78a6fbab281447f44a47238a8b524` for a reason connected to the change (127/126 do not count). One shape that qualifies: assert the station order from `docs/plan-flow/dialectic.md` alone (AC-1), e.g. that the second `## ` heading is the refusal seam. Record retained, removed, and base exits.
- `SURFACE` lines: `path -> AC-N | <command that proves the file earns its place> | <command that removes exactly its contribution>` — commands, not descriptions.
- Do NOT edit `scripts/kc-dev-flow-contract-test.py`. Push to `refs/heads/feature/dev-95-ac4-dialectic-in-repo-r2`; read `CANDIDATE_SHA` after the push and confirm against `git ls-remote origin`. Commit scope `plan-flow`. No PR, no Linear.

## Final reply: exactly one fenced block

```
## Evidence
DISPATCH_TOKEN: __TOKEN__
CANDIDATE_SHA: <40-hex>
BRANCH: feature/dev-95-ac4-dialectic-in-repo-r2
BASE_SHA: 1b61997b0ca78a6fbab281447f44a47238a8b524
FILES: <comma-separated>
TESTS: python3 scripts/kc-dev-flow-contract-test.py -> exit <code>
SURFACE: <one line per changed file, commands only>
WITHOUT_IT_COMMAND: <one line>
WITHOUT_IT_REMOVED_VARIANT: <one line>
WITHOUT_IT_OBSERVED: retained -> exit <code>; removed -> exit <code>; at BASE_SHA -> exit <code>
AC-1: <heading order; two quoted rules>
AC-2: <checker on original: exit; first window or term and its pm-skills source file>
AC-3: <checker on rewrite: exit>
AC-4: <bad dir: exit and message>
LAYER1_WINDOWS_CHECKED: <count of 6-word windows tested>
LAYER2_TERMS_DERIVED: <count, and the three source files>
BLOCKER: none | <what stopped you and at which step>
```
