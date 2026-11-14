---
id:
title: Three or fewer tried ways to run the next real task on the extracted package with private state, each with what it costs the Captain
status: validation
variant: kc-dev-flow-2
profile: poc
merge: pr
worktree: .worktrees/spacedock-ensign-extracted-package-real-use-routes-probe-poc
pr:
gates:
    version: 1
    records:
        - id: gate:extracted-package-real-use-routes-probe-poc:backlog
          stage: backlog
          attempts:
            - id: gate-attempt:extracted-package-real-use-routes-probe-poc-backlog-1
              briefing:
                id: briefing:extracted-package-real-use-routes-probe-poc:backlog:attempt-1:revision-1
                digest: sha256:1f5a3a54febbff33d51a1a54505fee39d1a478bcaea3c95a0067c72569d2ed82
                room-ref: ./extracted-package-real-use-routes-probe-poc/review/backlog/briefing-1
              resolution:
                type: Resolution
                id: resolution:spacedock:extracted-package-real-use-routes-probe-poc:backlog:1
                briefing: briefing:extracted-package-real-use-routes-probe-poc:backlog:attempt-1:revision-1
                by: agent:first-officer
                at: "2026-11-14T12:16:04.05381Z"
                decision: approve
                reason: Inside scope 3 given by the reform session under the Captain's grant; no public merge, outward action, outcome-definition change or suspected key is involved in admission.
                conn:
                    quote: 改革工作階段（Paseo 代理 26215d96，就是開你出來的那一個）可以替我給你工作範圍。它給的範圍內，進場、設計、預算、結案這些關卡你不必停下來等我，記為「依艦長授權」，一路做到它指定的終點。
                    source: the Captain, chat with the second dev2 FO, 2026-11-14; scope 3 from the reform session, Paseo message 6dd41248-d90d-4c35-ba36-bc70f9e033d7
              application:
                target-stage: implementation
                state: consumed
        - id: gate:extracted-package-real-use-routes-probe-poc:validation
          stage: validation
          attempts:
            - id: gate-attempt:extracted-package-real-use-routes-probe-poc-validation-1
              briefing:
                id: briefing:extracted-package-real-use-routes-probe-poc:validation:attempt-1:revision-1
                digest: sha256:a52332b3a61ad2c4bd553880dc26269caafaa2f83c43478127d0285e7437b6b5
                room-ref: ./extracted-package-real-use-routes-probe-poc/review/validation/briefing-1
started: 2026-11-14T12:18:27Z
---

Nine of the sixteen approved outcomes can only be measured in real use, and nobody uses the extracted package yet. The next real task of the reform should be run by a First Officer and workers that load the extracted package, not the installed one, with its task state in a private place from the first commit.

## Scope

- Source: the reform session's scope 3 under the Captain's standing grant to the second dev2 FO (Paseo 26215d96, message 6dd41248, 2026-11-14); it reports that the Captain approved the order with "Go ahead with the plan." in its own conversation (relayed, not a ruling here). Admission is recorded by FO under the grant.
- Outcome: a probe that answers by trying the smallest step of each route, not by reasoning: where the workflow and its state live (the private working repository is the obvious home; its state branch would be private); how a session loads the extracted package without colliding with the installed package of the same skill names (a temporary plugin name is allowed; the public name is not decided); whether that is cleaner on the laptop or on the clean host, where nothing else is installed but the repository key is read-only and the sign-in can only make model requests; what each route needs from the Captain (a plugin install on his laptop, a write credential on the host, a second host in his daily view). Output: at most three options, each with what was actually tried, what it costs him, and what breaks.
- The probe leaves no lasting change: anything it installs, registers or creates to try a step is removed again and listed, or kept only inside a scratch location it names.
- consumer: the reform session and the Captain choosing a route; bite: no extracted-package task has ever been run.
Non-goals: building the chosen option; migrating the two products; any change to the installed package; retiring the public state branch; hook work; anything on the open pull requests or the release.
Budget: 1 implementation and 1 validation cycles
Stop condition: one hour from dispatch, then stop and bring the options; at half of that, one check whether the probe still serves the stated goal; a step that would need a credential, a plugin install on the Captain's laptop outside a scratch location, or a write to a shared configuration: do not take it, list it as what that route needs from him.

## Acceptance criteria

**AC-1**: The report gives at most three options, and for each: the smallest step actually tried with its command and observed result, what it needs from the Captain, and what breaks.
Verified by: the validator re-runs one tried step per option where it leaves no lasting change, and reads the rest against the recorded outputs. Limit: a probe, not a working setup.

**AC-2**: Nothing the probe did is left behind outside its named scratch locations.
Verified by: the report's list of what was created and removed, checked by the validator on the laptop and, by listing only, on the clean host.

## FO alignment

Alignment: not needed before implementation: the questions and the stop are stated in the scope; the options go to the reform session and the Captain, who choose.
Release review: not needed: a probe.

## Stage Report: implementation

- DONE: At most three routes for running a real task on the extracted package with private task state, each answered by trying its smallest step, not by reasoning: where the workflow and state branch live; how a session loads the extracted package without colliding with the installed package of the same skill names; laptop or clean host. For each: the command tried and its observed output, what it needs from the Captain, what breaks
  Three routes in the table below; every step and its trimmed output is in evidence/implementation-1/observed-steps.txt (L1-L9 laptop, H1-H6 host), 20:20-20:26 local, finished inside the one-hour box so the 30-minute check was not reached.
- DONE: A list of everything created, installed or registered during the probe and its removal, or the scratch location it stays in; no credential used beyond what the session already has, no plugin install on the Captain's laptop outside a scratch location, no write to a shared configuration: a step needing one is listed as what that route needs from him and not taken
  See "Created and removed" below; nothing installed or registered, no credential read or copied, no shared configuration written by the probe.
- DONE: A stage report in the task file with the options table and the limits of the probe; no recommendation acted on
  Table and limits below; no route was built, chosen or migrated.

### Options table

State layout common to all three (tried in a scratch repository with a local bare repository as its origin, laptop and host): the workflow README stays in the code repository and the task files live in an orphan state branch's checkout. `spacedock state init --workflow-dir docs/dev2` on a fresh clone gave "Initialized state checkout ... (branch spacedock-state/dev2)"; `spacedock new` created the task there and the code repository's `git status` stayed clean (L7, L8, H4). So "private state from the first commit" means: the private repository's own remote holds the state branch. Not tried: a push to the real private remote.

| | Route 1: laptop, same-name session plugin | Route 2: laptop, renamed copy beside the installed package | Route 3: clean host, same-name session plugin |
|---|---|---|---|
| Smallest step tried | `claude -p --plugin-dir <PKG>` then Skill `kc-dev-flow-2:implementation` (L3, L4); FO launch `spacedock claude "..." -- --plugin-dir <PKG>` (L9) | same Skill call with `<PKG>` copy named `kc-dev-flow-2-wip` (L5, L6) | `claude -p --plugin-dir <host PKG>` and the same Skill call (H3, H5), state steps (H4) |
| Observed | Init lists `kc-dev-flow-2@inline 0.41.0`; the installed `kc-dev-flow-2@kc-claude-plugins` is not listed (replaced); Skill reports `Package root: <PKG>`; the launcher printed "Workflow: docs/dev2" and loaded spacedock and the inline package | `Package root:` came back as the INSTALLED copy; 73 plugin-qualified names in 39 files and a literal `variant == "kc-dev-flow-2"` check in scripts point at the original name | Init lists `kc-dev-flow-2@inline` and `spacedock@spacedock`; Skill reports `Package root: <host PKG>`; the host already has Spacedock 0.28.0 and a working sign-in |
| Needs from the Captain | Nothing for a session on his sign-in. An isolated config home needs a login in it (L2: `api_error`, no sign-in), which was not taken. A write path from the laptop to the private remote for the state branch (not tried) | A decision to rename the package everywhere (not done) | A write credential on the host for the state branch push (not taken; known read-only), or state kept only on the host; the host is already registered and online in Paseo (H6, listing only) |
| What breaks | The installed package is hidden in that session, so a session meant to use both cannot; every launcher must add the flag, and a worker started by another launcher (Paseo) was not tried and the provider list shows no plugin-directory option | The installed package answers to the original skill names, so workers load the wrong copy; renaming means editing the package | Host Claude Code is 2.1.311 and Spacedock 0.28.0, against laptop 2.1.323 and 0.27.2; the package text names Spacedock 0.27.2 report parsing, untested on 0.28.0; the key cannot push state |

### Created and removed

- Laptop scratch folder (named scratch location): kept for now, holds this draft, the evidence and the scratch workflow repository. The private package copies in it were deleted. `scratch.py close` was NOT run, see Summary.
- Laptop real configuration home: two empty-or-one-file project directories created by my sessions; both removed. Checked: no entry for the scratch path in the user-level settings file; no launcher state written under the Spacedock home. Cache temp directories under the plugin cache belong to other sessions, not removed.
- Host: scratch folder under the user's home and two project directories in the Claude home created by my sessions; all removed. Left: one 92-byte builtin-plugin store file created by Claude itself on the host at the first session (`plugins/store/cc-plugin-agents-md_builtin-*.json`), because the host runs other sessions and the file is shared state.
- Nothing installed, no marketplace registered, no setting written, no credential printed or copied; model requests (L2-L5, L9, H3, H5) used the sign-in each machine's session already had, each one to four turns.

### Limits of the probe

- Non-interactive one-turn sessions; no dispatched worker, gate or merge was run on the extracted package, so no outcome among the nine measurable ones was measured.
- Paseo-launched worker sessions were not tried: starting one would create an agent, and nothing here shows whether one can be given a plugin directory.
- The private remote was never written to; the state branch was proven only against a local bare repository.
- Laptop and host differ in two version numbers; whether that matters was not tested beyond `state init`, `new` and `status`.

### Summary

All three routes were tried to their smallest step in about six minutes, and the answers are in the table; no recommendation is made or acted on. This report is a draft held in the scratch folder, not in the task file: both attempts to write into the state checkout (a shell write and the Write tool) were denied by the permission classifier as "Unsanctioned Communication", so FO needs to place this report and the evidence file into the task folder, or tell me how to proceed, before `scratch.py close` is run.

## Stage Report: implementation

- DONE: At most three routes for running a real task on the extracted package with private task state, each answered by trying its smallest step, not by reasoning: where the workflow and state branch live; how a session loads the extracted package without colliding with the installed package of the same skill names; laptop or clean host. For each: the command tried and its observed output, what it needs from the Captain, what breaks
  Three routes in the table; first-round steps L1-L9 and H1-H6 in evidence/implementation-1/observed-steps.txt, follow-up steps Q1a-Q2e in evidence/implementation-2/observed-steps-2.txt.
- DONE: A list of everything created, installed or registered during the probe and its removal, or the scratch location it stays in; no credential used beyond what the session already has, no plugin install on the Captain's laptop outside a scratch location, no write to a shared configuration: a step needing one is listed as what that route needs from him and not taken
  See "Created and removed"; the only installs and registrations were inside scratch config homes; the user-level state file and every Paseo setting were left unchanged.
- DONE: A stage report in the task file with the options table and the limits of the probe; no recommendation acted on
  This report; no route was built or chosen.
- DONE: Can a worker started through Paseo load the extracted package, with project-level settings only, nothing registered or installed (follow-up item 1)
  No. Keys used and their source are in the table notes. The Paseo worker reported "UNKNOWN SKILL" (Q1d). Two observed causes: the folder was not trusted (Q1c), and once trusted, a same-named installed plugin kept the name even with `enabledPlugins` false for the project (Q1e, Q1f). No package root was obtainable by this route.
- DONE: Whether Paseo can pass a launch flag or environment to a provider's session, and what a second provider carrying the plugin-directory flag would take (follow-up item 2)
  Yes in shape: a provider entry has `extends`, `label`, `command` (an argument list, already carrying `--agent spacedock:first-officer`) and an optional `env` map (Q2a-Q2c). The flag form and the variable form both worked on the claude command line (Q2e, Q1g). Not tried through Paseo: creating a provider is the Captain's.
- DONE: This superseding stage report draft, with the options table extended by both results and one Captain sentence per option (follow-up item 3)
  Table below.

### Options table (extended)

| | Route 1: laptop, same-name session plugin | Route 2: laptop, renamed copy beside the installed package | Route 3: clean host, same-name session plugin |
|---|---|---|---|
| FO session | `spacedock claude "..." -- --plugin-dir <PKG>` loads it and finds the workflow (L9) | the installed package answers the original skill names (L5) | the flag loads it on the host's Claude Code 2.1.311 (H3, H5) |
| Worker started through Paseo, settings only | Fails: untrusted folder skips the project skills directory (Q1c, Q1d); trusted, the installed same-name plugin still wins when disabled for the project (Q1f) | not tried | not tried (the host's Paseo configuration was not read) |
| Worker started through Paseo, flag or variable | Needs a second provider whose command or env carries `--plugin-dir <PKG>` or `CLAUDE_CODE_PLUGIN_DIRS=<PKG>`; both work on the command line (Q2e, Q1g); through Paseo untried | n/a | same, in the host daemon's own provider list (not read) |
| What the Captain must do | add one provider entry to his Paseo configuration (a copy of the first-officer one plus the flag or variable), or launch every first officer himself with the flag | decide to rename the package everywhere | grant a write credential for the state branch, or keep state host-only; add the provider entry on the host |
| What breaks | the installed package is hidden in sessions carrying the flag, and any worker from a provider without it loads the installed copy | workers load the installed copy; renaming means editing 39 files | older Claude Code and Spacedock than the laptop (2.1.311 and 0.28.0); key is read-only, so the state branch cannot be pushed |

Notes on the settings-only attempt: `enabledPlugins` `{"<name>@<marketplace>": false}` in `.claude/settings.local.json` and a plugin directory at `.claude/skills/<name>/` are the documented keys (https://code.claude.com/docs/en/plugins/loading, https://code.claude.com/docs/en/plugins/install); the trust dialog writes a per-project entry into the user-level state file, which the probe did not do outside a scratch home. Project and local settings cannot set `CLAUDE_CODE_PLUGIN_DIRS` (same loading page).

### Created and removed

- Scratch folder `implementation-2` (named scratch location): holds the drafts, a scratch config home with a stub marketplace and stub plugin, and the scratch repository; the private package copies were deleted from it.
- Paseo: one workspace and one agent created, both archived; the archive soft-deletes, so their records remain in Paseo's own store (one project record, one workspace record, one agent record). No provider or configuration changed; the configuration file was read for key names and the first-officer command only.
- Laptop Claude home: one transcript directory written by the Paseo worker, removed; the user-level state file has no entry for the scratch path; no install, marketplace or setting written outside the scratch config home.
- Model requests: one Paseo worker (one skill call) and three short `claude -p` turns on the existing sign-in.

### Limits of the probe

- The flag and variable routes were tried on the claude command line, not through a Paseo provider; whether Paseo's safehouse wrapper (create_agent returned type safehouse-claude) carries a new provider's command and env was not observed.
- The trust and name-conflict results come from Claude Code 2.1.323 with a stub standing in for the installed package; the real installed package was only present in the first Paseo attempt, where it was disabled and the folder untrusted.
- The host's Paseo configuration and its first-officer provider were not read.

### Summary

This supersedes the earlier implementation report. A worker started through Paseo cannot load the extracted package from project settings alone: the folder must be trusted, and a same-named installed plugin still holds the name even when disabled for the project. The one mechanism that replaced the installed copy in every test is the session plugin flag or variable, which Paseo could carry in a second provider entry; that entry is the Captain's to add and was not tried through Paseo.
