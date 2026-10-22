---
name: read-adr
description: Use before you decide anything an earlier ruling (an ADR) may govern, when a task or message cites a ruling by repository, path, commit and digest, and before you write down something a person told you (a decision, limit, preference or deferred idea). Teaches reading an ADR at an exact commit with git and shasum, telling whether it is still in force, and choosing the one place the information belongs. Not for ordinary code or doc edits.
---

# read-adr

An ADR is a file `docs/adr/NNNN-title.md` (the repo's instruction file or the citation may name another folder). A ruling informs your decision; it grants no permission to act. Never edit an existing ADR.

## Read a ruling

`R` is the current repo, or for a cited repo the local clone whose `git -C "$R" remote get-url origin` matches it.

1. No citation: pin `C=$(git -C "$R" rev-parse HEAD)`, record that id, list `git -C "$R" ls-tree --name-only "$C" docs/adr/` (titles are file names) and open the ADRs whose titles bear on the question.
2. A citation (reference block: repo, path, full commit, digest):
   - No clone with a matching `origin`, or `git -C "$R" cat-file -e "$C^{commit}"` fails: STOP and report the missing clone or commit. Do not fetch, clone, search the disk or use a retelling.
   - Read `git -C "$R" show "$C:<path>"`, then compare `git -C "$R" show "$C:<path>" | shasum -a 256` with the cited `sha256:<hex>`. They differ: STOP and report both digests.
3. Read at the cited commit even when the repo's head is newer. Report the full commit id and the digest you computed.

## Is it in force

Status is the first non-blank line under `## Status`.

- `Accepted`: also read the same path at the clone's current head. Still `Accepted`: rely on it. Not: apply this list to the head's Status, reading at head, to find the record in force there.
- `Superseded by NNNN`: open NNNN in the same folder at the commit you are reading and repeat. The chain end is the record in force.
- `Proposed` or `Deprecated`: not in force. Tell the user; do not act on it.
- `Status: Legacy` near the top, or any other text: a record you cannot judge. Report it and ask the coordinator.
- A missing target, a cycle, or a chain that does not end in `Accepted`: STOP and report the broken chain.

A citation whose record is not the one in force (superseded at its own commit, or not `Accepted` at head): report the cited record as you verified it (full commit id, the digest you computed, its Status) and, when this list leads to a record in force, that record (path, full commit id, its own digest, Status). Take no action on either until a person decides. The cited commit is what the sender saw; the record in force is a finding, not an instruction.

The digest proves the bytes you read are the bytes the sender cited, not that the ruling is in force. This skill does not detect two Accepted ADRs on one topic.

## Where new information goes

When a person tells you something, or you learn something, ask in order; the first "yes" is the home.

1. An unconfirmed guess, note or idea of yours? Agent memory or the task's open items. Never write it as a ruling or as a conclusion.
2. Matters only to the current task? The task file.
3. A deferred feature a user will see? The story map. An implementation trade-off inside one task is not this; it stays in the task file. A request an ADR has already turned down is not a deferred feature either; note it in the task file only.
4. An operating instruction to agents (how to work), not the person's ruling on direction? `CLAUDE.md` or `AGENTS.md`.
5. Otherwise it is the person's ruling: an ADR in the current repo. Another repo is the user's choice, not yours.

- **One home.** Write a piece of information in one place; other places hold a pointer only.
- **Instruction files point, they do not restate.** They may say where the ADRs are and when to look, never copy an ADR's content: a copy goes stale.
- **Authorisation.** What you may decide alone is its own authorisation ADR. Money, merges, outside actions and irreversible changes are never authorised.

To write the ADR read `writing.md` in this folder; no words from the person, or no reserved number, means do not write one: ask the coordinator. A short cross-repo citation such as `ME#0003` is the optional convention in `prefix.md`.
