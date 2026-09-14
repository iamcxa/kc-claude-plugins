# POC Receipt — Mermaid sequence companion, PR #440

Worktree: `.worktrees/spacedock-ensign-mermaid-sequence-companion-has-no-repeatable-check`
Reset command: `git fetch origin cfb804d64f1e0ef35862505ee68c26c51c176076 && git reset --hard cfb804d64f1e0ef35862505ee68c26c51c176076`
`git rev-parse HEAD` → `cfb804d64f1e0ef35862505ee68c26c51c176076` (confirmed before any other step)

## AC-1 — typecheck: FAILS at baseline, independent of the PR's own code

Command: `cd kc-journey-map && npm ci && npx tsc`
`npm ci` — exit 0 (374 packages).
`npx tsc` — **exit 2**, not 0:

```
server/client/App.tsx(6,29): error TS7016: Could not find a declaration file for module '../../lib/records.mjs'.
```

This error is unrelated to `sequence.ts` — `lib/records.mjs` has no `.d.ts` and `tsconfig.json`
does not allow-implicit-any-override it. `git log -1 -- lib/records.mjs` → `3fd2fc59` (#417), which
predates this PR. So AC-1's baseline claim ("`npx tsc` exits 0") **does not hold at `cfb804d`**,
for a reason unrelated to the Mermaid companion.

Mutation (to check the falsifier still works despite the pre-existing failure): inserted
`const typeBreakingProbe: number = input.source` after line 9 of `server/client/sequence.ts`.
Re-ran `npx tsc` — exit 2, now **2 errors**, the new one being
`server/client/sequence.ts(10,8): error TS2322: Type 'string' is not assignable to type 'number'.`
Reverted the edit; `git diff --stat server/client/sequence.ts` after revert showed no changes.

Verdict: **AC-1 fails as written.** `tsc` does not exit 0 at `cfb804d` before any mutation — a
pre-existing, PR-440-unrelated declaration-file gap in `lib/records.mjs` already breaks it. The
falsifier property (a `sequence.ts` type error is visible in `tsc`'s output) does hold.

## AC-2 — production build: bundle builds and the dynamic import resolves; mutation fails the build

Command: `cd kc-journey-map && npx vite build`
Exit 0. Output dir `server/client/dist`. Full asset list (101 files) captured; the dynamic-import
target was confirmed by:

```
$ grep -o 'import([^)]*dist-esm[^)]*)' server/client/dist/assets/index-*.js
import(`./dist-esm-DTH9OtbL.js`)
$ grep -o "createMermaidDiagram" server/client/dist/assets/dist-esm-*.js
createMermaidDiagram
```

`@tldraw/mermaid`'s `createMermaidDiagram` export is reachable through the compiled dynamic
`import()` — the import resolves in the output.

Total dist bytes (all files, incl. CSS/HTML): `find server/client/dist -type f | xargs ls -la | awk
'{sum+=$5} END {print sum}'` → **5,391,377 bytes**. Rebuilt from the same untouched source a second
time and got the identical byte total and identical chunk filenames — deterministic build.

Mermaid chunk weight — measured, not exact, and the method is stated because a clean before/after
diff was not obtainable (see mutation below, which fails the build entirely rather than producing a
leaner one to diff against):
- Lower bound: JS chunks containing the literal string `mermaid` sum to **1,924,564 bytes** (out of
  5,313,527 total JS bytes).
- Upper bound: total JS bytes minus the three chunks that exist independent of any Mermaid feature
  (`index-*.js` the main entry, `rolldown-runtime-*.js`, `defaultLocale-*.js`) = **3,398,433 bytes**.
  Nothing else in this app imports `mermaid` or its dependencies (`dagre`, `cytoscape`, `katex`,
  `rough.esm`, several `d3-*` pieces) — `grep -rn mermaid server/client/*.tsx server/client/*.ts`
  shows the only reference is `sequence.ts`'s dynamic import.
- Reported range: **~1.9–3.4 MB of the ~5.1 MB JS payload is attributable to Mermaid**, all
  lazy-loaded via dynamic `import()` (not in the eagerly-loaded `index-*.js`).

Mutation: removed `@tldraw/mermaid` from `package.json` `dependencies`, ran `npm install` (which
pruned it — confirmed `ls node_modules/@tldraw/ | grep mermaid` → no match, 112 packages removed).
`npx vite build` (redirected, exit code checked directly, not through a pipe) → **exit 1**:

```
Error: [vite]: Rolldown failed to resolve import "@tldraw/mermaid" from
".../server/client/sequence.ts". This is most likely unintended...
```

No `dist/` was produced by the mutation build — confirming there is no leaner "without Mermaid"
bundle to diff against; hence the heuristic bounds above.

Revert: restored `package.json` and `package-lock.json` (both had been saved before the mutation).
`npm ci` failed once with a workspace-related error because `package-lock.json` had drifted from
`npm install`'s in-place edit; that lockfile was restored from the pre-mutation copy too, and a
subsequent `npm ci` succeeded (374 packages) with `@tldraw/mermaid` present again in
`node_modules`. Rebuilt: exit 0, identical 5,391,377-byte total and identical chunk set as before
the mutation — confirms the revert is clean. `git status --short` on the worktree shows no diff.

Verdict: **AC-2 holds.** Build succeeds, dynamic import resolves, mutation fails the build,
Mermaid's added weight is reported as a measured range with method disclosed.

## AC-3 — sequence-smoke.mjs against an isolated frontend/API pair

`agent-browser` is present: `agent-browser --version` → `0.32.0`. AC-3 is runnable.

Isolation:
- `JOURNEY_API_PORT=58234`, API started via `npx tsx server/canvas-server.ts`. `curl
  http://localhost:58234/health` → `{"ok":true,"tldraw":"5.4.0","port":58234,"rooms":[],"active":[]}`
- `JOURNEY_ROOMS_DIR=/tmp/journey-rooms-smoke-mermaid-poc` (dedicated temp dir, removed after the
  run)
- Frontend: `VITE_JOURNEY_API_URL=http://localhost:58234 npx vite dev --port 58235 --strictPort
  --host 127.0.0.1` → ready, `curl -o /dev/null -w '%{http_code}' http://127.0.0.1:58235/` → `200`
- Room id: script-generated `sequence-smoke-<uuid>` (set via its own `randomUUID()`, appended as
  `?room=` to the origin passed in)

Command: `node scripts/sequence-smoke.mjs http://127.0.0.1:58235`
Exit 0. Full JSON output:

```json
{
  "backup": "native edit retained",
  "first": { "name": "Book pickup — sequence", "pageId": "page:Iy-Idss5H36g5petUK1IX", "shapes": 18, "sourcePath": "docs/journey/book-pickup-sequence.mmd" },
  "malformed": "refused",
  "numberedMessages": 6,
  "preservedRecords": 66,
  "second": { "name": "Book pickup — sequence (2)", "pageId": "page:AMn6BUNm6rzKFrAwmnCPy", "shapes": 18, "sourcePath": "docs/journey/book-pickup-sequence.mmd" }
}
```

Assertion count correction: the script has **13 `assert()` call sites**, not seven (12 distinct
named checks plus one generic `preserved()` helper reused three times). No thrown error means every
one passed. Each named check, by line:
1. `arrows.length === 6` — six native message arrows rendered
2. per-number loop (1–6) — each autonumber label present
3. `alt [Available]` branch label rendered natively
4. all shapes are native and untagged `journey`
5. `editor.getPage(...).meta.sequence.source` carries provenance
6. a manual native text edit persists after being applied
7. re-render adds a distinguishable page (`(2)` suffix, new pageId)
8. a manual native edit and an unrelated manually-created shape/page survive the re-render
   (`preserved()`)
9. malformed input (`Alice->>` with no target) throws / is refused
10. malformed input added no new records
11. malformed input did not change the active page
12. explicit unnumbered source produces no autonumber labels
13. the backup JSON (`serializeTldrawJson()`) retains the native edit

Verdict: **AC-3 holds** — all assertions passed against an isolated pair, receipt above names both
ports, the rooms dir, the room id pattern, and every check.

Teardown: killed the API and frontend processes by PID (`kill -9`), confirmed with `ps aux | grep`
no matching processes remained, removed the temp rooms dir.

## AC-4 — tldraw / @tldraw/mermaid symbols

Installed versions: `node_modules/tldraw/package.json` → `"version": "5.4.0"`;
`node_modules/@tldraw/mermaid/package.json` → `"version": "5.4.0"` (matches the pin).

- `editor.getTextOptions()` — `node_modules/@tldraw/editor/dist-cjs/index.d.ts:2212`:
  `getTextOptions(): TLTextOptions;`
- `editor.options.maxPages` — `node_modules/@tldraw/editor/dist-cjs/index.d.ts:8190`:
  `readonly maxPages: number;` (and the interface default is documented at line 1069:
  `readonly maxPages: 40;`)
- `createMermaidDiagram`'s `blueprintRender` option —
  `node_modules/@tldraw/mermaid/dist-cjs/index.d.ts:167`: `blueprintRender?:
  BlueprintRenderingOptions;`

Verdict: **AC-4 holds** — all three symbols exist in the installed 5.4.0 type declarations, cited by
symbol and declaration file.

## AC-5 — SKILL.md description trigger delta

`git show origin/main:kc-journey-map/skills/kc-journey-map/SKILL.md` description (before):
> Triggers on "journey map", "user journey", "畫 user journey", "產出 journey 圖", "journey vs
> reality", "現況跟 項目對不對" [sic — actual text: "現況跟 journey 對不對"], "fill the journey
> board", "plan this release", "準備這個 release 開發", or a FigJam/screenshot of a journey board
> handed over to complete.

`git show cfb804d64f1e0ef35862505ee68c26c51c176076:kc-journey-map/skills/kc-journey-map/SKILL.md`
description (after, this PR's head):
> Triggers on "journey map", "user journey", "畫 user journey", "journey vs reality", "fill the
> journey board", "plan this release", "準備這個 release 開發", "sequence companion", or a journey
> board handed over to complete.

Confirmed: `產出 journey 圖` and `現況跟 journey 對不對` are both dropped; `sequence companion` is
added. `gh pr view 440 --json body` was fetched and read in full — it documents validation results
but contains **no mention** of dropping either trigger; the drop is undispositioned in the PR body.

Verdict: **AC-5 fails as written** — the triggers are dropped, and the PR body does not record a
decision to drop them (neither option named in the AC is satisfied).

## Overall

| AC | Result |
|----|--------|
| AC-1 | Fails — pre-existing `lib/records.mjs` declaration-file gap breaks `tsc` at baseline, unrelated to this PR; the falsifier itself (sequence.ts mutation) does work |
| AC-2 | Holds — build succeeds, dynamic import resolves, mutation fails the build, weight reported as a measured range (~1.9–3.4 MB) with method stated |
| AC-3 | Holds — all 13 assertions (not seven) passed against an isolated frontend/API pair |
| AC-4 | Holds — all three symbols confirmed present, cited by declaration file |
| AC-5 | Fails — both triggers dropped, PR body does not disposition the drop |

Worktree left clean at `cfb804d64f1e0ef35862505ee68c26c51c176076` (`git status --short` empty). No
push, no PR write, no CI edit, no npm-script edit made.
