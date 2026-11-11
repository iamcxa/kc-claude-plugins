# Pre-registration: does a worker keep architecture documents true after changing behaviour?

Written 2026-11-11 before any scored run. Author of the convention under test is also the author of this
harness, so the scorer is mechanical and a fresh-context reviewer re-scores from the raw trees afterwards.

## Question

After a task changes behaviour, does a fresh implementation worker leave the architecture documents true,
and put a ruling, a deferred idea and a new flow in the right place — under dev2 as shipped with a flat
document, with the layered layout alone, and with the layered layout plus the convention text?

## Arms

| Arm | Document layout | Rules the worker reads |
| --- | --- | --- |
| A | one `ARCHITECTURE.md` in prose | kc-dev-flow-2 at e8664a72: implementation `principles.md`, `retained-documents.md`, the workflow's Affected documents paragraph, `doc_impact.py` |
| B | `docs/architecture.md` map + `docs/architecture/<topic>.md` with fixed sections | same as A |
| C | same as B | A's rules + `.flow/documents.md` (`CONVENTION` in `world.py`, 251 words) |

The same nine fact sentences build both layouts (`F` in `world.py`). No task names a document.

## Chain

Six tasks (`STEPS` in `run.py`) run in order in one repository, each by a fresh headless worker that sees
only the repository: cancel window 36 to 18 hours; add a no-show state; an owner ruling that ends the Harbor
Club exemption; reminder 20 to 44 hours plus a deferred idea; a refactor with no behaviour change; a new
waitlist flow. The harness commits and tags after each step.

## Measures

Primary: facts true in the architecture documents at the end of the chain, of 10 (`FACTS` in `score.py`),
by regular expression on literal values that appear nowhere else in the world.
Secondary: of five behaviour changes, how many were documented in the step that made them; stray
Markdown files; for B and C, whether the waitlist got its own topic file and a map row; words in the
architecture documents at the end; tests passing at the end.
Judged by the reviewer, not the script: whether a sentence still says Harbor Club members are exempt.

## Runs

Codex `gpt-6.1-sol`, effort xhigh (the package's implementation default): 3 arms x 2 repetitions = 6 chains,
36 runs. Claude `sonnet`: 3 arms x 1 repetition = 3 chains, 18 runs, as a second host. A step that exits
non-zero or times out is retried once from the previous tag and the retry counts. Hard stop at 62 runs.
One rehearsal step (arm C, repetition 0, step 1) checks the harness and measures time and tokens; it is
not scored.

## Reading the result (fixed now)

Per host, on the mean of the primary measure:

- A at 9 or more: the control is at ceiling; the POC cannot separate the arms and says so.
- C minus A at 2 or more: the convention with its layout helps. B minus A at 2 or more: the layout alone helps.
- C minus A under 1: no measurable difference on write-back.
- Anything between: reported as inconclusive, with the per-fact table.

Two chains per arm cannot support a claim finer than that. Nothing here shows the documents are useful to
a reader, that validation would catch a miss, or what happens in a real repository over months.

## Not changed after the first scored run

`world.py`, `run.py` STEPS and PROMPT, `score.py` FACTS and expressions, this file. A change gets a dated
line in `CHANGES.md` with its reason.
