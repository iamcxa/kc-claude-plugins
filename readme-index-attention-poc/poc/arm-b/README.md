---
commissioned-by: kc-dev-flow-2
entity-type: task
id-style: slug
entity-label: task
entity-label-plural: tasks
extensions: [roborev, codex, copilot, learn, peers]
second-reviewer: copilot
state: .spacedock-state
trunk: main
stages:
  defaults:
    worktree: false
    concurrency: 1
    model: sonnet
  states:
    - name: backlog
      initial: true
      gate: true
    - name: ideation
      gate: true
      context-sections:
        - Dispatch facts
    - name: implementation
      worktree: true
      context-sections:
        - Dispatch facts
        - Review-finding disposition
        - Decision records
        - Captain amendments
        - Affected documents
        - Number guards
    - name: validation
      worktree: true
      fresh: true
      feedback-to: implementation
      gate: true
      context-sections:
        - Dispatch facts
        - Review-finding disposition
        - Decision records
        - Captain amendments
        - Affected documents
        - Number guards
    - name: done
      terminal: true
---

# Development workflow
<!-- kc-dev-flow-2 0.24.0 x-release-please-version -->

This is the adopted workflow's authority for SD stages and task schema. Resolve
its absolute directory and retain `--workflow-dir` on SD commands, including
worker reads and recovery. Skills guide work; SD owns dispatch, gates and state.

## Rule index

This README is an index. Every rule of this workflow lives in one file under `rules/`
(relative to this README's directory). Open a file with the Read tool at the moment its
trigger below happens, before you act on it; a rule you did not open is a rule you did not
follow. Do not open a file whose trigger has not happened.

| File | Open it when |
| --- | --- |
| `rules/file-naming.md` | you locate or create a task file |
| `rules/schema.md` | you admit a task or check its profile against the stages |
| `rules/stages.md` | you pick a stage worker's or special agent's model; you record a call to chief-engineer, engineering-reviewer or observer; you run the package and checkout version checks, build or send any worker dispatch or follow-up message, save a dispatch record or name a package script in one; `status --set` refuses to leave a stage |
| `rules/stage-backlog.md` | a task is at backlog: gate content, seed check, release review, journey fields |
| `rules/stage-ideation.md` | a task is at ideation: alignment result, gate content, design corrections |
| `rules/stage-implementation.md` | a task enters implementation |
| `rules/stage-validation.md` | a task enters validation or its gate is prepared: gate content, acceptance script, POC boundary marker |
| `rules/stage-done.md` | a task reaches done |
| `rules/dispatch-facts.md` | you write down what a worker is told about completion signal, package root or secrets |
| `rules/review-finding-disposition.md` | a worker or reviewer reports a finding: materiality fields and categories |
| `rules/fo-steps-review-findings.md` | you decide what to do with a finding (decline, repair, hold), count external review rounds, put a Needs decision to the Captain, read his approval as a ruling, or write `Override:` / `Precedent:` |
| `rules/decision-records.md` | an ADR is written or validated |
| `rules/fo-steps-decision-records.md` | a ruling is settled at a gate, in a worker report or mid-stage; before the next gate is presented |
| `rules/captain-amendments.md` | the Captain changes something he has already accepted, or sends an approved task back to an earlier stage |
| `rules/affected-documents.md` | implementation exits or validation reruns the document-impact check |
| `rules/number-guards.md` | the task has a `db` surface, lands an ADR, or is a POC; migration and ADR numbering rules |
| `rules/fo-steps-number-guards.md` | before an implementation dispatch for such a task; before pushing to a shared environment; two tasks hold one number |
| `rules/delivery-authority.md` | before any push, PR, merge ask or merge; the `pr-merge` mod; a rework after merge guard |
| `rules/extensions.md` | a stage with a listed extension is dispatched, an extension's result is read, or a merge is asked |
| `rules/workflow-state.md` | you commit task state or set up the state checkout |
| `rules/task-template.md` | you create a task |
