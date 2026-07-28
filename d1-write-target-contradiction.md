---
title: Two documents disagree on where D1 patterns are written, and the public corpus is the symptom
status: backlog
source: found by cross-model review of a sprint draft, 2026-07-27; verified against both files
design:
id: kjssc8rgcjt7jd81qg39zeqb
---

`kc-pr-review` Step 8 and its own reference document give opposite instructions about where
learned patterns go.

| Source | Instruction |
|---|---|
| `SKILL.md:1870` | "**D1 auto-append** — skill-level patterns are appended to `learned-patterns.md` without gate" |
| `knowledge-capture.md:5` | "Dimension 1: Skill-Level (auto-append to **LOCAL**, no gate)" |
| `knowledge-capture.md:7` | "Auto-appended to the per-user **LOCAL** store — **NOT directly to the public plugin reference file**" |
| `knowledge-capture.md:22` | "**Write mode**: Auto-append to LOCAL only… Run `/kc-plugin-forge dreaming kc-pr-flow` to promote to public when ready" |

`kc-pr-flow/reference/learned-patterns.md` **is** the public plugin reference file. So SKILL.md
directs writes to exactly the destination knowledge-capture.md forbids, and SKILL.md is the one
the review actually follows.

## Why this matters beyond being a doc bug

`learned-patterns.md` is 1193 lines and 104 entries, read on every non-trivial review. Two
entities exist to deal with that growth: `learned-pattern-selection` (v5) proposes reading less of
it, and `learned-pattern-append-bound` (3w) proposes bounding the writes.

**Both may be treating a symptom.** If the LOCAL-then-promote design is the intended one, the
public corpus was never supposed to grow unbounded — it grows because a contradicting instruction
won, and every review has been appending straight past the `dreaming` promotion gate that exists
to curate it. That would make the corpus's size an accident rather than a design pressure, and it
changes what `v5` and `3w` are for.

It would also mean entries have been landing in a **public marketplace plugin** without passing
the promotion step that reviews them — worth checking against `kc-plugin-forge`'s sanitize
discipline, since that gate exists partly to keep per-user material out of published files.

Note one further inconsistency inside `knowledge-capture.md` itself: `:112` says "D1: auto-append
via Edit… — no commit needed (plugin repo)", which points at the plugin repo rather than a LOCAL
store, so the reference is not internally uniform either.

## What this entity must decide first

Which instruction is correct. That is a design question, not a defect triage: LOCAL-then-promote
gives curation and keeps the public file small; direct-append gives immediate cross-project reuse
and is what every existing entry assumed. The 104 entries already in the file were written under
the direct-append reading, so choosing LOCAL implies deciding what happens to them.

**AC-1 — One documented destination for D1 writes, and the other document agrees with it.**
Verified by: SKILL.md Step 8, `knowledge-capture.md`, and the `kc-pr-flow/CLAUDE.md` reference index all naming the same target, plus a stated disposition for the 104 existing entries. Falsified by: any remaining path that says LOCAL where another says the plugin reference, or a decision recorded without saying what happens to what is already there.
