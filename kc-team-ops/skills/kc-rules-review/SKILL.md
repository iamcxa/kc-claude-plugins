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

- The user says some version of 「我一直在糾正同一件事」or "you keep doing this".
- The user quotes their own rule back at you — the strongest possible signal, because it proves the rule exists and did not fire.
- A rule file has grown and nobody knows which parts still earn their place.
- A rule change just landed and downstream files may quote the old section names.

**Do not use** for a single skill's behaviour in a single repo — `recce-team:reflection` owns that
(one target skill, one repeated problem, one gated fix). Do not use for a memory inventory —
`recce-team:memory-survey` owns that. This skill is the fleet-wide, whole-rule-set pass.

## Step 1 — Measure

```bash
kc-team-ops/scripts/rule-firing-report.sh --since YYYY-MM-DD --patterns your.tsv
```

The patterns file is TSV: `kind<TAB>label<TAB>regex`, where `kind` is `friction` or `firing`.
Declare one `firing` row per rule that has an observable marker (a required prefix, a field name,
a file the rule makes you read). **A rule with no possible marker cannot be measured, and that is
itself the finding** — see Step 2.

Counts are for comparing runs, not for quoting as truth. The script writes every matched human
turn to `rule-review-human-turns.tsv`; read the hits before you believe a number.

The bundled report script reads Claude Code logs only. When `~/.codex/AGENTS.md` is the target,
use those counts only as source-rule evidence; prove Codex firing with the isolated A/B route below.
Never label Claude firing counts as Codex behavior.

## Step 2 — Cross-tabulate

| Friction | Firing | Verdict |
|---|---|---|
| high | low | **Rule exists, no trigger.** Rewrite it as a check with a countable condition. Do not add prose. |
| high | zero | **Rule missing.** Add it — as a check, not a paragraph. |
| low | zero | **Candidate for deletion** — but first ask which of the two zeros this is. |
| low | high | **Working.** Leave it alone. |

**Two kinds of zero, and they get opposite treatment:**

- *Zero because never needed* — genuinely dead weight. Delete.
- *Zero because it worked* — a safety rule whose whole value is that it is never violated. Deleting it is how you find out.

Separate them by asking what the world looks like if the rule is gone, not by counting.

## Step 3 — Check for an owner before deleting

A rule that looks dead is often a **duplicate of a live capability that owns the concept
elsewhere** — a plugin reference, a stage contract, a test that asserts the path. Grep the fleet
for the concept before cutting.

- Found an owner → **propose deleting the copy and name the owner**, through Step 4 like any other change. Do not delete it yourself; removal is the user's call.
- Found no owner → the rule is the only home. Removing it drops the capability.

Finding an owner is the start of the check, not the end. Before proposing removal, answer both:

- **Does the assertion cover content or only existence?** A contract test that asserts a path
  resolves does not stop the two copies from saying different things. Diff them. If they have
  already drifted, deleting the copy silently drops whatever only the copy says.
- **Do they load in the same places?** An owner loaded by two stage contracts does not cover a rule
  file read in every session. Removing the copy narrows where the rule applies, and that narrowing
  is the real cost to put in front of the user.

## Step 4 — Decide, one at a time

Put each change to the user as a single decision with: the evidence, your recommendation, **what
gets worse under your recommendation**, what breaks if the choice is wrong, and the reversal cost.
Use the harness's question UI. Do not bundle — coupled decisions may share a turn only when one
answer changes the other's options, and then say why in one sentence.

Run the user's own necessity test on every rule you propose to add, including the ones you are
tempted to slip in because they are obviously good. A rule that did not survive a decision does
not belong in the file.

## Step 5 — Apply, and find the orphans

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

Then run Step 5's orphan grep again against the repos you touched. Propagation creates new copies,
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
5. After a pass and the user's propagation decision, apply Step 5 to the real user file and restart
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
