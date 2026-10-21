# Blind scorer: instructions

You score five anonymous question lists (one per task, files `<task>-Z.md`) against a written answer key. You do not know which interrogator wrote them and must not find out.

Open only: this file, the answer key `answer-keys.md` (read-only, in the closed POC's `blind/` folder), and the five `<task>-Z.md` files in this folder.
Do not open: `../raw/`, `../report.md`, the task file, or anything under the closed POC other than `answer-keys.md` and its own `blind/READER.md` for the scoring rule. Score before anything else is read.

Tasks (five): number-guards-readme-shrink, fo-write-checks, chat-only-evidence-observer-blind, delivery-gate-settles-skipped-checks, special-role-calls-fire-when-needed.

## Procedure

Follow the closed POC's `blind/READER.md` steps 1 to 4 for the single list per task: mark each key item `hit`, `partial` or `miss` under the rule written in `answer-keys.md`, quote the question number and Q line for every hit and partial, count strict hits for tier 1 (all), tier 1 askable `A` only, tier 2, count `L` items apart, report partials in a lenient column, and run the ungrounded check on snapshots rebuilt with `git archive <base> | tar -x` into empty directories outside every repository (bases: number-guards-readme-shrink and fo-write-checks c60e89e1; chat-only-evidence-observer-blind 5a951034f270efe967f56d1d3c3c69436d37b8ad; delivery-gate-settles-skipped-checks and special-role-calls-fire-when-needed 891a9a24b51e5e9fda02a992c6a27910a216787d). Save scores to `scores-<your id>.md` in this folder.
