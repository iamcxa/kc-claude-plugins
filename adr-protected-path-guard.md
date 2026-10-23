---
title: An agent that edits a file an accepted ADR protects is shown that ADR at the moment of the edit
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: backlog
gates:
    version: 1
    records:
        - id: gate:adr-protected-path-guard:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:adr-protected-path-guard-backlog-1
              briefing:
                id: briefing:adr-protected-path-guard:backlog:attempt-1:revision-1
                digest: sha256:7a78134a35d63f1efe239a12082a435681ded25af41ef62885cf060ab7f27e44
                room-ref: ./adr-protected-path-guard/review/backlog/briefing-1
              withdrawal:
                by: agent:first-officer
                at: "2026-10-23T08:25:36.682526Z"
                reason: 'Captain 「可以，先測試這個，然後再考慮其他方案。」 (2026-10-23) to FO''s 「要撤回這道關卡、改開註解 POC 嗎？」: a code-side ADR comment POC runs first; this item waits for its result and for the other options he named.'
---

## Scope

- Source: the Captain 「開」 (chat, 2026-10-23), answering FO's 「現在要決定的：要不要開一個 pilot 任務，做 ADR 路徑檢查？ 我建議開。」, which described: an optional ADR field naming the code paths it protects, a script listing which protected paths a change touches and their ADRs, a reminder at edit time, and acceptance by re-running the same scenario with and without the guard.
- Bite: dev2-poc `adr-hidden-reason-poc` (archived 2026-10-23): with the protecting ADR present, 2 of 8 refactor runs undid a choice only that ADR explains; both never read it, and both edited the protected file (`src/report_mailer.js`); the 6 runs that read it kept the choice; kc-adr showed no effect (Claude never invoked the skill). The no-ADR control undid it 4 of 4.
- Upstream first: spacedock 0.27 and kc-dev-flow-2 0.28.0 have no ADR-to-code-path mapping (`adr-path:` is only the ADR directory; grep 2026-10-23). Sibling adopters (carlove, subspace-relay) not yet checked; ideation checks them. Harness to reuse: `_archive/adr-hidden-reason-poc/harness/` (S14) in the `spacedock-state/dev2-poc` checkout.
- Ships in kc-adr: the optional field in `kc-adr/references/adr-template.md` and `adr_lint.py` acceptance of it, a checker script, and the edit-time reminder. Whether Codex can run an edit-time reminder is to be verified at ideation, not assumed.
- Non-goals: back-filling the field into existing ADRs; changing kc-dev-flow-2's copies (owned by `kc-adr-tools-with-dev2-copy`); a CI-only check with no edit-time reminder.

## Acceptance criteria

**AC-1**: Given an accepted ADR that names protected paths, the checker lists every changed file matching them with the ADR's number and title, and lists nothing for a change outside them; tests pin both, and `adr_lint.py` still passes every existing ADR without the field.
**AC-2**: On Claude Code, an edit to a protected file shows the agent that ADR's number, title and path before it continues; an edit elsewhere shows nothing. Shown by a recorded run, not by reading the hook.
**AC-3**: Re-running S14 with the guard on, pass rule unchanged from the archived harness, gives fewer undone choices than the archived A0 cells, on the run count approved at ideation; the report states the counts and limits.

## FO alignment

Alignment: needed at ideation: the field name, where the reminder runs, Codex support and the AC-3 run count are design choices for the Captain.
Surfaces: none
Visible change: none
Release review: not needed: the map was skipped for kc-adr by the Captain's authorization.
