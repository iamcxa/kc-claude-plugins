# Preview: r1 cycle 2, the runbook and read-back, the Slack notice, and the ops record

DISPOSABLE. A sketch of what a person sees, so the re-cut design can be run and looked at before anything is built. It is not the product and not a base for the implementation. It uses relay (`spacedock-dev/subspace-relay`, the dogfood project) with a fictional trigger repository, inbox site and event times; the three ADR reference blocks in the record are real (read-only from relay's clone at origin/main `485306242b80`, probe P5). It calls no network, reads no secret and changes nothing outside this folder.

Needs: node 20 or later. Run from this folder:

    node r1-preview.mjs runbook              # exit 0: the written setup runbook, S1 to S12, owner and exact commands per step
    node r1-preview.mjs readback ok          # exit 0: every read-back row PASS
    node r1-preview.mjs readback waiting     # exit 1: first run, only the Slack row waiting
    node r1-preview.mjs readback failed      # exit 1: a FAIL, an ERROR and the Slack row waiting
    node r1-preview.mjs slack opened         # the Block Kit payload (also: joined, other, refused, retried, uncertain, selftest, escaped, long)
    node r1-preview.mjs record joined        # the ops record in the Draft PR (also: opened, refused)
    node r1-preview.mjs html                 # rewrites slack.html, terminal.html and record.html from the same text

Pictures: `preview-slack.png` (slack.html: nine notices light, five dark, five at phone width, 900 px), `preview-record.png` (record.html: the record as opened, after a joined event, with a refused citation, dark, phone width, 900 px) and `preview-setup.png` (terminal.html: runbook and three read-back runs, 1400 px). Rendered on 2026-10-23, last after the second design review's fixes, with `agent-browser screenshot --full`, the browser CLI the repository's e2e-pipeline uses.

`cycle-1/` holds the attempt-1 previews of the setup command (plan, apply, verify), which amendment 1 withdrew; they are context, not under review.
