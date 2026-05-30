# Learned Patterns

Cross-project patterns accumulated during PR review and feedback resolution.

Curate periodically and PR valuable entries back to the origin repo.

---

## Pre-emit quote-the-line gate beats per-finding adversarial fan-out (2026-05-30)

To raise review precision (kill false positives), the cheap and correct mechanism is an **inline, zero-agent gate**: before any finding is emitted, require it to quote its motivating `file:line` + verbatim source, then self-check whether the quoted code substantiates the claim. The expensive and wrong mechanism is **per-finding adversarial fan-out** — spawning N skeptic subagents per finding to refute it. Measured on a real 13-finding cross-layer PR (3 event-sourced routers + specs): per-finding 3-lens fan-out cost **~2.8M tokens (≈14× a Standard-tier inline review)** because cost scales `O(findings × lenses)` with each skeptic re-reading the same files from scratch. The 3 false positives it correctly killed were all the "claim about code that isn't there" class (probe assumed dead but the guard and decider read different CQRS stores; a claimed missing comment that never existed; a "reformat" that pre-existed in git history) — exactly the class the inline quote-the-line gate self-refutes at zero agent cost. **Rule**: deliver review precision as (1) an inline pre-emit quote-the-line gate at the collator, plus (2) at most ONE always-on whole-diff adversarial pass (a single Claude adversarial subagent and/or a Codex cross-model pass — `O(1)` not `O(findings)`). Never verify findings with per-finding subagent fan-out. If a reviewer claims code is dead/unreachable, require it to quote both the guard and the duplicated handler; divergent CQRS stores (materialized view vs event store) make the path reachable. Workflow-style multi-agent orchestration earns its keep only at the OUTER scale layer (large-diff partition-and-synthesize, batch/fleet review across many PRs, loop-until-dry whole-codebase audit), never as the inner per-finding verifier.

## Nullish coalescing converts explicit null to undefined — silent field-clear bug (2026-03-24)

When a PATCH API uses the convention `null = clear, undefined = no change`, writing `body.field ?? undefined` silently converts the clear intent to a no-op. The nullish coalescing operator treats `null` and `undefined` as equivalent (both trigger the fallback), so `null ?? undefined` returns `undefined`. The decider then sees `undefined` and skips the update. **Rule**: For clearable fields in PATCH routers, always use an explicit null check (`body.field === null ? '' : body.field`) instead of `??`. This pattern recurs in any event-sourced system where the decider uses `!== undefined` to detect changes.

## Proxy enrichment must validate status + shape before parsing (2026-03-27)

When an endpoint proxies to an internal service and enriches the response (e.g., adding `actor_type` from a local DB), the proxy helper may filter gateway errors (502/503/504) but pass through application errors (400/404/500) as valid Response objects. If the enrichment code blindly calls `json.loads(response.body)` and iterates the result, a dict error payload where a list was expected — or vice versa — causes wrong behavior or crashes. PR #1099 had this in two places: `/checks` expected a list, `/checks/{id}` expected a dict. **Rule**: When reviewing proxy enrichment code, verify: (1) status_code < 300 guard, (2) `isinstance` check on parsed JSON shape, (3) fallback path when either fails. The proxy helper's gateway filter is necessary but not sufficient.

## Producer return set must match consumer switch branches (2026-03-27)

When a function returns a fixed set of string values (e.g., `"success" | "error" | "pending" | "info"`), every consumer that dispatches on those values must handle ALL of them explicitly. PR #1099 had `derive_check_run_status` returning 4 values but `_build_checks_section` only had 3 explicit branches — `"pending"` fell into an `else` clause that used a different field (`is_checked`), silently showing the wrong icon. The producer had a docstring listing all values, but the consumer was written before `"pending"` was added and was never updated. **Rule**: When reviewing code that adds a new return value to a string-union function, grep for all consumers and verify each has a branch for the new value. An `else` clause that "works" for the new value by accident is a bug — it may produce correct output for some inputs but wrong output for others (e.g., `is_checked=True` + `pending` → ✅ instead of ⏳).

## Branch names with special characters break GitHub Actions (2026-03-28)

Branch name `pr/phase-12+12.1` caused multiple GitHub Actions workflows to fail. The `+` character is URL-encoded differently across contexts and breaks `${{ github.head_ref }}` in workflow expressions. **Rule**: Use only alphanumeric characters, hyphens, underscores, dots, and forward slashes in branch names. Avoid `+`, `@`, spaces, and other special characters.

## Cross-convention param naming causes dead code in shared helpers (2026-03-27)

When REST API and MCP API use different param key conventions for the same concept (e.g., `node_id` string vs `node_names`/`node_ids` arrays), shared helper functions that only handle one convention silently produce fallback output for the other. PR #1242 had `generate_run_name` checking only `node_names` — REST-created schema_diff runs (using `node_id`) always got the generic "Schema diff" name. The helper appeared correct until Copilot traced the actual param flow from both API entry points. **Rule**: When reviewing a shared utility that reads from `params` dict, trace ALL callers to verify which param keys they actually set. If multiple entry points use different naming (REST vs MCP vs UI), the utility must handle all conventions with documented priority order.

## Cross-plugin state file override must respect explicit user config (2026-03-30)

When two scripts (e.g., a SessionStart hook and a startup script) communicate via a shared state file in `/tmp/`, the script that reads the state file must not unconditionally override values that the user explicitly set (env vars, config files). PR #16 (<plugin-repo>) had `start-mcp.sh` reading a hook-written state file that silently overrode `<APP>_MCP_PORT` env var. The state file protocol should be: `explicit user config (env var) > state file > layered settings > defaults`. **Rule**: When reviewing state file handoffs between scripts, verify the reader guards the state file read with a check for explicit overrides (e.g., `[ -z "${ENV_VAR:-}" ] && [ -f "$STATE_FILE" ]`). The writer's output should never outrank the user's explicit intent.

## Python str-Enum comparison is NOT broken — AI reviewers flag it incorrectly (2026-03-30)

`class MyEnum(str, enum.Enum)` inherits `str`, so `MyEnum.VALUE == "value"` is `True`. AI reviewers (Copilot on PR #1099) flag `event.event_type == "check_created"` as "will never match for real DB rows" — this is factually wrong. The `str` base class ensures string comparison works. **Validation heuristic**: When an AI reviewer claims an enum-vs-string comparison "will never match", check the enum's base classes. If it inherits `str` (or `IntEnum` for ints), the comparison works by design. Accept the "use enum constant" suggestion as a style improvement, but reject the "bug" classification.

## Committed files modified at runtime create dirty working tree (2026-03-30)

When a plugin commits a config file (e.g., `.mcp.json`) that a hook rewrites at runtime, the working tree becomes dirty after every session start. This is invisible for marketplace installs (cache directory, no git) but affects developers working on the plugin repo. PR #16 committed `.mcp.json` with default port 8081, then the SessionStart hook rewrites it when the port changes. **Rule**: When reviewing PRs that add committed files which are also modified by hooks or scripts, check `.gitignore`. If the file is tracked AND runtime-modified, flag it — either gitignore it (generate on first run) or document the tradeoff.

## gh api --jq does NOT support jq flags like --arg (2026-03-30)

`gh api --jq '<expr>'` applies a jq filter to the API response, but it does NOT support jq-native flags like `--arg`, `--slurp`, or `--rawfile`. Writing `gh api ... --jq --arg sha "$VAR" '...'` causes `gh api` to interpret `--arg` as extra positional arguments and fail. When `2>/dev/null || echo "0"` swallows the error, the filter silently returns the fallback value — appearing to work but never actually filtering. PR #545 had this exact bug: SHA-aware dedup always returned "0" because `--arg sha` was never passed to jq. **Rule**: When reviewing `gh api --jq` calls that reference shell variables, verify the variable is either: (1) embedded via shell interpolation in the jq string (safe for hex SHAs, risky for user input), or (2) the output is piped to `jq --arg name "$VAR" '...'` as a separate process. `gh api graphql` has `-f` for variables, but `gh api --jq` has no equivalent.

## Rewrite PRs need regression-aware review against old implementation (2026-04-02)

When a PR rewrites a function (not just modifies it), standard code review validates the new code in isolation — "does the new implementation look correct?" — but misses behavioral regressions relative to the old implementation. PR #1134 rewrote `resetTracing()` with empty catch blocks (`/* best effort */`) that looked reasonable in isolation, but the old code on main had `console.debug` logging. The reviewer (<reviewer-B>) caught this by comparing against main. **Rule**: When reviewing a PR that rewrites (not just edits) a function, fetch the old implementation from the base branch and diff behaviors: error handling, logging levels, resource cleanup, return value semantics. "Looks correct" is not the same as "preserves all prior behaviors that matter."

## One-shot error suppression defeats the observability it claims to add (2026-04-02)

A `firstFlushLogged` boolean guard that silences ALL subsequent errors after the first attempt reintroduces the exact class of silent failure the PR was designed to fix. If the first flush succeeds and later flushes fail (e.g., Langfuse goes down), the operator gets zero signal. PR #1134's `flushLangfuse()` had this — fixed by replacing one-shot with rate-limited logging (once per 60s). **Rule**: When reviewing observability code that uses a "log only once" pattern, ask: "If the 500th call fails but the 1st succeeded, does the operator know?" If the answer is no, the pattern defeats its purpose. Rate-limited logging (timestamp-based interval) preserves signal without causing log spam.

## Resource lifecycle pairing — every `new` needs a `shutdown` path (2026-04-02)

When `new SomeProvider()` is created as a local variable inside an init function but a `reset()` function is expected to clean up all state, the provider leaks because reset can't reach it. PR #1134 created `const langfuseProvider = new NodeTracerProvider(...)` inside `initLangfuse()` but `resetLangfuse()` only cleaned up the processor, not the provider. The provider was passed to `setLangfuseTracerProvider()` (globalThis), but reset+re-init cycles in tests accumulated orphaned providers. **Rule**: When reviewing init/reset pairs, verify every `new` in the init function has a corresponding cleanup in reset. If a resource is stored only as a local variable or passed to an external registry, it needs a module-scope reference for cleanup. Check: `grep 'new ' init_function` → each match should have a `shutdown`/`dispose`/`close` in the reset function.

## Documentation code snippets are unverified — treat as code in review (2026-04-02)

Code examples in `.md` files are not validated by type-checkers, linters, or test runners. PR #1134's CLAUDE.md showed `afterAll(() => flushTracing())` without `await`, contradicting the Gotchas section that says "Tests must use `async afterEach` + `await resetTracing()`". No automated tool caught this. **Rule**: When reviewing PRs that add or modify code snippets in documentation, verify each snippet against the actual API: async functions need `await`, imports match real exports, parameter types match signatures. Docs code is the most-copied, least-verified code in any project.

## Post-squash-merge continuation PRs dilute AI reviewer signal with planning artifact noise (2026-04-13)

When a milestone branch is squash-merged to main and the branch continues with new work, the subsequent PR's diff includes ALL planning artifacts (.planning/, docs/) that were excluded from the squash commit. PR #558 (carlove) had 825 files changed but only 2 source code files — the rest were .planning/ docs, E2E artifacts, and GSD metadata. Copilot generated 13 threads, 11 of which targeted planning artifacts (duplicate milestones, hardcoded paths in plan templates, stale progress numbers). Only 2 threads targeted actual code. **Triage heuristic**: For post-squash-merge continuation PRs, immediately filter threads by path — `.planning/`, `docs/`, `.claude/` threads are almost always informational (reply and move on). Reserve validation effort for threads targeting `src/`, `apps/`, `scripts/`, `packages/`. **Prevention**: Consider excluding `.planning/` from PR diffs via `.gitattributes` linguist-generated, or split planning docs into a separate PR.

## Eval patch files with answer-hinting comments undermine test validity (2026-04-02)

When eval scenarios use "deleted file" patches that get reverse-applied to create buggy state, any comments inside the patch content (like `-- BUG: uses count ratio instead of cost ratio`) become visible in the created SQL files the agent reads during evaluation. This gives the agent a direct hint about the bug, undermining the eval's ability to measure detection capability. **Rule**: When reviewing PRs that add eval/test scenarios with patches, check whether the patch content contains comments that hint at the expected answer. Bug documentation belongs in the scenario YAML or a separate SCENARIOS.md, not in the code the agent will inspect.

## Ground truth docs must be cross-checked against authoritative YAML (2026-04-02)

When eval scenarios have both human-readable documentation (SCENARIOS.md) and machine-readable ground truth (YAML files), the two can drift. PR #21 had SCENARIOS.md claiming `dashboard_impact: yes` and `issue_found: yes` for code-001, while the YAML ground truth (which the scorer actually uses) said `false` for both. Both code-reviewer and comment-analyzer agents independently caught this — confirming that cross-referencing documentation against code is a high-value check. **Rule**: When reviewing PRs with eval scenarios, always verify that documentation claims match the YAML ground_truth fields, especially for boolean fields where yes/no disagreement is easy to miss.

## Template literal escaping in LLM prompts must be rendering-verified (2026-04-08)

Standard code review — even multi-pass with correctness, security, and cross-reference checks — does not evaluate what a JavaScript/TypeScript template literal actually renders to. PR #1143 had `\\\`\\\`\\\`suggested-actions` in a prompt template that rendered as `\`\`\`suggested-actions` (each backtick preceded by a literal backslash). Code reviewers see the source `\\\`` and think "escaped backtick, looks right" — but the double-escape produces an extra `\` in the output. The LLM copies this invalid fence, and the Python parser (`parse_suggested_actions_from_summary`) fails to match. Copilot caught this; an 8-pass Claude review did not. **Rule**: For files containing LLM prompt templates, add a "prompt rendering" review pass: mentally evaluate (or actually run) the template literal output and verify the rendered text matches the parsing regex on the receiving end. Pay special attention to fenced code blocks where backtick escaping compounds.

## Pre-ship review must check commit structure, not just aggregate diff (2026-04-08)

When a PR has multiple commits with deliberate separation-of-concerns, reviews that only see the aggregate diff can't judge whether orthogonal changes are properly isolated. PR #1143 had `strictMcpConfig: true` correctly isolated in its own commit (<sha>), but a review Pass F flagged it as "orthogonal bundled change — should be a separate commit" because it only saw the final diff. This is a false positive that wastes author time responding. **Rule**: When reviewing PRs with 5+ commits, read `git log --oneline` before filing "this should be a separate commit" feedback. If the change IS already a separate commit, the review pass should note "already isolated in commit X" rather than flagging it.

## Defensive parsing needs type check, not truthy check (2026-04-08)

When filtering LLM-generated JSON data, `dict.get("field")` returns a truthy value for lists, dicts, numbers, and non-empty strings alike. If downstream code uses the value as a set/dict key (unhashable types crash) or performs string operations, the filter must explicitly check `isinstance(value, str)`. PR #1143's `parse_suggested_actions_from_summary()` used `a.get("id")` as a filter — Copilot's round 5 review caught that a malformed JSON with `"id": ["list"]` or `"id": {"dict": 1}` would pass the filter and crash at `set()` construction in `should_fallback_to_full_regen()`. The initial defensive parsing was added in round 2 without this level of rigor. **Rule**: When filtering LLM-generated structures for downstream use, check the exact type you need (`isinstance(x, str)`, `isinstance(x, int)`), not just truthiness. Especially important for fields used as dict/set keys or in string operations.

## Near-identical test files at different paths survive glob-based test runners (2026-04-08)

When test configuration uses a broad glob like `src/**/*.test.ts`, duplicate test files at different paths (e.g., `src/agents/__tests__/foo.test.ts` and `src/tests/foo.test.ts`) both run silently without warning. PR #1143 had two amendment prompt test files with 80% overlapping assertions — the `__tests__/` version was an earlier draft, and the `src/tests/` version was the intended canonical location, but neither was deleted. Both passed in CI, so no signal. **Rule**: When creating test files, grep for existing tests of the same export before writing. When reviewing, check if the PR adds a test file for a function that already has tests elsewhere. Convention-based detection: if a project uses `src/tests/` exclusively, any `__tests__/` directory in the same PR is suspicious.

## Scalar-to-array migration in event-sourced evolve must fallback to scalar (2026-03-30)

When upgrading a scalar FK to an array field (e.g., `primaryServiceId` → `primaryServiceIds`), the DB migration backfills the materialized projection, but event replay rebuilds state from events alone. If the evolve function initializes the new array as `[]` without checking the old scalar, replaying historic `Created` events loses the legacy link — `primaryServiceIds` stays empty unless a later `LinksSet` event exists. PR #546 had this in both decider and view evolve. The adapter's `mapToViewState` also needed a fallback from the array column to the scalar for partially-backfilled rows. **Rule**: When reviewing a scalar→array field migration in an event-sourced domain, verify three locations: (1) decider evolve initializes array from scalar, (2) view evolve does the same, (3) adapter/repository `mapToViewState` falls back to scalar when array is empty. The DB backfill covers the projection table but NOT the event stream — replay safety requires all three.

## Semantic refactor must update doc/code/test as one unit (2026-04-07)

When changing the semantics of a function (not just renaming or moving it), three sources of truth must be updated together: (1) the implementation, (2) JSDoc/docstrings on that implementation, (3) tests asserting the behavior. Updating only one creates a three-way disagreement that compiles, runs, and passes — until a reviewer notices. PR #1145 had `buildLookupIndex` with the dedup strategy flipped from "last-wins" to "first-wins" in a prior commit; the inline `// First occurrence wins` comment was added but the JSDoc still said "Last write wins" and the test still asserted `version: 'last'`. The test passed because it was written for the old behavior and never re-run after the semantics changed. Copilot caught all three in one review pass. **Rule**: When reviewing a PR that changes function semantics (not signature), grep for the function name across `*.ts`, `*.test.ts`, and JSDoc comments in the same file, and verify all three tell the same story. A passing test suite is not proof of consistency — it can be proof that the test was written before the semantics flipped.

## kc-pr-create and kc-pr-review have asymmetric agent coverage (2026-04-09)

`kc-pr-create` Step 10a ("Self-Review & Fix Loop") dispatches only 2 of the 5 `pr-review-toolkit` agents: `code-reviewer` and `comment-analyzer`. The remaining 3 — `silent-failure-hunter`, `type-design-analyzer`, `pr-test-analyzer` — are not run during PR creation, but ARE run when `kc-pr-review` (or `claude-code-review`) fires post-PR. PR #1145 shipped with 7 CRITICAL/HIGH silent-failure findings and 1 HIGH type-design finding that were not caught during pre-PR self-review but were caught when @<reviewer-B> ran a post-PR review with the full toolkit. This is the wrong direction: from an author perspective, pre-PR review should be **stricter** than post-PR review (catch problems before they become reviewer feedback), but the current skill wiring makes it weaker. **Rule**: (1) When handling pre-PR self-review via `kc-pr-create`, manually supplement by dispatching `silent-failure-hunter`, `type-design-analyzer`, and `pr-test-analyzer` before marking the PR ready — don't rely on the skill's default 2-agent set. (2) When a post-PR review surfaces items that a pre-PR review should have caught, check whether they come from one of the three missing agents; if so, this is a skill coverage gap, not an author oversight. **Skill fix candidate**: add at minimum `silent-failure-hunter` to `kc-pr-create` Step 10a — silent failures have the highest blast radius and are exactly the kind of bug that becomes embarrassing if caught by a reviewer.

## Cross-reference external agents against your own findings, not just the PR (2026-04-09)

When a reviewer posts a multi-agent review summary (e.g., "Reviewed with 5 specialized agents"), independently dispatch the same agents against the PR yourself before responding. This catches two things: (1) items the reviewer's run missed (different random seeds, partial file reads, single-agent-per-dispatch vs batched), (2) items where the reviewer's agent surfaced a valid finding but a different agent would have caught additional related items. PR #1145: @<reviewer-B>'s review had 8 important items; running the same 3 agents independently surfaced 7 more HIGH/CRITICAL items across the same files (including H7 `InputKey` brand type and C4 mock MCP stderr invisibility). Neither the reviewer nor I would have caught all of these alone. **Rule**: When a reviewer uses multi-agent tooling, treat their output as a starting point — dispatch the same tools yourself with full file context, diff the findings, address the union. This also uncovers skill coverage gaps (see above — we'd never have spotted the kc-pr-create / kc-pr-review asymmetry without running the missing agents manually).

## AI reviewers flag advisory `engines.node` mismatches as blockers (2026-04-11)

npm/pnpm `engines.node` is advisory metadata unless `engine-strict=true` is set in `.npmrc`. AI reviewers (Copilot on PR #1177) flag cases where a transitive dep declares a stricter floor than the declaring package (e.g., `chevrotain@12.0.0` declares `engines: {node: '>=22.0.0'}` but `<service>/<agent>/package.json` declares `>=20`) as install/runtime risk — but the package's code doesn't actually use any Node 22-specific runtime API, CI/Docker both run Node 24, and local tests pass cleanly on Node 20.19.6. Bumping `engines.node` to match would introduce phantom `pnpm install` warnings on the only environment actually on the lower version for zero functional gain. **Validation heuristic for any "dep X requires Node Y but we declare Z" flag**: (1) grep for `.npmrc` with `engine-strict` — no strict-engine means install can only warn, never fail; (2) check CI workflows' `node-version` pin and production Dockerfile `FROM node:*`; (3) trace whether the complaining dep is reachable from the production entry point (esbuild bundle from `src/index.ts`) versus test-only utilities; (4) actually run the affected module on the lower Node version via `tsx --test` or equivalent to verify runtime behavior. If (1)–(4) all clear, classify as advisory-metadata false positive and reply with evidence instead of bumping the floor. Corollary: the fact that a reviewer's suggestion is technically grounded (the dep *does* declare >=22) does not make it actionable — empirical verification always beats declaration comparison.

## Spacedock parent/child workflow: PR code lives on ensign worktree, not FO tracking branch (2026-04-11)

When a spacedock workflow is commissioned with a custom PR-create mod (e.g., `_mods/kc-pr-create.md`), the PR branch and the first-officer (FO) tracking branch are separate git refs on separate worktrees. FO commits carry workflow state (`dispatch:`, `bounce(uat→fix):`, `pr-review:`, `review-resolve(round-1):`) while the ensign worktree carries the actual PR code on a `spacedock-ensign/<entity-slug>` branch. Running `kc-pr-review-resolve` from the FO worktree causes all file reads to miss — the files Copilot reviewed live on the ensign branch at a different SHA (PR #1177 example: FO branch `feature/<ticket-b>-<feature-slug>` at `<sha>` vs ensign branch `spacedock-ensign/<author>-mermaid-syntax-error` at `<sha>`, and Copilot's review `commit_id` matched the ensign HEAD). **Rule**: Before validating AI reviewer claims against files, run `git worktree list | grep spacedock-ensign` to check whether the PR is being managed by a spacedock workflow. If it is, cd into the ensign worktree (`.worktrees/spacedock-ensign-<entity-slug>`) and do all file reads, edits, commits, and pushes from there. The FO branch only gets commits for entity-state updates (e.g., writing `review_feedback:` back into `docs/<workflow>/<entity>.md`). Review commit SHA (`reviews[].commit_id` from the GitHub API) always matches the ensign worktree HEAD, never the FO HEAD — use that as a fast "am I in the right worktree?" check.

## Review agents without Bash access produce false positives on cross-branch PRs (2026-04-14)

When dispatching `pr-review-toolkit:code-reviewer` or `pr-review-toolkit:comment-analyzer` for a PR on a branch not currently checked out, these agents cannot run `git show FETCH_HEAD:<file>` or any git commands because they lack Bash access. They attempt to read the PR branch files via the Read tool on `.git/objects/` pack files (creative but fails on binary data). The result: agents reason about code they cannot see, producing findings based on assumptions about the PR changes rather than actual code. PR #1187 (<infra-repo>) had 3/5 code-reviewer findings as false positives — `flag_modified` usage (confirmed present), `actions_marker` addition (confirmed present), and `detail=str(e)` leak (confirmed safe) — all because the agent couldn't verify its assumptions. **Mitigation options**: (1) Use `general-purpose` agent type instead (has Bash), with review-focused prompt instructions. (2) Create a worktree for the PR branch before dispatching, so agents can Read files at a known path. (3) Pre-fetch all changed files into a temp directory and include file paths in the agent prompt. (4) Accept the false-positive rate and rely on Step 5c baseline validation to filter — this is what the current skill does, but it wastes agent tokens. Option (2) is most reliable if worktree setup cost is acceptable.

## ToB security reviewer provides positive verification value beyond finding bugs (2026-04-14)

The `tob-security-reviewer` agent's 12 `clean_patterns` entries provided concrete positive security evidence (HMAC verification correct, regex anchored, flag_modified used, cross-tenant prevention confirmed, etc.) that no other agent type produces. When all ToB findings are LOW/MEDIUM and classified as DOC after baseline check, the clean_patterns still justify the agent dispatch by giving the reviewer specific evidence to back an APPROVE decision. Without clean_patterns, APPROVE means "I didn't find anything wrong." With them, APPROVE means "I verified these 12 security properties are correctly implemented." This is especially valuable for webhook/auth PRs where "no findings" could mean "didn't look hard enough." **Action**: When presenting ToB results in the review body, always include clean_patterns as a verification summary, even when all findings are advisory.

## Seed/test credentials in committed E2E files are not credential leaks if documented (2026-04-09)

AI reviewers (Copilot on PR #552) reliably flag hardcoded credentials in E2E flow files as "sensitive info leaking via git history" — even when the credentials are for seed/dev accounts that only exist in local/preview databases and are publicly documented in the project's own CLAUDE.md. Example: `seed-user@example.com` / `seedpass` appears in `verify-phase22-media.yaml`, but the same account and password are already listed in `<app>/CLAUDE.md` Test Users table (with an explicit "Default Password: seedpass (all users)" note). Templating these to env vars would add zero real security — the same credentials are already checked in as team documentation. **Validation heuristic**: When an AI reviewer flags hardcoded credentials in a test/seed/E2E file, grep the project's CLAUDE.md and docs/ for the same values. If they appear as documented seed/test users, classify as false positive — reply explaining the context rather than refactoring. The refactor would make the flow harder to run locally without any production safety benefit. **Exception**: If the credentials look like real production values (company email domains, complex passwords, API keys matching secret formats), treat as valid even without documentation cross-check.

## "Flag without consumer" — adding a type field without updating readers (2026-04-22)

When a PR adds an optional flag to a shared type (e.g., `error?: boolean` on `JudgeResult`), verify that at least one consumer reads the flag and changes behavior. The type system does not enforce reads — `r.passed` still compiles without checking `r.error`, so the flag is dead on arrival. PR #1216 (<TICKET-A>) added `JudgeResult.error` with a JSDoc saying "Don't trust `passed` when true" — but `cli.ts` and `bq/runner.ts` still dispatched purely on `r.passed`, making API-error judge results indistinguishable from real content failures. **Validation heuristic**: when reviewing a PR that adds an optional field to a type, grep for all `.fieldName` reads in the codebase. If zero consumers exist and none are added by the PR, flag it: "field added but never read — intent declared but not realized." This is distinct from "unused export" (which the type checker can catch with `noUnusedLocals`) because optional fields on existing types are invisible to unused-detection.

## Feature-removal PRs produce predictable doc drift that AI reviewers catch (2026-04-21)

When a PR removes a feature/module, AI reviewers (Copilot on PR #568, `fix/remove-dead-auth-webhook-trigger`) consistently find 3 classes of doc drift that slip past the author: (1) JSDoc on neighboring code still referring to call sites that no longer exist (e.g., `setup.ts` JSDoc "Special user methods for webhooks" after the webhook chain was removed), (2) troubleshooting tables whose remediation steps rely on the removed code path (e.g., CLAUDE.md row "User stuck in 'invited' → Trigger auth update event" after the notify_user_authenticated trigger was dropped), (3) "Consumers"/"Callers" lists still naming the removed caller OR naming a caller that never actually matched the list's semantic (e.g., vault-setup.sql "Consumers: jwt_custom_access_token()" when that function actually reads from a view, not Vault). The third category is especially subtle because the claim can be freshly introduced by the PR author during the removal sweep itself — writing a "while I'm here, let me update the consumers list" edit without tracing the actual data flow. **Pre-push sweep rule**: after a feature removal, grep for the removed symbol name across `*.md`, JSDoc in `*.ts`, and SQL/shell comments; update or delete anything that references it. For any "X consumes/uses Y" claim written during the sweep, verify against the canonical source (migration SQL for DB functions, function definition for types, grep for runtime callers for methods) before writing. A one-pass visual scan is not enough — AI reviewers will catch what the eye missed. **Resolve-side heuristic**: when an AI reviewer flags "comment says X uses Y but it doesn't," this is almost always right. The factual claim is trivially checkable (read the canonical definition); accept-without-debate is the efficient response.

## Cross-AI-reviewer thread deduplication — same issue, two voices (2026-04-23)

When a repo has multiple AI reviewers running (e.g., `copilot-pull-request-reviewer` + `<ai-summary-reviewer>`), they reliably duplicate coverage on the high-signal items. PR #571 (PROJ-303) had 10 unresolved threads from 2 bots, but deduplication collapsed them to 6 unique issues — keyboard double-fire (2 threads, same file), vitest setup scope (2 threads), and ResourcePageShell API decision mismatch (2 threads) were all same-finding/different-voice. Current skill triage presents each thread as its own row, inflating the work estimate and inviting duplicate fix commits. **Triage heuristic**: before proposing the action plan, group threads by `(file, conceptual_issue)` rather than by `(file, line, author)`. Present as "Issue N: X threads from Y reviewers." Reply to each thread separately (reviewers won't see cross-thread acknowledgment), but fix once. This also reveals when reviewers actually disagree — rare and high-signal — vs when they just agree in parallel.

## PR description drift after iter-based execution — "decision violation" means doc stale, not code (2026-04-23)

When a PR's execute phase goes through multiple iterations that reverse decisions locked in the initial plan (e.g., explicit-props → compound-children shell API), the PR description's "Decisions (locked)" section is NOT auto-updated. AI reviewers correctly flag the mismatch as a "decision violation" pointing to the code. PR #571 had <ai-summary-reviewer> and copilot both flag `ResourcePageShell` compound API as "violates PR description decision #2" — but the authoritative state was the code (iter #2 commit <sha> (commit subject paraphrased) consciously reversed the decision; PLAN.md was already compound; proof-of-life page consumed compound). **Validation heuristic for "decision violation" threads**: (1) git log the flagged file for any commit with keywords "drop/remove/replace/reverse" since PR creation, (2) read the plan's task spec in `.planning/<feature>/PLAN.md` — does it match code or PR description?, (3) check the proof-of-life / first-consumer file — which API does it use? If plan + consumer + recent commits all point one way and PR description points the other, PR description is stale. Fix by updating PR description, not the code. **Pre-push rule for iter PRs**: before `git push` on an iter that reverses a locked decision, also update the PR description's Decisions section. AI reviewers will catch the mismatch otherwise.

## Lockfile-shaped artifacts are team tooling, not local junk (2026-04-23)

AI reviewers (Copilot on PR #571) reliably flag unfamiliar lockfile-shaped JSON files (e.g., `skills-lock.json`, `.agents/skills/*`) as "generated/agent-local, not referenced anywhere, should be gitignored." For genuinely local artifacts (`.claude/settings.*.bak`, `.cozempic-init.lock`) this is correct. For **tool-lockfiles that pin team-shared resources** (find-skills' `skills-lock.json` pinning an externally-sourced skill with a computed hash, similar to `package-lock.json`), gitignoring would delete the team's version-lock mechanism. **Triage heuristic before gitignoring**: (1) does the file have a `version` field + per-item hash/source/SHA? — lockfile smell, (2) does the sibling directory contain actual content (not just cache)? — shared-source smell, (3) does the tool that generates it have a "team mode" or multi-user use case? — tool-config smell. If any → ask user "this looks like a team-shared lockfile; keep + document, or gitignore?" before recommending removal. Corollary: when keeping, reply to the reviewer with the intentionality rationale so future AI reviews can learn the pattern. Copilot specifically has no persistent memory across PRs, but human readers of the thread discussion benefit.

## Requesting Copilot review needs the `[bot]` suffix via direct API, not `gh pr edit` (2026-04-23, updated 2026-05-13)

The skill's Step 7 Option 2 ("re-request AI review safely") originally prescribed `gh pr edit PR_NUM --add-reviewer <bot>` to re-trigger AI reviewers without @mentioning them in PR comments. This works for bots registered as repo collaborators (e.g., Claude via `claude-review.yaml` workflow).

**For GitHub Copilot specifically, the gh CLI surface is broken** — but the underlying REST API DOES work if you use the literal `[bot]` suffix in the reviewer name. Originally documented (PR #569, 2026-04-23) as "Copilot cannot be re-requested at all"; PR #17 (2026-05-13) discovered the working API call:

```bash
# ✅ WORKS — direct API with literal [bot] suffix
gh api -X POST repos/OWNER/REPO/pulls/PR_NUM/requested_reviewers \
  -f 'reviewers[]=copilot-pull-request-reviewer[bot]'

# ❌ FAILS silently — gh CLI returns "ok edited" but Copilot is NOT in requested_reviewers
gh pr edit PR_NUM --add-reviewer copilot

# ❌ FAILS with HTTP 422 — same name without [bot] suffix
gh api -X POST repos/OWNER/REPO/pulls/PR_NUM/requested_reviewers \
  -f 'reviewers[]=copilot-pull-request-reviewer'
```

Verified twice on PR #17: initial-request AND re-request after a follow-up push both succeed via the `[bot]`-suffix API call. The `HTTP 422: Reviews may only be requested from collaborators` error still applies to the unsuffixed variant — what GitHub actually requires is the bot's full identifier including `[bot]`.

**Implementation note**: `kc-pr-review-resolve` uses the direct API call for Copilot (per Step 7 re-request flow, 2026-05-13). `kc-pr-create` does NOT currently request Copilot reviewers — it only polls for auto-triggered review responses (Step 12 `--ci` flow); when it eventually adds an explicit reviewer-request, adopt the same direct-API pattern. `gh pr edit --add-reviewer` remains correct for collaborator bots (Claude, Coderabbit paid). The author's `login` field for the resulting Copilot review will be `copilot-pull-request-reviewer` (NOT `Copilot` as it appears in `requested_reviewers`) — see the next entry below.

**Fallback if even the API call fails** (haven't seen it, but for safety): (a) human clicks "Re-request review" on Copilot's avatar in the PR UI, (b) wait for auto-review-on-push if the repo enables it, (c) push an empty commit to force a new commit event.

## Copilot's author.login varies by GitHub API endpoint (2026-05-13)

When monitoring or filtering for Copilot reviews, the bot's `login` string differs across endpoints — a filter built for one endpoint silently misses on another:

| Endpoint | Field | Returns |
|---|---|---|
| `/pulls/{n}` → `requested_reviewers[]` | `.login` | `Copilot` (capital C) |
| `/pulls/{n}` → `reviews[]` | `.author.login` | `copilot-pull-request-reviewer` |
| Inline review comments (`/pulls/{n}/comments`) | `.user.login` | `copilot-pull-request-reviewer[bot]` |

PR #17 monitor used `select(.author.login == "Copilot")` and silently reported "no Copilot review" for an hour while Copilot had reviewed within 5 minutes. Safest jq filter form: `select(.author.login | startswith("copilot") or . == "Copilot")` — robust to GitHub adding new variants.

## Copilot's "low confidence" suppressed comments are often correct (2026-05-13)

When Copilot's PR review body contains a `<details><summary>Comments suppressed due to low confidence</summary>` section, READ the suppressed comments. PR #17 had exactly one suppressed comment about `verify-install.sh` strict-mode handling — verified against actual code, it was a real bug (CI strict-mode env var was only consulted on the import-failure branch, not on bun-missing). Fix landed as commit `f3aed43` before merge.

**Rule**: same trust-but-verify discipline as for non-suppressed Copilot comments. "Low confidence" is Copilot's miscalibration, not a reliable signal of finding quality. Sample size is small (n=1); re-evaluate after more PR cycles, but default to read.

## kc-pr-review misses "mundane but important" quality gates that multi-pass reviewers catch (2026-04-24)

PR #1213 (<infra-repo>, 48 files) was reviewed by both `/kc-pr-review` and <reviewer-A> (Claude Code running an 8-pass systematic review: Correctness → Security → Cross-Ref → Error Handling → Test Coverage → Diff-Specific → Performance → Async). kc-pr-review found 3 valid code-logic findings (detached ORM objects, DRY bypass). <reviewer-A> found those same logic issues PLUS 10 additional findings across 6 categories that kc-pr-review completely missed:

| Category | <reviewer-A> found | kc-pr-review gap |
|----------|-----------|-----------------|
| Config file security | cozempic hooks in shared settings.json (BLOCKER) | Doesn't review config/dotfiles |
| Accidentally committed files | .bak, .lock, .pid ephemeral files (BLOCKER) | Doesn't scan for non-code artifacts |
| Fixture PII | Personal email in test fixture | Doesn't scan fixtures for PII |
| Linter compliance | 3 biome format violations, 3 non-null assertions | Doesn't run external linting tools on diff |
| Dead code | 74 lines of orphaned judge criteria (zero imports) | Doesn't grep for unused exports |
| Comment ↔ code consistency | Comment claims "Passed/Analyzed" but builder only uses run_status for Error | Doesn't verify that code comments match actual behavior |

**Root cause**: kc-pr-review is a single-pass "read diff, find code bugs" flow. It excels at logic-level review but has no structured passes for: (a) running linters/formatters on changed files, (b) scanning non-code files (config, fixtures, gitignore), (c) verifying comment claims against referenced code, (d) detecting dead code via import analysis. **Improvement plan**: Add 3 optional verification passes to kc-pr-review Step 4.5 (Pre-scan): **(1) Lint gate (4.5f)** — run project linter on changed TS/Python files, report violations as findings. **(2) Non-code scan (4.5g)** — check config files, test fixtures for PII, gitignore consistency with committed files, accidentally committed ephemeral files. **(3) Dead code check (4.5h)** — for new exports in the diff, grep for imports; flag zero-import exports. These are mechanical checks that don't require LLM reasoning — they're tool-output verification, the exact class kc-pr-review currently skips. **Status**: Steps 4.5f/g/h implemented in commit `<sha>` (2026-04-24).

## Silent mock gaps in exception-swallowing code paths are invisible to diff-only review (2026-04-24)

When a PR adds a new function call (e.g., `get_session_state(sa_session)`) inside a `with` block that is wrapped in a broad `except Exception` handler, existing tests pass silently even without mocking the new call — the exception is swallowed and the fallback path produces correct-looking output. PR #1213 added S3-based `run_status` enrichment to both `_rerender_pr_comment` handlers. The existing tests mocked `get_db_session` (to provide `sa_session`) but not the new `get_session_state` call. Since `sa_session` is a `MagicMock`, `cast(str, MagicMock())` produces garbage S3 bucket names → boto3 throws → exception handler catches → `run_status` enrichment silently skipped → tests pass because `is_checked`-based rendering works independently. The `run_status="error"` → `"❌ Error"` rendering path was **completely untested** across 8 rerender tests.

**Why LLM reviewers miss this**: Discovering the gap requires **3-hop reasoning**: (1) identify the new production call, (2) trace its dependency chain to an external service (S3), (3) check whether the test mocks cover that chain, (4) determine whether the exception handler masks the failure. Diff-only review sees `mock_sa_session = MagicMock()` and assumes mock coverage is complete. CI green reinforces the assumption. Review agents without Bash (pr-review-toolkit:code-reviewer) can't run tests with `mock.assert_called_once()` or coverage analysis to surface the gap.

**Detection heuristic**: When reviewing a PR that adds new function calls inside `try/except` or `with` blocks in production code, AND existing tests mock the enclosing scope (e.g., `get_db_session`) but not the new call: (1) trace the new call's dependency chain — does it reach an external service (S3, DB, HTTP)? (2) check if the enclosing scope has a broad exception handler (`except Exception`, `except BaseException`, bare `except:`) (3) if both: flag as "test passes via exception swallowing, not via correct execution." This is a specific instance of the "Mock pollution from new fire-and-forget calls" pattern (MEMORY.md) but harder to catch because the failure is silent (no test error, no log output).

**Improvement**: This class of bug is NOT mechanically detectable via lint/grep (unlike 4.5f/g/h). It requires understanding call chains and exception flow. Currently only catchable by: (a) `pr-review-toolkit:code-reviewer` with Bash access (can run targeted coverage analysis), (b) `pr-review-toolkit:silent-failure-hunter` (designed for exactly this class — exception-swallowing audit), or (c) multi-pass review that explicitly traces new calls through exception handlers. **Action**: When dispatching review agents for PRs that modify code inside try/except blocks, always include `silent-failure-hunter` alongside `code-reviewer`.

## Dead-export check must include scenario `assertions:` arrays, not just imports (2026-04-27)

Pre-scan 4.5h (Dead Export Detection) currently greps for `import.*NAME` to confirm a new export is wired. PR #1245 (<infra-repo>) added `createCheckDescriptionsNeutral` BQ assertion: exported from `tool-usage.ts`, re-exported via `assertions/index.ts` barrel, AND imported by its own unit test in `tool-usage.test.ts`. By import-grep alone the export looked wired. **But no BQ scenario actually included the assertion in its `assertions:` array** — all scenarios in `src/tests/bq/scenarios/*.ts` use `DISALLOWED_TOOLS_ASSERTIONS`, `subagentDelegated`, `toolWasCalled`, etc. The PR claimed "BQ assertion validates tool call inputs against forbidden patterns" but mock/real BQ runs would never invoke it. Dead at the framework level despite passing import-grep.

**Detection heuristic**: For test-framework code (BQ scenarios, Jest test factories, registered hooks), the wiring step that matters is **registration into a runner-consumed array**, not just importing the symbol. After import-grep passes, do a second-pass grep for the symbol's name appearing as a *value* in array literals (`assertions: [..., NAME(), ...]`, `hooks: [NAME, ...]`, `cases: [..., NAME, ...]`). If found in barrels but not in any consumer-array position → still dead at the framework level. Surface as HIGH (not NIT) when the PR's claimed regression coverage depends on the registration. **Implementation note**: extend 4.5h to flag `import { NAME }` followed by zero appearances in array-literal positions across registry/scenario/factory-shaped files.

## Defense-in-depth comments referencing companion-PR pre-fix behavior become lies post-merge (2026-04-27)

PR #1245 (<infra-repo>) fixed <TICKET-C> with a defense-in-depth `_auto_approve_successful_checks` whose docstring said: *"Catches two known gaps in the MCP server's auto-approve: 1. submit_run race condition (run_coroutine_threadsafe in <core-repo>/apis/run_func.py) causes run.status to stay RUNNING..."*. Companion PR `<core-repo>#1342` is the root-cause fix for exactly that race. **Post-companion-merge, the docstring describes a bug that no longer exists** — gap #1 disappears, "two known gaps" becomes "one", and a future maintainer reading the docstring will look in `run_func.py` for `run_coroutine_threadsafe`, not find it, and conclude the function is dead defense-in-depth (then delete it, reintroducing fragility).

**Review heuristic**: When a PR's defense-in-depth justification references a companion PR's pre-fix state, flag the comment for reframing as a *historical guard* rather than a *current bug narrative*. Pattern: rewrite "X causes Y" → "Historical: X (DRC-NNNN, fixed upstream in repo#PR). The guard remains because [orthogonal-reason]." This survives the companion merge: the historical reference is timestamped + locator-stable, and the guard's continued existence has independent justification. Bonus: any cross-repo `file.py:LINE` citation in the docstring is also flagged for replacement with a search-anchor (e.g., `search for "auto_approve_on_success"`) — line numbers across repo boundaries rot in one release cycle.

## Cross-session UUID lookups in code reading external state files widen the trust boundary (2026-04-27)

PR #1245 added `_import_checks_from_state` is_checked sync that reads `<session-state>.json` from S3 and uses `get_check_by_id(check_id)` (UUID-only lookup, no session filter) to fetch + write to a check. The original code used `if existing_check: continue` — read-only, so cross-session lookup was harmless. Adding a write path turned an "implicit but unused" trust-on-state into "implicit and exploitable" — a crafted state file containing a `check_id` from another session could now flip `is_checked=True` on a check owned by a different project/org. The session-scoped variant `get_check_by_check_id_and_session()` exists in the same module but wasn't reached for.

**Review heuristic for state-file consumers**: When a PR converts a previously read-only or skip-only path that processes external-state IDs into a write path, run an explicit "session-scope audit": for every UUID/ID lookup in the new write path, ask *"is this ID always valid for the current session/tenant scope, or is the lookup unscoped?"*. Specifically grep the file for sibling functions whose names include `_by_*_and_session` / `_by_session` / `*_scoped_by_*` — these are usually the secured variants. If the new write path uses the unscoped lookup while a scoped variant exists in the same module, flag as HIGH (not MEDIUM) regardless of how hard exploitation is, because the trust-boundary widening is permanent and grows over time.

## Dead BQ/eval assertions: exported + unit-tested but never wired into a scenario (2026-04-27)

PR #1245 added a `createCheckDescriptionsNeutral()` BQ assertion that was exported from `assertions/index.ts` and exercised by an `assertions/tool-usage.test.ts` unit test, but never appeared in any scenario's `assertions:` array. The PR description claimed "BQ assertion validates tool inputs against forbidden patterns" — but as wired, BQ mock + real runs never invoked it. If the prompt was later edited to allow `LOGIC ERROR` again, BQ regression would not catch it. The "tests pass" signal was real but useless: the unit test only proved the regex worked when the function was called, not that anything in production calls it.

**Review heuristic for new BQ/eval assertions**: When a PR adds a new assertion / matcher / judge criterion exported from a behavior-test framework, do NOT accept "unit test exists" as evidence the assertion is in force. Run an explicit caller audit: grep the scenario / test-spec directory (e.g., `bq/scenarios/`, `eval/cases/`) for the assertion's symbol name. If zero scenario-level callers exist, classify as DEAD CODE (HIGH severity) — the regression check the PR claims to add does not actually run. Same pattern applies to: ESLint custom rules without a scenario in `eslint-config`, RuboCop cops without a `spec/cop_spec.rb` integration test, Semgrep rules in a config file but not in any CI workflow.

## Audit-event divergence: parallel mutation paths with asymmetric audit emission (2026-04-27)

PR #1245 had two code paths that could both flip `is_checked=True`: (a) `_import_checks_from_state` sync block (no `APPROVAL_CHANGE` event), (b) `_auto_approve_successful_checks` (event emitted). Worse, ordering made the gap silent: import ran first → wrote `is_checked=True` → `_auto_approve_successful_checks`'s gate (`if not db_check.is_checked`) was False → no event ever emitted for those checks. **The Activity timeline silently dropped one entire class of approvals.**

**Review heuristic for audit-tracked field writes**: When a PR adds a write to a field that has audit-event semantics elsewhere (e.g., `is_checked` paired with `APPROVAL_CHANGE`, `status` paired with `STATUS_CHANGE`, `role` paired with `ROLE_CHANGE`), grep the codebase for ALL writers of that field. Each writer must either (1) emit the audit event, or (2) be downstream of a writer that does (and whose gate ensures the event fires). Specifically check **ordering between coupled writers**: if writer A flips the field then writer B's "only-if-not-already-set" gate runs, B's audit emission is suppressed for everything A touched. Recommend centralization (single source of truth) when possible — multiple parallel writers of an audit-tracked field is a structural smell.

## Race-condition fixes that move work from event-loop to executor introduce new cross-thread store-ordering windows (2026-04-27)

PR #1342 (<org>/<core-repo>) fixed <TICKET-C> by changing `update_run_result` from `async def` (scheduled via `run_coroutine_threadsafe` onto the event loop thread) to plain `def` called synchronously inside the executor thread `fn()`. This correctly eliminates the original race (callers seeing stale `run.status` after `await future`). But it introduces a new, smaller race: the body has multi-field stores (`run.result = result` THEN `run.status = FINISHED`; `run.error = e` THEN `run.status = FAILED`). Async-loop readers (`wait_run_handler`, `list_run_handler`) can interleave between the two stores and observe `result is not None` with `status == RUNNING`, which is exactly the symptom-shape the consumer-side defense in PR #1245 was protecting against.

Pre-fix: writes serialized on the loop thread, readers same thread → consistent state, single race symptom (status stuck on RUNNING).
Post-fix: writes on executor thread, readers on loop thread → CPython GIL covers per-store atomicity but multi-store sequence is no longer atomic. Sub-µs window where partial state is visible.

**Review heuristic for race-condition fixes that change thread-of-execution**: When a PR moves work between threads (event loop ↔ executor, main ↔ worker, sync ↔ async-scheduled), enumerate the ALL fields the moved code mutates. For each field, identify all readers in the OTHER thread. Check whether any reader inspects MULTIPLE fields together (e.g., `if run.result and run.status == FINISHED`) or uses one field as a completion signal for the other. If yes, the multi-store sequence in the moved code creates a new visible-partial-state window. Mitigations to suggest: (1) invert store order so the "completion signal" field is set LAST, (2) introduce a lock around the multi-store sequence, (3) document the GIL/CPython assumption explicitly. Don't accept "GIL covers it" without verifying that no reader depends on multi-field consistency.

## Cloud-side exception classes that don't inherit base exception → narrow `except` silently leaks (2026-04-27)

PR #1342's `_tool_run_check` wrapped `_tool_lineage_diff` + `_create_metadata_run` + auto-approve in `try / except DomainException`, intending to surface DB errors as `ValueError` to the MCP caller. But `update_check_by_id` in cloud mode raises `CloudSpecificException`, which inherits directly from `Exception` — NOT from `DomainException`. The narrow `except` clause does not catch it, and the cloud-side error propagates unwrapped to the MCP caller, breaking the consistent error contract.

**Review heuristic for cloud/local mode pairs**: When a function uses `try / except <SpecificException>` around a DAO/repository operation, check whether the operation has a cloud-mode variant that raises a DIFFERENT exception class. Specifically: (1) read the DAO method's body to find all `raise` statements, (2) check the inheritance chain of each raised type (`Foo.__bases__` in REPL or via grep `class Foo`), (3) confirm the `except` clause covers all plausible types. Cloud / local mode is a common factory pattern where two implementations raise unrelated exception classes — `except <LocalOnlyException>` then misses every cloud-mode failure. Same pattern applies to: filesystem vs S3 backends, in-memory vs Redis cache, SQLite vs Postgres adapters.

## Defense-in-depth comments and load-bearing docstrings: cross-repo coupling makes "obvious cleanup" dangerous (2026-04-27)

PR #1342 (root-cause fix in `<core-repo>`) and PR #1245 (defense-in-depth in `<infra-repo>`) form a coupled pair. The root-cause repo's `update_run_result` docstring contains the historical narrative — "Previously this was async + scheduled via run_coroutine_threadsafe..." — that the consumer-side `derive_check_run_status` workaround in #1245 cites as its *canonical justification*. If a future maintainer reads only the <core-repo> repo, the docstring looks like a "describes a fixed bug — safe to remove" candidate. Removing it leaves the consumer-side defense without explanation, then the consumer-side defense looks like dead code, then someone removes it, then the original race re-emerges if anyone reverts the fix.

**Review heuristic for cross-repo defense-in-depth pairs**: When reviewing either side of a coupled root-cause + consumer-defense pair, document **sunset conditions** explicitly. Add to docstrings: "Safe to remove once X in repo#PR is removed (those guards depend on this rationale being preserved here as canonical justification)." This way the load-bearing nature of the comment is visible to anyone editing it. Same applies to: deprecated-API shims that exist for a specific consumer's migration window, fallback code paths that exist because a downstream service has known unreliable behavior, version-pin overrides that exist because a transitive dependency has a known regression. Sunset conditions transform "looks like dead code" into "this stays until X removes their dependency on it" — much harder to delete by accident.

## Self-review APPROVE on own PR returns HTTP 422 — pre-detect reviewer == author (2026-04-27)

GitHub PR review API rejects `event: APPROVE` when the reviewer is the PR author with: `"Review Can not approve your own pull request"` (HTTP 422). Discovered on PR #1245 v2 re-review where Step 4 ownership check was true (admin) but the reviewer is also the PR author. APPROVE was the natural verdict given all v1 findings were closed, but the API failed and the review had to be re-posted as COMMENT with explicit sign-off note. Single retry consumed the post quota for that review (each post creates a new GitHub review thread; partial failures are not idempotent).

**Skill heuristic**: Step 7 (Post Review) should **pre-detect reviewer == PR_AUTHOR** before constructing the payload. Compare `MY_USERNAME` (already captured in Step 3) against `PR_AUTHOR` (already captured in Step 2). If equal AND default event is APPROVE: silently downgrade to COMMENT, prepend a one-line note to the review body — `"Sign-off equivalent (would APPROVE if not author): ..."` — and proceed. No need to ask the user. The downgrade is a GitHub limitation, not a review-quality decision.

**Implementation note**: this is a one-line guard at the start of Step 7's payload-build, not a post-failure retry. Retrying after 422 wastes one network round-trip and creates an aborted review record that may show up in `gh pr view --json reviews` audit trail. Apply the guard pre-emptively.

**Adjacent gotcha**: GitHub also rejects `REQUEST_CHANGES` from the PR author (same 422 reason, "Can not request changes on your own pull request"). The downgrade path is identical: REQUEST_CHANGES → COMMENT with explicit "blocking concerns" note in the body. Same heuristic, broader scope.

## Cross-thread state mutation: store ordering + sentinel preservation (2026-04-27)

PR #1342 fixed one race (run.status stuck at RUNNING after `await future`) by moving `update_run_result` from async-scheduled (event-loop thread) to synchronous (executor thread). This introduced TWO new races inside the same function:

1. **Store-order race**: success path stored `run.result = result` BEFORE `run.status = FINISHED`. Async readers in the loop thread checking `if run.result is not None` could observe "result-present + status-RUNNING" — terminating their wait loop on a half-written object.
2. **Sentinel-overwrite race**: success path unconditionally wrote `run.status = FINISHED`, silently overwriting CANCELLED set by `cancel_run` from the loop thread mid-execution. The original async path was at least serialized on the loop, making it deterministic in tests; the new sync path on the executor thread sees no such serialization.

Both fall under the same root issue: CPython's GIL provides per-attribute atomicity, but a multi-store sequence is not serialized with the loop-thread reader.

**Review heuristic for cross-thread state writers**: When a PR moves a multi-store mutation from one thread context to another (executor↔loop, worker↔main, async↔sync), audit two invariants:

1. **Store order vs reader's terminating condition**: identify what reader-side condition signals "work done" (e.g., `run.result is not None`, `task.done()`, `state == TERMINAL`). The matching writer-side terminal-status store MUST happen LAST — never before any of the supporting fields (result/error/output) are populated. Inverted order = readers can return mid-write.
2. **Sentinel preservation**: any unconditional `state = TERMINAL` assignment in code that runs alongside cancel/abort/timeout logic must be guarded with `if state != CANCELLED:` (or equivalent sentinel). Both success AND failure paths need the guard — easy to add it to one and miss the other (PR #1342's pre-fix code had the guard on failure path only).

When reviewing such PRs, also require: (a) docstring explicitly declaring the cross-thread store-ordering invariant readers can rely on, (b) regression tests for the cancel-collision branch (set CANCELLED before future resolves, verify it stays CANCELLED).

## Review body: separate "directly verified" from "PR-body claims" (2026-04-27)

Self-PRs and PRs with rich `## Testing` / `## UAT` sections tempt the reviewer to repeat the author's own metrics ("8/10 approved", "57+ tests passing") in the review body — making it sound like the reviewer independently confirmed those numbers. This conflates two evidence levels and quietly erodes review credibility. A safety hook in this codebase actually blocks posting when it detects fabricated UAT figures.

**Pattern**: structure the review body with two explicit sections at the top:

```markdown
**What I verified directly** (read diff + grep + biome/ruff on changed files + line-traced break-point):
- ...

**What I did NOT independently verify** (relying on PR body / prior reviews):
- UAT claims (PR body says X — I did not re-trigger Y)
- Companion PR / cross-repo work (not in scope)
```

This:
- Forces the reviewer to be honest about probe level (B vs C).
- Makes it easy for the author to spot which claims need their own backing evidence vs which they can lean on the review for.
- Survives copy-paste — future readers immediately see what was verified at the time of review vs what was inherited.

**Adjacent rule**: in the break-point coverage section, declare your probe level explicitly ("My probe level: B — test execution exists, not C runtime"). Don't paper over the gap by quoting the author's UAT level as if you ran it.

**When to apply**: every review where the PR body contains specific metrics (approval rates, test counts, latency improvements, coverage %) that the reviewer didn't personally re-measure. If you didn't run it, don't quote it as evidence in the verification matrix — quote it under "relying on PR body".

## GraphQL thread-reply mutations: backticks in body must use --input JSON file (2026-04-28)

`gh api graphql -f query='mutation { addPullRequestReviewThreadReply(input: {... body: "...`code`..."}) ...}'` fails with `unmatched "` when the body contains markdown code spans, even if all `"` and `'` are correctly escaped. Reason: zsh (and bash) interpret backticks inside single-quoted strings as command substitution under specific edge cases — particularly when the backtick is followed by `}` or other shell-meaningful tokens that confuse the parser. Multiple replies in a parallel batch can succeed for plain-text bodies and fail for code-span bodies, leaving partial state. PR #1245 hit this on threads 7+8 (replies referencing `if db_check and not db_check.is_checked` in code spans).

**Rule**: For any GraphQL mutation whose `body` field contains markdown code spans, code blocks, or any backticks, write the full mutation as a JSON file with `query` + `variables` and pass via `gh api graphql --input /tmp/payload.json`. The `--input` path treats the body string as opaque data — no shell interpretation.

**Pattern**:
```json
{"query":"mutation($id: ID!, $body: String!) { addPullRequestReviewThreadReply(input: {pullRequestReviewThreadId: $id, body: $body}) { comment { id } } }","variables":{"id":"PRRT_xxx","body":"reply with `code` and ```fences``` and \\b regex"}}
```

This is parameterized GraphQL (variables separate from query) — both shell-safe AND injection-safe. Adopt as the default mutation pattern in kc-pr-review-resolve Step 6 reply construction; reserve inline `-f query=` only for queries with no user-controlled body content.

## PR-level review body pointing to "see review comment" may live as issue comment, not review comment (2026-04-28)

When a PR-level review's body is short ("See review comment for details") and offers no actionable content directly, the actual review payload may be posted as a **PR-level issue comment** (`/repos/.../issues/{n}/comments`) rather than as part of the review record (`/repos/.../pulls/{n}/reviews/{id}/comments`). PR #1245: wcchang1115's CHANGES_REQUESTED review body was a 14-word pointer; the full 90-line "Code Review" with verdict, validation passes, and ISSUE 1 lived in a separate issue comment posted in the same minute. Skill triage that fetches only `/pulls/N/reviews` + `/pulls/N/reviews/{id}/comments` would see the NO-GO signal but no actionable content, and might classify as "purely informational" — wrongly.

**Rule**: After fetching PR-level reviews in Step 2, if any review's body is shorter than ~40 words AND points to "review comment" / "see comment" / "details below" / "see PR comment", **also fetch `/repos/.../issues/{n}/comments`** and look for issue comments from the same author within ±5 minutes of the review's `submitted_at`. Match by author + timestamp proximity. Treat the matched issue comment as the actual review payload for triage purposes. **Suggested skill addition**: extend kc-pr-review-resolve Step 2 with a "stub-pointer" follow-up — when a review body's character count is below a threshold AND contains pointer phrases, auto-fetch issue comments for the same author in the same time window and surface them in the triage report under the original review's row.

## Reviewer flagging "trust boundary" docstring is a prompt to enforce in the type system (2026-04-28)

When a reviewer points out that a function's safety relies on a docstring "trust boundary" / "caller MUST pass session-scoped X" contract, the implicit message is *"this contract is invisible to the type system, so future caller drift can break it without compiler warning"*. Treating this as documentation-only and replying "the docstring already explains it" preserves the fragility. The actionable response is to upgrade the contract from docstring-enforced to function-enforced — add the constraint as a parameter (e.g., `session_id: UUID`) and let the implementation validate via the parameter (e.g., `filter_by(id=, session_id=)`) instead of trusting input shape. PR #1245 v2 N1: `_auto_approve_successful_checks` had a "Trust boundary: caller passes session-scoped checks" docstring — the only call site was correct, but adding `session_id` parameter + scoped `filter_by` made the function self-defensive against future refactors that might leak unscoped check lists in.

**Rule**: When a reviewer flags a function whose docstring contains the phrases "trust boundary" / "caller must" / "safe because the caller" / "scoping is the caller's responsibility", do not just defend the docstring. Evaluate whether the constraint can be lifted into the signature: (1) what value does the caller currently pass that proves the scope? (2) can the function take that value as a parameter and validate via a query/filter? (3) does this preserve all existing call sites with a small refactor? If yes to all three, prefer the type-system upgrade over the docstring defense — it removes a class of future bugs entirely. Add a regression test that exercises a wrong-scope call and verifies the function rejects it (catches reviewers' "can future drift break this?" question with a passing test as the answer).

## Cross-platform doc prescriptions need symmetric verification + deterministic assertions (2026-04-28)

When a doc / mod prescribes parallel paths for multiple platforms (GitHub vs GitLab, macOS vs Linux, npm vs pnpm), AI reviewers reliably catch (a) verification steps that only cover one platform and (b) success criteria written as prose ("expecting non-empty", "should pass"). PR #584 (carlove) `pr-merge.md` had `gh pr view ... --json assignees (expecting non-empty)` as the verify step — Copilot flagged it on two axes: GitLab path had no documented verify command, and the "non-empty" criterion was not a runnable assertion. Both findings were valid; fixed by adding the `glab mr view` equivalent and replacing the prose criterion with `jq '.assignees | length > 0'` that prints a literal `true`/`false`.

**Rule**: When reviewing or writing docs that prescribe multi-platform commands, audit two dimensions per step: (1) **Coverage symmetry** — every platform branch needs the same lifecycle (create, edit, verify, abort). If GitHub has a verify command, GitLab needs one too. (2) **Assertion concreteness** — every "verify" / "check" / "ensure" step needs a runnable command whose output is binary (boolean print, exit code, or grep-match). Prose like "expecting non-empty" / "should be set" / "must look correct" is undocumented and untestable. Apply the heuristic: if a future automation script ran this doc, would it know whether to proceed? If not, the assertion needs to be a deterministic command. Related: `2>/dev/null` swallowing errors in a doc-prescribed bash snippet is the same anti-pattern at the input side — both produce silent failures.

## Tests that re-implement production logic instead of importing the real symbol are tautologies (2026-04-28)

When a unit test wants to exercise a "small piece of pure logic" embedded inside a larger function, the tempting shortcut is to copy that pure piece into the test file and assert against the local copy ("mirrors the parsing logic in `Adapter.listWithCount()`"). The test passes. But it would also pass if the production function silently dropped or transformed the value the test was protecting — because the test never calls the production code path. PR #582 (carlove) had `customer-profile-view-repository.adapter.spec.ts` with locally-defined `parsePassedFilters()` mirroring the inline filter exclusion in `listWithCount()`. The T3-c test asserted `assigned_employee_id` survived filtering — but only against the local mirror, not the adapter. Copilot caught this. Fix: extract the pure piece as an exported helper from the adapter file, import + call it in the test, delete the local copy. Now drift in the adapter breaks the test.

**Rule**: When reviewing a test file, scan for any code that *resembles* the system-under-test logic (utility functions, regex parsers, filter pipelines, value normalizers) defined locally in the test rather than imported from the source module. Each such mirror is a tautology — flag for refactor. Heuristic question: "If someone deleted the corresponding production code, would this test fail?" If the answer is no, the test is testing itself, not the system. Two cleaner alternatives: (a) extract the inline logic into an exported pure helper at the adapter / module level, then import in the test (works when the logic is already side-effect-free), or (b) write an integration-style test that exercises the full function with mocked dependencies (works when the logic is interleaved with side effects). Option (a) is preferred for narrow, pure, well-named primitives — keeps test scope tight without losing real-symbol coverage. Bonus: add a belt-and-suspenders assertion against the exclusion/allow list itself (e.g., `expect(VIRTUAL_FILTER_FIELDS).not.toContain('assigned_employee_id')`) to catch the inverse drift where someone adds the field to the exclusion set.

## Drizzle auto-generated migrations capture ALL schema at generation time — backdated migrations cause duplicate-column errors (2026-04-29)

When `drizzle-kit generate` runs while the Drizzle schema includes columns added by another feature branch (e.g., PROJ-301's `community` + `preferred_time_slots`), those columns are included in the generated migration. If the PROJ-301 migration is later added with a backdated timestamp (sorting BEFORE the auto-generated migration), both migrations attempt to `ADD COLUMN` the same column — causing PostgreSQL SQLSTATE 42701 ("column already exists") on preview branches and RC deployments. **Fix**: `ADD COLUMN IF NOT EXISTS` for any column that was present in the Drizzle schema at migration generation time but may have been added by an earlier-timestamped migration. **Detection heuristic**: Before committing a Drizzle-generated migration, `grep` the migration for `ADD COLUMN` and cross-check against all migrations with earlier timestamps. If any earlier migration adds the same column, apply `IF NOT EXISTS`. **Prevention**: When manually backdating a migration timestamp, check whether any later migration (that was generated while the column was already in the schema) also adds the same column.

## ts-rest strictStatusCodes: ternary status codes produce union type incompatible with router handler signature (2026-04-29)

In ts-rest routers with `strictStatusCodes: true`, a handler that returns `status: isConflict ? 409 : 422` produces type `{ status: 409 | 422; body: ... }`. This union is not assignable to the discriminated union of individual response types — TypeScript complains that `409 | 422` is not assignable to `422` (or whichever type it tries to match first). The compiler error appears on the router handler assignment, not on the return statement, making it hard to trace. **Fix**: Split into two explicit return branches — `if (isConflict) { return { status: 409 as const, ... } }; return { status: 422 as const, ... }`. The `as const` ensures literal type inference. **Applies when**: adding a new status code to an existing route (e.g., 409 for conflict semantics) and the rejection handler previously returned a single status with a ternary for the new case.

## [2026-04-29] Claude Code Plugin: bash variable scoping across code blocks

**Pattern**: In command.md / SKILL.md files, each bash code block is executed as a separate shell invocation (Claude Code Bash tool: "shell state does not persist"). Variables set in one block are NOT available in a later block.

**Pre-scan trigger**: When a diff in a command.md or SKILL.md file contains a bash variable defined in one code block (detection/setup block) and referenced in a later bash code block (action block), flag as MEDIUM — the second block will silently fail or produce wrong behavior.

**Telltale pattern to grep**:
```
grep -n '^\$[A-Z_]\+=' detection_block
# then check if same variable name appears in a later bash block
```

**Fix pattern**: Make action blocks self-contained — either re-compute the value inline, or restructure so the full logic runs in one bash block.

**Source**: PR #24 (<org>/<plugin-repo>) — `$MARKER` set in detection block, used in Branch C marker write block; marker write silently failed because `$MARKER` was undefined in the new shell.

## [2026-04-29] Re-review verification matrix when author pushes "address review" commits

**Pattern**: When an author pushes follow-up commits in response to a prior review (signals: user says "author 有更新" / "已修" / "addressed comments", or new commit messages like `fix(...): address X review comments`), the re-review must NOT degenerate into "did the diff change?". It must rebuild a verification matrix mapping each prior concern → expected fix → actual fix in HEAD.

**Process**:
1. Fetch prior review comments via `gh api repos/OWNER/REPO/pulls/N/comments --jq '.[] | select(.user.login=="MY_USER")'` to recover the original concerns and severities
2. Build a 4-column matrix: `# | Concern | Source (review id) | Fix in <commit-sha> | Verified ✅/⚠️/❌`
3. For each row, verify the fix targets root cause (not surface symptom). Check the new code at HEAD, not just the diff.
4. Audit the new code for related-but-untouched issues (e.g., if author fixed bug X in block A, check if the same anti-pattern exists in block B that wasn't part of the prior review)

**Anti-pattern to avoid**: Reading `gh pr diff` and scanning author's reply comments → APPROVE without rebuilding the matrix. This misses (a) fixes that are surface-only, (b) regressions introduced by the fix itself, (c) related issues elsewhere in the file.

**When to skip**: First review on a PR (no prior concerns to match against) — use standard flow.

**Source**: PR #24 (<org>/<plugin-repo>) re-review — V1 (`$MARKER` fresh-shell bug) and V2 (echo cosmetic) were both addressed in <sha> with author adopting suggested fix code verbatim. Verification matrix in review body served as transparent record of what was checked.

## [2026-05-04] Partial fix doesn't auto-close a finding — re-read each clause

**Pattern**: When an author addresses a finding with a partial fix (e.g., adds a guard but the underlying anti-pattern persists in another form), the finding is NOT closed. Re-read the original finding description clause-by-clause and check each clause survives the fix.

**Concrete examples**:
- "Regex re-compiled per message" — author adds `WeakMap` cache. Cache fixes the *perf* clause, but if the original finding also called out a *correctness* sub-issue (e.g., misleading attribution in a diagnostic loop), that sub-issue persists. Don't auto-withdraw the whole finding.
- "Optional capture group throws" — author adds config-load `extract.length ≤ groupCount` check. The check rejects mismatched counts, but doesn't reject `(\d+)?`-style optional groups (count matches at load, undefined captured at runtime). Original failure mode survives.

**Process**: For each prior finding marked addressed, identify (a) the surface symptom the author fixed, (b) the failure mode the original finding described, (c) whether (a) covers all of (b). If gap exists, re-state the residual finding with new severity reflecting what's left.

**Anti-pattern**: Marking finding as ✅ FIXED based on commit message claiming it's fixed, without re-reading the finding's full clause set.

**Source**: PR #21 (<org>/<team-repo>) round 2 — prior round's `#1 regex re-compile` was fully fixed by WeakMap cache, but prior `#2 diagnostic loop` had two clauses (perf + attribution) and only perf became moot; attribution had to be re-issued as round-2 #9 with explicit "(Replaces prior round's withdrawn #2.)" framing.

## [2026-05-04] PR description test/type-check claims must be verified by actual run

**Pattern**: When a PR description states a specific test count, type-check status, lint status, or build status (e.g. "81/81 pass", "type-check clean", "0 lint errors"), DO NOT cite the author's number in the verification summary. Run the command in a fresh worktree and cite the actual result.

**Why**: Author may have run the check at an earlier commit, in a different env (Node version, OS), or on an uncommitted local state. The PR HEAD may produce different results. Discrepancies become high-confidence findings.

**Process**:
1. After clone, run `npm ci` (or equivalent) to install exact lockfile-pinned deps
2. Run the claimed checks (`npm test`, `npm run type-check`, `npm run lint`)
3. Verify against PR description claim. If divergent, flag as HIGH severity (factual claim doesn't match reality)
4. For test failures, run 3× to confirm determinism vs flake
5. For test failures, run failing test in isolation (`--test-name-pattern`) to confirm it's not a test-ordering / cleanup artifact

**Concrete reporting**: Write the actual numbers in verification summary, with the author's claim quoted: `Unit tests | 78/81 pass — PR description claims 81/81. See #N`. The discrepancy itself becomes an inline finding.

**Source**: PR #21 (<org>/<team-repo>) round 2 — PR description claimed `81/81 pass`. Actual `npm test` produced `78 pass / 1 fail / 2 cancelled`, deterministic across 3 runs in fresh clone of HEAD `<sha>`. Failing test was the `[ack-error]` security path test the author had explicitly added in commit `<sha>` to address Copilot's review — meaning the security claim was unverified by automation.

## [2026-05-04] ToB security agents systematically upgrade reviewer's "config typo" findings to HIGH

**Pattern**: When self-classifying a finding around extract field collision / reserved key override / silent default behavior, default reviewer instinct underestimates severity by framing as "operator config error" or "edge case". The ToB security agent reframes via attacker viewpoint — values flow from attacker-controlled message text, not just from operator config — and identifies real attack paths that justify HIGH severity.

**Concrete examples**:
- "Capture group can override reserved meta key" → reviewer frames as MEDIUM "config collision". ToB agent: capture VALUE is attacker-controlled within message text; an `extract: [requester]` field lets attacker forge `requester="admin_override"` in `<channel>` tag → impersonation attack → HIGH.
- "auth.test() may not return bot_id" → reviewer frames as LOW "silent degradation, log a warning". ToB agent: bot-loop guard fails open under valid Slack API responses → fail-safe pattern (drop all bot_id messages when own identity unknown) → HIGH.

**Pre-emptive correction**: For findings touching (a) values that flow from external systems into security-relevant decisions, (b) silent default behavior under edge-case API responses, (c) operator-controllable knobs that affect threat model — assume reviewer's instinct underestimates by one severity level. Run ToB security agent before finalizing classification.

**Source**: PR #21 (<org>/<team-repo>) round 2 — `#10 emitter override` upgraded MEDIUM → HIGH (S1), `#11 bot_id undefined` upgraded LOW → HIGH (S2). Both upgrades came with concrete attack scenarios the manual review hadn't articulated.

## [2026-05-04] Recurring test-env-fragility: re-verify same class of finding every round

**Pattern**: When round N catches an env-version-dependent test failure (e.g., "tests pass on author Node 25, fail on reviewer Node 22"), DO NOT assume round N+1 is free of the same class. Author's local env doesn't change between rounds. Re-run the same test verification at every subsequent round of the same PR.

**Concrete signal**: Two consecutive rounds both surface tests that pass on author's machine but fail in fresh worktree at supported Node versions per `engines.node`.

**Process**:
1. After the first such finding, expect the next round to reintroduce a similar one (different test, same root cause).
2. Re-run `npm test` in fresh worktree at every subsequent round, even if commit message claims `X/X pass`.
3. When found, frame it as "recurring pattern" not "isolated bug" — author needs to fix the env-coupling, not just the failing test.

**Source**: PR #21 (<org>/<team-repo>) — round 2 caught `slack.test.ts` async race failing on Node 22 (passing on Node 25). Round 3 caught `regex.test.ts:33` failing on Node 22 (asserting `(?i:foo)bar` is valid JS regex, which it isn't on any Node version). Same author, same env-fragility, different test — only re-running tests at round 3 caught it.

## [2026-05-04] Variant detection compounds across rounds — siblings of round-N fixes appear in round-N+1

**Pattern**: When round N raises a finding around a specific anti-pattern (e.g., raw interpolation of attacker-controlled value into a key=value log line), the round-N fix typically addresses ONE site. Sibling sites with the same anti-pattern persist in untouched code. Round N+1 should grep / agent-scan for the same pattern across the codebase to surface variants.

**Concrete examples from PR #21 round 3**:
- Round 2 #11 fixed `msg.subtype` log-injection in `handler.ts`. Round 3 found the same pattern in 6 other sites: `[backfill-error]`, `[shutdown-error]`, `[socket-error]`, `[ack-error]`, `[handler-error]`, `fatal:` — all interpolating `e.message` raw.
- Round 2 #4 fixed missing `sender_not_allowed:<rule>` log in backfill. Round 3 found the same asymmetry persisted for `bot_loop` and `subtype` drops — those still silent in backfill, per-message in handler.
- Round 2 #7 fixed `${{ inputs.* }}` shell interpolation. Round 3 found a sibling: `${{ steps.* }}` outputs from jq-extracted JSON values flowing into `$GITHUB_ENV` without sanitization — same anti-pattern (untrusted value flowing into shell context), different vector.

**Process for round N+1 reviewer**:
1. For each round-N fix, identify the anti-pattern signature (e.g., "raw interpolation of foreign value into structured log").
2. Grep the codebase for that signature.
3. Dispatch `pr-review-toolkit:code-reviewer` and `kc-pr-flow:tob-security-reviewer` with explicit instruction to scan for variants of round-N findings, NOT just regression on the fix.
4. Each variant becomes a new round-N+1 finding with reference back to the round-N anti-pattern.

**Anti-pattern**: Round N+1 review only verifies "did the round-N specific code path get fixed?" without scanning for siblings. Misses the next bug-likely surface area.

**Source**: PR #21 round 3 surfaced 3 sibling-class variants (R2 error-message log injection, R3 backfill silent drops, A1 GITHUB_ENV jq injection) that were structurally adjacent to round-2 findings but in untouched code.

## [2026-05-04] Verification matrix table format for round-N≥2 reviews

**Pattern**: Re-reviews where the author claims to address all prior-round findings should lead the review body with a verification matrix table — one row per prior finding, with explicit `✅ CLOSED / ⚠️ RESIDUAL / ❌ STILL OPEN` and a brief evidence link.

**Why this beats prose summary**:
- Author scans the table to confirm each finding is accounted for; doesn't have to cross-reference round-N comment IDs.
- Reviewer's accountability is explicit — claiming closure requires citing the new file:line that proves it.
- "Residual" rows make partial fixes visible without restarting the finding (e.g., "round-2 #11 fixed for subtype, residual for error messages → see new #4").
- Future-you reading the review thread reconstructs state in 30 seconds.

**Format**:
```markdown
| # | Round-2 finding | Status | Notes |
|---|---|---|---|
| #1 | matcher.ts optional capture throws | ✅ CLOSED | `src/matcher.ts:40` `if (captured === undefined) continue` |
| #11 | sanitize msg.subtype | ✅ CLOSED for subtype; ⚠️ RESIDUAL for error messages — see **#4** |
```

Place between the opening framing paragraph and the new-findings inline section.

**Source**: PR #21 round-3 review used this format on 24 prior findings; author was able to grok closure status without re-reading round-2 comments individually.

## [2026-05-04] Multi-round review: surface convergence trajectory at the final round

**Pattern**: When a PR goes through ≥3 rounds of review, the final round's review body should include a trajectory table showing block-merge count and verdict per round. This converts a sequence of binary verdicts into a process-quality signal both reviewer and author can read at a glance.

**Format**:
```markdown
| Round | Block-merge | Total inline | Verdict |
|---|---|---|---|
| 1 | 4 | 9 | COMMENT |
| 2 | 8 | 24 | REQUEST_CHANGES |
| 3 | 3 | 12 | REQUEST_CHANGES |
| 4 | 0 | 3 (all LOW) | APPROVE |
```

**Why this matters**:
- Author sees their response work converged the finding count — validates the iteration cost.
- Reviewer's accountability is explicit — round-2's count being higher than round-1 means deeper inspection (parallel agents, test execution) caught more, not that the PR got worse.
- Future engineers reading the closed PR understand the review intensity from the table without re-reading 4 rounds of comments.

**Anti-pattern**: Final-round review that just says "APPROVED, ship it" — loses the trajectory information embedded in the review thread that future-readers would otherwise have to reconstruct.

**When to skip**: Single-round PRs (no trajectory to show), or PRs where round count was driven by author churn (rebases, scope changes) rather than findings response — in those cases the table can mislead.

**Source**: PR #21 (<org>/<team-repo>) <TICKET-D> — 4 rounds: round-2 introduced parallel agent dispatch (24 findings vs round-1's 9), then converged 8→3→0 block-merge as author addressed each round comprehensively.

## [2026-05-04] APPROVE event can carry LOW inline comments — don't downgrade verdict to keep findings

**Pattern**: GitHub's review API permits inline comments on `APPROVE` events. They render as informational suggestions, not blockers. When the final review has only LOW / defense-in-depth findings, send `APPROVE` event AND include the LOW findings as inline comments — don't downgrade the verdict to `COMMENT` just to "preserve" the findings.

**Wrong instinct**:
- "I have 3 findings, so I should send COMMENT not APPROVE."
- "If I send APPROVE the LOW findings get hidden."

**Reality**:
- `APPROVE` with inline comments shows author the review passed AND the suggestions exist for follow-up.
- `COMMENT` would imply ambivalence about merge-readiness when the reviewer is actually confident.
- LOW findings on APPROVE explicitly signal "non-blocking — track as follow-up issue if you care, otherwise skip" — clearer than the same content under COMMENT.

**Calibration**:
- 0 block-merge, 0 medium → APPROVE no comments
- 0 block-merge, 0-N LOW → APPROVE with LOW inline comments  ← this case
- 0 block-merge, 1+ medium → COMMENT (medium implies meaningful follow-up)
- 1+ block-merge → REQUEST_CHANGES

**Source**: PR #21 (<org>/<team-repo>) round-4 — sent APPROVE with 3 LOW inline comments (NEL char gap, sanitizeLogMessage doc, semver CLI output unvalidated). Author can address them as follow-up without merge being blocked.

## GitHub review API: inline comment line must be inside a diff hunk (2026-05-05)

Posting a PR review via `POST /repos/{owner}/{repo}/pulls/{n}/reviews` with `comments[].line` pointing to an unchanged line returns `422 Unprocessable Entity` with `"Line could not be resolved"`. GitHub's review API only accepts inline comments on lines that are part of the PR diff (added or context lines around hunks) — pinning to a file's actual line N when that line wasn't touched by the diff fails.

**Workaround**: pin the comment to the closest changed line in the same file (e.g., the diff hunk for an unrelated fix nearby) and reference the actual target line in the comment body ("line 30 below, not in this diff hunk"). Alternative: fold the finding into the review body as advisory.

**Detection**: before submitting, sanity-check that each `comments[].line` falls within a `+++` hunk window from `git diff main...PR_HEAD -- <file>`. If not, either move the line or convert to body advisory.

**Source**: PR #25 (<org>/<plugin-repo>) — `paste -sd ', '` bug at hooks/scripts/{suggest-review.sh:30, pre-commit-guard.sh:33} was outside the md5-fix diff hunks; first POST returned 422, second POST pinned to lines 21 and 20 (last line of md5 fix block) with body note pointing to the real target.

## Advisory items need "concrete impact" gate, not just "claim is true" (2026-05-05)

Two failure modes when writing PR review advisory items:

**1. Fabricated specifics** — writing a specific number (count, percentage, range) without running the command to get it. Round numbers like "11 items" or "5 lines" are red flags. Either pull the actual count via `grep -c` / `wc -l` etc., or use fuzzy quantifiers ("all unchecked", "several places", "a handful").

**2. No concrete impact path** — flagging a tool warning (e.g., shellcheck SC2034) without checking whether the tool is actually invoked in the repo (CI gate? pre-commit? existing `disable=` convention?). A "valid claim" is necessary but not sufficient — the finding must have a path to user-visible impact.

**Pre-post checklist for each advisory item**:

- [ ] Specific numbers come from a command I just ran (not estimates)
- [ ] Who hits this? When? What symptom?
- [ ] If "tool X would warn about Y" — is X actually invoked here (CI / hook / convention)?
- [ ] Fix description is specific enough to apply directly

Any unanswered → rewrite with fuzzy quantifier, downgrade to NIT, or drop entirely.

**Source**: PR #25 (<org>/<plugin-repo>) self-correction at issue #<comment-id> — "11 items" was actually 20 (count never run); SC2034 advisory was retracted (no shellcheck CI in repo, no `disable=SC2034` convention to break, zero impact path).

## Cross-PR producer/consumer review surfaces stale prompts (2026-05-05)

When two PRs form a producer/consumer contract (e.g., MCP server + plugin agent that calls it), reviewing them in isolation misses doc drift on the consumer side. Review them as a pair: the consumer's prompt should be checked against the producer's actual response shape via `git log -S"<field-name>"` on the producer to see when fields were renamed.

**Process**:
1. After fetching the consumer PR diff, identify any prompt/agent file (`*.md` with section markers like "This call returns" / "Output format" / "Section N").
2. Extract the producer-side field names the prompt references.
3. `cd <producer-repo> && git log -S"<field>" -- <producer-source>` — find the commit that introduced or renamed the field.
4. If the rename predates the consumer prompt's last touch, the prompt is stale.

**Why agents miss this**: an LLM reading the agent file sees plausible field names and doesn't grep the producer to verify they still exist. The compiler doesn't catch it (Markdown). Tests don't catch it (they mock the response shape, often unwittingly using the same stale names).

**Source**: PR #1349 (<org>/<core-repo>) cross-PR validation against PR #25 (<org>/<plugin-repo>) — `<reviewer-doc>.md` referenced `impacted_models` / `not_impacted_models` / `suggested_deep_dives`, but server returned `confirmed_*` (since commit <sha>) and per-model `next_action` (since <sha>). Both renames months old, never propagated to the plugin doc.

## Producer-side review must scan log/persistence sites for new sensitive args (2026-05-05)

When a PR adds an MCP tool (or any RPC handler) with a new sensitive argument (`api_token`, `password`, `secret`, etc.), check every log call site in the request-handling layer to confirm redaction. Tool args are typically logged in two places:

1. **Stderr / stdout** via `logger.info(f"... {arguments}")` at the call_tool dispatcher
2. **Persistent debug log** via a custom logger writing the full request payload

Both are ALWAYS-on in their respective modes. Once a sensitive arg lands in either, it leaks via attached log files / shared bug reports / stdout capture in CI.

**Detection heuristic**: when the diff adds a new tool schema with a property name matching `(token|password|secret|api[_-]?key)`, grep the same file for `logger\.(info|debug)` and any `log_*` calls within the request-handling functions. Verify each one redacts before writing.

**Suggested fix shape**: `SENSITIVE_ARG_KEYS = {"api_token"}` constant + dict-comprehension redaction once at the dispatcher, reused by both log sinks.

**Source**: PR #1349 (<org>/<core-repo>) review — `set_backend(api_token=...)` schema added without redaction; both `logger.info(f"[MCP] Arguments: {json.dumps(arguments)}")` (always-on stderr) and `MCPLogger.log_tool_call(name, arguments, ...)` (persistent JSON when `--debug`) wrote the raw token.

## Token-leak triage: entry path, not just logger presence (2026-05-05)

When checking for sensitive-arg leaks across a multi-file producer (e.g., MCP server + cloud client utility), don't grep all `logger.*` calls and flag every one. Triage by entry path first:

| Token entry path | Risk | Why |
|---|---|---|
| LLM-supplied via tool/RPC argument | **HIGH** — scrutinize every logger that touches the args dict | The dispatcher typically logs the full args dict for observability. LLM is an untrusted caller for log-sanitation purposes. |
| Constructor / config injection from a trusted caller | LOW — only flag if logger explicitly serializes `self.token` or `headers` | Token never crosses a serialization boundary unless author writes it explicitly. Reading the code class-by-class confirms this. |
| Env var read at startup | LOW by default; HIGH if a debug-mode startup banner echoes env | Single read site; easy to verify. |

A finding only applies where (entry path = LLM-supplied) ∧ (logger touches args/headers/kwargs). Both conditions must hold. Skip all log calls in trusted-path modules (constructor-injected, env-read).

**Process for a `<core-repo>`-shaped review** (MCP tool dispatcher + multiple cloud client utility files):
1. Identify the LLM-args dispatcher (`call_tool` / `handle_request`). Its log calls are first-class targets.
2. For other cloud client files, check the constructor signature: if the token comes from a typed parameter (not from kwargs/dict), and the file has no `logger.info(... self.token ...)` / `logger.info(... headers ...)`, it's safe. Skip.
3. For env-var reads: grep for `os.environ.get("...TOKEN..."` and verify no startup banner echoes it.

**Source**: PR #1349 (<org>/<core-repo>) follow-up scan of `util/cloud/base.py` after the inline HIGH was posted on `mcp_server.py`. `CloudBase._request` builds `Authorization: Bearer {self.token}` header but the file has zero logger calls; token enters via constructor from trusted callers (CLI config / startup), never via tool args. Confirmed safe without flagging. The leak was uniquely in the MCP dispatcher because that's the only place LLM-supplied args meet a logger.

## Stale-prompt scan must include hook scripts that inject LLM context (2026-05-05)

Extends the cross-PR stale-prompt pattern: when checking consumer-side prompt drift against producer field renames, don't only grep `*.md` agent definitions. Also scan **hook scripts that inject `additionalContext` / `systemMessage`** — those are runtime prompt injection points that the LLM sees on every tool/event trigger.

**Detection heuristic** in a Claude Code plugin:
- Grep `additionalContext`, `systemMessage` in hooks/scripts/*.sh and hooks/*.json
- For each hit, check if the value string includes producer-side field names (e.g., the names you'd grep for in a prompt review)
- Stale references in hooks are HIGHER impact than stale references in agent definitions: agents are dispatched on demand, hooks fire automatically (often after every Bash/Edit/PreToolUse trigger)

**Why this is easy to miss**: hooks live in a different directory (`hooks/scripts/`) from the agent (`agents/`). A reviewer focused on the agent's prompt won't think to grep the hook scripts. The first round of cross-PR validation only caught the agent definition; the hook re-injection of the same stale strings was uncovered later when the author touched the hook file for an unrelated paste-bug fix.

**Source**: PR #25 (<org>/<plugin-repo>) re-check after `<sha>` — `suggest-review.sh:31` injects "MANDATORY: You MUST call impact_analysis to get the authoritative impacted_models and not_impacted_models lists" into PostToolUse `additionalContext` after every `dbt run/build/test`. Same stale field-name pollution as `<reviewer-doc>.md`, fires on a completely different trigger surface.

## Self-defeating regression test: silent skip on missing precondition

**Pattern (PR #1269 / <org>/<infra-repo>, 2026-05-05):** When a regression test is specifically built to catch a class of bug that ONLY manifests under a particular environmental condition (a built artifact, an env var, an external dependency), check whether its skip-when-absent path silently passes. If yes, the test is a self-defeating decoration — it provides false confidence while re-introducing the very failure mode it exists to prevent.

**Concrete case:** PR #1269 added `mermaid-lint-cjs-shim.test.ts` to lock down a CJS-bundle-only DOMPurify shim regression. The test loads `dist/mermaid-lint-mcp.cjs` via spawn-child-node. When the dist is absent, the test logs `SKIP: ...` and `return`s — green. There is no `pretest` hook running `pnpm build`. Anyone running `pnpm test` cold (clean checkout, post-`rm -rf dist/`, CI config drift) gets the regression test silently noop'd. The original case-015 failure mode ("passes locally because src/ ESM tests are fine, breaks in Docker because dist/*.cjs is broken") is exactly what the test was built to prevent — and the silent skip re-opens that exact gap.

**Reviewer detection in 5 seconds:** grep the test file for `existsSync\|process.env.\|skip\|return;` near the top of `it`/`test` blocks. If the test gracefully no-ops on a missing artifact and there's no `pretest`/`global-setup` enforcing the precondition, flag it.

**Three fix patterns (in preference order):**
1. **Enforce in package.json:** Add `"pretest": "pnpm build"` (or whichever produces the artifact). Pays a few seconds for guaranteed coverage.
2. **Hard fail with helpful message:** Replace `return` with `assert.fail("dist/X missing — run \`pnpm build\` before \`pnpm test\`")`. Developer fixes by running build once; subsequent runs work because esbuild output is deterministic.
3. **CI-gated skip:** `if (!existsSync(p)) { if (process.env.CI) throw new Error(...); console.log('SKIP: ...'); return; }` — keeps developer-friendly local soft-skip while making CI failures loud. Lower preference because it relies on `process.env.CI` being set correctly.

**Why agents miss this:** Code-review LLMs read the test, see the skip path is logged (not hidden), and treat it as "developer-friendly". They don't ask "what is the precondition for this test to actually run, and is anyone enforcing it?" The pattern is recognizable only by tracing back from "what is this test specifically guarding?" → "does the skip path defeat that guard?"

**Generalizable to:** any test that asserts on a built artifact (`dist/`, `target/`, `out/`), a generated fixture (`generated/`, `proto/*.pb.go`), an env var that drives a code path (`process.env.FEATURE_X`), or an external service (DB connection, MCP server, API mock).

## Run full biome check, not just lint, in pre-scan

**Pattern (PR #1269 / <org>/<infra-repo>, 2026-05-05):** Project pre-commit hooks often run `biome lint` (errors only) for speed. `biome check` runs both lint and formatter. Format violations slip through pre-commit but fail CI's `pnpm lint:check` (which includes formatter). Pre-scan in PR review must run full `biome check` on changed files to catch format-only issues that committed clean.

**Concrete case:** `mermaid-lint-cjs-shim.test.ts:73-77` had a format violation (multi-line `execFileAsync` args biome wants inlined). `pnpm exec biome lint <file>` returned 0 errors (only checks lint rules); `pnpm exec biome check <file>` returned 1 error (format). Ensign reported "biome lint clean" and pushed; CI would have caught it on the format pass.

**Skill update:** in pre-scan 4.5f Lint Gate, when biome is the project linter, run `biome check`, not `biome lint` — the additional format pass is cheap (Rust-based, sub-second) and catches a class of errors invisible to `biome lint`.

## Cleanup-after-import patterns need try/finally for global mutation

**Pattern (PR #1269 / <org>/<infra-repo>, 2026-05-05):** When code mutates a global (`globalThis.window`, `process.env`, `Object.prototype`) before an `await import(...)` and cleans up after, the cleanup MUST be in a `finally` block. Otherwise an import failure (network/ENOENT/module-init throw) leaks the global mutation forever — and if the import is memoised (singleton promise, lazy-init cache), the leak latches permanently across the entire process.

**Concrete case:** `loadMermaid()` in `mermaid-lint.ts` did:
```ts
mermaidPromise = (async () => {
  const cleanup = await shimDompurifyForHeadlessParse();
  const mod = await import('mermaid');  // ← if this throws...
  cleanup();                            // ← ...this never runs
  return mod.default;
})();
```
If `import('mermaid')` throws once, `globalThis.window` permanently pollutes the process and `mermaidPromise` latches the rejection — every subsequent caller re-awaits and re-fails.

**Reviewer detection:** any function that mutates a global state before `await import` / `await fetch` / `await dynamicLoad` should have try/finally around the await. Grep for global mutations (`globalThis.`, `process.env.`, `Object.defineProperty(`, prototype patches) followed within ~5 lines by an `await` of a side-effecting call. If no try/finally wraps the cleanup, flag it.

**Class boundary:** stateless mutations (e.g., setting then resetting a local variable) don't need this discipline; only mutations that escape the function's scope (globals, module-level state, registries) need it.


## Memoised promise + global mutation = double-latch failure trap

**Pattern (PR #1269 / <org>/<infra-repo>, 2026-05-05, Copilot re-review):** When a function memoises a promise (`let x: Promise<T> | null = null; if (x === null) x = ...`) AND that promise mutates global state inside its body, you must handle BOTH:
1. **Cleanup-on-rejection** — try/finally so the global mutation is torn down even when the promise rejects (covers leaked stub/global pollution).
2. **Reset-on-rejection** — `.catch()` handler that resets the memo to `null` so the next caller can retry, guarded by `memo === thisPromise` to avoid racing with another caller that already cleared and replaced.

**Failure mode without (1):** transient import/network error → cleanup never runs → globalThis polluted permanently → `typeof window !== 'undefined'` checks elsewhere become "wat".

**Failure mode without (2):** transient error → memo permanently latches the rejection → every future caller re-awaits the same rejected promise and re-fails identically → only process restart recovers. Even worse than no memo, because the user sees the SAME failure forever, masking the transient nature.

**Reviewer detection:** look for the pattern
```ts
let memo: Promise<T> | null = null;
async function load() {
  if (memo === null) {
    memo = (async () => { /* mutates global, awaits side-effect */ })();
  }
  return memo;
}
```
Both fix patterns must be present:
```ts
const promise = (async () => {
  const cleanup = await installGlobal();
  try { return await sideEffect(); }
  finally { cleanup(); }
})();
promise.catch(() => { if (memo === promise) memo = null; });
memo = promise;
```

**Generalisable to:** lazy DI containers, lazy connection pools, lazy loaded plugins/extensions, any "set up the world once, cache forever" pattern. The first review pass typically catches one (cleanup OR reset); the second pass catches the other.

## Sentinel-input health checks must throw on ANY findings, not just expected-shape findings

**Pattern (PR #1269 / <org>/<infra-repo>, 2026-05-05, Copilot re-review):** When a startup health-check uses a hand-crafted "known-good" input and inspects the result for a specific error shape (e.g. `findings.find(f => f.message.includes('addHook'))`), the early-return path on "no matching shape" silently passes any other regression class. The sentinel input was crafted to lint clean — ANY finding is a regression.

**Anti-pattern:**
```ts
const findings = await lint(KNOWN_GOOD_INPUT);
if (findings.find(matchesSpecificBug)) throw new Error('case-X regression');
// implicit: pass on no match — but ANY finding on KNOWN_GOOD_INPUT is a regression!
```

**Correct pattern:**
```ts
const findings = await lint(KNOWN_GOOD_INPUT);
if (findings.length === 0) return; // healthy
const specificBug = findings.find(matchesSpecificBug);
if (specificBug) throw new Error(`case-X regression: ${specificBug.message}`);
// Generic catch — surface unknown regression class with diagnostic info
throw new Error(`unexpected lint failure on known-good input: ${findings[0].message}`);
```

**Reviewer detection:** any health-check / canary / smoke test that
1. uses a static known-good input
2. branches on a specific error shape
3. has no else-branch on "found findings I didn't recognise"
…is silently brittle. Flag with severity MEDIUM unless the function is documented as "best-effort detection of one specific bug class."

**Generalisable to:** schema validators against canonical fixtures, parser smoke tests, configuration validators, integration test sentinels. Any "we know this should pass" test where the failure-recognition is narrower than the failure-detection.

## Failure-path assertions must surface both stdout and stderr

**Pattern (PR #1269 / <org>/<infra-repo>, 2026-05-05, Copilot round-3 re-review):** Tests that spawn child processes (`execFile`, `spawn`, `exec`) and surface failure via `assert.fail` or `expect.fail` MUST include both `stdout` and `stderr` in the failure message. Many process patterns write progress/diagnostics to stdout and only the fatal error to stderr; surfacing only one drops half the signal in CI logs.

**Anti-pattern:**
```ts
} catch (err) {
  const e = err as { stderr?: string; message?: string };
  assert.fail(`process crashed. stderr: ${e.stderr || e.message}`);
}
```

**Correct pattern:**
```ts
} catch (err) {
  const e = err as { stdout?: string; stderr?: string; message?: string };
  const stderrPart = (e.stderr ?? '').trim() || e.message || '(empty)';
  const stdoutPart = (e.stdout ?? '').trim() || '(empty)';
  assert.fail(`process crashed.\n  stderr: ${stderrPart}\n  stdout: ${stdoutPart}`);
}
```

**Generalisable to:** any subprocess test pattern (Node child_process, Python subprocess, Go exec.Cmd). The asymmetric "only stderr" pattern is a common drift because the success path often only checks stdout, and developers mirror that thinking into the failure path without realising stdout breadcrumbs are most useful precisely when the process is failing partway through.

## Sentry capture_message and traces_sample_rate are independent

**Pattern (PR #1270 / <org>/<infra-repo>, 2026-05-06):** When reviewing observability/telemetry PRs that mix `set_measurement` and `capture_message`, verify the sampling story for each:

- `traces_sample_rate` controls **transaction** sampling. `set_measurement(name, value, unit)` attaches data to the current transaction, so it rides whatever sample rate the transaction was selected by.
- `sample_rate` (default `1.0`) controls **event** sampling — applies to `capture_message`, `capture_exception`, `capture_event`. NOT controlled by `traces_sample_rate`.

**Failure mode:** A PR sets `traces_sample_rate=0.1` and adds `_emit_event(level="info", ...)` calls on every successful request, expecting the 10% sampling to throttle Sentry event volume. In reality, every info event fires unsampled. With a busy endpoint this exhausts Sentry's monthly event quota fast — and silences error events that share the same quota bucket.

**What to flag:** Any new `capture_message(level="info"|"warning", ...)` call site on a request hot path where the author cites `traces_sample_rate` in the rationale. Request a `before_send` hook, downgrade to `set_measurement` + tags (sampled with the transaction), or explicit `random.random() < SAMPLE` gating.

**Generalisable to:** OTel Span Events vs Metrics, Datadog distribution metrics vs `submit_event`, Honeycomb spans vs custom events. The general lesson: **sampling controls are per-data-class, not per-SDK.** Always trace each data class to its specific control.

## Starlette add_middleware is LIFO — last added = outermost

**Pattern (PR #1270 / <org>/<infra-repo>, 2026-05-06):** When reviewing PRs that add or reorder ASGI middleware in a Starlette/FastAPI app:

- `app.add_middleware(MiddlewareCls)` performs `user_middleware.insert(0, ...)` — the LAST `add_middleware` call ends up at index 0.
- `build_middleware_stack` then iterates `reversed(middleware)` to wrap, so the FIRST `add_middleware` call ends up innermost (closest to the router) and the LAST is outermost.
- For requests: outermost runs first, innermost runs last (closest to handler).
- For responses: innermost runs first (handler returns), outermost runs last (sees final headers/body).

**What to flag:** Any PR claim about middleware ordering ("must run before X") that doesn't match this LIFO + reverse-execution semantics. Also flag missing in-code documentation when the PR depends on a specific ordering — Starlette's reverse-execution-order is a known footgun, and a future maintainer reordering without context will silently break the invariant.

**Generalisable to:** Express `app.use()` order (FIFO, opposite of Starlette), Koa middleware (FIFO), Django middleware (top-down for request, bottom-up for response). The general lesson: **middleware ordering semantics differ per framework.** Verify by reading the framework's `add_middleware` / `use` source, not by intuition.

## # noqa on non-violating lines misleads readers

**Pattern (PR #1270 / <org>/<infra-repo>, 2026-05-06):** A `# noqa: <RULE>` comment placed on a line that does NOT trigger the rule is a code smell — it suggests the author either misunderstood the rule or copy-pasted the suppression. Specifically for ruff:

- `S110` is "try-except-pass" — only fires when the `except` block contains literal `pass`. A block that logs and re-raises does NOT trigger S110.
- A `# noqa: S110` on a logging-and-raising block falsely signals to readers that exceptions are silently swallowed.

**What to flag:** Any new `# noqa: <RULE>` where the line clearly doesn't violate the rule. Quote the rule's actual definition and the line content. Ask author to either remove the noqa or fix the underlying issue (which doesn't exist here).

**Generalisable to:** ESLint disable comments, mypy `type: ignore`, Pylint disable, Rubocop disable. Drive-by suppressions accumulate; the cleanup cost compounds. The general lesson: **a noqa is a documented exception, so its application must match the rule's actual scope** — otherwise the comment lies about the code's invariants.

## Roman numeral phase labels invert reading order

**Pattern (PR #1270 / <org>/<infra-repo>, 2026-05-06):** When reviewing telemetry/event payloads with phase or stage identifiers, prefer self-documenting strings (`"s3_hit"`, `"proxy_fallback"`, `"cloud_fallback"`) over Roman numerals or sequence numbers (`"I"/"II"/"III"`, `"phase_1"/"phase_2"/"phase_3"`).

**Why this matters:** In observability data — Sentry events, Langfuse traces, Datadog metrics — labels are queried out of code context. A dashboard filtered on `phase_detected: I` requires the viewer to know which code path emitted it. Roman numerals are particularly bad because they imply ordering ("I came before III") that often inverts the actual code flow (in PR #1270, "III" is the newest preferred path and "I" is the legacy fallback).

**What to flag:** Any new event/metric label with non-descriptive sequence values. Suggest the renaming up-front; once dashboards are built on the labels, renaming requires migration.

**Generalisable to:** event types, error codes, feature flag names, A/B test variants. The general lesson: **observability labels are read by humans without code access — they must be self-documenting at the point of use.**

## error_message=str(e) leaks infrastructure to third-party SaaS

**Pattern (PR #1270 / <org>/<infra-repo>, 2026-05-06):** Many codebases already flag the HTTP `detail=str(e)` anti-pattern (leaks credentials/internal info to API clients). The same anti-pattern applies to telemetry: `capture_message(extras={"error_message": str(e)})` exfiltrates exception strings to a third-party SaaS (Sentry, Datadog, Langfuse).

`boto3` exceptions embed bucket ARNs, IAM role ARNs, internal hostnames; SQLAlchemy exceptions can embed connection strings; subprocess exceptions can embed full file paths. Sending these verbatim to an external observability service is information disclosure with a much wider audience than HTTP error responses.

**What to flag:** New telemetry call sites that pass `str(e)` or `repr(e)` as event extras. Recommend `error_type=type(e).__name__` only, OR use the SDK's `capture_exception(e)` which applies the project's PII-scrubbing rules. Cross-reference the project's existing `detail=str(e)` triage rule (likely already in CLAUDE.md) — the rule applies to telemetry too.

**Generalisable to:** any third-party logging/observability SDK (Sentry, Datadog, New Relic, Honeycomb, Langfuse, OpenTelemetry exporters). The general lesson: **third-party observability is a data-egress channel.** Treat it with the same data-classification rigor as HTTP responses.

## Cascade workflow self-review evidence paths often don't exist in repo

**Pattern (PR #1270 / <org>/<infra-repo>, 2026-05-06):** PRs generated by cascade-style workflows (or similar agentic pipelines) often cite trace files in PR bodies — e.g., `<workspace>/docs/<trace-id>/_trace/`. Verify the directory actually exists in the repo at HEAD before treating the trace path as authoritative evidence.

**Failure mode:** Reviewer follows the trace path, gets 404, treats the cascade self-review claims as unverifiable, then either rejects the PR or approves on faith. Both are wrong responses to a fixable problem.

**What to flag:** Any PR body referencing trace/log/evidence paths. Run `ls <path>` on the head SHA. If absent, ask author to either (a) commit traces under a real repo path, or (b) remove the path reference. Also flag stale tracking IDs ("DRC cascade-001") that aren't real Linear/Jira tickets — they will rot once the cascade workflow artifacts are pruned.

**Generalisable to:** any auto-generated PR (LLM agents, code generators, scaffold tools). The general lesson: **trust-but-verify the PR body's pointers.** Auto-generated text often references local-only artifacts.

## CI gap: dist-level regression test exists but no workflow runs it

**Pattern (PR #1269 / <org>/<infra-repo>, 2026-05-06, <reviewer-B> human review):** When a PR adds a regression test that targets a deployed artifact (`dist/*.cjs`, `target/release/*`, compiled binary, generated proto/code), check whether ANY GitHub Actions workflow actually invokes `pnpm test` (or equivalent) for that subdirectory. The existence of a test file that hard-fails on missing artifact in CI does NOT mean CI runs that test — it just means that IF the test is invoked, the artifact must exist.

**Concrete case:** PR #1269 added `mermaid-lint-cjs-shim.test.ts` with `if (process.env.CI) { assert.fail("dist missing — pnpm build must run"); }`. The intent was "CI catches drift." But:
- `build-<service>.yml` builds Docker images, never runs `pnpm test`
- No other workflow exists for `<service>/<agent>/**`
- Result: the regression test only catches drift when a developer remembers to `pnpm test` locally before pushing

The runtime startup health-check provided fail-loud-on-boot protection, but that's first-prod-startup-time loudness, not pre-merge loudness. The PR's stated lesson — "code paths that only run in deployed bundle need dist-level tests" — only holds if the test is invoked somewhere automated.

**Reviewer detection in 30 seconds:** When a PR adds a test file in subdirectory `X/` that loads or spawns a build artifact, run:
```bash
grep -rl "X/" .github/workflows/ | xargs grep -l "pnpm test\|pnpm run test\|npm test" 2>/dev/null
```
If empty: file as inline comment severity HIGH/Important — "test exists but no workflow invokes it."

Bonus detection: also check `Dockerfile*` for `pnpm test` — sometimes test-on-build is wired into the Docker layer rather than a workflow. If neither the workflow nor the Dockerfile invokes test, the regression coverage is purely manual.

**Generalisable to:** any project with monorepo subdirectories where some directories have CI test workflows and others don't. The asymmetry is the smell — if `<cloud-app>/` has `web-unittest.yaml`, `api_server/` has `server-unittest.yaml`, and a new test lands under `<service>/<agent>/`, ask "is there an `agent-unittest.yaml` for this directory?"

## CI silent-skip via git pathspec / working-directory mismatch

**Pattern (PR #1269 / <org>/<infra-repo>, 2026-05-06, <reviewer-B> round 5):** When a CI workflow step uses `git diff --name-only ... -- '<pathspec>'` to compute a list of changed files for downstream tools (lint, test runner, formatter), git interprets `<pathspec>` **relative to cwd**, not the repo root. If the step runs with `working-directory:` set to a subdirectory AND the pathspec includes the same subdirectory prefix, the pathspec resolves to a non-existent nested path and matches nothing — the step silently no-ops.

**Concrete case:** PR #1269 round 5 lint step:
```yaml
working-directory: ./<service>/<agent>
run: |
  CHANGED=$(git diff --name-only "$BASE_REF...HEAD" -- \
    '<service>/<agent>/**/*.ts' \
    ...) | sed ... | grep ... || true
  if [ -z "$CHANGED" ]; then exit 0; fi
```
From inside `<service>/<agent>/`, the pathspec `'<service>/<agent>/**/*.ts'` resolves to `./<service>/<agent>/**/*.ts` which doesn't exist. git diff matches nothing → CHANGED empty → step exits 0 with zero coverage. Every PR's lint step printed "No agent source files changed — skipping biome" and ran no biome at all.

**Three failure-amplifying patterns combined:**
1. Pathspec was repo-root-relative-looking (matches what `gh pr diff --name-only` outputs), seducing the author into thinking it's correct
2. `|| true` on the pipe swallowed any "no match" signal
3. The `if [ -z "$CHANGED" ]` early-exit was framed as a benign optimisation ("skip if no relevant files") but was actually the silent-skip mechanism for ALL files

**Reviewer detection (5 seconds):** any CI step that combines `working-directory:` + `git diff --name-only -- <pathspec>` warrants a reproduction run. Specifically:
```bash
cd <working-directory>
git diff --name-only <base>...HEAD -- '<one of the pathspec entries>'
# Expected: ≥1 file. If empty, the pathspec is broken.
```

**Three correct patterns (any one):**
- (a) **Drop the prefix, use cwd-relative pathspecs** (`'src/**/*.ts'` instead of `'<service>/<agent>/src/**/*.ts'`). git diff's output is still repo-root-relative, so any downstream `sed | grep` for repo-relative paths still works.
- (b) **Use git's `:(top)` magic prefix** to make pathspec absolute regardless of cwd: `':(top)<service>/<agent>/**/*.ts'`.
- (c) **Run from repo root** via `git -C "$GITHUB_WORKSPACE" diff --name-only -- '<pathspec>'`.

Option (a) is smallest diff and matches the project's pre-commit `--staged` pattern most directly.

**Generalisable to:** any CI step that uses git pathspecs from a subdirectory. The classic blast radius is "lint step exists but never runs" — which is doubly bad because the green check creates false confidence that linting was performed. Especially dangerous when the lint step was added specifically to close a previous CI gap (recursive irony — the fix for the original silent failure has its own silent failure).

**Bonus tell:** if the step's "skip" branch echoes a message like "No X changed — skipping" but you can't recall a single PR where the step ACTUALLY linted something, that's the smell. CI logs the message every run; nobody reads them.

## AI reviewers and human reviewers operate at different abstraction layers

**Pattern (PR #1269 / <org>/<infra-repo>, 2026-05-06, observed across 5 review rounds):** Copilot and human reviewers find systematically different classes of bugs. They are NOT redundant — they are complementary. A "modern" PR review pipeline that drops one in favor of the other will leak the dropped layer's bug class.

**Concrete observation across 5 rounds on PR #1269:**

| Round | Reviewer | What they caught |
|-------|----------|------------------|
| 1 | Copilot | function-level robustness: missing stack trace in fatal handler, `findings[0]` too narrow, ESM `__dirname` ReferenceError |
| 2 | Copilot re-review | deeper trace of round-1 fix: rejected promise latching, health-check still too narrow |
| 3 | Copilot round 3 | information loss: `assert.fail` only surfaced stderr, not stdout |
| 4 | Human (<reviewer-B>) | **system-level wiring: CI doesn't actually run the test the PR was built to ensure** |
| 5 | Human (<reviewer-B>) | **system-level wiring: lint step's git pathspec resolves wrong relative to working-directory, silently no-ops** |

The human reviewer sat with the diff, asked "what does this protect against if it's ever exercised?" and discovered a chain of unwired CI gaps the AI never surfaced. Three rounds of AI review didn't find them because they're not visible inside individual files.

**Why the asymmetry exists:**
- AI reviewers context-window per-file; their cross-file reasoning is bounded by what they can fit in context. They're excellent at "is this hunk internally consistent and correct?"
- Human reviewers default to building a system model: which CI workflow runs this test? what calls this function? what's the actual deploy path? They notice when the system model has a hole.

**Reviewer detection / methodology:**
- If a PR's review feedback is 100% AI-generated, suspect the system-wiring layer wasn't reviewed. Run a manual pass asking: "Does this CI step actually run? Is this test actually invoked? Does the deploy path actually exercise this code?"
- Conversely, if a PR's human reviewer didn't flag any micro-correctness issues (stack traces, error message details, narrow guards), suspect they didn't read every hunk. Ask the human reviewer to confirm they trace-checked specific code paths.

**Routing implication:** in this skill (`kc-pr-review-resolve`), AI reviewer findings tend to be classified as "valid bug, fix mechanically." Human reviewer findings tend to require thinking about WHY the failure mode exists, not just HOW to fix it. The fix-mechanically vs fix-thoughtfully ratio is roughly 80/20 vs 20/80 between the two reviewer types.

## Local state vs CI state asymmetry — local pass ≠ CI pass

**Pattern (PR #1269 / <org>/<infra-repo>, 2026-05-06, two distinct CI failures in the same PR):** A development environment accumulates state — built artifacts from prior `pnpm build`, IDE-compiled type info, cached `node_modules`, hand-curated `.env` files, manually `source`d shell variables. CI starts from zero. **Local "all green" provides ~zero evidence that CI will be green** for any change that depends on environment state.

**Concrete cases on PR #1269 (both authored by FO, both caught only by CI red):**

1. **TS2307 in CI but not local**: My new `<agent>-unittest.yaml` ran `pnpm exec tsc --noEmit`. Locally clean (tsc 0 errors). CI red with 5x `Cannot find module '@<org>/<workspace-pkg>'`. Reason: my worktree had `packages/trace-extraction/dist/index.d.ts` built from prior development; CI fresh checkout doesn't build the workspace package automatically. Fix needed `pnpm --filter @<org>/<workspace-pkg> build` step.

2. **Lint step silent-skip in CI**: My next iteration scoped biome to changed files via `git diff --name-only -- '<service>/<agent>/**/*.ts'`. Locally I tested by running the equivalent command from repo root — it worked. The CI step ran with `working-directory: ./<service>/<agent>` and the pathspec resolved relative to that cwd, matching nothing. I had not reproduced from inside the cwd before pushing.

**The deeper rule:** any CI variation must be reproduced under conditions the CI runner will face — `cd` to the actual `working-directory`, start from a fresh git clone or `git stash` everything first, unset cached env vars. The local "I ran it and it worked" is testing a different system than CI.

**Cheapest reproducer** (in order of cost):
1. **Push and watch CI red/green.** Costs you the embarrassment of a red commit but is the most accurate signal. Acceptable for CI workflow PRs because the workflow change IS the change being tested.
2. **`git worktree add /tmp/fresh-test main && cd /tmp/fresh-test`** — fresh checkout in same machine. Catches accumulated-state bugs.
3. **Docker container starting from `actions/runner-image`'s base** — most accurate but slowest setup.

**Specific things that drift between local and CI:**
- Built workspace package outputs (`dist/`, `target/`, `__pycache__`)
- Type checker caches (`.tsbuildinfo`, `.mypy_cache`)
- Dependency lockfile vs installed `node_modules` mismatch
- Environment variables (`.env` exists locally, only `secrets.*` in CI)
- Shell variables (`source venv/bin/activate` was run hours ago in your terminal)
- IDE-injected paths (your IDE prepends `/usr/local/opt/...` to PATH)
- Git pathspec / cwd interpretation when `working-directory:` is set
- Symlinked node_modules from monorepo neighbors

**Reviewer detection in PR review:** any CI YAML change should be reviewed with the question "what would happen if I ran this from the working-directory in a fresh git clone?" If the author can't answer concretely, request a fresh-state reproducer before merging.

## Fix-Guard-Name-Check-the-Guard: four-step closure for silent-failure bug fixes

**Pattern (PR #1269 / <org>/<infra-repo>, 2026-05-06, observed across 5 review rounds on a single bug):** When fixing a silent-failure-class bug (production was wrong but CI/tests/users didn't notice), the discipline that ACTUALLY closes the bug class — not just the instance — has four steps. Most PRs stop after step 2.

**The four steps:**

1. **Fix** — change the root cause. The actual code fix.
2. **Guard** — add a regression test / runtime check / startup health-check that would have caught the original silent failure if it existed at the time.
3. **Name** — capture the failure pattern in a searchable artifact (project review-lessons, plugin learned-patterns, MEMORY.md, CLAUDE.md). The naming makes it grep-findable for future maintainers ("oh, we've seen this class").
4. **Check the guard** — verify the guard itself doesn't have the same silent-failure shape it's designed to catch. **This is the step most PRs skip and it's the load-bearing one for closing the bug class.**

**Why step 4 is critical — silent failures self-replicate:** the developer who wrote the silent-failing original code is the same developer writing the silent-failing guard. The same blind spots that produced the original bug produce the guard with the same blind spot. PR #1269 demonstrated this three times in a single PR:

| Layer | Silent-failure shape | Caught by |
|-------|---------------------|-----------|
| Original bug (`mermaid-lint.ts` shim CJS branch) | early-return on `import.meta.url !== 'string'` assumed inlined DOMPurify had `addHook`; in fact `valid:false` returned for every prod call → agent silently used ASCII tree | Customer screenshot, after ~18 days |
| First guard (`mermaid-lint-cjs-shim.test.ts`) | `if (!existsSync(distPath)) { console.log('SKIP'); return; }` re-introduced silent skip when CI didn't `pnpm build` first | FO self-review (cycle 2) |
| Second guard (`<agent>-unittest.yaml` lint step) | `git diff -- '<service>/<agent>/**/*.ts'` from inside that very subdirectory matched nothing → `if [ -z "$CHANGED" ]; then echo "skipping"; exit 0` printed friendly skip on every PR | <reviewer-B> human review (round 5) |

**The smell that should trigger step 4:** any "skip if N/A" branch in the guard's logic. Be especially suspicious of:
- `if (!existsSync(...)) skip`
- `if (CHANGED is empty) skip`
- `if (process.env.X !== 'production') skip`
- `try { ... } catch { return; }` patterns
- Friendly log messages on the early-exit path ("nothing to do", "skipping", "no changes detected")

**The four-step closure question to ask in review:** "If this guard's skip-branch fired on every run for a year, would the green-check still create false confidence?" If yes, the guard has the original bug's shape and step 4 isn't done.

**Reference fixes for "I caught my own guard's silent failure":** PR #1269 commits `<sha>` (CI hard-fail when bundle missing under `process.env.CI`), `<sha>` (cwd-relative pathspec). Both are step-4 closures retroactively applied after step-3 reviewers spotted the recursive irony.

## Library override + assumed behavior = two-commit implicit-contract bomb

**Pattern (PR #1269 / <org>/<infra-repo>, 2026-05-06, the original case 015 root cause):** Bug class that single-commit code review structurally cannot catch: **commit A** introduces code that assumes library X behaves a certain way; **commit B** (often unrelated, often a dependency upgrade) breaks that assumption. The bug only exists at the intersection of A + B; reading either commit in isolation looks correct.

**Concrete case on PR #1269:**
- `<sha>` (<TICKET-B> feat) — `mermaid-lint.ts` CJS branch did `if (typeof import.meta.url !== 'string') return; // bundled — DOMPurify already has addHook` based on `dompurify@<3.4.0`'s observed CJS export shape. Single-commit review: the early return looks like an optimisation with a sensible-sounding comment.
- `<sha>` (CVE batch) — added `pnpm overrides: { "dompurify": ">=3.4.0" }` to satisfy a security advisory. Single-commit review: a routine version bump, sensible.
- A + B together: `dompurify@3.4.0` added a stricter DOM guard that early-returns from `createDOMPurify()` without defining `addHook` when `getGlobal()` is null (Node). The shim's "DOMPurify already has addHook" assumption silently falsified. `validate_mermaid` returned `valid:false` for every prod call for ~18 days.

**Why neither commit's review caught it:**
- A's reviewer didn't have B's diff in context. They couldn't predict that a future Dependabot bump would break the assumption.
- B's reviewer didn't trace every consumer of dompurify's behavior; they trusted the version range was a "patched + backwards-compatible" CVE bump.

**Reviewer detection — when to flag a PR for two-commit-bomb risk:**
1. Any PR that adds code making explicit assumptions about a third-party library's behavior (presence of method, shape of return value, ordering of side effects). Look for code comments like "this works because library X always Y" or `// safe — Z is always defined`. Each is a load-bearing assumption that needs an automated assertion.
2. Any PR that bumps a dependency major or minor version via overrides/pins. Grep the codebase for monkey-patches, conditional behavior, `instanceof` checks, presence-of-method tests on that library. Each is a place where the assumption could break.

**Defenses to require:**
- For A-style PRs: add a contract test (`expect(typeof DOMPurify.addHook).toBe('function')`) at the assumption boundary. Cheap, runtime-equivalent to a TypeScript type guard.
- For B-style PRs: review the changelog of every bumped library for behavioral changes (not just security fixes). For `>=` overrides especially, check the upper bound — what's the worst-case behavior change in the version range you opened?
- Across-the-board: any code that mutates global state assuming a library's behavior should have a startup health-check that exercises the assumption. PR #1269's `runStartupHealthCheck` is the reference shape.

**Reference:** PR #1269 case 015 (commits `<sha>` + `<sha>` → 18-day silent prod regression).

## Telemetry safety helper completeness — wrap ALL related calls or none (2026-05-06)

**Pattern (PR #1270 / <org>/<infra-repo> re-review, 2026-05-06):** When a PR introduces a "telemetry must never crash production" helper module wrapping selected Sentry calls in try/except (e.g., `emit_measurement`, `emit_event`), audit the call-site files for OTHER related Sentry APIs that are still called raw — especially `set_tag`, `set_user`, `set_context`, `add_breadcrumb`. Half-wrapping creates an inconsistency that's hard to spot in review:

- `emit_measurement` → wrapped in try/except (helper)
- `set_measurement` → never called raw (good)
- `set_tag` → still called raw at ~12 sites in same file (gap)

In Sentry SDK 2.x, `set_tag` IS documented as safe-on-uninit, so the practical risk is near-zero. But the asymmetry violates the helper's stated rationale ("telemetry must never crash") and makes the safety guarantee depend on the SDK version's defensive behavior rather than explicit code.

**Rule for review:** When a PR adds a `try/except: pass` telemetry helper, grep the consumer file for OTHER `sentry_sdk.<call>(` patterns. If any are left raw, either (a) extend the helper (`set_tag_safe`, etc.), or (b) document in the helper's docstring why those specific calls are exempt. Don't accept "set_tag is safe by SDK convention" as a rationale unless that's explicit in code.

**Reference:** PR #1270 re-review advisory A.

## Re-review trust-but-verify discipline (2026-05-06)

**Pattern (PR #1270 / <org>/<infra-repo> re-review, 2026-05-06):** When re-reviewing a PR after the author claims "all findings fixed in <SHA>", do NOT trust the commit message. The reviewer's job is to verify each fix at code level by:

1. Building a one-row-per-prior-finding verification table (✅ / ⚠️ / ❌) BEFORE reading the new diff
2. For each prior finding, anchor on the ORIGINAL identifier (function name, variable, label) and grep the current HEAD to verify the change is real (e.g., removed identifier returns 0 hits, renamed event uses the new name in expected paths)
3. For semantic fixes (e.g., "node_id_mismatch should fire only on real 404s"), read the surrounding context to verify the dispatch logic actually separates the two cases — not just renamed in one branch
4. Run tests + lint + mypy in a worktree to confirm no regression

This trust-but-verify discipline produces an evidence-rich re-review body where every prior finding is explicitly closed or marked residual. PR #1270 had 13 prior findings; verifying all 13 took ~10 grep + 4 sed + 2 test runs + mypy. Cost: low. Value: high — author and downstream maintainers see exactly what was checked.

**Anti-pattern:** "I read the new diff and it looks fine, approving" — this is the failure mode where Claude or human reviewers approve fixes that didn't actually land (case feedback_teammate_trust_verify.md, MEMORY.md project knowledge).

**Reference:** PR #1270 re-review (commit <sha> verified against original 13-finding review).

## Sampled-metric alert sensitivity blind spot (2026-05-11)

**Pattern (PR #1270 Round-4 / <org>/<infra-repo>, 2026-05-11):** When a PR introduces Bernoulli sampling around a metric (e.g., gating `json.loads` deep-parse behind a 1% probability), check every downstream alert that depends on that metric.

The failure mode: sampling code and alert config are individually correct, but their interaction silently breaks "any occurrence triggers" alert semantics. Effective sensitivity drops by `1 / sample_rate`. The code reviewer sees the sampling block, says "looks right", and sees the alert config, says "looks right" — but never reasons about the composition.

**Rule for review:** When a diff adds sampling-gated emit of a metric M, ALWAYS:

1. Grep alert configs / runbooks / spec docs for references to M
2. For each consuming alert, classify the alert semantic:
   - **"Rate > threshold"** alerts: sampling is safe IF threshold is rate-of-rate (rate(M) / rate(N) > 0.05), since both numerator and denominator are sampled equally
   - **"Any occurrence triggers"** alerts: sampling breaks the alert — `1/sample_rate` fewer events fire
   - **"Count > N over window"** alerts: threshold needs to be scaled by sample rate
3. Flag the affected alerts in the review and propose: (a) widen sample rate to match alert tolerance, (b) document the scale-up factor in the alert config, or (c) always-emit the event part while sampling only the expensive part (e.g., `json.loads` sampled, but iteration over already-parsed dict always runs)

**Common shape:** Sampling reduces parse cost on hot path → tag like `sampled=true/false` added → forget that downstream `capture_message` / `_emit_event` inside the sampled block also got rate-limited.

**Anti-pattern:** Approving a sampled-instrumentation PR without grepping for the metrics' alert consumers.

**Reference:** PR #1270 Round-4 inline comment #2 — `lineage_nodediff_missing_fields` (P0 critical, "any occurrence triggers") sensitivity reduced 100× because `_missing` list-comp + `_emit_event` are inside the `if _node_count_sampled:` block.

---

## Pattern: Pre-existing vs PR-introduced build/lint warning verification (2026-05-12)

**When**: Reviewing a dep-bump PR (toolchain, transpiler, linter, lockfile) and the build / `lint:check` / `tsc` emits warnings that you can't immediately classify as pre-existing or new.

**Do not** quote the warning in the review without classification — readers will assume it's a regression introduced by the bump.

**Verification dance** (cheap, ~30s):
1. `git checkout origin/main -- <changed package manifest files>` in the worktree
2. `pnpm install` to materialize the *old* dependency set
3. Re-run the same build/lint command
4. Diff the warning surface against the PR-state run
5. `git checkout HEAD -- <files>` + `pnpm install` to restore PR state

If the warning count and call-sites are identical, classify as **pre-existing** and either omit from the review or explicitly call out "unchanged from `origin/main`" so the next reviewer doesn't re-investigate.

**Example (PR #1303, <infra-repo>)**: `esbuild@0.28.0` build emitted `[WARNING] "import.meta" is not available with the "cjs" output format` on `src/utils/mermaid-lint.ts:152,184`. Initial suspicion: new esbuild diagnostic. Verification by rebuilding on `origin/main` with `esbuild@0.27.3` showed the exact same warnings → pre-existing, not a regression. Final review explicitly stated "unchanged from `0.27.3`" so the PR could be approved without that finding blocking merge.

---

## Pattern: Cross-repo SOT-first sync when fix targets shared content (2026-05-13)

**When**: PR review finds an issue in a file that's byte-identical across a plugin SOT + N instance copies (typical of ship-flow's `plugins/ship-flow/_mods/` SOT + `docs/ship-flow/_mods/` instances across captain's repos).

**Default pattern** when fix is approved for cross-repo sync:

1. **Edit in plugin SOT first** (the canonical copy). Verify with `grep` that all occurrences are caught.
2. **Propagate via `cp`** to each instance — never re-edit. cp preserves byte-identity, eliminates drift risk from "fixing it differently" in each copy.
3. **md5 check after propagation**: `md5 file1 file2 file3 file4` — all hashes must match before any commit.
4. **One commit per repo** (cross-repo can't be atomic). Commit message names the SOT commit explicitly for archeology: `fix(ship-flow): ... (sync from spacedock-ui SOT, ${context})`.
5. **Push order**: SOT first, then instances. If SOT push is blocked by branch protection, fall back to feature-branch + PR per the rejected repo's flow.

**Anti-pattern**: editing the same fix in each instance independently. Even with a simple find/replace, prose context can drift (different surrounding lines, different quote style, slightly different rewording). The cp-from-SOT discipline eliminates this.

**Example (PR #710, carlove)**: Copilot flagged "Kent's design taste" in `_mods/design-officer.md` as hard-coded personal name. Same content existed in 4 byte-identical files: plugin SOT (`spacedock-ui/plugins/ship-flow/_mods/`), spacedock-ui instance (`spacedock-ui/docs/ship-flow/_mods/`), carlove instance, kc-claude-plugins instance. Fix landed in SOT first (commit `a8089508`), then cp-propagated + committed per repo. md5 check confirmed byte-identity. Reply on the inline thread named all 4 commit SHAs across 3 repos for cross-repo traceability.

---

## Pattern: chained `git checkout && git add && git commit` lands on wrong branch when checkout silently fails (2026-05-13)

**When**: Multi-step bash command does `git checkout BRANCH && cp FILE TARGET && git add ... && git commit ...` to apply a cross-branch fix.

**Failure mode**: If `git checkout BRANCH` fails (e.g., working tree has a file that conflicts with the branch switch — git says "Please move or remove them before you switch branches. Aborting"), bash continues to the next chained command. The `cp` overwrites the file in the CURRENT (wrong) branch. `git add` stages it. `git commit` lands the commit on the ORIGINAL branch.

The commit message looks correct, the file content looks correct, but the commit is on the wrong branch. `git push BRANCH` reports "Everything up-to-date" because the target branch has nothing new — the commit is on the OLD branch.

**Diagnosis (after the fact)**:
- `git branch --show-current` shows the unintended branch
- `git log --oneline -1` shows the fix commit on the unintended branch
- `git log INTENDED_BRANCH --oneline -1` shows the intended branch unchanged
- `git reflog | head -3` shows the checkout-attempt didn't move HEAD

**Recovery**: `git reset --hard origin/INTENDED_BRANCH` on the wrong branch (drops the orphan commit; preserved in reflog for safety). Then `git checkout` (now succeeds because working tree is clean post-reset). Then reapply the fix on the correct branch.

**Prevention**: Before any chained `git checkout && [stateful ops]`, either:
- Use `&&` exclusively (not `;` or newlines between commands) — `&&` halts on checkout failure
- OR: separate into two steps and verify `git branch --show-current` between them
- OR: use `git switch -C` (force-switch, creates branch if needed) for unambiguous intent

**Example (PR #710 review-resolve, carlove)**: Chained `git checkout kent/ship-flow-overhaul-phase-5-6 && cp PLUGIN_SOT INSTANCE && git add + commit + push`. Checkout failed (working tree had design-officer.md from a prior `cp` that the branch checkout would clobber). Bash continued, commit landed on `main` (unintended). Push to feature branch reported "Everything up-to-date" — misleading. Recovery: `git reset --hard origin/main` (orphan commit `98bab1ec1` preserved in reflog), checkout succeeded on clean tree, reapplied fix on feature branch as `46b35f2d7`, pushed cleanly.

---

## Pattern: Cost-benefit triage when one review flags N issues with M-repo blast radius (2026-05-13)

**When**: Reviewer (human or AI) leaves N comments on a single file that's propagated across M repos via SOT+instance discipline. Fixing K of N issues requires K × M file edits + K × M commits + K × M pushes.

**Triage by criticality × blast radius**:

- **Substantive issues** (correctness, template portability, security, broken UX) — fix across all M copies regardless of M's size. Cross-repo discipline matters here.
- **Minor style** (gerund-on-CamelCase, possessive-on-keychord, prose readability) — fix only when M=1. When M≥2, **acknowledge + defer** with explicit reasoning in the thread reply. Batch with future readability-pass commit if more style issues accumulate.
- **False positives** — reply explaining why the suggestion doesn't apply here; never auto-fix.

**Rationale**: 4-repo prose-only sync = ~4 minute work for ~0 user-visible value. The same 4 minutes spent on a substantive fix (template portability, broken link, broken example) delivers actual user value. Captain's repo personalization (acknowledged-as-is style) is a legitimate stop point.

**Reply discipline for deferred-style threads**: Be specific about WHY deferred. "Acknowledged — minor style, deferred from cross-repo sync this round. Will batch with future readability pass." Vague "will fix later" replies frustrate AI reviewers (they re-flag next round) and human reviewers (looks like dismissal).

**Example (PR #710, carlove)**: Copilot flagged 3 inline issues in `_mods/design-officer.md` — #1 hard-coded personal name (template portability, substantive), #2 `SendMessage'ing` gerund (minor style), #3 `Shift+Down's` possessive (minor style). Option C selected: #1 synced across 4 repos (substantive + portability matters for marketplace adopters); #2/#3 reply-only with explicit "deferred from cross-repo sync, minor style" rationale. PR merged after captain reviewed the 4-repo sync for #1. AI re-trigger skipped (would re-flag #2/#3 → noise loop).

**Corollary — workspace-dep build for type-check**: When the consumer package declares `"types": "dist/index.d.ts"` in `package.json` (e.g., `@<org>/<workspace-pkg>` → `<service>/<agent>`), the workspace dep MUST be built before the consumer's `tsc --noEmit` runs. Fresh worktrees that only ran `pnpm install` will report `TS2307: Cannot find module '@<org>/...'` even though the lockfile is correct. Build chain: `pnpm --filter @<org>/<workspace-pkg> build` first, then type-check the consumer.

## Cross-file doc claim verification (2026-05-13)

**Pattern (kc-pr-flow PR #18, 2026-05-13):** When a docs PR adds or modifies normative claims about other files/symbols ("X works", "all sites use Y", "see `path:NN`", "fixed in commit `<sha>`"), grep the cited subjects to verify the claim is grounded. Forward-looking claims that anticipate a future state are common during multi-commit rollouts and create silent doc drift if not caught.

**Detection signals:**

- Added doc lines containing both a normative auxiliary (`uses`, `should`, `must`, `all`, `every`, `works`, `broken`, `correct`, `fixed`) and a cited subject (backtick token, path, or commit SHA)
- Cited subject lives outside the diff (i.e., the claim references unchanged or separately-changed code)

**Why it slips review:** Doc-only changes read as standalone prose. Diff-scoped reviewers (agents and humans alike) don't reflexively grep for cited subjects unless prompted per-claim. The cost of grep is near-zero; the cost of merging a wrong doc claim is real — the next reader trusts the entry and bases work on it.

**Rule for review:** Operationalized as kc-pr-review §4.5j. Pure pre-scan, zero LLM tokens. Severity: MEDIUM when cited subject is missing; LOW when it exists but contradicts the claim (could be intentional gap).

**Reference:** kc-pr-flow PR #18 F2 (forward-looking claim about `gh-api-patterns.md` reviewer-add behavior) — caught manually during /review dogfood; §4.5j surfaces it automatically.

## Intra-doc rule-vs-example self-consistency (2026-05-28)

**Pattern (recce PR #1406, 2026-05-28):** When a docs PR adds a normative rule prohibiting pattern X (e.g. "There is no root `package.json`; pnpm commands from the repo root will fail"), the same diff often leaves untouched example commands elsewhere in the same file that violate the new rule. Multi-round AI/human review masks this: a first-round reviewer flags one offending line; the author fixes that line; the new rule lands in the diff; but other instances of pattern X in the same file are never grepped for. A second-round reviewer catches the contradiction, or worse, the wrong example survives merge and propagates to downstream agents.

**Detection signals:**

- Added doc lines containing a prohibitive-rule signature: `<X> will fail`, `<X> fails`, `never <X>`, `do not <X>`, `There is no <X>`, `MUST NOT <X>`, `<X> instead of <Y>`
- The prohibited pattern X is a concrete grep-able token (bare command, specific path, syntax form)
- Same file (or same diff) contains other example commands matching pattern X without the prescribed mitigation

**Why it slips review:** Reviewers (human and LLM) attend to each diff hunk in isolation. A rule landing in hunk A and an example violating it in hunk B is structurally invisible to per-hunk attention. Confirmation bias amplifies the miss: after verifying the new rule "looks correct," the reviewer doesn't pressure-test the rule against the rest of the same diff. Mid-PR fixups (reviewer-A flags one site, author fixes only that site) create a clean-on-paper PR with stranded counter-examples.

**Rule for review:** Operationalized as kc-pr-review §4.5k. Pure pre-scan — extract pattern X from the new rule, grep the same file/diff for remaining matches, filter the rule-statement line itself + already-compliant lines. Severity: MEDIUM when the offender is in the same diff (PR introduces the contradiction); LOW when offender is unchanged context (pre-existing, PR merely exposes it).

**Reference:** recce PR #1406 (2026-05-28) — `CLAUDE.md:16` adds "pnpm from repo root fails" rule; `CLAUDE.md:52` modified by same PR still issued bare `pnpm install && pnpm lint ... && pnpm build`. Copilot flagged L16, author fixed L16 only, @even-wei caught L52, kc-pr-review approved without spotting. §4.5k would have surfaced L52 automatically.

Complements §4.5i + §4.5j: §4.5i = code helper rollouts grep the *rest of the repo* for direct API calls; §4.5j = doc claims grep the *codebase* for cited subjects; §4.5k = doc rules grep the *same diff/file* for violating examples. Three cells of the same consistency-matrix primitive.

## Baseline-convention check at meta level (2026-05-13)

**Pattern (kc-pr-flow PR #18, 2026-05-13):** kc-pr-flow's §4f baseline-convention rule ("Before flagging a pattern as an issue, check whether the SAME pattern exists in unchanged code in the same file") works as a primitive at the code level. The same primitive applies at the **meta level** when one skill reviews another skill's output: before flagging a pattern in a SKILL.md / reference / agent file, grep the plugin (and adjacent plugins) for sibling usage.

**Detection signals:**

- Reviewer flags a pattern in a `*.md` / `skills/**` / `reference/**` / `agents/**` file as inconsistent or unsafe
- The pattern is mechanical / stylistic (placeholder convention, terminology, ordering), not a true correctness issue
- The flagged file is part of a multi-site convention that the reviewer's diff-scoped context doesn't see

**Rule for review:** Operationalized as `reference/review-triage.md` §4f extension. Threshold: **3+ sibling sites** in unchanged code = established convention. Explicit-instruction trump card: a documented "use placeholder X" line in the skill body overrides sibling count.

**Why it slips review:** Cross-skill review reads the target skill's diff as standalone prose. The reviewer's prompt context doesn't pre-load the whole plugin's convention surface, so patterns that are "obviously the standard" to the plugin author look like inconsistencies to a fresh-context reviewer.

**Reference:** kc-pr-flow PR #18 F1 (OWNER/REPO placeholder convention, 7+ sibling sites + SKILL.md L67 explicit instruction) — false-positive flagged by /review; the meta-level baseline check would have suppressed it. Complements §4.5j: §4.5j catches *forward-looking claims*, §4f-meta catches *retrospective false positives on established conventions*.

## Cross-review verdict persistence (2026-05-13)

**Pattern:** Iterative review cycles — and especially daemon mode polling — re-surface the same AI-reviewer comments on every cycle. Once the user has dismissed an Issue as `wont_fix` or `false_positive`, re-presenting it on the next cycle is pure noise. Persist verdicts per-branch with a stable fingerprint, suppress on re-encounter as long as the underlying file is unchanged.

**Detection signals:**

- Same `(file, conceptual_issue)` Issue appears in N consecutive review cycles on the same branch
- User dismissed the Issue in a prior cycle (`wont_fix` / `false_positive`)
- The file the Issue references has NOT been touched between the dismissal commit and `HEAD`

**Why it slips review:** Cross-AI dedup (Step 3.5) handles *within-cycle* duplication across reviewers. It does NOT handle *across-cycle* duplication of the same finding. Without persistence, every re-review surfaces previously-dismissed issues as if they were new — frustrating for the user and the reviewer (who also sees a fresh thread reply on an issue they thought was settled).

**Rule for review:** Operationalized as kc-pr-review-resolve Step 3.6 with persistence at `~/.claude/kc-plugins-config/pr-flow/review-state/{repo-slug}-{branch}.jsonl`. Fingerprint: `sha256(file + "|" + normalized_conceptual_issue)`. Suppress only `wont_fix` / `false_positive` verdicts (NOT `fixed` — fixes can regress and need re-validation).

**Reference:** Adapted from gstack `/review` Step 5.0 cross-review finding dedup (originally for self-review findings). Most valuable in daemon mode where polls amplify the re-surfacing problem. Complements §4.5j (forward-looking doc claims) and §4f-meta (retrospective baseline convention): all three operationalize "use the codebase's own state as the source of truth before flagging anything".
