# DEV-95 mechanical items — accept runs (FO, laptop)

## AC-4 round 3 (`4f7f0ebd`) — REFUSED; outcome `change`, returned to planning

The accept station on main said ACCEPT. The FO's S29 guard says otherwise, and this is S29's exact shape a second time: the without-it command invokes the checker, which does not exist at `BASE_SHA`, so the base run exits **127** — the command did not run, nothing flipped — and the command reads `/home/vercel-sandbox/.claude/...`, outside the tree (on the FO's machine it exits 2). The pair is unfalsifiable and the station let it through. Hardening dispatched as `dev94-ac2.g3`.

The finding that matters is AC-2: **the real checker (92 six-word windows against the pm-skills install, 307 headings and bold labels derived at run time) exits 0 on the state-branch ORIGINAL of stations 3–4.** The Brief's stop clause was "if it exits 0 on the original, stop and report that in BLOCKER"; the worker wrote `BLOCKER: none` and continued. Read as a result rather than as conduct: the Codex round-7 claim that stations 3–4 were "pm-skills templates with the words changed" is a judgment about field structure and paraphrase, and it is **not decidable by verbatim n-grams or heading-term matching**. A checker that passes both the original and the rewrite certifies nothing about either. Three repair rounds spent; no PR.

Delta for planning: DEV-95 AC-4's acceptance test ("grep over the pm-skills install") is the wrong instrument. Either the licence question is answered by a human or Codex read with the two texts side by side, or the test changes to something that can distinguish the original from the rewrite. The rewritten `docs/plan-flow/dialectic.md` itself (station 0, refusal seam before station 1, by-product question, borrowed skills as checklist) may still be wanted on its own merits — the Captain decides at UAT whether to land it without a mechanical licence check.

## AC-3/6/7 round 1 (`405c7309` pushed) — no Evidence block emitted

The branch exists with a commit; the transcript's only `## Evidence` is the template from the dispatch. See the transcript tail in this directory's notes before deciding re-send vs redispatch (S17: a usage-limit banner means keep the workspace and re-send after reset).
