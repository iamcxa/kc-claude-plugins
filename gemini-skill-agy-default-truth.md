---
title: The gemini skill stops saying agy refuses by default
status: backlog
variant: kc-dev-flow-2
---

Outcome: `kc-team-ops/skills/gemini/SKILL.md` states what headless `agy` actually does, and its analysis-only mode does not rely on a refusal that a test does not show.

Source: FO stated in the sitting 「我會開票修 gemini 技能那句話」, and the Captain answered 「照建議」, chat 2026-11-02.

Bite: batch 12's POC ran headless `agy` with no flag; it reported `always-proceed` and ran a shell command without asking. The skill says 「`agy`'s default refuses to run a」 tool (`SKILL.md`, its safety rule 1, read 2026-11-02).

Consumer: anyone invoking `kc-team-ops:gemini`.
