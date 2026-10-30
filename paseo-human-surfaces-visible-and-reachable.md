---
title: Inside Paseo, FO and workers open human-facing terminals and browser tabs in the Captain's visible workspace, reachable from his other devices
variant: kc-dev-flow-2
profile: pilot
merge: pr
status: ideation
gates:
    version: 1
    records:
        - id: gate:paseo-human-surfaces-visible-and-reachable:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:paseo-human-surfaces-visible-and-reachable-backlog-1
              briefing:
                id: briefing:paseo-human-surfaces-visible-and-reachable:backlog:attempt-1:revision-1
                digest: sha256:5f8a004229033ecfce7006217bc74aaf2c68502e2820bb61779448b089b1d8a8
                room-ref: ./paseo-human-surfaces-visible-and-reachable/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:paseo-human-surfaces-visible-and-reachable:backlog:1
                briefing: briefing:paseo-human-surfaces-visible-and-reachable:backlog:attempt-1:revision-1
                by: person:captain
                at: "2026-10-30T08:18:43.308083Z"
                decision: approve
                reason: The Captain 「對，全准且全確認」 (chat, 2026-10-30), answering FO's joint batch-11 backlog sitting of six gates whose ask was 「決定：六張全准進設計，並確認上面三件事？要改哪張直接說。」; accepts FO's recommendation and the confirmations stated in the gate question.
              application:
                target-stage: ideation
                state: consumed
---

## Scope

- Source: the subspace-relay dev2 FO (Paseo 1671c3a9) relayed the Captain's words of 2026-10-28: 「你這次有幾次終端機開錯在不同路徑，這個是否應該給dev2 fo提報讓它改進paseo ext機制？這裡其實有個改進點，只要在paseo環境內，應該盡可能在它裡面開browser + 終端機，且注意應該要確保跨裝置可用，例如你開localhost時我在手機上就不可用，因為開的不是手雞的localhost，一個可能的解決方案是現在的tailscale但是可能不夠通用，但這個沒關係讓dev2煩惱就好」. Relayed words are not a ruling until the Captain confirms them in this session.
- Bite: relay rr-pairs-once validation trials on staging, 2026-10-28 (relay state branch spacedock-state/dev2, task rr-pairs-once, validation-1/trials/ and dispatch/validation-1.md): a Codex trial worker's Paseo terminal opened with cwd /tmp/rr-sheet-worker and the Captain could not see it from his workspace; the live pairing request was cancelled and recreated (one request, about 2 minutes); trial scripts ran in a terminal he had to choose and browser steps opened in the macOS default browser, not a Paseo tab. Cross-device (a localhost page unusable from his phone) was raised, not yet hit.
- Upstream first: `extensions/paseo/EXTENSION.md` and the open paseo-codex-dispatch-practice change (#742, worker placement in its worktree); Paseo's own `paseo` skill and docs for terminals, browser tabs and workspaces; Tailscale only as the Captain's named candidate, read from its own docs.

## Non-goals

- Changing Paseo itself; product-specific routes (relay's code route for phones stays relay's).
- Exposing local servers beyond the Captain's own devices.

## Budget

- One package PR to the paseo extension; no new script unless the design shows a check is needed.

## Stop condition

- The rr-pairs-once trial replays with the terminal visible in the Captain's workspace and the browser step in a Paseo tab; return to the Captain if cross-device reach needs a network choice (such as Tailscale) the package cannot make generally.

## FO alignment

Alignment: needed before ideation; the cross-device approach is the Captain's.
Result: aligned at backlog: the Captain 「對，全准且全確認」 (chat, 2026-10-30) to FO's batch-11 backlog sitting, which asked 「決定：六張全准進設計，並確認上面三件事？要改哪張直接說。」, approved the outcome and bounds in this file. He confirmed the words the relay FO relayed. The cross-device approach stays his: ideation returns it as a decision at the ideation gate.
Surfaces: none
Visible change: none
Release review: not needed: workflow maintenance, on no journey map.
