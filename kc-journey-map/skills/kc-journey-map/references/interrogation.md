# Story interrogation

Before a release goes to development, a stranger questions its stories against the code,
and every question leaves the map answered, deferred, or open with the decision that settles it.
The point is to move decisions earlier: a question answered here is a question the build
does not stop on.

## When

- After a release is cut and before `lib/journey-handoff.mjs` produces its brief: it is
  step 0 of `release-review.md`, before the walk. The handoff refuses while any story in
  the selected release has an unanswered question.
- On stories that already exist, to find the gaps between the story and what was built.
  Answer those as gaps; they feed the next release instead of blocking one.

## Snapshot

Give the workers the code as it stands, without history, so they cannot read ahead:

```bash
git -C <repo> archive <ref> | tar -x -C <snapshot>
```

For a retroactive run on a built release, use the ref from before the release started.

## Prompt

One prompt. Replace the bracketed parts.

```text
You are a stranger to this project, asked to interrogate [N] user stories [before anyone
builds them | that are already built]. You only ask questions; you do not design, fix, or
write code.

Project snapshot (read ONLY this directory; do not read any other path on this machine,
and do not use git): <snapshot>
- Story map: <journey.yaml> — release `<release-id>` and its stories. Questions already
  recorded under a story's `questions:` list count as asked; do not repeat them.
- Architecture decisions: <decision-record path(s)>.
- Code: <code roots>.

The stories: <id — card, one line each>

Task: find the questions whose answer would change what gets built, reveal a gap between a
story and the code, or expose behaviour nobody has decided. Ground every question in
something you read: quote the story/decision line or name the code symbol that raises it.
Cover product behaviour, data/concurrency, security/permissions, operations, cost, and
testing. Skip questions the snapshot already answers clearly.

Time box: stop after about 15 minutes or 40 file reads, whichever comes first.

Output: write nothing to disk. Reply with a numbered list, at most 25 questions, most
consequential first. Each item:
Q: <question, one sentence>
Story: <story id or "all">
Grounds: <quoted line or code symbol + file>
Why it matters: <one sentence>
End with one line: "Reads: <n>, minutes: <n>".
```

Append this lens block for the default run and leave it out of the plain run:

```text
Reviewer lens. Judge which questions are worth asking by this discipline; the output format
above is unchanged. State the technical claim and the decision it affects. Check the evidence
against primary behaviour and governing limits. Separate an observed defect from an unsupported
possibility. Name the risk, how reversible it is, the durable obligation and the cheapest
credible alternative. Say what evidence would change the answer. Do not manufacture dissent or
ask the author to disprove ungrounded possibilities; raise a question only when its answer can
change the route, an accepted risk, or who decides.
```

## Running the stranger

One Codex run, with the lens, from the snapshot directory:

```bash
codex exec --sandbox read-only --skip-git-repo-check --cd <snapshot> --json \
  -m gpt-6.1-sol -c model_reasoning_effort='"high"' -o codex-answer.md - < prompt.md > codex-events.jsonl
```

Add a second, plain run (same command, prompt without the lens block) when the caller says the
release holds a decision that is hard to reverse: an event model, an architecture, a security
boundary or a data migration. Run no Claude worker. If `codex` is missing or the model is
refused, stop with `interrogation not run: <reason>`; `journey-review.mjs check` refuses a
record that says so.

`--sandbox read-only` stops Codex writing, not reading, so isolation is by instruction. Audit it
from the event stream before trusting the questions: every `command_execution` command must stay
inside the snapshot. Report the audit result with the questions. The time box is self-reported;
the read count is the real budget. The pinned model name goes stale and is edited by hand.

Why one stranger: two POCs scored the same five task snapshots against 13 key items, one run
per arm and one scorer. `gpt-6-astra` with the lens hit 6, `gpt-6.1-sol` with the lens 6 and sol
plain 5: no difference within one item. The lens and plain runs hit different items on three of
the five tasks, which is why a plain run is added for a hard-to-reverse decision. The Captain
kept sol with the lens because astra costs more. Interrogation does not replace validation.

## Answering and triage

Answer each question from the code at the current head, naming the symbol you read, then sort it
into one class:

| Class | Where it goes |
|---|---|
| Fact: the code or a record answers it | `answer:` on the story, no `source` |
| Gap: the story promises what the code does not do | `answer:` stating the gap; the next release picks from these |
| Already tracked: an existing task owns it | not recorded; name the task in the triage |
| Unconfirmed or duplicate | dropped and counted in the record's `dropped` |
| Decision: only the human settles it | ask; its home follows the five questions below |

A decision's home is the first "yes" of kc-adr's five questions. A ruling about this slice only
(question 3) or about one future task that he settles now (question 2: no task file exists yet, so
ask "settle now, or hold the release") is the question's `answer:` and `source:`. A ruling later
work must respect (question 5) is also written on the question and its id goes in the record's
`Carries` as `ADR owed: <question id>`; the first task filed on that story drafts the ADR from
`source.words`, and its pull request replaces `answer:` with a `doc:` trunk URL. An instruction to
agents (question 4) is reported to the caller and not written to the map. One held for a future
task stays open and the handoff waits.

**Rank and cap.** List the decision rows once, hard to reverse first, then by the number of
release stories whose handoff each blocks, each with a recommendation and what gets worse under
it. Ask them one at a time; a sitting asks at most 10 and the rest stay open for the next sitting.
The cap of 10 holds the one observed release (nine open after interrogating four stories); its
value is not measured.

**Writing a ruling.** On every ruling on a release question write `answer:` as one line,
`status: answered` and `source: {kind: release, ref: "<journey>/<release-id>", words: <his words>,
date: <YYYY-MM-DD>}`. Do not write `source` for a fact or a gap. A `doc:` link is a trunk URL,
because the canvas rejects a relative one and a link into a working branch dies. A gap that belongs
to no release is added with `journey-add-story.mjs`, which writes no `release`.

A question with no answer yet stays open on its story, or is deferred with `because:` when it
belongs to a later release. Record questions in block form:

```yaml
- id: <story-id>
  release: <release-id>
  card: "..."
  questions:
    - {id: q1, ask: "...", status: answered, answer: "...", source: {kind: release, ref: "<journey>/<release-id>", words: "...", date: 2026-10-22}}
```

Run `node lib/journey-lint.mjs <journey.yaml> <repoRoot>`; the release board draws each
question with its answer beside it.
