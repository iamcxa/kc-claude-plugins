---
title: An ADR that protects code names its files, each file carries a pointer back to it, and the linter keeps both true
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
            - id: gate-attempt:adr-protected-path-guard-backlog-2
              briefing:
                id: briefing:adr-protected-path-guard:backlog:attempt-2:revision-1
                digest: sha256:90b15d5f7a18f5f619085d7b7105f1b4f755897d4defd61648195ba8e2bb1280
                room-ref: ./adr-protected-path-guard/review/backlog/briefing-2
---

## Scope

- Source: the Captain 「開」 (chat, 2026-10-23) to FO's 「現在要決定的：要不要開一個 pilot 任務，做 ADR 路徑檢查？ 我建議開。」; then 「可以，先測試這個，然後再考慮其他方案。」 (backlog gate withdrawn for a code-side comment POC); then 「可以。」 (chat, 2026-10-23) to FO's 「你要決定的：要不要把 `adr-protected-path-guard` 改成這個範圍，再重新開它的 backlog 關卡？」, where "this scope" was: an optional ADR template field listing the files it protects; a `writing.md` rule to add a one-line `see docs/adr/NNNN-…md` pointer at each such site; a linter check that each listed file exists and carries the pointer, and that no code still points at a superseded ADR; no hook.
- Bite: dev2-poc `adr-hidden-reason-poc` (archived 2026-10-23): with the protecting ADR present, 2 of 8 refactor runs undid a choice only that ADR explains, both without reading it; control without the ADR 4 of 4. dev2-poc `adr-code-pointer-poc` (archived 2026-10-23): with one pointer comment at the site, 0 of 4 undone and 4 of 4 opened the ADR; in both Claude runs the trace shows the comment was the route to the ADR (a tie with 1 of 4 at this size, not shown to lower the rate).
- Upstream first: spacedock 0.27 and kc-dev-flow-2 0.28.0 have no ADR-to-code mapping (`adr-path:` is only the ADR directory; grep 2026-10-23); sibling adopters (carlove, subspace-relay) are checked at ideation.
- Ships in kc-adr: the optional field in `kc-adr/references/adr-template.md`, the pointer rule in `kc-adr/skills/read-adr/writing.md`, and the two checks in `kc-adr/scripts/adr_lint.py`, with tests.
- Non-goals: an edit-time hook; back-filling the field or pointers into existing ADRs; changing kc-dev-flow-2's copies (owned by `kc-adr-tools-with-dev2-copy`).

## Acceptance criteria

**AC-1**: An accepted ADR may list the files it protects; `adr_lint.py` fails when a listed file is missing or lacks a pointer to that ADR, and passes every existing ADR that has no list.
Verified by: linter tests for a missing file, a missing pointer and a correct pointer, plus a run over the repository's existing ADRs, exit 0.

**AC-2**: `adr_lint.py` fails when code points at an ADR whose Status is `Superseded by NNNN`, naming the file and the newer ADR.
Verified by: a linter test with a superseded ADR and a file still pointing at it, and a falsifier that removes the check and sees the test fail.

**AC-3**: `writing.md` tells a writer whose ADR protects code to list the files and add the pointer at each site, and an agent writing such an ADR does both.
Verified by: a text check of `writing.md`, and one recorded agent run per host (Claude, Codex) in a fictional repo that writes an ADR protecting a named file and passes the linter.

## FO alignment

Alignment: needed at ideation: the field name, the pointer format and how the linter finds pointers are design choices for the Captain.
Surfaces: none
Visible change: none
Release review: not needed: the map was skipped for kc-adr by the Captain's authorization.
