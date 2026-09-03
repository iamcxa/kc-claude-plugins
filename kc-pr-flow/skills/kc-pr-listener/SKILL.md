---
name: kc-pr-listener
description: "Use when setting up or fixing the menu-bar PR review listener — 'install pr listener', 'set up review listener on this machine', 'new machine PR review setup', 'SwiftBar 沒反應', 'menu bar icon missing', 'review 沒通知我', 'listener not dispatching', 'add a review backend', 'PR review listener 裝不起來', or adding a Conductor token for another GitHub organization."
argument-hint: "[install | status | troubleshoot | add-backend]"
---

All text output follows unified language preference. See plugin CLAUDE.md for query flow.

## Overview

The listener watches GitHub for pull requests where the user is a requested
reviewer, starts a review for each new one, and reports it in the macOS menu bar.
It never merges and never approves.

Menu bar and listener are one script: the plugin's refresh interval is the poll
interval, so there is nothing to supervise. Where a review actually runs is a
**backend** — `scripts/backends/CONTRACT.md`.

| Piece | Path |
|-------|------|
| listener + menu | `${CLAUDE_PLUGIN_ROOT}/scripts/pr-reviewer-listen.sh` |
| backends | `${CLAUDE_PLUGIN_ROOT}/scripts/backends/` |
| dispatch prompt | `${CLAUDE_PLUGIN_ROOT}/reference/reviewer-dispatch-prompt.md` |
| full behaviour | `${CLAUDE_PLUGIN_ROOT}/docs/reviewer-listen.md` |
| config (intent) | `~/.claude/kc-plugins-config/pr-flow/reviewer-listen.config.json` |
| state (derived) | `~/.claude/kc-plugins-config/pr-flow/reviewer-listen.state.json` |

Config survives; state can be deleted at any time and rebuilds on the next tick.

## install

```bash
brew install --cask swiftbar   # if missing
"${CLAUDE_PLUGIN_ROOT}/scripts/reviewer-listen-install.sh" --backend conductor
```

The script is idempotent and prints the two steps it cannot do itself: choosing
the plugin folder in SwiftBar's first-run dialog, and clicking **Resume
listening**. It installs paused deliberately — an install script must not dispatch
an unattended review.

Never ask the user to paste a token into the conversation. For a second GitHub
organization, direct them to run this in a terminal; it reads the token from a
hidden prompt, verifies it, and writes it 0600:

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/backends/conductor-token.sh" <github-org>
```

## status

```bash
jq . ~/.claude/kc-plugins-config/pr-flow/reviewer-listen.config.json
jq '{last_poll, last_error, open:(.open|length), seen}' ~/.claude/kc-plugins-config/pr-flow/reviewer-listen.state.json
tail -20 ~/.claude/audit/pr-reviewer-listen.log
```

Read `listening` for the switch, `review_model` / `review_effort` for what a dispatched review runs at, `repos` for which repositories are listened to, and
each `seen` entry's `status`: `dispatching` → `running` → `reviewed`, or `error`
with the backend's reason and an `attempts` count, or `unconfirmed` — a dispatch that
may already exist remotely, which is never retried automatically. Every entry carries the
`head_sha` it applies to; `source: "github"` means the entry was adopted from an
existing review of that commit rather than dispatched here.

## troubleshoot

| Symptom | Cause to check first |
|---------|----------------------|
| No menu-bar icon at all | SwiftBar was never granted a plugin folder. Open SwiftBar, set it to the folder the installer printed. |
| Icon gone after a reboot | The host is not launched at login. Toggle **Start at login** in the menu; if the row reads `unknown`, macOS refused Automation permission for System Events and the menu-bar app needs it granted. |
| Icon shows `off` | `listening` is false. Click **Resume listening**. |
| Icon shows `!` | `last_error` in state — usually `gh` auth expired. |
| Rows appear but nothing dispatches | The repo is toggled off, the PR is a draft, or `attempts` already reached 3. Click the row's **review now** to dispatch that one regardless. |
| A row is `❌` with "no project" | The repo has no project in that token's organization; a second organization needs its own token file. |
| Review finished but no notification | Switch the notification channel from the menu (`terminal-notifier` ⇄ `osascript`); either may lack permission to post on this Mac, and only `terminal-notifier` carries a click action. |
| A finished PR vanished from the list | Expected. GitHub drops a PR from review-requested once a review is submitted; look under **Finished reviews**. |

## add-backend

To run reviews somewhere other than Conductor, write one executable answering two
verbs — `create` and `status` — exactly as `scripts/backends/CONTRACT.md` specifies,
then prove it before wiring it in:

```bash
"${CLAUDE_PLUGIN_ROOT}/scripts/backends/conformance.sh" <your-backend>
```

Set `.backend` in the config to its filename without `.sh`. Polling, de-duplication,
notification, and menu rendering need no change — that is the point of the seam.
