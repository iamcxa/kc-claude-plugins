# Adoption question journey, FO-run, 2026-11-01, candidate a8536dc52

Four scratch repositories whose workflow lists paseo, Codex available. The Captain answered through the host's question dialog; each round named the path being exercised, so this proves what each answer writes, not how an unprompted Captain would answer.

| Round | Captain's answer | Result |
|---|---|---|
| Accept | selected Accept | three displayed rows written, one reviewed commit, fresh-shell resolve returns the tuple |
| Customize | selected Customize, then Astra/xhigh, Astra/high, Astra/xhigh one stage at a time | exactly those rows written and committed, resolve returns them |
| Cancel | typed 「取消」 | no file, no directory, manifest unchanged, resolve source readme-default |
| Unanswered | dismissed the dialog; the Captain: 「我關閉了，按 esc ，ui 上有 dismiss 可以按」 | same as Cancel |

The question ran on a Claude host through its dialog. Not exercised: the Codex host's question UI, and a real sync over a committed file.

## Real stage calls, 2026-11-01

The PR #757 and PR #759 validations were dispatched through the candidate's resolver: resolve, Roster header in the record, names check, build, immediate spawn. Requested versus child-reported settings are in spawn-757-validation.json and spawn-759-validation.json; both records carry the Roster header. Scratch rosters from this folder supplied the tuples.

Run: Astra/high and Astra/xhigh, so a changed supported effort on one model. Not run through the resolver: Sol/high, an unchanged continuation and a changed-tuple continuation. The #757 call passed no --author-record, so its family reads unverified; that was FO's omission.

Sources, extracted by FO from its transcript, FO's own record: question-receipts.jsonl (each question and answer with time), fo-commands.jsonl (the commands in order, including preflight, resolve, record, build and spawn). FO deleted the scratch repositories after the rounds; only the committed roster files, cancel and unanswered manifest results above and the commands remain, so a reviewer cannot re-inspect those repositories.
The validation-1 record carries the Roster header but no author references or family, because FO's dispatch script does not add them: the resolver reported them (family and authors) and FO did not copy them across. That is a gap in this record.
