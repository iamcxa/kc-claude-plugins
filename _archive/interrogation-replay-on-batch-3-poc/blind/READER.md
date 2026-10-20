# Blind second reader: instructions

You score two anonymous question lists (X and Y) per task against a written answer key. You do not know which list came from which interrogator, and you must not find out.

Open only: this file, `answer-keys.md`, and `<task>-X.md` / `<task>-Y.md` in this folder.
Do not open: `../sealed/` (the label map), `../raw/` (the labelled originals), `../extension.md` (per-arm question counts, which match list lengths), `../report.md` and the task file (the first run's labelled results and the implementer's reasoning). Score before anything else is read.

Tasks (five): number-guards-readme-shrink, fo-write-checks, chat-only-evidence-observer-blind, delivery-gate-settles-skipped-checks, special-role-calls-fire-when-needed.

## Procedure

1. For each task and each list, go through the key items in `answer-keys.md` one at a time and mark each `hit`, `partial` or `miss` under the scoring rule written there. Quote the question number and its Q line for every hit and partial, and the key item it answers.
2. Count strict hits per list for: tier 1 (all), tier 1 askable `A` only, tier 2. Count `L` items apart. Report partials in a separate lenient column.
3. Ungrounded check: for each list, test whether each question's Grounds line resolves. Recreate the snapshot first (empty directory outside every repository):
   `git -C <kc-claude-plugins repo> archive <base> | tar -x -C <empty dir>`
   with bases: number-guards-readme-shrink c60e89e1, fo-write-checks c60e89e1, chat-only-evidence-observer-blind 5a951034f270efe967f56d1d3c3c69436d37b8ad, delivery-gate-settles-skipped-checks and special-role-calls-fire-when-needed 891a9a24b51e5e9fda02a992c6a27910a216787d. The story text is in each question list's own Story/Grounds quotes and in the task's seed (`git show` is not needed; the key's Source column names the archived task). Report the count of ungrounded questions per list and name each.
4. Save your scores and quotes to a file in this folder named `scores-<your id>.md`. Do not edit the lists or the key.
5. Only after step 4 is committed: the FO opens `../sealed/coin.json` and maps X and Y to arms.

Counts that need no key: questions per list, and grounded non-hit questions per strict hit.
