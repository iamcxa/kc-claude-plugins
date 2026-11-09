---
title: Which delivery makes a dispatched worker read and apply a domain note unprompted (POC comparing A, B and C)
variant: kc-dev-flow-2
profile: poc
merge: pr
status: backlog
---

## Scope

- Source: the Captain 「開 POC 任務，比較 A、B、C」 (chat, 2026-11-09), answering 「請 kc-claude-plugins 的 dev2 FO 開一個 dev2-poc 任務，比較 A、B、C 三個版本嗎？」, relayed by Paseo agent 2d26599b (relayed, not a ruling here; the backlog gate confirms it). Adopter: the Captain 「relay 可以」 (same relay).
- Story: docs/journey/kc-dev-flow-2/journey.yaml S01 (merged in #792, 6dab84e2a); its q1 and q2 hold his rulings on where domain lessons live and 「落後就停下來等我」.
- Riskiest assumption: a dispatched worker, not told to, reads the relevant domain note and applies it. A domain note is a lesson true across repositories of one kind (for example Netlify), in learning.md's Applicability/Practice/Evidence shape.
- Variants, same task and trap for each:
  - A: a byte-identical copy committed in the adopter at docs/domain/netlify.md, plus one AGENTS.md line pointing at docs/domain/, kept fresh by a copy check in the shape of scripts/kc-adr-copy-sync.sh check.
  - B (the Captain's idea): before each dispatch FO clones or pulls the source into a gitignored docs/domain/ inside the worker's worktree and records the source commit in the dispatch record; also checks that the Codex sandbox can read it and that it is present in a fresh worktree.
  - C (control, upper bound): FO puts each applicable entry as a checklist line in the dispatch.
- Candidate trap (relayed): spacedock-dev/subspace-relay root learning.md's entry on Netlify dev, where the request client and the browser can reach different proxy hops or IP families.
- Measure: run on Codex (roster Sol/Astra) and Claude, repeated, counting read and applied, as the kc-adr read-and-route POC counted (relayed: Claude 6/10 to 9/10, Codex 5-6/10).
- Fact relayed by 2d26599b, not re-run here: a git submodule had 0 files in a fresh `git worktree add` and in a plain clone (git 2.54.0, 2026-11-06), so a submodule is out for A and B. Relay, web and v0 have AGENTS.md and no CLAUDE.md on main.
- Non-goals: choosing a winner or changing q2; if B wins, q2 becomes "stop when the update fails", which needs a new Captain ruling after the POC. Hold frequency belongs to a later slice.

## Budget
- One measurement with its harness and report; no package or adopter change ships from this task.

## Stop condition
- Each variant's read and applied counts per host are reported with their run records, and the report states which variants the result supports, without choosing.

## FO alignment

Alignment: needed at backlog: the trap, the run count per cell and where the harness lives are his to accept.
Surfaces: none
Visible change: none
Release review: not needed: story S01's journey has no release yet.
