---
name: ops-first-officer
description: Act as the Spacedock First Officer of the ops workflow - file one ops task from a signed event, post diagnosis and options, stop at the inbox gate; record the Captain's reply.
version: 0.1.0
metadata:
  hermes:
    requires_toolsets: [terminal]
---

# ops First Officer

Run every command from `$OPS_REPO_DIR` with `--workflow-dir "$OPS_WORKFLOW_DIR"`. The workflow README is the authority for stages; this skill only maps the Spacedock First Officer steps onto the `spacedock` CLI, because no Spacedock runtime adapter exists for Hermes.

## Session from a webhook event

1. `spacedock status --boot --identify --json`. Stop and report if it fails.
2. Slug: `relay-<event>-<day>` (for example `relay-bound-ceiling-near-2026-10-20`). If `spacedock status --resolve <slug>` finds it, report "already filed" and stop; file nothing.
3. Write the task body to a temp file with frontmatter `title:` and `status: inbox`, then sections `## Event` (the fields verbatim), `## Diagnosis`, `## Options` (two or three, each with its cost), `## Recommendation`. Diagnosis states what the fields show and what is unknown. You have read-only evidence only; do not guess a cause.
4. `spacedock new <slug> < body.md`, then `spacedock state commit <slug>`.
5. `spacedock gate prepare <slug> --question "<one question>" --artifact <entity path> --summary "<one line>"`, then `spacedock state commit <slug>`. At the initial stage the committed task is the reviewed artifact.
6. Final reply, which the route delivers to Slack: the slug, the diagnosis, the numbered options with recommendation, and "Reply in this thread with approve, revise or hold." Then stop. Never run `gate record`, `gate consume`, `merge guard`, `git push` or `gh pr merge`.

## Session from a Slack thread reply

Only the Captain's messages reach this session. A gate decision may be recorded only here.

1. `spacedock status --next --json`. Find the `ready_gates` row with `readiness: awaiting-captain`. If none, say so and stop.
2. Map his words: approve, revise or hold. If they are unclear, ask once and stop.
3. `spacedock gate record <slug> --decision <d> --actor person:captain --reason "<his words, verbatim>"`. Require exit 0 and `state=closed`.
4. Reply with the recorded decision and stop. Do not run `gate consume`; carrying out the option is a later stage.
