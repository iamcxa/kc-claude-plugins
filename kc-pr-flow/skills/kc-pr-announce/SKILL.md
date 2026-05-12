---
name: kc-pr-announce
description: Use when a feature is complete with PR and demo artifacts (e2e walkthroughs, Loom, screenshots), and user wants to announce on Slack. Triggers on "announce", "post to product", "draft product message", "公告", or after PR + demo completion.
arguments:
  - name: tone
    description: "Message tone preset: internal, stakeholder, external (default: internal)"
    required: false
  - name: lang
    description: "Language: zh-TW, en, mixed (default: from ~/.claude/kc-plugins-config/language.yaml)"
    required: false
  - name: channel
    description: "Slack channel name (e.g., team-secha-ext, team-secha). Resolves to channel ID from config."
    required: false
---

# Product Demo Announcement

Draft a Slack announcement for a completed feature, written from the **user's perspective** — what changed for them and why it matters.

## Arguments

| Arg | Values | Default | Description |
|-----|--------|---------|-------------|
| `--tone` | `internal`, `stakeholder`, `external` | `internal` | Controls detail level and audience focus |
| `--lang` | `zh-TW`, `en`, `mixed` | (from config) | Controls output language |
| `--channel` | channel name (e.g., `team-secha-ext`) | (multi-channel selection) | Single-channel mode. Omit for multi-channel selection. |

Parse from skill args string. Examples:
- `/kc-pr-announce` → tone=internal, lang=from config, multi-channel selection (project_defaults pre-selected)
- `/kc-pr-announce --tone stakeholder --channel team-secha-ext` → single-channel mode, all resolved
- `/kc-pr-announce --tone external --lang en` → tone=external, lang=en, multi-channel selection

### Tone Presets

| Preset | Audience | Detail Level | Style |
|--------|----------|-------------|-------|
| **internal** | Engineering team | High technical detail, implementation specifics, backtick code references | Casual, direct, "also found bug X" |
| **stakeholder** | PM + Design + Eng leads | Focus on user impact and what's enabled, technical details in "Key points" only | Informative, outcome-oriented |
| **external** | Open source / external community | Link-heavy, self-contained context, no internal jargon | Professional, welcoming |

### Language

Language is independent of tone — any tone can be in any language.

If `--lang` not provided, resolve in this priority order:

1. **Channel `defaults.lang`** (if channel is known) — audience context wins for communication
2. **`language.yaml` pwd match** — project context fallback
3. **`language.yaml` default** — final fallback

```
Read → ~/.claude/kc-plugins-config/channels.yaml  (check channel defaults first)
Read → ~/.claude/kc-plugins-config/language.yaml   (fallback if no channel lang)
```

**Why channel wins**: announcements target a channel's audience, not the codebase. `team-secha-ext` readers expect zh-TW even when the codebase (e.g., `~/Project/recce`) uses English.

| Value | Output |
|-------|--------|
| `zh-TW` | 正體中文 throughout (technical terms stay English in backticks) |
| `en` | English throughout |
| `mixed` | Chinese main text, English for section headers and technical terms |

### Channel Resolution

```
Read → ~/.claude/kc-plugins-config/channels.yaml
```

Two modes:

#### Single-channel mode (`--channel` provided)

1. Resolve specified channel → look up in `channels` map → use stored `id` + apply `defaults` (channel defaults override skill argument defaults; explicit `--arg` overrides both)
2. Workspace check → if channel has `workspace` field, validate before proceeding to draft (see Workspace Validation below)
3. Proceed to Step 2.1 with one channel

#### Multi-channel mode (default, no `--channel`)

1. Read all channels from `channels.yaml`
2. Identify suggested channels via `project_defaults`:
   - Expand `~` in config paths, strip trailing slashes from both config paths and `pwd`
   - Find longest prefix match. Tie-breaking: first match in array order wins.
   - Match found → that channel is pre-selected (marked with ✓)
   - Match found but **channel key not in `channels` map** → warn "project_defaults matched 'xxx' but not defined in channels map", no pre-selection
   - No match → no pre-selection (user must select at least one)
3. Present channel selection:
   ```
   📢 Available channels:
     ✓ 1. team-secha (stakeholder/zh-TW)  ← project_defaults
       2. team-secha-ext (external/zh-TW)
       3. product (stakeholder/en)
       4. nightwatch (internal/zh-TW)

   Select channels (comma-separated numbers, Enter = pre-selected only, 'all' = all):
   ```
4. User selects:
   - Numbers (e.g., "1,2") → those channels
   - "all" → all channels
   - Enter (empty) → pre-selected only; if none pre-selected → ask again
5. For each selected channel → resolve from `channels` map, apply `defaults`
6. Workspace check → run once per unique workspace across selected channels

**Out of scope**: symlink resolution. Paths are compared as literal strings after tilde expansion. Trailing slashes are stripped before comparison.

**Never ask for channel ID if it's already in the config.**

**Adding new channels**: When a channel is used for the first time, ask for channel ID and mention target, then offer to update `~/.claude/kc-plugins-config/channels.yaml`.

#### Resolution Examples

| pwd | --channel | Result |
|-----|-----------|--------|
| `~/Project/recce/recce-server` | (none) | multi-channel list, `product` pre-selected (project_defaults match) |
| `~/Project/carlove` | (none) | multi-channel list, `team-secha` pre-selected |
| `~/Project/something-new` | (none) | multi-channel list, none pre-selected |
| `~/Project/recce` | `team-secha` | single-channel mode, `team-secha` only |

`project_defaults` only affects **pre-selection in multi-channel mode**. Language resolution chain is unchanged: channel `defaults.lang` > `language.yaml` pwd match > `language.yaml` default.

#### CTA (Call-to-Action)

`defaults.cta` is an optional string in `channels.yaml`. If present, the skill performs **literal string substitution** — replace `{test_steps}` placeholder only, preserve all existing formatting (emoji, Slack mrkdwn `*bold*`, etc.) as-is. Append the resolved string to the draft body (before "Key points:" section).

**Placeholder `{test_steps}`**: Derive from PR context in priority order:
1. **E2E flow steps** (most reliable — already validated)
2. **PR body** (user-facing description)
3. **Commit messages** (last resort)

Format: `→` as step separator, keep to one line. Aim for 5-8 steps; truncate to key user actions if the flow is longer.

**Three conditions:**
- `cta` absent or empty → skip, no CTA block in the draft
- `cta` present AND `{test_steps}` derivable → render with placeholder resolved
- `cta` present BUT no meaningful test steps (e.g., refactor PR, backend-only, "no user-facing changes") → **omit CTA block**, note to user: "CTA skipped — this PR has no user-facing test flow"

**Do NOT** invent a CTA when the channel config doesn't have one. **Do NOT** fabricate test steps — if the PR has no user-facing changes, omit the CTA.

#### Workspace Validation

Triggered at step 5 of Channel Resolution, only when `channel.workspace` is set. Runs after channel resolution, before draft.

1. Look up `workspaces[channel.workspace].domain`
   - Workspace name not found in config → warn "workspace 'xxx' not found in config", proceed
2. Call `slack_read_user_profile` → extract workspace domain from response
   - API failure or unparseable domain → warn "could not verify workspace", proceed (graceful degradation)
3. Compare domains
   - Match → proceed silently
   - Mismatch → warn: "⚠ Channel '{name}' belongs to workspace '{ws}' ({domain}), but current Slack connection is '{other}'. Continue anyway?" → user confirms (proceed to draft) or re-selects channel (restart from step 3, then re-present Step 2.1 summary for the new channel)

Workspace validation is a **guard, not a gate**. Never hard-block sending. If a second mismatch occurs after re-selection (e.g., all channels share the same workspace), inform the user and proceed to draft — do not loop indefinitely.

## Slack mrkdwn Mention Syntax

**CRITICAL**: Plain text `@here` does NOT trigger Slack mentions. You MUST use special syntax:

| Intent | Write this | NOT this |
|--------|-----------|----------|
| @here (notify online) | `<!here>` | `@here` |
| @channel (notify all) | `<!channel>` | `@channel` |
| @everyone | `<!everyone>` | `@everyone` |
| @username | `<@U123456>` | `@username` |
| @usergroup | `<!subteam^S123456>` | `@groupname` |

The draft shown to the user displays `@here` for readability, but the actual `slack_send_message` call MUST use `<!here>`.

## Process

### 1. Gather Context

```bash
gh pr view <NUMBER> --json title,body,url,labels
```

Find demo artifacts:
```bash
# E2E artifacts
find .claude/e2e/reports -name "*.mp4" -o -name "*report.md" -newer .git/HEAD 2>/dev/null | sort
# Or user provides Loom URL / other links
```

Read consolidated report (if exists) for flow count, pass/fail, and key observations.

### 2. Resolve Channel & Defaults

Read → `~/.claude/kc-plugins-config/channels.yaml`

Follow Channel Resolution rules above.

### 2.1 Proactive Context Summary

After gathering PR info and resolving channels, **proactively present** the following:

1. **Selected channels** — table showing each channel's resolved defaults:
   ```
   Selected channels:
   | # | Channel | Tone | Lang | Mention | CTA | Provenance |
   |---|---------|------|------|---------|-----|------------|
   | 1 | team-secha | stakeholder | zh-TW | <!channel> | ✓ | project_defaults |
   | 2 | product | stakeholder | en | <!subteam^...> | ✗ | user-selected |
   ```
2. **Override note** — if `--tone` or `--lang` provided, note they override ALL channel defaults
3. **Tone presets reminder** — one-line table for reference

Channel provenance (shown per channel):
- Pre-selected via `project_defaults`: "(project_defaults match: {matched_path})"
- Explicitly passed via `--channel`: "(from --channel arg)"
- User selected from list: "(user-selected)"

**Why**: Users see exactly what each channel will receive before drafting begins.

### 3. Match Voice & Format

Search user's recent announcements via Slack MCP (optional — skip if voice rules below are sufficient):

```
slack_search_public_and_private:
  query: "from:<@USER_ID> in:<channel> Hey"
  sort: timestamp, sort_dir: desc, limit: 5
  include_context: false
```

### 4. Handle Demo Media

**Private repo image limitation**: GitHub draft release asset URLs require authentication. They render in PR comments (reader is logged in) but **fail in Slack** (unfurler has no auth → 403). `user-attachments` URLs (from web UI drag-drop) are public but have no CLI upload API ([cli/cli#1895](https://github.com/cli/cli/issues/1895)).

**Strategy**: Never embed image URLs in Slack messages for private repos. Link to the PR comment instead — readers click through to see screenshots in GitHub's authenticated context.

| Source | In Slack message | Action |
|--------|-----------------|--------|
| **PR comment with screenshots** | Link to PR comment URL | `E2E 驗證（N/N pass）：\n{PR comment URL}` |
| **Loom / external URL** | Embed link directly | Loom URLs are public, always work |
| **Local files only** | Link to PR | Warn: "Upload screenshots to PR comment first: `gh release upload` + `gh pr comment`" |

**For PR comments** (separate from Slack): Use draft release URLs (`gh release upload`) — these render correctly for authenticated GitHub users.

Note: Slack MCP only supports text messages — no file upload API.

### 5. Draft Messages

**For each selected channel** (in order), generate a draft using that channel's resolved defaults (tone/lang/mention/cta). Explicit `--tone` or `--lang` args override all channel defaults uniformly.

**Structure (from actual posts):**

```
Hey {mention}, {ticket/topic} — {one-sentence impact: what changed for users}.

{Context paragraph — what was done and why, 2-3 sentences max}
• {Feature/change 1 — concrete description}
• {Feature/change 2}
• {Feature/change 3}

E2E walkthrough（Claude 自動跑的，{N}/{N} pass{, 0 errors if clean}）：
{PR comment URL with screenshots or video link}

{CTA block — if channel has `defaults.cta`, render here with `{test_steps}` resolved}

Key points:
• {User-facing behavior or architectural insight}
• {Integration/observability highlight}
• {What this enables next or known debt}

PR: {PR_URL}

Sent using @Claude
```

**Tone-specific adjustments:**

| Section | internal | stakeholder | external |
|---------|----------|-------------|----------|
| First line | Topic + impact | User outcome only | User outcome + context |
| Bullet list | Implementation details, backtick refs | What changed for users, no code | Feature descriptions, self-contained |
| Key points | Architecture, bugs found, tech debt | What's enabled next, business value | How to use, what's next |
| "Also..." | OK (secondary fixes, side findings) | Only if user-relevant | Only if noteworthy |
| PS line | Tag reviewers, callbacks | Optional | Contribution invitations |

**Voice rules (from Kent's actual posts):**
- First line: `Hey {mention}, {topic} — {impact summary}.` (always this pattern)
- Bullet points use `•` not `-`
- Technical terms in backticks: \`user_id\`, \`handleCommand()\`, \`/conflict-scan\`
- Tables OK for live examples or data (risk levels, step results)
- Credit origins: "This came from @X's idea in #channel"
- Secondary changes: "Also..." paragraph after main content
- Footer: always "Sent using @Claude"
- PS line OK for tagging specific reviewers or callbacks
- No "Great news!" / "Excited to announce" — just state what changed

**Checklist before showing draft:**
- [ ] First sentence is user-impact, not implementation detail
- [ ] Under 200 words (Slack readability)
- [ ] Linear ticket(s) included (SC-xxx or DRC-xxx)
- [ ] Demo links are shareable URLs (not local file paths)
- [ ] Mention target resolved (from config or user input)
- [ ] "Sent using @Claude" footer
- [ ] Tone matches preset (no code in stakeholder lead, no jargon in external)
- [ ] Language matches resolved lang setting
- [ ] **Mentions use Slack mrkdwn syntax** (`<!here>` not `@here`)
- [ ] **CTA resolved** — three cases: (1) `cta` present + test steps derivable → included with `{test_steps}` filled; (2) `cta` present + no user-facing test steps → omitted with note; (3) `cta` absent → no CTA block
- [ ] **Workspace validated** — if channel has `workspace` field, workspace check passed or user confirmed mismatch
- [ ] **Channel selection shown** — multi-channel list with pre-selection, or single-channel confirmation

### 6. Review & Send

**Single-channel**: Show draft with **readable** mention format (`@here`). After approval, send via `slack_send_message` with **Slack mrkdwn** mention format (`<!here>`).

**Multi-channel loop**: For each selected channel (in order):

```
--- Draft {n}/{total}: #{channel_name} ({tone}/{lang}) ---

{draft content}

--- End draft ---
  1. Send
  2. Edit → re-draft
  3. Skip this channel
```

- Option 1: Send via `slack_send_message` with Slack mrkdwn mentions → proceed to next channel
- Option 2: User provides edits → regenerate draft → show again
- Option 3: Skip → proceed to next channel

**After all channels processed**, show summary:
```
📢 Announcement summary:
  ✓ #team-secha — sent
  ✗ #team-secha-ext — skipped
  ✓ #product — sent
```

**Why per-channel loop (not batch)**: Each channel may have different tone/lang/cta — the user needs to review each draft individually.

## Common Mistakes

- **`@here` not triggering** — MUST use `<!here>` in the API call. Plain `@here` is just text.
- **Local file paths in message** — .mp4 paths are not URLs. Always resolve to shareable links first.
- **Engineering-first language in stakeholder tone** — "Added X integration" tells engineers what you built, not users what they gained.
- **Missing Linear ticket** — always include for traceability.
- **Asking for channel ID when it's already in config** — check `~/.claude/kc-plugins-config/channels.yaml` first.
- **Mixing tone and language** — tone controls detail/audience, language controls output language. They are independent axes.
- **Workspace mismatch silent failure** — sending to a channel ID from a different Slack workspace silently fails. If `workspace` field is set, always run workspace validation before sending.
- **project_defaults matched but channel key missing** — `project_defaults` maps path → channel name, but that name must exist in the `channels` map. If it doesn't, warn the user instead of silently falling through.
- **project_defaults path mismatch** — `~` must be expanded in config paths; `pwd` is already absolute. Trailing slashes cause prefix match failures. Always strip trailing slashes before comparison.
