---
title: In a long session, FO breaks fewer workflow rules when the rule reappears at the moment it applies
variant: kc-dev-flow-2
profile: poc
merge: pr
status: backlog
---

Filed on the Captain's 「好，就這樣」 (chat, 2026-10-17) closing readme-index-attention-poc (dev2-poc workflow), after he asked whether the model already holds about 5000 words without losing focus.

## Scope

- What the closed POC showed: in short scenarios the whole-README arm followed the probed rules 13 of 15, the same as the index arm, and three of five probes were followed every run by both; reading about 5500 words at once showed no measurable loss when the rule is used right away. It did not test long sessions.
- The question here: the observer's violations come from late in long sessions, where the README was read long before the action. Does a rule that reappears at the moment it applies (a script's `next:` line, a per-moment file, a hook) reduce violations there, compared with the README read once at startup?
- Existing signal, not a controlled comparison: the bare-package-script-name rule appeared in 5 of 10 observer reports dated 2026-10-13 to 10-15 and 0 of 5 dated 10-16 to 10-17, after `dispatch_records.py --names` started printing it at dispatch.
- Precondition: a long-session test harness exists (an FO run with realistic accumulated context before the probe). Do not start the POC without it; building that harness is the first question at backlog.
- Non-goals: no README restructure here; a restructure is filed only if this POC passes a bar the Captain sets.
