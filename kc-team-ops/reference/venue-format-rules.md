# EM Plan Review — Venue Format Rules

P5 delivery. Detect the venue from the plan source; format accordingly. **Review language is always English** (matches Kent's PR-review-language convention); conversational notes back to Kent stay in his preferred language.

## HARD GATE (all venues)
Never post to any external venue without Kent's explicit go for THIS message. Draft → show → ask → post on approval. One approval never carries to a different message or venue.

## Slack (thread reply)
- Send via the Slack MCP tool with `thread_ts` = the parent message ts (reply in-thread, not to channel).
- The Slack MCP tool accepts **standard markdown** (`**bold**`, `` `code` ``, `-` bullets) and converts to Slack mrkdwn.
- **Mentions:** convert `@name` → real `<@USERID>`. Resolve IDs from the thread (`slack_read_thread` returns `From: Name (Uxxxx)`) or `slack_search_users`. Mention the people you credit / address (it notifies them); don't over-mention.
- Severity dots (🔴🟠🟡) and arrows (→) render fine.
- **Message-design judgment:** if a meta / culture point is distinct from the review, post it as a **separate follow-up reply**, not bolted onto the review — keeps each message focused and on-topic for the thread.

## Linear (comment) — WAF-safe rules
Linear MCP writes route through a Cloudflare WAF that 403s on common technical-markdown. Apply EVERY time (full list in the target repo's `AGENTS.md` → "Linear MCP — Cloudflare WAF Workaround"):
- **Prose-ify file refs:** write "line 287 of `next_auth_adapter_api.py`", NOT `next_auth_adapter_api.py:287` chained across one sentence.
- **No shell template expansions:** never a literal `$VAR` / `${VAR}` even inside backticks — describe the variable in prose.
- Break nested function-call syntax onto separate lines inside fenced code blocks, not inline in prose.
- Soft-cap ~3KB; split into Part 1 / Part 2 if longer.
- If a write returns `<!DOCTYPE html>` + "Attention Required! | Cloudflare" → content-matched block. Reword per the above; do NOT retry the same payload (the WAF rejects deterministically on content).

## Inline (to Kent)
- Default when there is no external venue, or when Kent wants to decide where to post.
- Give a paste-ready block in the target format, plus a one-line note on what you'd change per venue.

## Calibration & framing (all venues)
- Frame contestable claims as **experiments / open questions**, not declarations — especially anything 50/50 or governance-level. Don't assert in a public channel what you haven't pressure-tested.
- Lead with the point. Credit teammates. Close with "yours to take or leave."
- Optional footer signalling AI-assisted authorship if the channel culture expects it (the author decides).
