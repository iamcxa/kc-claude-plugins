## Where new information goes

Not everything you learn belongs in an ADR. Pick the home by who will rely on it:

| Information | Home | Who writes it |
| --- | --- | --- |
| A direction that spans repos; a life, career or finance ruling that has no engineering repo | The decision space, `../mira-decisions/docs/adr/`: draft a new numbered ADR file there (never edit an existing one) | You draft; Mira confirms and merges it by pull request |
| A product rule, limit or direction inside one engineering repo that will constrain later work | A new numbered ADR in that repo's `docs/adr/` | You write the file; the coordinator confirms it |
| A trade-off that matters only to the one task | The task file (`tasks/TASK-NNN.md`) | You |
| A deferred user-facing feature | The story map (`docs/journey/story-map.md`) | You, in its Deferred section |
| How agents should work in a repository | `AGENTS.md` / `CLAUDE.md` | Mira, or you with her agreement |
| Your own notes and hunches | `.agent/notes.md`; never an authority | You |
| Scope an agent may decide alone | A dedicated authorisation ADR; money, merges, outside actions and irreversible changes are never authorised | Mira decides |

Principle: what other agents or later work will rely on goes in a versioned place a person confirmed (the decision space or an ADR). What affects only the current task stays in the task. What describes how to work goes in the instruction file. Do not turn every piece of information into an ADR.
