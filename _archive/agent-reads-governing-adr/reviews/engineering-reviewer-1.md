# Engineering reviewer 1: agent-reads-governing-adr, Amendment 1 against PR #698

Verdict: proceed. Amendment 1 withdraws nothing else the Captain approved. The build at 589c54e57fe969b6049bad737be8615e96b7b54e implements the amended design and adds nothing beyond it. One point is wider than his words: the check refuses every ref, not only branches. That needs one disclosure line in the merge ask, not a hold.

```yaml
engineering_reviewer_report:
  question: >
    Does Amendment 1 (refuse any REF:docs/adr reference instead of resolving refs
    against origin; AC-4 superseded by AC-8) withdraw anything else approved at the
    ideation gate, does PR #698 implement the amended design and nothing beyond it,
    and is there a Material finding that should hold the merge ask?
  revision: iamcxa/kc-claude-plugins#698 head 589c54e57fe969b6049bad737be8615e96b7b54e (Draft, base main)
  conclusion: >
    No withdrawal. The amendment replaces only the ref-resolution half of the check
    (Mechanism 3(b), AC-4's origin/tag/local-only rows and its fetch falsifier).
    AC-1, AC-2, AC-3, AC-5, AC-6 and AC-7, the non-goals, D2 (no measurement gate),
    D3 (AGENTS.md plus the @AGENTS.md import), D4 (path-filtered, not-required job),
    qnow-as-its-own-task, the five-file list and the without-it bar are untouched.
    AC-8 is narrower than AC-4: it drops the removed-directory, placeholder and
    stale-pointer rows. Those were not withdrawn by the Captain. The build keeps all
    three as tests, so in effect nothing is lost. The build does what the amendment
    says: no fetch, no network, refusal for the stated reason, existence of a
    tracked path, and the bare-directory check. No Material finding.
  material_evidence:
    - >
      Captain's words (Amendment 1): 「路徑檢查改成「禁止指向分支」」, answering FO's
      「…遇到「指向分支」的寫法就直接報錯，要求改成指向主線上的檔案；不去遠端查分支是否存在。」
      Briefing-2 index.json summary: "a path check that refuses branch refs
      (Amendment 1)". Only the amendment's Design paragraph adds "or other ref".
    - >
      PR diff, scripts/adr-path-check.py (81 lines): REF_FORM matches any
      `X:docs/adr...` and refuses it with "point at the file on the trunk". There is no
      fetch, ls-remote or cat-file. PATH_FORM checks `docs/adr/...` against
      `git ls-files`. A bare `docs/adr` needs a tracked NNNN-*.md, and placeholders are
      skipped. The workflow runs the test and then the check, with `contents: read`,
      a pinned checkout and `persist-credentials: false`, and no fetch-depth or
      network step.
    - >
      My own run (a temp clone of the head, fetched by SHA and removed afterwards):
      `python3 -B scripts/adr-path-check.test.py` gave "Ran 14 tests", OK.
      `python3 -B -I scripts/adr-path-check.py` exited 0 on the head. In a probe line,
      `git show v1.0:docs/adr/0001-x.md` and `abc1234:docs/adr/` were each refused
      ("names ref `v1.0`" and "names ref `abc1234`"), exit 1. A GitHub blob URL to a
      missing ADR passed silently, which is the stated limit.
    - >
      The tests also refuse `HEAD:docs/adr/...` and `<branch>:docs/adr/NNNN-x.md`
      (test_other_ref_forms_are_refused). Retained beyond AC-8:
      test_removed_directory_fails_with_reason_not_a_traceback,
      test_directory_without_numbered_adr_fails, test_placeholders_are_not_paths, and
      a STALE fixture shaped like qnow's pointer, which is refused whether the branch
      exists locally, exists on origin, or exists nowhere.
    - >
      release-please-config.json packages at the head: the 11 plugin directories only.
      No package covers the repo root, `scripts/` or `.github/`, so the squash title
      `feat(scripts): …` bumps no component.
    - >
      `gh pr view 698`: the five files are the ones Batch overlap names. The PR body
      carries `## without-it unanswered`: the read effect is unmeasured (D2), the REF
      refusal has no consumer here, and compaction and Codex subagents were not probed.
  risk_tradeoff: >
    Risk is low and cheap to reverse: one paragraph, one import line, and a
    not-required job of about 6 s that runs only on matching PRs (one sample, run
    39659320119). Refusing every ref is stricter than "branch". Today it can refuse
    nothing in this repository, because no instruction file names a ref. Narrowing it
    is a one-regex change. The durable obligation is qnow's task copying the script;
    without that, the refusal has no consumer anywhere (validation F3, already
    disclosed). The alternative is to narrow REF_FORM to branch names and let
    HEAD/SHA/tag pass. That reopens a resolver question the Captain removed. Not
    recommended.
  recommendation: proceed
  confidence: high
  disproof_condition: >
    The Captain says 「禁止指向分支」 meant branches only and wants HEAD, SHA or tag
    forms to pass. Or a release-please package is found that covers root,
    scripts/ or .github/ paths. Or an instruction file on main at merge time names a
    REF:docs/adr form the refusal would break.
  authority_boundary: >
    Advisory only. The Captain owns the merge ask, any narrowing of the refusal, and
    closing throwaway PR #699. FO owns task-file corrections and gate records. CI
    keeps its scoped (not-required) function.
```

## Findings (none Material)

1. Disclosure, not a hold: the refusal is wider than the Captain's words. He ruled 「禁止指向分支」 (forbid branch pointers), and briefing-2 says "refuses branch refs". The amendment's Design paragraph adds "or other ref", and the build refuses HEAD, tags and SHAs too. My probe confirms the `v1.0:` and `abc1234:` forms are refused, and the tests assert the `HEAD:` form. This is consistent with FO's question to him, which asked to require the file on the trunk. Put one line in the merge ask so his approval covers it.

2. Polish, FO record hygiene: the task file's `## Design` still describes the superseded mechanism. Mechanism step 3(b) describes the fetch resolver. Step 4 says "plus a local bare `origin`; one case per row of AC-4". The PRFAQ press release says "`git show REF:path` that does not resolve". The mermaid edge reads `K -->|resolves| D`. Limits says "Fetching a named ref needs network at check time". So the record carries two incompatible designs. The amendment block governs, and the build follows it. A later reader (learn, observer) could take the stale text as the design. No build change is needed.

3. Covered by the build: AC-8 is narrower than the AC-4 it replaced. It drops the removed-directory case, the placeholder case and the stale-pointer fixture. The Captain withdrew none of these; the narrowing came from drafting. The build keeps all three as tests. The bare-directory check is the only part of the script that can bite in this repository today (Design, "Bite and consumer"), so keeping it matters. Validation's directory-always-true mutant turned exactly the two directory cases red.

4. Record note for the Captain: the ideation gate approval (resolution 2) is recorded from his D1 and D2 answers. The record says "This briefing binds those answers after the fact". No separate approve word is quoted. The merge ask is his next ruling and would cover this. Flagged only so he knows how the approval was recorded.

5. Polish, stated limit: GitHub blob URLs and prose naming a branch pass the check. `docs/adrs` and `docs/adr-old` are read as the bare directory. A `word:docs/adr/` with no space is read as a ref. None of these can change the route; all are already disclosed in the PR body or the validation findings.
