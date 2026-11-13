# Contract draft: Captain question records (`asks.jsonl`, format version 1)

Status: draft for a blind reader, 2026-11-14. Not yet implemented. Nothing in this
document is a Spacedock (workflow runtime) format; it is written by kc-dev-flow-2 only.

## 1. What this is

A dev2 First Officer (FO, the agent that runs a workflow) sometimes asks the
Captain (the human owner) a question outside a scheduled Spacedock gate. Each such
question is one **record**. A record is **open** from the moment it is asked until
the Captain's answer is recorded or the FO withdraws it.

A reader (a dashboard, an inbox, a script in another repository) can list every
open question of a workflow, with who waits, since when, and whose move it is, by
reading files only. A reader never needs to read chat, labels or reply text.

## 2. Where records live

- One file per task: `<state checkout>/<task slug>/asks.jsonl`, next to the task
  file `<state checkout>/<task slug>.md`. A task stored as `<slug>/index.md` uses
  the folder `<slug>/`.
- The state checkout is a git branch (for this workflow `spacedock-state/dev2`).
  A reader in another repository reads it with `git show <ref>:<path>` or a clone;
  it needs no access to the FO's machine.
- A file is append-only. The writer never edits or deletes a line. A reader may
  rely on this: a line once seen keeps its content.
- Only the tool `task_timeline.py` writes these lines (section 7). Lines are
  committed by the FO in its normal state commits, so a reader on the remote
  branch sees a line only after that commit is pushed. Expect a lag of minutes.
- A file absent means "no record kept for this task", not "no questions".

## 3. Line format

Each line is one JSON object, UTF-8, no line breaks inside. Every line written by
this version carries:

| Field | Type | Meaning |
| --- | --- | --- |
| `v` | integer | Format version. This document defines `1`. |
| `event` | string | One of `ask`, `reask`, `revise`, `answer`, `acted`, `withdraw`. |
| `key` | string | Stable id of the question: `<task slug>#<n>`, n = 1, 2, … in order of `ask` lines in this file. Never reused, never renumbered, unchanged by a title edit or a revision. |
| `at` | string | UTC time the tool wrote the line, ISO 8601 with `Z`, from the machine clock. Never typed by hand. |

Lines in one file are in the order they were written. Times may be compared
across files.

A line without `v` is a **legacy line** (written by kc-dev-flow-2 0.40.0 to 0.41.x):
`{"at": "...", "asked": "<question text>"}`. It counts as one question asked at
`at`. Its later state is unknown: a reader must not list it as open and must not
list it as answered. It has no key; if a reader needs one, use
`<task slug>#legacy-<line number>`.

### 3.1 `ask` — the question is put to the Captain

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `asked` | string | yes | The question exactly as shown to the Captain (same field name as legacy lines). |
| `asked_at` | string or null | yes | When the question was shown. Equals `at` when the tool ran at the moment of asking (the rule). `null` when the FO records it afterwards: **waiting since is unknown**. Never an estimate. |
| `channel` | string | yes | Where it was asked: `chat`, `dialog` (the host's question dialog), `review` (a Spacedock Review briefing), `message` (an agent-to-agent relay). |
| `by` | object | yes | Who waits: `{"name": "<FO session name>", "agent_id": "<id or null>"}`. `agent_id` is null when the host gives none. |
| `options` | list | no | Choices offered, each `{"id": "<short id>", "text": "<as shown>"}`. Absent or `[]` for an open-ended question. |
| `recommend` | string or null | no | The option id FO recommends, or null for none. |
| `grounds` | string | no | FO's reason for the recommendation, one or two sentences, as shown. |
| `holds` | string | yes | What waits on the answer: `task` (no work proceeds on this task), `acceptance` (work continues, but the task cannot pass its next gate or delivery until answered), `nothing` (work continues; the answer changes later work only). |
| `refs` | list | no | Material the Captain is asked to look at, each `{"kind": "file" \| "commit" \| "url" \| "command" \| "record", "ref": "<path, sha, url, command or record id>", "ready": true \| false}`. `ready: false` means it does not exist yet (for example, a report still running). |

The question's **revision** after an `ask` is 1.

### 3.2 `reask` — the same question shown again

Fields: `channel` (as above); `briefing` (string or null: the Spacedock Review
briefing id or URL when this re-ask published the question there). A re-ask does
not change the question, the options or the waiting-since time. Each re-ask is one
more interruption of the Captain.

### 3.3 `revise` — the question or its options changed while open

Fields: `revision` (integer, previous + 1) and the full replacement of every
`ask` field that the FO shows to the Captain: `asked`, `options`, `recommend`,
`grounds`, `holds`, `refs`. A reader takes the latest `revise` (or the `ask` if
none) as the current text. A revision does not reset waiting-since: the Captain
has been waiting on this decision since the first `ask`. `reason` (string, required)
says why it changed.

### 3.4 `answer` — the Captain's answer is recorded

| Field | Type | Required | Meaning |
| --- | --- | --- | --- |
| `revision` | integer | yes | The revision the answer was given against. |
| `words` | string or null | yes | His words, verbatim. `null` when he answered without words (for example a Review approve button). |
| `option` | string or null | yes | The option id he chose, when it can be read without interpretation (he pressed it, or his words name it). Otherwise null. |
| `resolution` | string or null | yes | The id of the record that holds his answer outside this file: a Spacedock Review resolution id, or null for chat and dialog answers. |
| `channel` | string | yes | Where he answered, same values as `ask`. |
| `said_at` | string or null | yes | When he answered, copied from a source that stamps it (a Review resolution). `null` when no source stamps it; then the answer happened no later than `at`. |

At least one of `words`, `option`, `resolution` is non-null. If `revision` is less
than the current revision, he answered an earlier version; the record is still
answered and the reader should show the mismatch.

### 3.5 `acted` — FO acted on the answer

Fields: `what` (string: what FO did), `refs` (list, as in `ask`: for example the
Captain amendment, the gate resolution id, the commit).

### 3.6 `withdraw` — FO no longer needs the answer

Fields: `reason` (string: for example "superseded by gate <id>", "asked again as
<key>", "no longer needed because …"). A withdrawn question is closed without an
answer.

## 4. State of a question

A reader folds the lines of one `key` in file order:

```
ask ──► open ──answer──► answered ──acted──► done
         │  ▲                │
     reask │ revise          └─(acted may never come; answered is a valid resting state)
         │
         └──withdraw──► withdrawn
```

- **open**: has `ask`, no `answer`, no `withdraw`. Only open questions are waiting on
  the Captain.
- **answered**: has `answer`, no `acted`. Waiting on the FO.
- **done**: has `acted`.
- **withdrawn**: has `withdraw` and no `answer`.

Any event after `answer` or `withdraw` other than `acted` is a writer error; the
reader keeps the first closing event and may report the rest.

## 5. What a reader may rely on

For each key, a reader may compute and show:

| Reader field | How to compute |
| --- | --- |
| kind | always `question` for this file. |
| key | `key`. |
| version | number of lines with this key; it rises on every change. |
| task | the folder name. |
| question | `asked` of the latest `revise`, else of the `ask`. |
| options, recommendation, grounds, holds, refs | same source as question. |
| who waits | `by` of the `ask`. |
| waiting since | `asked_at` of the `ask`; `null` means unknown. Never the time of a re-ask, a revision or a Review publication. |
| interruptions | 1 + number of `reask` lines. |
| last shown | `at` of the latest `ask` or `reask`, and its `channel` and `briefing`. |
| state | section 4. |
| whose step | `captain` when open; `fo` when answered; none when done or withdrawn. |
| blocked or continuing | `holds` of the current revision: `task` = blocked; `acceptance` and `nothing` = continuing. |

A reader may not rely on: the text of `grounds` or `what` being machine-readable;
`option` being set whenever `words` exist; any line existing for a question the
FO forgot to record (an omitted ask is invisible); questions inside Spacedock gates
(those are gate records in the task file's frontmatter, not in this file).

## 6. Examples

```json
{"v":1,"event":"ask","key":"demo-task#1","at":"2026-11-13T08:00:05Z","asked_at":"2026-11-13T08:00:05Z","asked":"Open the task with this scope?","channel":"dialog","by":{"name":"dev2 FO","agent_id":"a1b2"},"options":[{"id":"yes","text":"Open it"},{"id":"no","text":"Not now"}],"recommend":"yes","grounds":"Two FOs relayed the same need today.","holds":"nothing","refs":[]}
{"v":1,"event":"reask","key":"demo-task#1","at":"2026-11-13T09:10:00Z","channel":"review","briefing":"briefing:demo-task:ask-1"}
{"v":1,"event":"answer","key":"demo-task#1","at":"2026-11-13T09:12:30Z","revision":1,"words":null,"option":"yes","resolution":"resolution:review:demo-task:1","channel":"review","said_at":"2026-11-13T09:11:02Z"}
{"v":1,"event":"acted","key":"demo-task#1","at":"2026-11-13T09:15:00Z","what":"Filed the task","refs":[{"kind":"commit","ref":"0123abc","ready":true}]}
```

## 7. Writer (FO side), for orientation only

The FO records each event with one command at the moment it happens, for example
`task_timeline.py <state> <task> ask "<question>" --channel dialog --holds nothing
--option yes="Open it" --recommend yes --grounds "..."`, and later
`... answer <key> --words "..."`. The tool stamps `at`, assigns `key`, and refuses a
line that breaks this document. A reader does not need the tool.

## 8. Not covered by version 1 (open)

- A question that belongs to no task yet (for example "should I open a task for
  X?"). Version 1 has no place for it.
- Gate questions. Whether a lister also shows open Spacedock gates as rows of kind
  `gate`, read from the task files' `gates:` frontmatter, is a design decision
  pending with the Captain.
- A rule that publishes a question to Spacedock Review after it has gone
  unanswered for a number of turns is pending with the Captain; if adopted it
  appears here only as `reask` lines with `channel: review`.
