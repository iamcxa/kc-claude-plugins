---
title: An agent reads the governing ADR at the moment it decides, from a pointer and an injected title list it cannot miss
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:agent-reads-governing-adr:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:agent-reads-governing-adr-backlog-1
              briefing:
                id: briefing:agent-reads-governing-adr:backlog:attempt-1:revision-1
                digest: sha256:4555cfe2d87c5df9e402e1068a17b3198b7ff83581d292254a521244ec91a858
                room-ref: ./agent-reads-governing-adr/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:agent-reads-governing-adr:backlog:1
                briefing: briefing:agent-reads-governing-adr:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-21T07:28:59.894802Z"
                decision: approve
                reason: Captain 「繼續」 (chat, 2026-10-21), answering FO's question 「這 5 張都批准進入設計嗎？」 for the five batch-5 backlog gates presented together; approves entering ideation under the pilot profile, as recommended.
              application:
                target-stage: ideation
                state: pending
---

## Scope

- Source: finding relayed by the decision-log Paseo session (agent 1bcf070c, 2026-10-20), compared against "The ADR your agent never read" (https://tianpan.co/blog/2026/07/02/the-adr-your-agent-never-read). Captain ruling in this session: 「ADR 部分按你說的做」 (2026-10-20), approving FO's proposal 「在 dev2 開一張待辦任務，不開 GitHub issue。做法照你說的，從各 repo 這一層下手」: an instruction-file pointer to `docs/adr`; a hook that lists every ADR title at session start or dispatch, derived from the files so it cannot go stale; a check that the ADR paths AGENTS.md and CLAUDE.md name resolve; this repository and qnow first; a package rule only after the effect is measured.
- Bite, read 2026-10-20: qnow origin/next AGENTS.md lines 24-27 point agents at branch `docs/qnow-target-architecture-adr`, which `git ls-remote` does not find, while `docs/adr/0001-qnow-target-architecture.md` exists on `next` at 165414 bytes (handed to the qnow FO the same day); kc-claude-plugins origin/main CLAUDE.md and AGENTS.md mention ADR 0 times.
- Present in kc-dev-flow-2 0.26.0 (per the relayed finding, to re-read at ideation): verbatim Words/Options/Recommended, FO decision records, ideation reads ADRs in its area, the Precedent rule, comments cite ADRs, `adr_lint.py` checks a Superseded-by target exists. Missing: the implementation worker is not told to read ADRs; no way to find the ADRs "in its area"; validation checks format, not contradiction; no staleness audit or size limit.
- Upstream first: Spacedock and kc-dev-flow-2 hooks and dispatch; ADR 0003 (adopter-owned hooks); the kc-decision-log CLI (PR #681, planning) may later serve as the find-and-read tool; merge-guard-stops-unasked-merges also adds adopter hooks, so the two designs share a hook layout.
- Non-goals: splitting qnow's 165 KB ADR 0001 (qnow's call); contradiction checking at validation unless measurement shows the pointer and list are not enough.

## FO alignment

Alignment: needed at ideation; which adopters and which hook moment are his to accept.
Surfaces: none
Visible change: none
Outside this repository's surfaces: each first adopter's AGENTS.md or CLAUDE.md and its user- or repo-level hook files (this repository and qnow).
