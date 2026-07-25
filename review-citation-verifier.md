---
title: Mechanically verify reviewer file:line citations
status: backlog
source: fabricated citations observed from two separate reviewers during PR #56 validation and PR #58 cross-model review, 2026-07-25
started:
completed:
verdict:
worktree:
issue:
pr:
design:
id: dkx7mc8r9rm0zt8x2p0fks58
---

Review discipline already says to check every cited `file:line` against the actual file, and to discard a reviewer's whole round when roughly a third of its citations are wrong. That check is currently done by hand, by an agent, on findings that are themselves persuasive prose — which is exactly the situation where it gets skipped.

It is not hypothetical. During PR #56's validation one reviewer's citations were all accurate, while PR #58's cross-model reviewer reported a P1 citing credential paths that do not appear anywhere in the file it named. Its underlying concern turned out to be real, so the finding was worth keeping — but the citation was invented, and only reading the code revealed which part to trust.

Scope: a deterministic checker that takes findings with `file:line` references and reports, per reviewer round, which citations resolve, which do not, and the resulting error rate — enough for the existing discard rule to be applied on evidence rather than impression. No model in the loop; it is a filesystem check.

## Acceptance criteria

**AC-1 — A round containing a citation to a non-existent path or an out-of-range line is reported as such, with a per-round error rate.**
Verified by: fixtures mixing valid citations, a missing file, and a line past end-of-file; the checker names each and computes the rate. Falsified by: a fabricated citation reported as valid, or a valid one reported as broken.

**AC-2 — The checker cannot be fooled by a citation that resolves but points at unrelated content.**
Verified by: it reports the cited line's actual text so the caller can compare it against the finding's claim (the quote-the-line gate this feeds). Falsified by: reporting only existence, which would let a plausible-but-wrong line number pass.
