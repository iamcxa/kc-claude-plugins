# Story interrogation

Before a release goes to development, two strangers question its stories against the code,
and every question leaves the map answered, deferred, or linked to a decision record.
The point is to move decisions earlier: a question answered here is a question the build
does not stop on.

## When

- After a release is cut and before `lib/journey-handoff.mjs` produces its brief. The
  handoff refuses while any story in the selected release has an unanswered question.
- On stories that already exist, to find the gaps between the story and what was built.
  Answer those as gaps; they feed the next release instead of blocking one.

## Snapshot

Give the workers the code as it stands, without history, so they cannot read ahead:

```bash
git -C <repo> archive <ref> | tar -x -C <snapshot>
```

For a retroactive run on a built release, use the ref from before the release started.

## Prompt

One prompt, both workers. Replace the bracketed parts.

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

## Running the two workers

Run them in parallel from the snapshot directory:

```bash
cd <snapshot> && claude -p --model sonnet --tools Read,Grep,Glob --allowedTools Read,Grep,Glob \
  --output-format stream-json --verbose < prompt.md > claude-events.jsonl
codex exec --sandbox read-only --skip-git-repo-check --cd <snapshot> --json \
  -o codex-answer.md - < prompt.md > codex-events.jsonl
```

The Claude answer is the `result` event's text. `--sandbox read-only` stops codex writing,
not reading, so isolation is by instruction for both. Audit it from the event streams
before trusting the questions: every Claude `tool_use` `file_path`/`path`, and every codex
`command_execution` command, must stay inside the snapshot. Report the audit result
with the questions. The time box is self-reported; the read count is the real budget.

Keep both workers. In the first two runs (one release, before and after it was built),
codex asked more of the questions the build later hit (12 of 17 against 4 of 17), but
Claude alone asked the question that became a brand-level data decision. Both missed the
three concurrency and bypass issues that only appeared while building. Interrogation does
not replace validation.

## Answering and triage

Deduplicate the two lists, then answer each question from the code at the current head,
naming the symbol you read. Sort every question into one of four classes with the human:

| Class | Where it goes |
|---|---|
| Fact — the code or a record already answers it | `answer:` on the story |
| Gap — the story promises what the code does not do | `answer:` stating the gap; the next release picks from these |
| Decision — only the human can settle it | the project's decision record, then `answer:` plus `doc:` linking the entry |
| Already tracked — an existing task owns it | not recorded; name the task in the triage |

Ask the human one decision at a time. Record the ruling in the project's decision record
before linking it: follow the convention the project already has (for example
`docs/adr/`), and create one only when none exists. The development flow writes its own
lasting rulings into that same record, so both tools meet there without either knowing
the other.

A question with no answer yet stays open on its story, or is deferred with `because:`
when it belongs to a later release. Record questions in block form:

```yaml
- id: <story-id>
  release: <release-id>
  card: "..."
  questions:
    - {id: q1, ask: "...", answer: "...", doc: "<decision-record link>"}
```

Run `node lib/journey-lint.mjs <journey.yaml> <repoRoot>`; the release board draws each
question with its answer beside it.
