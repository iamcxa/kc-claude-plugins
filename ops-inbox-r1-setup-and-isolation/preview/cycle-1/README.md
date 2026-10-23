# Preview: the ops-inbox setup command and the Slack notice

DISPOSABLE. A sketch of the proposed output so the design can be run and looked at before anything is built. It is not the product and not a base for the implementation. It uses a fictional project (`example-owner/mira-shop`), calls no network, reads no secret and changes nothing outside this folder.

Needs: node 20 or later. Run from this folder:

    node setup-preview.mjs plan               # exit 0: every step, who does it, the exact command
    node setup-preview.mjs apply noyes        # exit 2: without --yes apply only lists what it would run
    node setup-preview.mjs apply first        # exit 1: one agent step failed, one waits on a Captain step
    node setup-preview.mjs apply rerun        # exit 0: rerun changes only what differs
    node setup-preview.mjs verify ok          # exit 0: every step read back
    node setup-preview.mjs verify failed      # exit 1: a FAIL, an ERROR and the Slack step waiting
    node setup-preview.mjs verify waiting     # exit 1: only the Slack step waiting
    node setup-preview.mjs slack started      # the Slack payload (also: refused, retried, uncertain, selftest, long, sentry, longtext, nofields)
    node setup-preview.mjs html               # rewrites slack.html and terminal.html from the same text

Pictures: `preview-slack.png` (slack.html: nine notice states in light, four in dark, four at phone width) and `preview-setup.png` (terminal.html: plan, three apply runs, three verify runs). Both were rendered on 2026-10-23, after the second design review's cheap fixes, with `agent-browser screenshot --full` (the browser CLI the repository's e2e-pipeline uses), at 900 px and 1400 px wide. The Slack pictures are a local mock of Slack's look; Slack draws the real message from the Block Kit payload `slack <state>` prints.
