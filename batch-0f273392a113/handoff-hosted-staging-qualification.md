# Handoff: QNow Next hosted staging qualification (entity r33jtp5370kxngzbr6cd7rej)

Source of truth: `qnow-next-hosted-staging-qualification/index.md` on iamcxa/qnow `spacedock-state/dev` (6,207 lines: 84 implementation cycles, 21 Captain authorization receipts), plus the two child Conductor workspaces' final reports (DEV-35 3f53345e, DEV-36 64d00bbd). Written by the kc-claude-plugins FO on 2026-09-07 from those records; nothing here is inferred beyond them.

## Who did it
The First Officer seat for the qnow-next sprint ran as Codex sessions in the local Conductor workspace `carlove-v1/kyoto` (remote iamcxa/qnow, branch feat/qnow-next-claim-probe), 2026-08-21 → 2026-08-31, with the entity's work in the ensign worktree `spacedock-ensign-qnow-next-hosted-staging-qualification` (branch of the same name, 48 commits ahead of main, no PR). Those sessions are gone; the kyoto workspace no longer holds the worktree. The branch and the state report remain.

## What it set out to prove (Pilot, ideation approved 2026-08-23)
At one exact revision on an isolated hosted staging: a reception user signs in through the dedicated staging Identity provider, sees only the synthetic pool for one server-side tenant/branch assignment, claims one scheduled order, and reads it back in Mine and Detail after reload; a second reception user in the same branch races the claim (exactly one wins); a third user in another tenant is denied; a lost browser response is replaced by a readback, never a second mutation. Rule from ideation: implementation may prepare code and zero-mutation preflight only; every hosted mutation needs a fresh exact resource / operation / cleanup-owner / spend authorization (hence 21 receipts).

## What was proven (hosted, exact revision)
- Cycle 69: exact candidate deploy with migrations 0000–0007 through a caller-cwd-independent operator; the sole runtime probe returned a revision-bound 503 at handler construction (then subdivided into four named phases).
- Cycle 74: **first exact-revision hosted success** — one deploy, all eight migrations applied, QNow-owned runtime compatibility receipt admitted at HTTP 200. Infrastructure admission only; no Identity actors, no journey.
- Cycle 83: bounded provider env-only diagnostic — the pinned nested secret response shape admitted for all six production/functions keys, then all six deleted and proven absent.
- Locally, in support: Identity bootstrap / hosted Function bootstrap / hosted Identity / Web client tests 31/31; the acceptance operator contract (four modules: exact execution sequence, Netlify candidate/live-pointer lifecycle, hosted Identity and fixture adapters, package entry point) with one-deploy and cleanup-only-after-first-failure enforced.

## What is still unproven
- The product journey itself (AC-6..AC-10: three real hosted Identity actors, database-derived assignment authority, tenant denial, exact-once claim race, readback). Every attempt stopped before it: cycle 77 (runner could not instantiate its Playwright adapter), cycle 81 (provider's post-create filtered env record did not meet the secret-safe contract), cycle 84 (the temporary TypeScript runner was classified as CommonJS; first-failure rule forbade a retry).
- Hosted migration-before-publish ordering (cycle ~8 saw `applied: []` from the provider's native journal; Netlify Support was contacted; HOLD recorded).
- Per DEV-36's own report: the package-default provider path has never been rehearsed against the real provider; the first real run must be watched.

## What has durable value (carry to main)
- `experiments/netlify-refine-poc/qnow-next/hosted/` (26 files): the acceptance operator contract, Netlify session lifecycle with rollback pointer binding, secret-safe structural readback, canary scan, deploy diagnostics. This is the runner DEV-36 (#1174) hardened; #1174's eight review fixes (run id out of paths, bootstrap window vs deploy timeout, deploy latch, error surfacing) sit on top of it.
- The headed-browser environment planner and smoke (`local/headed-browser-*.mjs`) — already on main via #1180 (DEV-35).
- The identity port + conformance suite — on main via #1177 (DEV-25).
- The authorization-receipt discipline (exact revision, one deploy, cleanup owner, spend cap, hard stop) — reusable as ship-flow's pattern for any hosted mutation.

## What to drop or fold
- Cycle-specific temporary runners under /tmp shapes and the superseded operator logic deleted in cycle 78 (already gone).
- Diagnostic-only scripts whose questions were answered (env-record shape, online-build read-only probes) can stay as tools but need no journey wiring.

## What a PR to main needs (Captain's rule: main → staging → prod)
The 48 commits touch 92 files (+31.5k/−2.6k). A reviewable path: (1) land `hosted/` as its own PR with `test:hosted-gates`, `test:netlify-package` and the self-check as its evidence (credential-free); (2) rebase #1174 onto that; (3) run DEV-37 from main in a Conductor cloud workspace under a fresh cycle-85-style authorization receipt, one deploy, watched. The remaining commits (config, docs, migrations 0000–0007 if not already on main) go with (1) or a separate PR; check each migration against main first.
