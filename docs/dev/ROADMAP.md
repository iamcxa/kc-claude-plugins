# Roadmap — `docs/dev`

Sprint boundaries and sequencing only. This file never tracks task state; that is
`spacedock status --workflow-dir docs/dev`. Owner: captain, or the sprint commander
writing on the captain's direction.

## Sprint 2 — finish the once-only path, then open pre-scan honesty

Opened 2026-07-26, immediately after `sv` (`reconcile-degraded-mode-symmetry`) merged as
PR #63 and recorded its ledger row.

**Theme.** `sv` made `post` and `resume` agree on a degraded reconcile read, and in doing so
exposed the rest of the once-only path: a pagination defect that makes the feature unusable
on a busy PR, and a validator weak enough to bound the guarantee `sv` just shipped. This
sprint closes those, pays down the test-loop tax that made `sv` expensive, then opens the
largest honesty gap in the review kit.

Scope is the **kc-pr-flow track only**. The `e2e-*` entities (`gz`, `rd`, `3t`) are driven
by a separate session and are deliberately untouched here.

### Sequence

| # | id | slug | status | why it sits here |
|---|----|------|--------|------------------|
| 1 | `qh` | review-post-suite-cost | **done** (#67, `f7dd1a0`) | Held both contended files. 65 → 9 spawns; CI job 488s at 139 assertions against main's 512–598s at 137. |
| 2 | `11` | reconcile-list-element-shape | next | The named residual bounding `sv`'s shipped guarantee; fix already pinned to one shape. |
| 3 | `n9` | gh-list-adapter-pagination | | Once-only posting is unusable on any PR whose reviews list paginates. |
| 4 | `2t` | prescan-coverage-honesty | | Main course: eleven pre-scans that cannot distinguish "ran, found nothing" from "skipped". |

Stretch, only if appetite survives the first four: `v5` (`learned-pattern-selection`) — the
natural successor to `2t`, same file, next section, and the one backlog item that gets
strictly worse on its own. Deferring costs time; starting it with no budget left costs a
half-finished edit to an 1884-line skill.

### Why this order — two contended files, not four independent tasks

Sequencing here is dominated by same-file collisions, not by dependency arrows. Two files
are contended by most of the backlog:

- **`kc-pr-flow/scripts/review-post.sh`** — `qh`, `11`, `n9`, and later `vf`, `x0f`, `7j`.
- **`kc-pr-flow/skills/kc-pr-review/SKILL.md`** — `2t` (Step 4.5, `:468-728`), `v5` (Step 8,
  `:1834`), `q0` (Step 4-Codex `:409`/`:413` and Step 5.5 `:794`), `1c` (Step 4.5), `3w`
  (Step 8 D1).

`qh` is the only entity touching **both** contended surfaces, verified by grep rather than
inferred from its body: six `python3` call sites in `kc-pr-flow/scripts/review-runtime.sh`
and two in `kc-pr-flow/scripts/review-post.sh` (`:53`, `:69`). `2t` touches
`review-runtime.sh` as well — its capability-policy assertions live at `:1979` and `:2073`.
Scheduled late, `qh` waits for every other slice to clear both files; scheduled first, it
clears the way and makes each following slice's test loop cheaper. Its evidence is measured,
not argued: `python3` costs 565 ms per launch on this machine at 0% CPU, and one `post`
spawns 65 of them.

`11` before `n9`: `11`'s fix is already pinned to one shape
(`all(.reviews[]; type == "object")`), while `n9` must still decide how a multi-page adapter
composes. Cheapest known-shape work first, inside the same file visit.

`2t` last of the four because it opens the `SKILL.md` line that the next sprint continues.

### Defect-lane determination

Under the README's four conditions, **none of these four qualifies for the lane**; all take
the main line through `ideation`.

- `qh` — fails condition 4. Its own body lists four candidate fixes (long-lived helper
  process, shell date math, batched safe-I/O, parallel-by-suite CI matrix). Four defensible
  shapes is the textbook exclusion.
- `n9` — fails condition 4. No fix mechanism is chosen yet.
- `11` — fails condition 3. The fix changes both `post` and `resume`, so it is not a single
  seam even though its shape is settled.
- `2t` — fails conditions 3 and 4, and edits a closed schema.

### Appetite

Four slices, one implementation session each. `qh` and `2t` are the two that can overrun —
`qh` because ideation must pick one of its four candidates rather than try them all, `2t`
because it edits a closed schema. On overrun, cut rather than extend: `qh` falls back to the
parallel-by-suite CI matrix it already names, and `2t` defers the evidence payload `1c` is
expected to fill.

### Not in this sprint, on purpose

- **`q0` (reviewer-return-contract)** — must inherit `2t`'s representation instead of
  inventing a second one, and it edits `SKILL.md` too (`:409`, `:413`, `:794`), so it cannot
  overlap `2t` or `v5`. Its own body says to cut it after `2t` lands. Precondition for `dk`.
- **`vf` / `x0f` (daemon preauthorization)** — still coupled to a caller whose shape the
  captain has not settled (`4p` is parked; the two directions on record are `spacedock claude`
  and a self-built SD+ACP harness). The caller-agnostic part of `vf` already shipped as `sv`.
- **`1c`, `3w`** — downstream of `2t` and `v5`; scheduling them now means designing against a
  representation that does not exist yet.
- **`fn`, `24`, `qe`, `c3`, `w1`, `7j`, `dk`** — no forcing function this sprint. `w1` (dead
  audit link under split-root) is the cheapest and the best candidate for any gap.

### Filed mid-sprint, not scheduled into it

Two entities arrived from maintainer feedback on a live `kc-pr-review` run (kc-pr-flow 1.9.1)
after this sprint opened. Both edit `SKILL.md`, so both sit on the contended line above and
cannot overlap `2t`.

- **`zn` (review-kit-live-run-corrections)** — three prose fixes to one file. Its first item is
  worth ~140K tokens per occurrence: `SKILL.md:405-413` prescribes plain `codex exec`, whose
  output file is genuinely 0 bytes for the whole run, so an in-flight dispatch reads as a failed
  one. Measured here: `--json` grows within four seconds (405 → 22474 bytes) where plain sits at
  0 and writes 59 bytes at the end. That makes the fix an invocation change, not a note.
- **`x0r` (mock-boundary-contract-prescan)** — the fourth cell of the §4.5 consistency matrix:
  nothing checks a test's stub against the collaborator it replaces. Must follow `2t`, which
  owns the coverage representation a twelfth pre-scan has to fill.

`4n` (absolute-claims-need-an-enforcement-point) also arrived and closed inside the sprint: its
rule shipped as Proof Policy #6, and the captain declined the optional diff-time lint.

### Hazard carried in from the last sprint

`spacedock status --ac-scan`'s citation counter is not trustworthy — an AC citing three paths
scored `0` while one citing a single path scored `2`. The README makes that scan a hard
precondition for the ideation gate, so `2t` will hit it. The captain deferred the
spacedock-side fix; until then record the scan output and the discrepancy in the stage report
rather than treating a `0` as a finding about the AC.
