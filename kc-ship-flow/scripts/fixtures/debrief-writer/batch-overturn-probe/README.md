# probe batch — overturn-rule coverage

## Decisions made under `defaults` (append as they happen)

- 2026-09-06T01:00:00Z — decision A: referenced later by timestamp with "correction"; must be marked overturned.
- 2026-09-06T01:05:00Z — correction of 2026-09-06T01:00:00Z: decision A no longer applies. This note itself must NOT be marked overturned.
- 2026-09-06T01:10:00Z — decision B: this bullet contains the word correction but names no earlier timestamp, so nothing is marked.
- 2026-09-06T01:15:00Z — decision C: referenced later by timestamp with "retracted"; must be marked overturned.
- 2026-09-06T01:20:00Z — retracted 2026-09-06T01:15:00Z: decision C no longer applies.
- 2026-09-06T01:25:00Z — decision D, one of two bullets sharing this timestamp.
- 2026-09-06T01:25:00Z — decision E, the other bullet sharing that same timestamp.
- 2026-09-06T01:30:00Z — overturn 2026-09-06T01:25:00Z: this reference is ambiguous (two bullets share it) so neither D nor E is marked.
