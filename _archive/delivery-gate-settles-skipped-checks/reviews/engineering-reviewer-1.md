Engineering-reviewer report (kc-dev-flow-2:engineering-reviewer, opus), 2026-10-20, on PR #680 head e80e50cb; saved unedited by FO.

```yaml
engineering_reviewer_report:
  question: >
    The change makes delivery_gate.py ci_problem treat a CheckRun that finished SKIPPED or
    NEUTRAL as passing. A head where no check finished SUCCESS is still held, and runs_problem
    is unchanged. Does this let an unsafe head reach a merge ask or a carried merge (ADR 0023)?
    It reverses the SKIPPED/NEUTRAL clause of merge-gatekeeper AC-1.
  revision: iamcxa/kc-claude-plugins#680 head e80e50cb851ae1f5a5d4353ee34d07cb1733c89a (Draft, OPEN, 4/4 checks SUCCESS, read 2026-10-20)
  conclusion: >
    Safe with conditions. The new rule now matches GitHub's own merge model. It is not true that
    it "never lets an unsafe head through". It does let through one class GitHub also passes: a
    job skipped by mistake while a sibling job succeeded, when no always() fan-in job checks the
    skip. The old hold did catch that class, but it caught every by-design skip too, and all 3
    observed holds ended in a Captain override. So the hold surfaced the skip names but did not
    sort a mistaken skip from a by-design one; the overrides passed whatever was there. The
    floor is cheap and harmless, but it is not the guard against that class.
  material_evidence:
    - "GitHub Docs, troubleshooting required status checks (fetched 2026-10-20): 'Successful check statuses are success, skipped, and neutral'. A job skipped by a conditional 'reports Success'. A job skipped because a prerequisite failed 'may not block merging'. 'Use always() with needs for required checks that depend on other jobs.'"
    - "GitHub Docs, using jobs (fetched 2026-10-20): 'If a job fails or is skipped, all jobs that need it are skipped' unless an always()-style conditional is used."
    - "Shape A, newly passing (probed on a copy of the candidate code): a fan-in job without always() is skipped because the test job it needs was skipped, while lint succeeded. ci_problem returns None. The base rule held it. This is the shape GitHub's docs warn about."
    - "Shape B, newly passing: a test job skipped by a wrong if: beside a succeeded sibling, with no fan-in. The workflow run concludes success (relay#398 stored runs: ci completed/success with 4 SKIPPED jobs), so runs_problem does not catch it either."
    - "Shape C, still held: every job of a run skipped. The run concludes 'skipped' (this repo's runs 32832952254 and 32645994117: all jobs completed/skipped, run conclusion skipped). runs_problem holds it even when a Netlify deploy status SUCCESS meets the floor. This covers web's fork-PR shape."
    - "Shape D, still held: a job skipped because its prerequisite FAILED or was CANCELLED. The prerequisite's own FAILURE or CANCELLED is in the rollup. Also still held: WAITING, PENDING, QUEUED and IN_PROGRESS checks, a COMPLETED check with no conclusion, a status context in EXPECTED, ERROR or PENDING, and lowercase conclusions (all probed)."
    - "relay ci.yml (main): ci-gate runs on every pull_request (always()). Its only skip condition is verified_release_merge, which scripts/ci-runtime-change sets only on push. ci-gate checks every job's result against the classifier both ways, so shapes A and B are not reachable on relay PRs. Remaining relay residual: the classifier itself misclassifies. ci-gate stays consistent with a wrong classification. That is relay's own design, and the old hold also only surfaced it to an override."
    - "qnow pr.yaml (origin/next): ci-gate is always() and fails closed when classify did not succeed. When tests were needed and pr-test's status is not success it fails ('was skipped'), and it posts a ci-gate status context. A and B are not reachable on PRs that reach ci-gate. Release-please PRs skip the whole workflow, giving a skipped run that runs_problem holds, as before."
    - "web ci.yml (main): there is no fan-in. review-gate is the only test job. On a Release Please PR (head ref release-please--*), resolve-release-relay and release-pair should run. If either is skipped by mistake, the head passes beside a succeeded review-gate. That is shape B on web. The design's sentence 'Not reachable on ... web' covers review-gate only. Whether a release PR ever goes through a dev2 delivery ask is not verified."
    - "This repo: the only job-level if: is in e2e-pipeline-real-browser.yml, and when it skips the whole run is skipped, which stays held. No change here."
    - "The floor counts any SUCCESS, including a classify job or a Netlify deploy status context. On Actions-based CI it adds little beyond runs_problem; it matters only for rollups with only third-party checks, or with only a superseded skipped run."
    - "Limit: I did not run the full 68-test suite. I read the six new tests and probed ci_problem and runs_problem directly on a /tmp copy of the candidate code."
  risk_tradeoff: >
    Risk: since ADR 0023, shapes A and B can reach a carried merge with no skip name shown in the
    ask. The old hold at least showed the names to the Captain. This is reversible: one function,
    no data or state written. The ongoing cost is that a carried merge now trusts each adopter's
    fan-in for skips. Cheapest way to close shapes A and B for fan-in adopters later: an optional
    README key naming the single check that must finish SUCCESS (relay's header already says
    ci-gate is 'the only job whose name the merge path should ever know'). That is one name, not
    a list that drifts. Trigger it when an adopter without an always() fan-in, or a web release
    PR, goes through a delivery ask. It does not help web, which has no fan-in. Alternative: print
    the skipped names on a pass, which AC-7's word budget rules out.
  recommendation: adjust
  adjust_items:
    - "The candidate docstring says 'a check run its repository skips by design settles'. The code cannot know 'by design': it settles every SKIPPED and NEUTRAL check. The repo rule 'an absolute names its enforcement point or becomes a bounded claim' applies. Rewrite to the bounded claim, e.g. 'a check run that finished SKIPPED or NEUTRAL settles, as GitHub's merge model counts it'."
    - "The Captain's record of D1 should name shape A as the residual: 'a fan-in job without always() skipped together with the job it needs', and on web 'a release-please PR whose release-pair is skipped'. The design's Limits sentence and its 'not reachable on web' claim cover only shape B on a review-gate job. No code change is needed for this."
  confidence: high (GitHub semantics and the relay, qnow and this-repo workflow reads); medium (whether web release PRs reach a dev2 delivery ask)
  disproof_condition: >
    The recommendation becomes hold if any adopter is found whose delivery-asked PRs run a
    workflow with a conditional test job and no always() fan-in. It also becomes hold if a web
    Release Please PR is shown to go through delivery_gate check with an ADR 0023 carried merge.
    Separately, a GitHub run whose jobs were all skipped but which concluded success would remove
    shape C's guard.
  authority_boundary: >
    The Captain owns reversing merge-gatekeeper AC-1 and accepting the residual (D1). The
    validation stage and FO own the stage gate and the merge ask. delivery_gate.py keeps its
    deterministic hold. This report is advisory: it holds no gate and changes no state.
```

Files read (read-only):
- /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-delivery-gate-settles-skipped-checks/kc-dev-flow-2/scripts/delivery_gate.py (`ci_problem`, `runs_problem`, `check`)
- /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/.worktrees/spacedock-ensign-delivery-gate-settles-skipped-checks/kc-dev-flow-2/scripts/test_delivery_gate.py (`SettledChecksTests`)
- /Users/kent/conductor/workspaces/kc-claude-plugins/colombo/.context/dev2-adoption/worktree/docs/dev2/.spacedock-state/delivery-gate-settles-skipped-checks.md and its replay/ folder

The adopter workflows were read with `gh api` (spacedock-dev/subspace-relay `.github/workflows/ci.yml` and `scripts/ci-runtime-change`, spacedock-dev/subspace-web `.github/workflows/ci.yml`) and with `git show` for iamcxa/qnow `origin/next:.github/workflows/pr.yaml`. Side effects: one `git fetch` in /Users/kent/conductor/repos/qnow, which updated only its remote-tracking refs, and scratch copies in /tmp/er-probe and /tmp/er-*.yml. Nothing was written to any worktree or remote.