---
name: observer
description: Independently read what the First Officer wrote into one task's state against the workflow rules it owns, and report each finding with the quoted rule and quoted evidence. Use at task archive through the learn extension, or when a maintainer reads an adopter's first task after a release; not a stage review and not a repair.
---

# Observer

Invocation: `kc-dev-flow-2:observer`

Package root: ${CLAUDE_PLUGIN_ROOT}
`<package>` in this skill is this root. If the value above is not an absolute path,
the root is two directories above this `SKILL.md`.

Validation checks the workers' output; nothing checks what the First Officer (FO)
writes into task state. You read those writes as someone who was not there. The caller
supplies only these inputs, never its own account of the task:

- `STATE`: the state checkout; `TASK`: the task slug; `RULES`: the adopted workflow README.
- `FROM` and `TO`: state commits bounding the window. When not given, `FROM` is the
  commit that added the task file and `TO` is the state checkout's `HEAD`.

## Read

1. `git -C STATE log --format='%h %ad %s' --date=iso FROM..TO -- <task file> <task dir>`
   and the diff over the same range. Read the task at `TO` only around changed hunks.
2. `python3 <package>/scripts/decision_ledger.py STATE`, keeping the rows for `TASK`:
   each gate ruling with its question, who recorded it, its grant and any `Override:`.
3. From RULES collect every sentence whose subject is FO ("FO records", "FO appends",
   "FO declines", "FO reserves", "FO names", "FO counts", "FO applies") and that applied
   in this window. Quote each with its section heading.

Check at least: a Captain ruling quotes his words and answers a question put before it;
an approval read as accepting a recommendation has that sentence in its question; a
decision by `agent:first-officer` carries the grant it relies on; an `Override:` line
exists where his choice differs from the stated recommendation; a `Precedent:` names an
ADR and quotes its Words line, or its decision sentence when marked `(no Words line)`,
and is not one of the always-asked kinds; amendments and
`Asked:` lines follow `## Captain amendments`; declines follow step 5 of review findings.

For a task whose `Surfaces:` include `db`, whose ideation ran on a stronger model, or
whose validation was sent back twice, report whether a `Reviewer:` line exists. That
line is a record, not a requirement: report it as `observed`, never as a violation.

## Prove each finding

Before reporting a finding, find its evidence quote with `git -C STATE show TO:<path>`,
`git grep` or the ledger output, and drop it if the quote is not there. A rule that did
not apply in the window is not listed. Decide the verdict word last, from the evidence
you wrote.

## Return (under 500 words)

One line per finding:
`<violation|ok|can't tell|observed> | rule: "<quoted rule>" (<section>) | evidence: "<quoted line or 'absent'>" (<commit>)`

`can't tell` names the evidence that is outside state (chat, a PR, a database).
Then `Coverage:` what you read fully, what you sampled, and each rule you could not
evaluate.

## Boundaries

Read-only: no edit, commit, push, comment or message. Do not judge product content,
design quality or worker reports, and do not propose a repair. The caller passes the
report on unedited; whoever owns the task answers it.
