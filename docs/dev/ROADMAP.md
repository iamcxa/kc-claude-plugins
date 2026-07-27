# Roadmap — `docs/dev`

Sprint boundaries and sequencing only. This file never tracks task state; that is
`spacedock status --workflow-dir docs/dev`. Owner: captain, or the sprint commander
writing on the captain's direction.

## Sprint 3 — move deterministic work out of the model's context

Opened 2026-07-27, replacing the remainder of Sprint 2 after a cross-model review measured that
sprint against the captain's actual goals and found it did not serve them. Sprint 2's record and
the reason it was cut short are kept below rather than rewritten.

**The goals this sprint is graded on**, stated by the captain: the kit finds more real defects and
fewer false ones; it buys more per token spent; it takes less wall-clock per review; and it is more
agent-native, meaning an agent's claims are checkable or refusable by a mechanism rather than
resting on the agent having followed prose.

**Theme: mechanize what is mechanically decidable at an enforceable boundary, and measure the
quality, cost, and latency of the model work that remains.** Those goals are not mutually
exclusive. Moving a decidable check out of the model serves several at once — it costs no model
tokens and its output is not authored by the agent under review — but two conditions decide
whether that holds, and both are earned rather than assumed:

- **"Not agent-authored" depends on what the check inspects, not on it being a script.** Proof
  Policy #1 already says this: a script run over a self-written artifact is a self-issued stamp.
- **A check is only unskippable once a runtime boundary refuses its absence.** A grep written into
  prose is as skippable as the prose. That refusal is exactly what `2t` builds, which is why it
  gates `1c`.

Pure subtraction — spending fewer tokens by reading less — is the one approach where these goals
genuinely fight, and it is deliberately not the theme. Note also that not every item here is
mechanization: `62` and `qe` measure the model work rather than removing it, and `zn` repairs
orchestration. The theme names the direction, not a property every slice shares.

### Sequence

| # | id | slug | why it sits here |
|---|----|------|------------------|
| 1 | `zn` **item 1 only** | review-kit-live-run-corrections | Its first item is the only thing in this sprint arriving with a measurement: `SKILL.md:405-413` prescribes a `codex exec` mode whose output file stays 0 bytes for the whole run, so an in-flight dispatch reads as a failed one, and one live occurrence bought a duplicate ~140K-token review. Probed here: `--json` grows within 4s, plain writes 59 bytes at the end. Items 2 and 3 are prose corrections with no measurement — ideation splits or timeboxes them rather than carrying them along. |
| 2 | `qe` | benchmark-full-rerun-control | The token denominator. Its body says it "should land before any work that claims a token win", and `62` depends on it for the cost half of the comparison. Dropping it from the first recut was an oversight. |
| 3 | `62` | review-effectiveness-benchmark | The quality numerator, scoped as a **pilot**: pre-registered known defects on a frozen corpus, comparing two configurations that already exist. Every slice after it claims an improvement nobody can currently compute. |
| 4 | `2t` | prescan-coverage-honesty | Eleven pre-scans cannot distinguish "ran, found nothing" from "skipped". It builds the runtime refusal that makes a check unskippable, and owns the coverage representation `1c` must fill — so it gates `1c`. |
| 5 | `1c` | prescan-script-evidence | The cleanest four-goal item in the backlog: three mechanically decidable pre-scans stop needing a model, and their evidence can contradict the agent's own prose. |

**Stretch**

- `x0r` (`mock-boundary-contract-prescan`), **as a bounded fixture spike first**. It targets a real
  defect class that survived a green 5600-test suite, `mypy`, `ruff`, and a passing mutation round.
  But calling it "pure grep, zero tokens" overstates it, and its own entity says why: the detector
  is not independently validated (`:53`), it is Python-shaped with TypeScript scope unresolved
  (`:76`), and it carries a model-based companion check for the cases grep cannot reach (`:70`).
  Prove a Python-only detector catches the recorded defect without noisy findings; schedule the
  generalized version only after that.
- `v5` (`learned-pattern-selection`), and only once `qe` and `62` exist. It is pure subtraction,
  its token win is currently unmeasurable, and the cost breakdown suggests it is second-order
  regardless — fan-out dominates (~140K for the 3-agent minimum tier, ~200K Standard, ~240K Full,
  +35K pre-scan, +50–80K optional Codex), so a 1193-line corpus is not where the budget goes.

### Moved out of this sprint: once-only posting reliability

`n9` (`gh-list-adapter-pagination`) then `11` (`reconcile-list-element-shape`) — **in that order**,
which reverses Sprint 2. They belong to a separate once-only reliability track and should not be
counted as review-quality work: neither serves any of the four goals, and presenting them as if
they did would be false. Within their own track `n9` outranks `11`, because `n9` breaks the
shipped `gh` adapter on any ordinary busy PR while `11` is reachable only through a custom
transport, a body-rewriting proxy, or a future adapter. Sprint 2 had them backwards because it
preferred the fix whose shape was already pinned over the one with impact.

### Sequencing constraint, unchanged

`SKILL.md` remains contended: `zn`, `2t`, `1c`, `x0r`, `v5`, `q0`, `3w` all edit it, so they run
serially regardless of value. `62` is the exception — it adds a benchmark rather than editing the
skill, so it is the one item here that can genuinely run in parallel, and the natural candidate if
a second worker or a mini leg is available.

### Next tranche, not this sprint

`q0` (`reviewer-return-contract`) then `dk` (`review-citation-verifier`). `q0` gives reviewer
returns a contract the orchestrator can reject instead of best-effort prose; `dk` mechanically
verifies cited `file:line`, which needs `q0`'s structure to check against. `3w`
(`learned-pattern-append-bound`) follows `v5`.

### What Sprint 2 was, and why it was cut after one slice

Sprint 2 opened 2026-07-26 as "finish the once-only path, then open pre-scan honesty", sequenced
`qh` → `11` → `n9` → `2t`. **`qh` shipped** (#67, `f7dd1a0`): python3 spawns per `post` 65 → 9, CI
job 488s at 139 assertions against main's 512–598s at 137.

Then the captain named the four goals above and asked whether the sprint served them. A
cross-model review found it barely did: `11` and `n9` serve none of the four, `2t` serves two of
them partially, and the only clear token item was stretch work. It also observed that the sprint's
order came from same-file contention rather than goal value — collisions are a real constraint on
*how* work runs serially, but they are not an argument for *which* work runs first, and Sprint 2
let the constraint choose.

Two harder findings are recorded because they cost something to learn:

- **`qh`'s own ledger row is the warning.** 6 dispatches, 33 hours, ~1M tokens, and the outcome is
  a CI job number — not a measured reduction in any review's duration. Optimisation effort
  outrunning user value, and it cleared a full gate because nothing measures the thing it claimed
  to improve. That is why `62` sits second here and is not deferred again.
- **The kit's failure mode is accretion.** It keeps adding mechanisms to prove its elaborate prose
  workflow ran, instead of replacing prose and model work with a smaller executable core. The
  duplicate-dispatch incident behind `zn` is the tell: the orchestration was complex enough to buy
  the same 140K-token review twice by accident. This sprint's theme is chosen against that
  gradient, but does not resolve it — see below.

### The open question this sprint does not answer

The cross-model review argued the credible end state is a simplified default path —
`deterministic preflight → one structured reviewer → evidence/citation verifier → conditional
specialists only when the diff earns them → human confirmation` — with the full kit used less
rather than improved more. That is captain-owned scope and is deliberately not decided here.

This sprint is compatible with either answer: `1c` and `x0r` build the deterministic preflight a
leaner path would need, and `62` builds the instrument that would let a leaner path be compared to
the current one on evidence instead of argument. If the answer is "simplify", none of this is
wasted; if it is "keep and improve", the same work applies.

### Hazard carried forward

`spacedock status --ac-scan`'s citation counter is not trustworthy — an AC citing three paths
scored `0` while one citing a single path scored `2`. The README makes that scan a hard
precondition for the ideation gate, so `2t` will hit it. The captain deferred the spacedock-side
fix; until then record the scan output and the discrepancy in the stage report rather than treating
a `0` as a finding about the AC.
