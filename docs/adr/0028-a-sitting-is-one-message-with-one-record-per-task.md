# 0028. A sitting is one message with one record per task

Date: 2026-10-20

## Status

Accepted

## Context

FOs in four repositories ran batches of tasks by interim rules kept outside the package. Counted from pinned state exports on 2026-10-20, 100 Captain gate rows since 2026-10-17 fell into 62 runs of records at most 20 s apart, so presenting a stage's gates together held, but nothing in the package said so, and the records of web's second sitting and relay's third did not name it. A batch-start rule to reserve every ADR and migration number contradicted the Number guards rule in the workflow README (reserve when a task's own implementation dispatch is built), and observers flagged it twice, 7.5 h and 13 h before the dispatch. The measurements and the graded interim rules are in the task's `## Design`.

## Decision

**Words:** 「找一下 plugin FO 諮詢怎樣可以批次討論，批次實作，批次檢視的原則，這一段 dev2 還沒實裝，但是我需要你們按共同原則 dogfood 以便提高效率且降低我的負擔」 — Captain, 2026-10-17, chat; 「同意」 to settling the numbers conflict in this task — Captain, 2026-10-20, chat; at the ideation gate, 2026-10-20, D1 「好」, D2 「好，那就下一版，跟故事地圖一起」, D3 「好」, D4 「按建議」 and 「先不放，直到有方式可以找到“重複出現的同類發現”」.

**Options considered:**
- A sitting is every gate awaiting the Captain at one stage, put in one message, each task keeping its own Briefing, question and record, with his one answer quoted in each; `pr_watch.py tasks` prints one line for it when two or more gates await at one stage (chosen); a `batch:` field on the task or a stored list of members was not chosen, because `spacedock status --next --json` already names the gates and their stage and a field would be a second copy
- Every ideation written while another task is live ends with `### Batch overlap`, in `skills/ideation/principles.md` (chosen); the condition "a batch was named" was not chosen, since 4 of relay's 11 designs lacked the heading because each was written alone while other tasks were already building
- Number reservation stays at each task's own implementation dispatch build, README unchanged (chosen, D3); reserving every number before a batch's first dispatch was not chosen
- No sitting counter and no rule that a sitting is recognised by the interval between records (chosen, D1, as the Captain ruled in chat); FO counts his answers per batch from the ledger by hand as before
- The list-then-ask-one-at-a-time pattern is not in this task; it moves to the story-map task for the next release (chosen, D2)
- One follow-up task per delivered task, a repeated finding class calling the chief-engineer, and a cap of three concurrent workers stay out of the package (chosen, D4); the Captain's direction on concurrency is its own task, `fo-asks-to-raise-concurrency`

**Recommended:** each of D1 to D4 as the gate question stated, as the Captain amended them in chat on 2026-10-20 (D1 no sitting counter, D2 the story-map task, D4 the finding-class rule out until a repeated class can be found).

A sitting changes how many messages he reads, not what an approval covers: under the workflow README (`FO steps: review findings`) and ADR 0011 a plain approval accepts a recommendation only when that task's own question says so. Later work that presents several gates, reserves a number or writes an ideation design follows these rulings.

## Consequences

Reservation: `number_guards.py reserve` takes one more than the highest of the base tip and every other task file, so reservations made one task at a time inside one state do not collide, and the 24 tests in `test_number_guards.py` pass. A held number is exposed longer: ADR 0018 was reserved at a dispatch on 2026-10-16 12:20, taken on main by an out-of-band docs commit at 23:54 (11.5 hours later), and re-reserved the next day. The README's `Reserve.` step has FO reserve at the dispatch build, so a batch's numbers are not assigned during ideation; reserving all of a batch's numbers right before their implementation dispatches stays allowed, and `number_guards.py check` at implementation exit, validation and the PR head catches a number taken elsewhere.

The sitting line repeats on every startup and idle pass while two or more gates await, including after FO has presented. Whether FO presents in one message is seen only in the record and in the Captain's chat. The answer count stays a by-hand step until Spacedock review records each answer. Reopen when a batch's observer finds a design written while another task was live without `### Batch overlap`, or a stage's gates presented one by one while the line was printed.
