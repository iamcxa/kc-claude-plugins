# Contract: Captain question records (`asks.jsonl`, format version 1), revision 2

Format version 1, contract revision 2, 2026-11-14.
Nothing here is a Spacedock (workflow runtime) format; kc-dev-flow-2 writes it.

## 1. What this is

A dev2 First Officer (FO, the agent that runs a workflow) sometimes asks the
Captain (the human owner) a question outside a scheduled Spacedock gate. Each such
question is one **record**. A record is **open** from the moment it is asked until
the Captain's answer is recorded or the FO withdraws it. Only open records wait on
the Captain.

A reader can list every open question of a workflow, with who waits, since when and
what the answer holds, by reading files only.

## 2. Where records live

- The reader knows which project and workflow it reads from the checkout or branch
  it reads; no line names them. For this workflow the branch is
  `spacedock-state/dev2` of `iamcxa/kc-claude-plugins`.
- One file per task, in the task's folder:

  | Task file | Record file |
  | --- | --- |
  | `<slug>.md` | `<slug>/asks.jsonl` (the folder may hold nothing else) |
  | `<slug>/index.md` | `<slug>/asks.jsonl` |
  | `_archive/<slug>.md` or `_archive/<slug>/index.md` | `_archive/<slug>/asks.jsonl` |

- To enumerate, list the branch's paths (`git ls-tree -r --name-only <ref>`) and
  keep those matching `^(_archive/)?[^/]+/asks\.jsonl$`. A task archived while a
  question is open is a writer error; a reader lists it and may report it.
- A question is filed under the task the FO was working on when it arose, including
  a question about whether to open a new task. A question raised while no task was
  in progress is not covered by version 1.
- Files are append-only: a line once written keeps its content and position. Lines
  reach the remote branch when the FO pushes its state commit, usually minutes later.
- An absent file means "no record kept for this task", not "no questions".

## 3. Line format

One JSON object per line, UTF-8. Times are UTC, `YYYY-MM-DDTHH:MM:SSZ`, whole
seconds. Every version-1 line carries:

| Field | Type | Meaning |
| --- | --- | --- |
| `v` | integer | `1`. |
| `event` | string | `ask`, `reask`, `revise`, `answer`, `acted` or `withdraw`. |
| `key` | string | `<slug>#<n>`, n = 1, 2, … counting only `ask` lines of this file. Never reused, never renumbered. |
| `at` | string | When the line was written, from the machine clock. |

**Legacy lines** (kc-dev-flow-2 0.40.0 to 0.41.x) have no `v`:
`{"at": "...", "asked": "<text>"}`. Each is one question shown at `at`, state
unknown: list it neither as open nor as answered. It takes no key number.

**Forward compatibility.** Ignore fields this document does not define. Ignore a line
whose `event` is unknown. A line with `v` greater than 1: show its key's state as
unknown rather than guess.

### 3.1 `ask`

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `asked` | string | yes | The question exactly as shown. |
| `asked_at` | string or null | yes | When it was shown. Equal to `at` when written at the moment of asking. `null` when written afterwards; never estimated and never corrected later. |
| `channel` | string | yes | `chat`, `dialog` (the host's question dialog), `review` (a Spacedock Review briefing) or `message` (relayed by another agent). |
| `by` | string | yes | The asking FO's session name: who waits. |
| `holds` | string | yes | `task`: no work proceeds on this task until answered. `acceptance`: work continues, but the task cannot pass its next gate or be delivered until answered. `nothing`: work continues; the answer shapes later work only. |
| `options` | list | no | Each `{"id": "<short id>", "text": "<as shown>", "effect": "<what follows if chosen>"}`; `effect` optional. Absent means an open-ended question. An id keeps its meaning for the life of the key. |
| `recommend` | string or null | no | An id in `options`, or null. |
| `grounds` | string | no | FO's reason for the recommendation, as shown. |
| `approve_means` | string or null | no | The option a plain approval (an approve with no words) selects. Set only when the shown question says so in words; otherwise null. |
| `tasks` | list of strings | no | Other task slugs the answer applies to. The record exists once; those tasks do not repeat it. |
| `refs` | list | no | Material to look at: `{"kind": "file" \| "commit" \| "url" \| "command" \| "record", "ref": "<...>", "ready": true \| false}`. A `file` is relative to the task folder; a `record` is a Spacedock id in the same branch. `ready: false`: it does not exist yet. |

This is revision 1 of the question.

### 3.2 `reask` — shown to the Captain again

Fields: `channel`; `briefing` (string or null): the Spacedock Review briefing id when
this showing published the question there. A reask shows the current revision. Each
`ask` and `reask` is one showing, so one interruption; no other line is.

### 3.3 `revise` — the question changed while open

Fields: `revision` (previous + 1), `reason` (required), and the complete new value of
`asked`, `holds`, `options`, `recommend`, `grounds`, `approve_means`, `tasks`,
`refs`. An optional field left out of a revise is empty in the new revision, not
carried over. A revise is not a showing: when the FO shows the revised question it
also writes a `reask`. A revise does not change waiting-since. Earlier revisions stay
readable in their own lines; revision n is the `ask` (n = 1) or the `revise` with
`revision: n`.

### 3.4 `answer`

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `revision` | integer | yes | The revision current at the latest showing in the channel he answered in. |
| `words` | string or null | yes | His words verbatim; null when he gave none. |
| `option` | string or null | yes | The option he chose, read from his words or his button; for an answer without words, that revision's `approve_means`. Null when the question had no options or his words choose none. |
| `resolution` | string or null | yes | The Spacedock Review resolution id when he answered on Review; otherwise null. |
| `channel` | string | yes | Where he answered. |

At least one of `words` and `option` is non-null. An answer without words to a
question with options and a null `approve_means` cannot be written: the FO asks
him which option. `option` is read against the answered revision's options, so an
answer to an older revision stays valid; if the FO judges it no longer applies, the
FO asks a new question (a new key) rather than reopening this one.

### 3.5 `acted`

Field: `what` (string). The FO did what the answer asked.

### 3.6 `withdraw`

Field: `reason` (string). The FO no longer needs the answer.

## 4. State of a question

```
ask ──► open ──answer──► answered ──acted──► done
         │ reask, revise
         └──withdraw──► withdrawn
```

Fold the lines of one key in file order. Before its `ask`, a key's lines are
ignored; a second `ask` with the same key is ignored. The first `answer` or
`withdraw` closes the question and decides its state. After it, the only valid line
is one `acted`, and only after an `answer`. Every other line after closing is a
writer error: ignore it and report it.

## 5. What a reader may rely on

| Reader field | How to compute |
| --- | --- |
| key | `key`. A new line with the key means the record changed. |
| question, options, recommendation, grounds, approve_means, holds, refs, tasks | from the current revision. |
| who waits | `by` of the `ask`. |
| waiting since | `asked_at` of the `ask`. When null, show unknown; the question was shown no later than the `ask` line's `at`, so the wait is at least `now − at`. Never use a reask, revise or Review time. |
| interruptions | number of `ask` and `reask` lines. |
| last shown | the latest `ask` or `reask`: its `at`, `channel` and `briefing`. |
| state | section 4. Open: waits on the Captain. Answered: waits on the FO. Done and withdrawn: closed. |
| holds | three values as in 3.1; do not collapse them. |

A reader may not rely on: `grounds`, `effect`, `what` or `reason` being
machine-readable; a question the FO forgot to record existing at all; questions
inside Spacedock gates, which are gate records in the task file, not in this file.

## 6. Example

```json
{"v":1,"event":"ask","key":"demo-task#1","at":"2026-11-13T08:00:05Z","asked_at":"2026-11-13T08:00:05Z","asked":"Open the task with this scope? Approving accepts option yes.","channel":"dialog","by":"dev2 FO","holds":"nothing","options":[{"id":"yes","text":"Open it","effect":"FO files the task in backlog"},{"id":"no","text":"Not now"}],"recommend":"yes","grounds":"Two FOs relayed the same need today.","approve_means":"yes"}
{"v":1,"event":"reask","key":"demo-task#1","at":"2026-11-13T09:10:00Z","channel":"review","briefing":"briefing:demo-task:ask-1"}
{"v":1,"event":"answer","key":"demo-task#1","at":"2026-11-13T09:12:30Z","revision":1,"words":null,"option":"yes","resolution":"resolution:review:demo-task:1","channel":"review"}
{"v":1,"event":"acted","key":"demo-task#1","at":"2026-11-13T09:15:00Z","what":"Filed the task"}
```

## 7. Not covered by version 1

- A question raised while no task was in progress: FO first files the proposed task
  with Spacedock new and asks through its backlog gate.
- Open Spacedock gates. A lister may show them beside these records, read from the
  task files' `gates:` records; that is not this format.


## 8. Commands and gate rows

After `python3 <package>/scripts/task_timeline.py <state> <task>`, use
`ask "<question>" --by "<session>" --holds <task|acceptance|nothing>`.
The writer stamps UTC times and prints commands for later showings, answers and
withdrawals. `--channel` defaults to `chat`; `--late` writes `asked_at: null`.
`--option id=text[=effect]`, `--ref '{"kind":"file","ref":"design.md","ready":false}'`
and `--tasks other-task` may accompany an ask or revise; options and refs may repeat.
Use `--recommend id`, `--grounds "<reason>"`, and `--approve-means id` for the
recommendation and the stated meaning of approval. Revise takes a key,
`--revision N --question "<new question>" --holds <value> --reason "<reason>"`,
and the complete replacement fields. Reask takes a key, `--channel` and optional
`--briefing`. Answer takes a key, `--channel`, optional `--words`, `--option id`
and `--resolution`; its revision defaults to that channel's latest showing.
Acted takes a key and `--what`; withdraw takes a key and `--reason`.

`python3 <package>/scripts/task_timeline.py <state> --open --json` lists open
questions. Add `--as-of <UTC>` to fold lines written by that instant. The derived
`question` field is `asked` from the current revision; `waiting_min` is elapsed
minutes with `waiting_bound: exact` or `at least`. An unknown `waiting_since`
stays null, with the lower bound measured from `recorded_at`. `publish_review`
is true after three showings without a Review showing; FO publishes the briefing
and records a reask. This flag itself publishes nothing.

Add `--gates` to include each unresolved attempt in the task files' Spacedock
gate records once. Its question comes from the bound briefing, its owner is
unknown (`by: null`), and its wait is **at least** the time since the first state
commit naming the briefing id, using the author date; a missing or impossible
date stays unknown. Gate rows are not written into `asks.jsonl`.

The amendment omission check starts on the author date of the first commit introducing the approved ask sentence in the adopted workflow README, locating that README's repository with git; unavailable history, shallow history or an absent sentence skips this rule with a diagnostic.
`python3 <package>/scripts/design_surfaces.py check <task>` refuses an amendment
on or after that date whose `Asked:` question is absent from its task's records
and records naming the task in `tasks`. A late record restores the count without
inventing an asking time. Existing timing reports and legacy reading remain in
force under ADR 0080; only this omission check changes its report-only choice.
