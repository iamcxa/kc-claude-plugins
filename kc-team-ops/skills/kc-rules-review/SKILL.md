---
name: kc-rules-review
description: Use when the user wants to change their agent operating rules, says they keep correcting the same thing across projects, suspects a rule is being ignored, asks whether the rule file is too long, or asks which rules to delete. Also use after a rule change lands, when Claude and Codex user rules or downstream skills may need behavioral alignment.
---

# Rules Review

Audit an operating rule set — `~/.claude/CLAUDE.md`, `~/.codex/AGENTS.md`, project instruction
files, memories — against what actually happened in the user's sessions, then change it one
decision at a time.

**Core principle: measure two numbers per rule, not one.** *Friction* is how often the user
repaired your output. *Firing* is how often the rule left an observable trace. The verdict lives
in the pair, never in either alone.

**The trap this exists to stop:** friction points at one loud rule, and fixing that rule feels like
finishing. Measured against a control, the loud rule gets fixed either way — what goes unasked is
whether it ever ran, whether something else already owns it, and what the quiet rules' zeros mean.
The quiet rules are then scored on friction alone, which is how a safety rule that has never been
violated gets read as dead weight.

## When to use

- The user says some version of "you keep doing this" or "I correct the same thing every time".
- The user quotes their own rule back at you — the strongest possible signal, because it proves the rule exists and did not fire.
- A rule file has grown and nobody knows which parts still earn their place.
- A rule change just landed and downstream files may quote the old section names.

**Do not use** for one skill's behaviour inside one repository, or for a bare inventory of stored
memories. This is the whole-rule-set pass: it reads the rules that govern every session, and its
unit of change is a rule, not a single correction.

## Step 0 — Ask how far back, before reading anything

The window changes every number in this audit, and it is the user's call, not a default you pick
for them. Ask it with the harness's question UI as the first action, offering two weeks, one month,
two months, and a custom date — and say what each costs, because they find out otherwise only after
waiting: a one-day window returns in seconds, two weeks across six hundred sessions takes minutes.

Two facts belong in the question, because they change the answer:

- The coverage gradient at the end needs a wide window. Two weeks shows it; two days is noise.
- A window that does not reach back to the last rule change measures the old rules, not the new ones.

If a previous run exists, say when it was and what window it used. Repeating that window buys a
delta; changing it buys a fresh baseline and no comparison.

## Step 1 — Measure

```bash
kc-team-ops/scripts/rule-firing-report.sh --since YYYY-MM-DD --patterns your.tsv
```

The patterns file is TSV: `kind<TAB>label<TAB>regex`, where `kind` is `friction`, `firing`,
`incident`, or `codify`.

Declare one `firing` row per rule that has an observable marker (a required prefix, a field name,
a file the rule makes you read). **A rule with no possible marker cannot be measured, and that is
itself the finding** — see Step 2.

`codify` rows catch the user asking for something to become standing behaviour — "from now on",
"remember this", "write it into the rules". Each one has two ways to fail, and the second is the reason this audit
usually gets started: never written into the rule file at all, or written and never firing. Check
both against the actual file before reporting either.

### Enumerate the rule file before trusting any coverage

The patterns file is hand-written, so the audit sees only the rules someone thought to declare.
Open the rule file itself, list every rule in it, and split them:

- **Measurable** — the rule names a literal string it makes you emit, so it can have a `firing` row.
- **Unmeasurable** — the rule is real and has no observable marker. It cannot be given a firing row, and this pass cannot tell whether it runs.

**When a rule names its own string, use that string verbatim.** Do not paraphrase it into a friendlier
pattern, and do not widen it to catch near-misses. A rule requiring `without-it unanswered` in a PR
body was measured with `without-it|沒有它會|會壞什麼` and scored 147 firings in a month; the string the
rule actually asks for appeared **zero** times across four pull requests opened that day, each of which
used a self-invented heading instead. The loose pattern counted the agent discussing the rule and
reported it as the rule running.

The same slip has three instances on record — a close-out label that grew a second wording, a marker
added to a skill and never added to the patterns, and this one. Every time, the audit's own output is
what hides it: a healthy number appears where a zero belongs.

Report the second list by name, every run. On one real file, 3 of 19 rules were measurable; the
other 16 — upstream-first, cost, escalation, e2e acceptance among them — were invisible to the audit
and nothing said so. A report that covers a sixth of the rules and reads as complete is worse than a
short one that says which fifth-sixths it skipped.

This is also the only way to keep "the rule is absent" and "the rule is present and unmeasurable"
apart. They look identical from the patterns file and they call for opposite actions.

`incident` rows collect a different thing: turns where the user did work you never offered —
relaying what another session is doing, routing around you, repairing something you broke. These
are candidates, never counts. Normal division of labour reads identically, so every hit gets read.

Each run is kept under `~/.claude/kc-team-ops/rules-review/<timestamp>/` — the report, the matched
human turns, the incident pairs, and a `run.json` of every count. Nothing is overwritten, so a
second run the same day is readable against the first.

When the previous run used the same window and the same patterns, the report ends with what moved
since it, and says so when nothing did. When either changed, it refuses to compare and says why:
a delta against a different question is worse than no delta.

**Run the script or report that you could not.** Do not reconstruct the measurement by hand with
your own jq and your own patterns when the script fails — a hand-built run leaves no record, no
`run.json`, and a pattern set nobody can reproduce, so its numbers cannot be compared with the run
before it or the one after. Three hand-built passes are three different questions answered once
each. If the script will not run, say so, say what it printed, and stop; a missing audit is
recoverable and an uncomparable one quietly is not.

Counts are for comparing runs, not for quoting as truth. Every matched human turn is written to
`human-turns.tsv` in the run directory; read the hits before you believe a number.

The bundled report script reads Claude Code logs only. When `~/.codex/AGENTS.md` is the target,
use those counts only as source-rule evidence; prove Codex firing with the isolated A/B route below.
Never label Claude firing counts as Codex behavior.

**Read the coverage table before the friction table.** The report ends with the decoding rate
against the length of the agent's previous message. Voiced friction is the only kind the columns
can count; when the user stops correcting and starts adapting, nothing is said and no pattern
matches. Length is the one proxy that does not need the complaint to be spoken. Over a two-week
window the rate has run 3% under 500 characters against 10% above 1500 — over two days it is noise,
so give it a wide window or do not quote it.

Say plainly in the report that the pass misses unvoiced friction, and that a clean friction table
is not evidence of a comfortable user.

## Step 2 — Cross-tabulate

| Friction | Firing | Verdict |
|---|---|---|
| high | low | **Rule exists, no trigger.** Rewrite it as a check with a countable condition. Do not add prose. |
| high | zero | **Rule missing.** Add it — as a check, not a paragraph. |
| low | zero | **Candidate for deletion** — but first ask which of the two zeros this is. |
| low | high | **Working.** Leave it alone. |
| high | high | **Runs but is not believed.** The rule fires and the user asks anyway, so the claim is not carrying what would settle it. Do not add a rule; make the existing one state its evidence. |

The last row is the one that looks like every other row and is not. High friction reads as a gap and
invites a new rule, but the rule is already running — measured on real history, a verification rule
left 295 traces in a month while the user still asked "did you actually run this" 24 times. They were
not asking whether verification happened; they were asking whether it was real. A second rule saying
the same thing adds nothing. The fix is to make the claim carry the command that was run and what it
printed, so there is nothing left to ask.

**Two kinds of zero, and they get opposite treatment:**

- *Zero because never needed* — genuinely dead weight. Delete.
- *Zero because it worked* — a safety rule whose whole value is that it is never violated. Deleting it is how you find out.

Separate them by asking what the world looks like if the rule is gone, not by counting.

**A third case the two columns cannot show.** Zero friction, zero firing, *and* incidents against
that subject can mean no rule was ever violated because none was ever offered — the user simply did
that work alone. The friction column is structurally blind to this: the user never corrected you,
because you gave them nothing to correct.

**An incident is a candidate, not a verdict.** Read each one in `rule-review-incidents.txt` with the
assistant turn printed above it, and classify it before it counts:

| The turn before it shows | Classification | Remedy |
|---|---|---|
| nothing on the subject | **blind spot** | a rule, and possibly a different role (Step 4) |
| the user's own standing authority | **normal division of labour** | none; drop it |
| you offering to do it, then not | **follow-through failure** | a rule about finishing, not a role |
| you lacking the access or the tool | **capability limit** | fix the access; a rule changes nothing |

Only the first row may be used as evidence for changing the role. The third is the one most easily
mistaken for the first, and it is where changing the role does the most damage: it renames the agent
instead of making it finish.

## Step 3 — Check for an owner before deleting

A rule that looks dead is often a **duplicate of a live capability that owns the concept
elsewhere** — a plugin reference, a stage contract, a test that asserts the path. Grep the fleet
for the concept before cutting.

- Found an owner → **propose deleting the copy and name the owner**, through Step 5 like any other change. Do not delete it yourself; removal is the user's call.
- Found no owner → the rule is the only home. Removing it drops the capability.

Finding an owner is the start of the check, not the end. Before proposing removal, answer both:

- **Does the assertion cover content or only existence?** A contract test that asserts a path
  resolves does not stop the two copies from saying different things. Diff them. If they have
  already drifted, deleting the copy silently drops whatever only the copy says.
- **Do they load in the same places?** An owner loaded by two stage contracts does not cover a rule
  file read in every session. Removing the copy narrows where the rule applies, and that narrowing
  is the real cost to put in front of the user.

## Step 4 — Find the role the user is covering for

The friction table says which rules are broken. This asks a different question of the same corpus:
**which job is vacant.** Do not derive one from the other — friction measures where the agent fails,
and answering it with a job title recommends a communications hire because the engineer writes
unclear reports.

**The signal is a question the user asks that the agent should have asked.** Every turn falls into
one of two kinds, and only the second names a role:

| The turn | Kind | Example |
|---|---|---|
| points at the agent's last output and asks for it again | **repair** | "say that again more simply", "what does that mean" |
| applies a standing test to the work that the agent never applied | **role gap** | "what breaks if we drop it", "does upstream already have this", "whose move is it" |

A repair is fixed with a rule. A role gap means the user performed a function on the agent's behalf,
and the recurring question *is* the job description.

### Dispatch it, do not answer it yourself

Send `human-turns.tsv` from the run to a **fresh-context reviewer** — one that has not seen this
session's reasoning. An agent deciding which of its own duties are vacant is grading its own work,
and this step is the one place in the audit where that is the whole question.

Give the reviewer the two kinds above, the run directory, and this brief:

> Group the recurring role-gap questions by the function they perform. Name the role that function
> belongs to, anywhere on the software delivery arc — product, design, architecture, engineering,
> test, release, operations, data, security, documentation, delivery management, coordination. Do
> not restrict yourself to a fixed list, and do not invent a role to have an answer.

### What it must return

- **The role, or none.** "No vacant role" is a correct and expected result, and the reviewer must be told so. A catalogue this wide will always yield a plausible title if the reviewer feels obliged to produce one.
- **The recurring question that names it**, quoted from the user, with the exact turns it appeared in. Fewer than three separate occasions is a note, not a finding.
- **The default self-check to install** — that same question, turned on the agent. This is the deliverable; the title is the label on it.
- **What it would have pre-empted**: the specific past turns where the user had to ask. Not "communication would improve" — "you asked this on these three dates, and you would not have needed to."

That last item is what makes the recommendation falsifiable. A role proposal that cannot point at
turns the user would not have had to write is a job title with nothing under it.

### A recurring question is not yet a vacancy

Count alone picks the wrong role, and the margin is usually too thin to carry a job title. Run the
candidates through the audit's own test before naming one:

| The rule for that question | Firing | Verdict |
|---|---|---|
| absent from the rule file | — | **vacant** — nobody is doing this |
| present, with no observable marker | unmeasurable | **unknown, and say so** — never read as vacant. The rule exists; this audit cannot see whether it runs, and recommending a role here appoints someone to a job that may already be done |
| present, and never fires | zero | **vacant** — the rule is there and does not run, which is the highest-value finding this audit has |
| present, fires, and the question stopped | high | **occupied** — the low question count is the rule working, not a gap |
| present, fires, and the question keeps coming | high | **not a vacancy at all** — see Step 2's last row. The job is being done and disbelieved, which a job title cannot fix |

The third row is the one that gets missed. A question the user rarely asks looks like a small
cluster; it is often a seat that is already filled. Read it as evidence the rule is doing its job,
not as a role with weak support.

The fourth row is the one that produces a wrong hire. A reviewer given only the question counts read
24 recurring "did you verify this" as a vacant quality-assurance role; the firing column showed the
rule running 295 times over the same month. Counted, it looked like nobody was doing the job. Counted
against firing, the job was being done and not believed — and appointing someone to it would have
changed nothing.

This is Step 2's friction-against-firing applied to roles, and skipping it turns Step 4 into a
counting exercise that contradicts the rest of the audit.

### Say what it displaces

Attention is finite: across sixteen isolated runs the framing moved what got mentioned, so
mentioning one thing more means mentioning something else less. A role proposal has to name the
attention it competes with, and the strongest competitor is whatever is currently *working*.

A verification role, for instance, pulls attention toward proving the last step ran — and away from
scope and the next integrated step, which is where a well-fed engineering role spends it. Say that
in the proposal:

> Installing this displaces `<the currently working attention>`, which is firing `<n>` times.
> Watch that count on the next run; if it falls, the trade was real and you should decide whether
> you want it.

That makes the trade checkable on the next audit instead of a claim nobody revisits.

### Then say it, every run

**Required output, including runs that change nothing:**

> Role: `<name>` — default question: `<the one it asks before every reply>`. Chosen because
> `<the recurring question and how many separate occasions it appeared on>`.

Saying "Chief Engineer, unchanged — 'what breaks without it' on nine separate occasions" is the
output. Silence is not: the previous version of this step was written as optional and produced
nothing in several independent runs, because its only actionable rule was conditional on finding a
blind spot, and runs that found none correctly stopped.

**What a role does not do.** Across sixteen isolated runs on two task shapes, the framing did not
change what the agent recommended — the task decided that every time. One dimension separated: how
often a reply named who owns a thread, 3 and 3 under a chief-of-staff framing against 0 and 1 under
an engineering one. So install the question as a rule if the behaviour has to happen every run; the
role is the handle the user holds a dozen rules by, not the mechanism.

## Remedies already measured

Most rules this audit proposes are written fresh from the user's own accepted repair. A few have
been measured well enough to offer as a known text, and those are listed here. Offer one only when
its friction category actually shows up — an unprompted remedy is a rule with no failure behind it,
which is the thing this audit exists to remove.

### Close-out block — for the `status pull` category

When the friction is the user asking what is left, whether a thread can be closed, or whose move it
is, the remedy is a required field at the end of any reply that ends a unit of work:

```
Remaining: …
Next:      … (you / me)
Closable:  yes / no / unverified
```

Five things make it work, and dropping any of them breaks it:

- **A fenced block, never inline backticks.** A long inline span wraps into broken fragments in a terminal.
- **`Closable: yes` only after checking** — working tree, open PRs, task state. Unchecked is `unverified`. A wrong `yes` ends a session that still has live work, and that is the expensive failure; the other two fields cost nothing when wrong.
- **It replaces the empty closer**, it does not sit above one. "Want me to continue?" is what it exists to delete.
- **Write the labels in the language the reply is in.** The block is read every turn by someone whose comprehension cost is the thing it exists to lower; an English label at the end of an otherwise Chinese answer taxes that every time. The template above is the English wording, not a requirement to use English.
- **Enumerate the wordings, do not fix the language.** What breaks measurement is unbounded variation, not translation: a `firing` pattern is a regex, so `可收線|Closable` costs one alternation and covers both. Settle on one wording per language and add every one of them to the pattern — a synonym invented later is what silently zeroes the row.

## Step 5 — Decide, one at a time

Put each change to the user as a single decision with: the evidence, your recommendation, **what
gets worse under your recommendation**, what breaks if the choice is wrong, and the reversal cost.
Use the harness's question UI. Do not bundle — coupled decisions may share a turn only when one
answer changes the other's options, and then say why in one sentence.

Run the user's own necessity test on every rule you propose to add, including the ones you are
tempted to slip in because they are obviously good. A rule that did not survive a decision does
not belong in the file.

## Step 6 — Apply, and find the orphans

1. Back up the current file with a dated name. Verify the copy is byte-identical before overwriting. A rule file outside version control has no other record.
2. Swap, then verify: line count, section list, any `@` imports still present.
3. **Grep for orphaned references.** Every removed or renamed section may be quoted by a skill, an agent definition, or a reference doc. Report what still points at the old wording — including drift that predates this change.
4. Reconcile memories. A memory that now duplicates a rule should usually be **rewritten to keep only the evidence**, not deleted; the rule states what to do, the memory records what it cost to learn. Memory deletion needs the user's approval and must name the surviving source of truth.

Tell the user plainly that a rule file is read at session start, so open sessions keep the old
rules until they restart.

## Optional route — propagate across harnesses

**Offer this; never do it silently.** After a user-level `~/.claude/CLAUDE.md` change, ask whether
to carry its portable semantics into user-level `~/.codex/AGENTS.md`. For a repository rule file,
offer the sibling harness file in that repository. Do not mix user-level and repository scope.

Split the ruleset before offering, because not all of it should travel:

| Travels | Stays harness-specific |
|---|---|
| Necessity and retention tests | Question-UI and narration formats |
| Upstream-first and ownership rules | Harness-specific tool and worktree paths |
| Decision hygiene, conclusion-first | Plugin or skill routing |
| Cost and measurement discipline | Anything naming one harness's files |

Then run Step 6's orphan grep again against the repos you touched. Propagation creates new copies,
and a copy is correct only until one side moves — say which file is authoritative.

### Prove Codex behavior before applying the user file

Text parity is not behavior parity. Translate each traveling semantic rule into a Codex-native,
observable checkpoint. For example, a durable-addition gate can require a named marker before the
first write tool call. A marker mentioned only in the final report is self-attestation, not proof.

Run one isolated A/B before replacing `~/.codex/AGENTS.md`:

1. Create two fresh `CODEX_HOME` directories from the same current user `AGENTS.md`; add the
   candidate rule only to the green home. Keep authentication available without copying credentials
   into the fixture or report.
2. Run the same clean fixture, prompt, Codex version, model, and reasoning level in fresh
   `codex exec --ephemeral` sessions.
3. Inspect the event order, not only the final text. The green checkpoint must occur before the
   governed action; baseline must lack it; both runs must still deliver the requested outcome.
4. If the runs do not separate, the rule is not proven for Codex. Rewrite it as a lower-freedom
   checkpoint or leave it unsynced and report the gap.
5. After a pass and the user's propagation decision, apply Step 6 to the real user file and restart
   open Codex sessions. Never replace the live user file merely because the candidate text matches.

## Common mistakes

| Mistake | What to do instead |
|---|---|
| Treating high friction as a missing rule | Check firing first. The rule is usually already there. |
| Quoting the script's counts as fact | Read `rule-review-human-turns.tsv`. Regexes over-match. |
| Deleting a zero-firing rule immediately | Ask which kind of zero, then grep for an owner. |
| Bundling several rule changes into one question | One decision per turn. |
| Adding an obviously-good rule without a decision | It has to earn its place like every other rule. |
| Counting the agent's own dispatch prompts as user corrections | The script filters them; keep the filter if you adapt it. |
| Reporting the file got shorter | Measure bytes too — more checkable lines can be fewer bytes. |

## Red flags

- You are about to write a paragraph explaining a rule the file already contains.
- You cannot name an observable marker for a rule you are adding. It will not fire either.
- You are deleting a section without having grepped for who references it.
- You are declaring the ruleset improved without a rerun of Step 1 to compare against.
